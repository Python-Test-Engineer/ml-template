"""Phase 5 — Report: assemble Markdown summary report from prior phase outputs."""

from pathlib import Path
from datetime import date
import pandas as pd

RANDOM_SEED = 42
OUTPUT_DIR = Path("output/PROJECT_01")
PLOTS_DIR = OUTPUT_DIR / "plots"

REQUIRED_FILES = [
    OUTPUT_DIR / "audit.csv",
    OUTPUT_DIR / "dirty.csv",
    OUTPUT_DIR / "clean.csv",
    OUTPUT_DIR / "stats.csv",
]

PLOT_FILES = [
    "hist_grid.png",
    "bar_traffic_source.png",
    "box_session_by_source.png",
    "box_bounce_by_source.png",
    "box_conversion_by_source.png",
    "scatter_duration_vs_bounce.png",
    "scatter_pageviews_vs_conversion.png",
    "scatter_previous_vs_conversion.png",
    "heatmap_correlation.png",
    "bar_metrics_by_source.png",
    "violin_previous_vs_duration.png",
]


def check_inputs() -> None:
    missing = [p for p in REQUIRED_FILES if not p.exists()]
    if missing:
        raise ValueError(f"Missing required input files: {missing}")
    missing_plots = [f for f in PLOT_FILES if not (PLOTS_DIR / f).exists()]
    if missing_plots:
        raise ValueError(f"Missing plot files: {missing_plots}")


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    audit = pd.read_csv(OUTPUT_DIR / "audit.csv")
    dirty = pd.read_csv(OUTPUT_DIR / "dirty.csv")
    clean = pd.read_csv(OUTPUT_DIR / "clean.csv")
    stats_df = pd.read_csv(OUTPUT_DIR / "stats.csv")
    return audit, dirty, clean, stats_df


def df_to_md_table(df: pd.DataFrame) -> str:
    header = "| " + " | ".join(str(c) for c in df.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    rows = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(v) for v in row.values) + " |")
    return "\n".join([header, sep] + rows)


