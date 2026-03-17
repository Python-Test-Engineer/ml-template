"""Phase 4 - Feature Engineering & Modelling
Trains Logistic Regression, Random Forest, and XGBoost to predict
loss-making orders. Evaluates with stratified 5-fold CV.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    roc_curve,
    f1_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

# -- Constants -----------------------------------------------------------------
OUTPUT_DIR = Path("output/PROJECT_02")
MODEL_DIR = OUTPUT_DIR / "model"
PLOTS_DIR = OUTPUT_DIR / "plots"
RANDOM_SEED = 42
N_SPLITS = 5
DPI = 150

CATEGORICAL_FEATURES = ["Ship Mode", "Segment", "Category", "Sub-Category", "Region"]
NUMERIC_FEATURES = [
    "Sales", "Quantity", "Discount", "days_to_ship",
    "order_month", "order_year", "order_dayofweek",
]
TARGET = "is_loss"

sns.set_theme(style="whitegrid")


# -- Helpers -------------------------------------------------------------------
def load_data() -> pd.DataFrame:
    path = OUTPUT_DIR / "superstore_clean.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Required input not found: {path}. Run phase1_etl.py first.")
    return pd.read_parquet(path)


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
            ("num", "passthrough", NUMERIC_FEATURES),
        ]
    )


def build_pipelines(neg_pos_ratio: float) -> dict[str, Pipeline]:
    preprocessor = build_preprocessor()
    return {
        "Logistic Regression": Pipeline([
            ("pre", preprocessor),
            ("clf", LogisticRegression(
                max_iter=1000, C=1.0, class_weight="balanced",
                random_state=RANDOM_SEED,
            )),
        ]),
        "Random Forest": Pipeline([
            ("pre", build_preprocessor()),
            ("clf", RandomForestClassifier(
                n_estimators=200, class_weight="balanced",
                random_state=RANDOM_SEED, n_jobs=-1,
            )),
        ]),
        "XGBoost": Pipeline([
            ("pre", build_preprocessor()),
            ("clf", XGBClassifier(
                n_estimators=200, max_depth=6, learning_rate=0.1,
                scale_pos_weight=neg_pos_ratio,
                random_state=RANDOM_SEED, eval_metric="logloss",
                verbosity=0,
            )),
        ]),
    }


def cross_validate_model(
    pipeline: Pipeline, X: pd.DataFrame, y: pd.Series, cv: StratifiedKFold
) -> tuple[list[float], list[float]]:
    aurocs, f1s = [], []
    for train_idx, val_idx in cv.split(X, y):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        pipeline.fit(X_train, y_train)
        y_prob = pipeline.predict_proba(X_val)[:, 1]
        y_pred = (y_prob >= 0.5).astype(int)
        aurocs.append(roc_auc_score(y_val, y_prob))
        f1s.append(f1_score(y_val, y_pred, average="macro"))
    return aurocs, f1s


def extract_rf_feature_names(pipeline: Pipeline, X: pd.DataFrame) -> list[str]:
    ohe = pipeline.named_steps["pre"].named_transformers_["cat"]
    cat_names = ohe.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    return cat_names + NUMERIC_FEATURES


def save_fig(fig: plt.Figure, name: str) -> None:
    path = PLOTS_DIR / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved plot: {path.name}")


# -- Main ----------------------------------------------------------------------
def main() -> None:
    print("[Phase 4] Loading data...")
    df = load_data()
    print(f"  Shape: {df.shape}  |  Loss rate: {df[TARGET].mean():.1%}")

    X = df[CATEGORICAL_FEATURES + NUMERIC_FEATURES]
    y = df[TARGET]

    n_neg = (y == 0).sum()
    n_pos = (y == 1).sum()
    neg_pos_ratio = n_neg / n_pos
    print(f"  Class balance — 0: {n_neg}  1: {n_pos}  ratio: {neg_pos_ratio:.2f}")

    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_SEED)
    pipelines = build_pipelines(neg_pos_ratio)

    records = []
    refitted: dict[str, Pipeline] = {}

    for name, pipeline in pipelines.items():
        print(f"\n[Phase 4] Training {name}...")
        aurocs, f1s = cross_validate_model(pipeline, X, y, cv)
        print(f"  CV AUROC: {np.mean(aurocs):.4f} +/- {np.std(aurocs):.4f}")
        print(f"  CV F1-macro: {np.mean(f1s):.4f} +/- {np.std(f1s):.4f}")

        # Refit on full dataset
        pipeline.fit(X, y)
        refitted[name] = pipeline

        y_pred_full = pipeline.predict(X)
        cr = classification_report(y, y_pred_full, output_dict=True)

        records.append({
            "model_name": name,
            "cv_auroc_mean": round(np.mean(aurocs), 4),
            "cv_auroc_std": round(np.std(aurocs), 4),
            "cv_f1_mean": round(np.mean(f1s), 4),
            "cv_f1_std": round(np.std(f1s), 4),
            "precision_0": round(cr["0"]["precision"], 4),
            "recall_0": round(cr["0"]["recall"], 4),
            "f1_0": round(cr["0"]["f1-score"], 4),
            "precision_1": round(cr["1"]["precision"], 4),
            "recall_1": round(cr["1"]["recall"], 4),
            "f1_1": round(cr["1"]["f1-score"], 4),
        })

    # Save classification report
    report_df = pd.DataFrame(records)
    out = MODEL_DIR / "classification_report.csv"
    report_df.to_csv(out, index=False)
    print(f"\n  Saved: {out.name}")
    print(report_df[["model_name", "cv_auroc_mean", "cv_f1_mean"]].to_string(index=False))

    # -- Feature importance plot (Random Forest) ─────────────────────────────
    print("\n[Phase 4] Plotting feature importances (Random Forest)...")
    rf_pipeline = refitted["Random Forest"]
    feature_names = extract_rf_feature_names(rf_pipeline, X)
    importances = rf_pipeline.named_steps["clf"].feature_importances_
    fi_df = pd.DataFrame({"feature": feature_names, "importance": importances})
    fi_df = fi_df.sort_values("importance", ascending=True).tail(20)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(fi_df["feature"], fi_df["importance"], color="steelblue")
    ax.set_title("Top 20 Feature Importances (Random Forest)")
    ax.set_xlabel("Importance")
    save_fig(fig, "15_feature_importance.png")

    # -- ROC curves ─────────────────────────────────────────────────────────
    print("[Phase 4] Plotting ROC curves...")
    fig, ax = plt.subplots(figsize=(8, 7))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    for (name, pipeline), color in zip(refitted.items(), colors):
        y_prob = pipeline.predict_proba(X)[:, 1]
        fpr, tpr, _ = roc_curve(y, y_prob)
        auc = roc_auc_score(y, y_prob)
        ax.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})", color=color, linewidth=2)
    ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random baseline")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves — Loss-Order Prediction")
    ax.legend()
    save_fig(fig, "16_roc_curves.png")

    print("\n[Phase 4] OK - Model artefacts saved.")


if __name__ == "__main__":
    main()
