"""Phase 3 - Statistical Analysis
Correlation matrix, Kruskal-Wallis, chi-square, discount breakeven,
RFM scoring, STL decomposition.
"""
from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.tsa.seasonal import STL

# -- Constants -----------------------------------------------------------------
OUTPUT_DIR = Path("output/PROJECT_02")
PLOTS_DIR = OUTPUT_DIR / "plots"
TABLES_DIR = OUTPUT_DIR / "tables"
RANDOM_SEED = 42
ALPHA = 0.05
DPI = 150

sns.set_theme(style="whitegrid")


# -- Helpers -------------------------------------------------------------------
def load_superstore() -> pd.DataFrame:
    path = OUTPUT_DIR / "superstore_clean.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Required input not found: {path}. Run phase1_etl.py first.")
    return pd.read_parquet(path)


def save_fig(fig: plt.Figure, name: str) -> None:
    path = PLOTS_DIR / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved plot: {path.name}")


# -- Analysis functions --------------------------------------------------------

def correlation_heatmap(ss: pd.DataFrame) -> None:
    print("[Phase 3] Correlation matrix...")
    numeric_cols = ["Sales", "Quantity", "Discount", "Profit", "days_to_ship", "profit_margin"]
    corr = ss[numeric_cols].corr(method="pearson")
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                square=True, linewidths=0.5, ax=ax)
    ax.set_title("Pearson Correlation Matrix")
    save_fig(fig, "12_correlation_heatmap.png")


def profit_by_category_table(ss: pd.DataFrame) -> None:
    print("[Phase 3] Profit by category table...")
    agg = ss.groupby(["Category", "Sub-Category"]).agg(
        count=("Profit", "count"),
        mean_profit=("Profit", "mean"),
        median_profit=("Profit", "median"),
        mean_profit_margin=("profit_margin", "mean"),
    ).reset_index()
    loss_pct = ss.groupby(["Category", "Sub-Category"])["is_loss"].mean().reset_index()
    loss_pct.columns = ["Category", "Sub-Category", "pct_loss"]
    agg = agg.merge(loss_pct, on=["Category", "Sub-Category"])
    agg["pct_loss"] = (agg["pct_loss"] * 100).round(2)
    out = TABLES_DIR / "profit_by_category.csv"
    agg.to_csv(out, index=False)
    print(f"  Saved: {out.name}  ({len(agg)} rows)")


def kruskal_wallis_tests(ss: pd.DataFrame) -> list[dict]:
    print("[Phase 3] Kruskal-Wallis tests...")
    tests = [
        ("Profit ~ Region", "Region"),
        ("Profit ~ Segment", "Segment"),
        ("Profit ~ Category", "Category"),
    ]
    results: list[dict] = []
    for test_name, col in tests:
        groups = [grp["Profit"].values for _, grp in ss.groupby(col)]
        h_stat, p_val = stats.kruskal(*groups)
        conclusion = "significant" if p_val < ALPHA else "not significant"
        results.append({
            "test_name": test_name,
            "statistic": round(h_stat, 4),
            "p_value": round(p_val, 6),
            "dof": len(groups) - 1,
            "conclusion": conclusion,
        })
        print(f"  {test_name}: H={h_stat:.2f}, p={p_val:.4e} -> {conclusion}")
    return results


def chi_square_test(ss: pd.DataFrame) -> dict:
    print("[Phase 3] Chi-square test (Segment x Ship Mode)...")
    ct = pd.crosstab(ss["Segment"], ss["Ship Mode"])
    chi2, p_val, dof, _ = stats.chi2_contingency(ct)
    conclusion = "significant" if p_val < ALPHA else "not significant"
    print(f"  chi2={chi2:.2f}, p={p_val:.4e}, dof={dof} -> {conclusion}")
    return {
        "test_name": "Segment x Ship Mode (chi-square)",
        "statistic": round(chi2, 4),
        "p_value": round(p_val, 6),
        "dof": dof,
        "conclusion": conclusion,
    }


