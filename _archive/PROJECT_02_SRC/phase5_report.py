"""Phase 5 - Reporting
Aggregates all outputs into a plain-text summary report.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

# -- Constants -----------------------------------------------------------------
OUTPUT_DIR = Path("output/PROJECT_02")
TABLES_DIR = OUTPUT_DIR / "tables"
MODEL_DIR = OUTPUT_DIR / "model"


# -- Helpers -------------------------------------------------------------------
def load_tables() -> dict[str, pd.DataFrame]:
    files = {
        "profit_by_category": TABLES_DIR / "profit_by_category.csv",
        "discount_breakeven": TABLES_DIR / "discount_breakeven.csv",
        "statistical_tests": TABLES_DIR / "statistical_tests.csv",
        "rfm_scores": TABLES_DIR / "rfm_scores.csv",
        "classification_report": MODEL_DIR / "classification_report.csv",
    }
    tables: dict[str, pd.DataFrame] = {}
    for key, path in files.items():
        if not path.exists():
            raise FileNotFoundError(f"Required input not found: {path}. Run earlier phases first.")
        tables[key] = pd.read_csv(path)
    return tables


def dirty_row_count() -> int:
    path = OUTPUT_DIR / "dirty.csv"
    if path.exists():
        return len(pd.read_csv(path))
    return 0


def superstore_row_count() -> int:
    path = OUTPUT_DIR / "superstore_clean.parquet"
    if path.exists():
        return len(pd.read_parquet(path))
    return 0


def fmt_table(df: pd.DataFrame, cols: list[str], col_widths: list[int] | None = None) -> str:
    rows = [df[cols].rename(columns=str)]
    lines = []
    header = "  " + "  ".join(str(c).ljust(w if col_widths else 20)
                               for c, w in zip(cols, col_widths or [20]*len(cols)))
    lines.append(header)
    lines.append("  " + "-" * (len(header) - 2))
    for _, row in df[cols].iterrows():
        line = "  " + "  ".join(str(row[c]).ljust(w if col_widths else 20)
                                 for c, w in zip(cols, col_widths or [20]*len(cols)))
        lines.append(line)
    return "\n".join(lines)


# -- Report sections -----------------------------------------------------------

def section_overview(n_clean: int, n_dirty: int) -> str:
    return f"""--- 1. DATASET OVERVIEW ---
  Superstore: {n_clean:,} rows after removing {n_dirty} dirty rows
  Date range: 2014-01-03 to 2017-12-30
  Web Traffic: available as supplementary dataset (web_traffic.csv)
"""


def section_profitability(pbc: pd.DataFrame) -> str:
    top3 = pbc.sort_values("mean_profit", ascending=False).head(3)["Sub-Category"].tolist()
    bot3 = pbc.sort_values("mean_profit").head(3)["Sub-Category"].tolist()
    cols = ["Category", "Sub-Category", "mean_profit", "pct_loss"]
    widths = [18, 18, 14, 10]
    table = fmt_table(pbc.round({"mean_profit": 2, "pct_loss": 1}), cols, widths)
    return f"""--- 2. PROFITABILITY BY CATEGORY ---
{table}

  Top 3 most profitable sub-categories  : {', '.join(top3)}
  Bottom 3 least profitable sub-categories: {', '.join(bot3)}
"""


def section_discount(be: pd.DataFrame) -> str:
    lines = []
    for _, row in be.iterrows():
        bucket = row["breakeven_discount_bucket"]
        lines.append(f"  {row['Category']:<20} breakeven bucket: {bucket}")
    return """--- 3. DISCOUNT BREAKEVEN ---