def build_report(audit: pd.DataFrame, dirty: pd.DataFrame,
                 clean: pd.DataFrame, stats_df: pd.DataFrame) -> str:
    total_raw = len(clean) + len(dirty)
    dirty_count = len(dirty)
    clean_count = len(clean)

    # Dirty breakdown
    if dirty_count > 0:
        dirty_breakdown = dirty["reason"].value_counts().reset_index()
        dirty_breakdown.columns = ["Reason", "Count"]
    else:
        dirty_breakdown = pd.DataFrame(columns=["Reason", "Count"])

    # Numeric summary on clean data
    numeric_cols = ["Page Views", "Session Duration", "Bounce Rate",
                    "Time on Page", "Previous Visits", "Conversion Rate"]
    num_summary_rows = []
    for col in numeric_cols:
        s = clean[col]
        num_summary_rows.append({
            "Column": col,
            "Mean": round(s.mean(), 4),
            "Median": round(s.median(), 4),
            "Std": round(s.std(), 4),
            "Min": round(s.min(), 4),
            "Max": round(s.max(), 4),
        })
    num_summary = pd.DataFrame(num_summary_rows)

    # Per-source means
    source_metrics = clean.groupby("Traffic Source")[
        ["Session Duration", "Bounce Rate", "Conversion Rate"]
    ].mean().round(4).reset_index()
    source_metrics.columns = ["Traffic Source", "Avg Session Duration",
                               "Avg Bounce Rate", "Avg Conversion Rate"]

    best_conversion_source = source_metrics.loc[
        source_metrics["Avg Conversion Rate"].idxmax(), "Traffic Source"]
    lowest_bounce_source = source_metrics.loc[
        source_metrics["Avg Bounce Rate"].idxmin(), "Traffic Source"]
    highest_engagement_source = source_metrics.loc[
        source_metrics["Avg Session Duration"].idxmax(), "Traffic Source"]

    # New vs returning
    new_conv = clean[clean["Previous Visits"] == 0]["Conversion Rate"].mean()
    returning_conv = clean[clean["Previous Visits"] > 0]["Conversion Rate"].mean()

    # Top correlated features with Conversion Rate (from numeric cols excluding itself)
    corr_target = "Conversion Rate"
    corr_cols = [c for c in numeric_cols if c != corr_target]
    corr_vals = clean[corr_cols + [corr_target]].corr()[corr_target].drop(corr_target)
    corr_sorted = corr_vals.abs().sort_values(ascending=False)
    top_corr_feature = corr_sorted.index[0]
    top_corr_value = round(corr_vals[top_corr_feature], 4)

    # Stats significance
    stats_df_display = stats_df.copy()
    stats_df_display["significant"] = stats_df_display["significant"].map(
        {True: "Yes", False: "No"})
    sig_targets = stats_df[stats_df["significant"]]["target"].tolist()

    # Plot links (relative to report.md location in output/PROJECT_01/)
    plot_links = "\n".join(
        f"![{f}](plots/{f})" for f in PLOT_FILES
    )

    data_quality_finding = (
        f"{dirty_count} rows removed ({round(dirty_count / total_raw * 100, 1)}% of raw data)."
        if dirty_count > 0 else "No dirty rows detected; all data passed quality checks."
    )

    sig_sentence = (
        f"Differences across Traffic Sources are statistically significant (p < 0.05) for: "
        f"{', '.join(sig_targets)}."
        if sig_targets else
        "No statistically significant differences found across Traffic Sources at p < 0.05."
    )

    report = f"""# Web Session Analytics — Summary Report

**Generated:** {date.today().isoformat()}
**Dataset:** data/data.csv | **Clean rows:** {clean_count} | **Dirty rows removed:** {dirty_count}

---

## 1. Data Quality

{df_to_md_table(dirty_breakdown) if dirty_count > 0 else "_No dirty rows detected._"}

{data_quality_finding}

---

## 2. Dataset Overview

{df_to_md_table(num_summary)}

---

## 3. Traffic Source Analysis

{df_to_md_table(source_metrics)}

- **Best source for conversion:** {best_conversion_source}
- **Highest engagement (session duration):** {highest_engagement_source}
- **Lowest bounce rate:** {lowest_bounce_source}

---

## 4. Conversion Insights

- **New visitors** (Previous Visits = 0) mean Conversion Rate: **{round(new_conv, 4)}**
- **Returning visitors** (Previous Visits > 0) mean Conversion Rate: **{round(returning_conv, 4)}**
- Top feature correlated with Conversion Rate: **{top_corr_feature}** (r = {top_corr_value})

---

## 5. Statistical Significance

{df_to_md_table(stats_df_display)}

{sig_sentence}

---

## 6. Key Findings

1. **{best_conversion_source}** delivers the highest average Conversion Rate among all traffic sources.
2. **{highest_engagement_source}** drives the longest sessions, indicating strong content engagement.
3. **{lowest_bounce_source}** achieves the lowest bounce rate, suggesting high landing-page relevance.
4. {"Returning visitors convert at a higher rate than new visitors." if returning_conv >= new_conv else "New visitors convert at a higher rate than returning visitors — consider improving retention."}
5. {f"Kruskal-Wallis tests confirm significant variation across sources for {', '.join(sig_targets[:2])}." if sig_targets else "No metric shows statistically significant variation across traffic sources."}

---

## 7. Plots

{plot_links}
"""
    return report


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("PHASE 5 — REPORT")
    print("=" * 60)

    check_inputs()
    audit, dirty, clean, stats_df = load_data()

    report_text = build_report(audit, dirty, clean, stats_df)

    out_path = OUTPUT_DIR / "report.md"
    out_path.write_text(report_text, encoding="utf-8")

    print(f"Saved: {out_path}")
    print(f"\nReport preview (first 30 lines):")
    print("\n".join(report_text.splitlines()[:30]))


if __name__ == "__main__":
    main()