def discount_breakeven(ss: pd.DataFrame) -> None:
    print("[Phase 3] Discount breakeven analysis...")
    ss2 = ss.copy()
    ss2["discount_bin"] = pd.cut(ss2["Discount"], bins=10)
    agg = ss2.groupby(["Category", "discount_bin"])["Profit"].mean().reset_index()
    agg.columns = ["Category", "discount_bin", "mean_profit"]
    agg = agg.sort_values(["Category", "discount_bin"])

    records = []
    for cat, grp in agg.groupby("Category"):
        be_row = grp[grp["mean_profit"] < 0].head(1)
        if not be_row.empty:
            records.append({
                "Category": cat,
                "breakeven_discount_bucket": str(be_row["discount_bin"].values[0]),
                "mean_profit_at_breakeven": round(be_row["mean_profit"].values[0], 2),
            })
        else:
            records.append({
                "Category": cat,
                "breakeven_discount_bucket": "never negative",
                "mean_profit_at_breakeven": None,
            })

    df_be = pd.DataFrame(records)
    out = TABLES_DIR / "discount_breakeven.csv"
    df_be.to_csv(out, index=False)
    print(f"  Saved: {out.name}")
    print(df_be.to_string(index=False))


def rfm_scoring(ss: pd.DataFrame) -> None:
    print("[Phase 3] RFM scoring...")
    ref_date = ss["Order Date"].max() + pd.Timedelta(days=1)

    rfm = ss.groupby("Customer ID").agg(
        Recency=("Order Date", lambda x: (ref_date - x.max()).days),
        Frequency=("Order ID", "nunique"),
        Monetary=("Sales", "sum"),
    ).reset_index()

    # Quartile scores: 4 = best
    rfm["R"] = pd.qcut(rfm["Recency"], q=4, labels=[4, 3, 2, 1]).astype(int)
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
    rfm["M"] = pd.qcut(rfm["Monetary"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
    rfm["RFM_Score"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)

    def segment(row: pd.Series) -> str:
        r, f, m = row["R"], row["F"], row["M"]
        if r == 4 and f == 4 and m == 4:
            return "Champions"
        if r >= 3 and f >= 3 and m >= 4:
            return "Loyal"
        if r <= 2 and f <= 2 and m <= 2:
            return "At Risk"
        return "Mid-tier"

    rfm["Segment"] = rfm.apply(segment, axis=1)
    rfm["Recency"] = rfm["Recency"].astype(int)
    rfm["Frequency"] = rfm["Frequency"].astype(int)
    rfm["Monetary"] = rfm["Monetary"].round(2)

    out = TABLES_DIR / "rfm_scores.csv"
    rfm.to_csv(out, index=False)
    print(f"  Saved: {out.name}  ({len(rfm)} customers)")
    print(rfm["Segment"].value_counts().to_string())

    # Plot segment distribution
    seg_counts = rfm["Segment"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5))
    seg_counts.plot(kind="bar", color=sns.color_palette("tab10", n_colors=len(seg_counts)), ax=ax)
    ax.set_title("RFM Customer Segments")
    ax.set_xlabel("Segment")
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=30)
    save_fig(fig, "13_rfm_segments.png")


def stl_decomposition(ss: pd.DataFrame) -> None:
    print("[Phase 3] STL decomposition...")
    monthly = ss.set_index("Order Date").resample("MS")["Sales"].sum()
    monthly.index = monthly.index.to_period("M").to_timestamp()
    monthly = monthly.asfreq("MS", fill_value=0)

    stl = STL(monthly, period=12, robust=True)
    result = stl.fit()

    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    axes[0].plot(monthly.index, result.observed, color="steelblue")
    axes[0].set_title("Observed")
    axes[1].plot(monthly.index, result.trend, color="orange")
    axes[1].set_title("Trend")
    axes[2].plot(monthly.index, result.seasonal, color="green")
    axes[2].set_title("Seasonal")
    axes[3].plot(monthly.index, result.resid, color="red")
    axes[3].axhline(0, linestyle="--", color="black", linewidth=0.8)
    axes[3].set_title("Residual")
    fig.suptitle("STL Decomposition of Monthly Sales", y=1.01)
    fig.tight_layout()
    save_fig(fig, "14_stl_decomposition.png")


# -- Main ----------------------------------------------------------------------
def main() -> None:
    print("[Phase 3] Loading clean Superstore data...")
    ss = load_superstore()
    print(f"  Shape: {ss.shape}")

    correlation_heatmap(ss)
    profit_by_category_table(ss)

    kw_results = kruskal_wallis_tests(ss)
    chi2_result = chi_square_test(ss)

    all_tests = kw_results + [chi2_result]
    tests_df = pd.DataFrame(all_tests)
    out = TABLES_DIR / "statistical_tests.csv"
    tests_df.to_csv(out, index=False)
    print(f"  Saved: {out.name}")

    discount_breakeven(ss)
    rfm_scoring(ss)
    stl_decomposition(ss)

    print("\n[Phase 3] OK - All statistical outputs saved.")


if __name__ == "__main__":
    main()