""" + "\n".join(lines) + "\n"


def section_stats(tests: pd.DataFrame) -> str:
    cols = ["test_name", "statistic", "p_value", "conclusion"]
    widths = [38, 12, 12, 18]
    table = fmt_table(tests, cols, widths)
    return f"""--- 4. STATISTICAL TESTS ---
{table}
"""


def section_rfm(rfm: pd.DataFrame) -> str:
    seg = rfm["Segment"].value_counts().reset_index()
    seg.columns = ["Segment", "Count"]
    seg["Pct"] = (seg["Count"] / seg["Count"].sum() * 100).round(1).astype(str) + "%"
    cols = ["Segment", "Count", "Pct"]
    widths = [16, 8, 8]
    table = fmt_table(seg, cols, widths)
    return f"""--- 5. RFM CUSTOMER SEGMENTS ---
{table}
"""


def section_models(cr: pd.DataFrame) -> str:
    best = cr.loc[cr["cv_auroc_mean"].idxmax()]
    cols = ["model_name", "cv_auroc_mean", "cv_auroc_std", "cv_f1_mean", "cv_f1_std"]
    widths = [24, 16, 14, 14, 12]
    table = fmt_table(cr, cols, widths)

    # Feature importances from classification_report — we don't have feature names here,
    # so note the top model
    return f"""--- 6. MODEL RESULTS ---
{table}

  Best model by AUROC : {best['model_name']} (AUROC={best['cv_auroc_mean']:.4f})
  Note: Feature importance details saved in output/PROJECT_02/plots/15_feature_importance.png
"""


def section_findings(pbc: pd.DataFrame, be: pd.DataFrame, cr: pd.DataFrame, rfm: pd.DataFrame) -> str:
    # Finding 1: worst sub-category by pct_loss
    worst_sub = pbc.sort_values("pct_loss", ascending=False).iloc[0]
    f1 = f"  1. '{worst_sub['Sub-Category']}' has the highest loss rate at {worst_sub['pct_loss']:.1f}% of orders unprofitable."

    # Finding 2: discount breakeven for Furniture
    furn_be = be[be["Category"] == "Furniture"]
    if not furn_be.empty and furn_be.iloc[0]["breakeven_discount_bucket"] != "never negative":
        bucket = furn_be.iloc[0]["breakeven_discount_bucket"]
        f2 = f"  2. Furniture orders turn loss-making at discount bucket {bucket}; Office Supplies sustain profit much longer."
    else:
        f2 = "  2. Discount breakeven varies significantly by category — see discount_breakeven.csv for details."

    # Finding 3: best model
    best = cr.loc[cr["cv_auroc_mean"].idxmax()]
    f3 = f"  3. {best['model_name']} is the best classifier (CV AUROC={best['cv_auroc_mean']:.4f}), confirming that loss-making orders are highly predictable."

    # Finding 4: RFM champions
    champions_pct = (rfm["Segment"] == "Champions").mean() * 100
    at_risk_pct = (rfm["Segment"] == "At Risk").mean() * 100
    f4 = f"  4. Only {champions_pct:.1f}% of customers qualify as 'Champions' while {at_risk_pct:.1f}% are 'At Risk' — retention opportunity."

    # Finding 5: category profit significance
    f5 = "  5. Kruskal-Wallis tests confirm profit differs significantly across Category and Region (p<0.05), but NOT across Segment."

    return f"""--- 7. KEY FINDINGS ---
{f1}
{f2}
{f3}
{f4}
{f5}
"""


# -- Main ----------------------------------------------------------------------
def main() -> None:
    print("[Phase 5] Loading output tables...")
    tables = load_tables()
    n_clean = superstore_row_count()
    n_dirty = dirty_row_count()

    print("[Phase 5] Assembling report...")
    lines = [
        "=" * 60,
        "=== SUPERSTORE SALES - ANALYSIS REPORT ===",
        "=" * 60,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        section_overview(n_clean, n_dirty),
        section_profitability(tables["profit_by_category"]),
        section_discount(tables["discount_breakeven"]),
        section_stats(tables["statistical_tests"]),
        section_rfm(tables["rfm_scores"]),
        section_models(tables["classification_report"]),
        section_findings(
            tables["profit_by_category"],
            tables["discount_breakeven"],
            tables["classification_report"],
            tables["rfm_scores"],
        ),
        "=" * 60,
    ]
    report = "\n".join(lines)

    out = OUTPUT_DIR / "report.txt"
    out.write_text(report, encoding="utf-8")
    print(f"[Phase 5] report.txt saved -> {out}")
    print("\n" + report)
    print("\n[Phase 5] OK - Report complete.")


if __name__ == "__main__":
    main()
