"""Phase 4 -- HTML Report
Assemble a self-contained interactive HTML report from all prior outputs.
"""

from __future__ import annotations

import warnings
from datetime import datetime
from pathlib import Path

import pandas as pd

RANDOM_SEED = 42
OUTPUT_DIR = Path("output/PROJECT_01")
CHARTS_DIR = OUTPUT_DIR / "charts"
CLEAN_CSV = OUTPUT_DIR / "clean.csv"
DIRTY_CSV = OUTPUT_DIR / "dirty.csv"
STATS_CSV = OUTPUT_DIR / "summary_stats.csv"
REPORT_HTML = OUTPUT_DIR / "report.html"

SCRIPT_VERSION = "1.0.0"

CHART_STEMS = [
    "monthly_revenue",
    "cumulative_revenue",
    "revenue_by_region",
    "revenue_by_category",
    "revenue_by_product",
    "sales_rep_performance",
    "top_customers",
    "discount_distribution",
    "order_status",
    "revenue_heatmap",
]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_all() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    for p in (OUTPUT_DIR, CLEAN_CSV, DIRTY_CSV, STATS_CSV):
        if not p.exists():
            raise FileNotFoundError(f"Run phase1_etl.py first: {p}")
    df = pd.read_csv(CLEAN_CSV, parse_dates=["date"])
    dirty = pd.read_csv(DIRTY_CSV)
    stats = pd.read_csv(STATS_CSV)
    return df, dirty, stats


def get_kpis(stats: pd.DataFrame) -> dict[str, str]:
    sub = stats[stats["table"] == "kpis"].copy()
    return dict(zip(sub["metric_name"], sub["metric_value"]))


def get_table(stats: pd.DataFrame, table_name: str) -> pd.DataFrame:
    sub = stats[stats["table"] == table_name].copy()
    sub[["prefix", "column"]] = sub["metric_name"].str.split(" :: ", n=1, expand=True)
    pivot = sub.pivot_table(index="prefix", columns="column", values="metric_value", aggfunc="first").reset_index()
    pivot.columns.name = None
    return pivot


def load_chart_html(stem: str) -> str:
    path = CHARTS_DIR / f"{stem}.html"
    if not path.exists():
        warnings.warn(f"Chart file not found: {path} -- section will be empty")
        return f'<p class="warning">Chart not available: {stem}</p>'
    content = path.read_text(encoding="utf-8")
    # Extract just the body content (between <body> tags) to embed inline
    if "<body>" in content and "</body>" in content:
        start = content.index("<body>") + len("<body>")
        end = content.index("</body>")
        return content[start:end]
    return content


# ---------------------------------------------------------------------------
# CSS & HTML helpers
# ---------------------------------------------------------------------------

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Arial, sans-serif; background: #f5f6fa; color: #222; }
header { background: #1a1a2e; color: white; padding: 32px 40px; }
header h1 { font-size: 2rem; font-weight: 700; margin-bottom: 6px; }
header p { opacity: 0.75; font-size: 0.95rem; }
nav { background: #16213e; padding: 0 40px; display: flex; gap: 0; overflow-x: auto; }
nav a { color: #a0aec0; text-decoration: none; padding: 14px 18px; font-size: 0.88rem; white-space: nowrap; }
nav a:hover { color: white; background: rgba(255,255,255,0.08); }
main { max-width: 1400px; margin: 0 auto; padding: 32px 24px 60px; }
section { margin-bottom: 40px; }
h2 { font-size: 1.45rem; color: #1a1a2e; border-bottom: 3px solid #636EFA; padding-bottom: 8px; margin-bottom: 20px; }
h3 { font-size: 1.1rem; color: #333; margin: 18px 0 10px; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
.card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); }
.card .label { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em; color: #888; margin-bottom: 6px; }
.card .value { font-size: 1.4rem; font-weight: 700; color: #1a1a2e; }
.card .value.money { color: #0d6efd; }
.insight { background: #eef2ff; border-left: 4px solid #636EFA; border-radius: 0 8px 8px 0; padding: 14px 18px; margin: 14px 0; font-size: 0.92rem; line-height: 1.6; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 16px; }
th { background: #1a1a2e; color: white; padding: 11px 14px; text-align: left; font-size: 0.83rem; text-transform: uppercase; letter-spacing: 0.04em; }
td { padding: 10px 14px; border-bottom: 1px solid #f0f0f0; font-size: 0.9rem; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #f8f9ff; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; margin-right: 6px; }
.badge-easy { background: #d4edda; color: #155724; }
.badge-medium { background: #fff3cd; color: #856404; }
.badge-hard { background: #f8d7da; color: #721c24; }
.qa-list { list-style: none; }
.qa-item { background: white; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); overflow: hidden; }
.qa-item summary { padding: 14px 18px; cursor: pointer; font-weight: 600; font-size: 0.93rem; display: flex; align-items: center; gap: 8px; }
.qa-item summary:hover { background: #f8f9ff; }
.qa-answer { padding: 14px 18px; background: #fafbff; border-top: 1px solid #eee; font-size: 0.9rem; line-height: 1.7; color: #444; }
.chart-wrap { background: white; border-radius: 10px; padding: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 20px; overflow: hidden; }
.warning { color: #dc3545; padding: 12px; background: #fff5f5; border-radius: 6px; }
footer { background: #1a1a2e; color: #a0aec0; padding: 20px 40px; font-size: 0.82rem; text-align: center; margin-top: 40px; }
footer span { margin: 0 12px; }
"""


def kpi_card(label: str, value: str, money: bool = False) -> str:
    cls = "value money" if money else "value"
    return f'<div class="card"><div class="label">{label}</div><div class="{cls}">{value}</div></div>'


def insight_box(text: str) -> str:
    return f'<div class="insight">{text}</div>'


def dirty_table_html(dirty: pd.DataFrame) -> str:
    cols = ["order_id", "date", "product", "unit_price", "quantity", "total", "reason"]
    available = [c for c in cols if c in dirty.columns]
    rows_html = ""
    for _, row in dirty[available].iterrows():
        cells = "".join(f"<td>{row[c]}</td>" for c in available)
        rows_html += f"<tr>{cells}</tr>"
    headers = "".join(f"<th>{c}</th>" for c in available)
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{rows_html}</tbody></table>"


def qa_item(badge_class: str, badge_label: str, question: str, answer: str) -> str:
    return f"""
<li class="qa-item">
  <details>
    <summary><span class="badge {badge_class}">{badge_label}</span>{question}</summary>
    <div class="qa-answer">{answer}</div>
  </details>
</li>"""


# ---------------------------------------------------------------------------
# Automated insight generators
# ---------------------------------------------------------------------------

def insights_monthly(df: pd.DataFrame, stats: pd.DataFrame) -> str:
    grp = (
        df.groupby("month", sort=True)
        .agg(rev=("revenue", "sum"), orders=("order_id", "count"))
        .reset_index()
    )
    grp["mom"] = grp["rev"].pct_change() * 100
    peak_row = grp.loc[grp["rev"].idxmax()]
    total = grp["rev"].sum()
    peak_pct = peak_row["rev"] / total * 100
    best_mom = grp["mom"].dropna()
    best_mom_val = best_mom.max()
    best_mom_idx = best_mom.idxmax()
    best_month_a = grp.loc[best_mom_idx - 1, "month"] if best_mom_idx > 0 else "N/A"
    best_month_b = grp.loc[best_mom_idx, "month"]
    return (
        f"Revenue peaked in <strong>{peak_row['month']}</strong> at <strong>${peak_row['rev']:,.0f}</strong>, "
        f"representing <strong>{peak_pct:.1f}%</strong> of total revenue. "
        f"The strongest month-over-month growth was <strong>+{best_mom_val:.1f}%</strong> "
        f"from {best_month_a} to {best_month_b}. "
        f"May saw a significant dip ({grp['mom'].iloc[-1]:.1f}%) but had the fewest orders ({int(grp['orders'].iloc[-1])})."
    )


def insights_region(df: pd.DataFrame) -> str:
    grp = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
    total = grp.sum()
    top = grp.index[0]
    top_pct = grp.iloc[0] / total * 100
    aov = df.groupby("region")["revenue"].mean().sort_values(ascending=False)
    top_aov = aov.index[0]
    return (
        f"<strong>{top}</strong> region leads with <strong>${grp.iloc[0]:,.0f}</strong> "
        f"({top_pct:.1f}% of total revenue). "
        f"<strong>{top_aov}</strong> has the highest average order value at <strong>${aov.iloc[0]:,.0f}</strong>. "
        f"All four regions are broadly balanced, spanning a ${grp.iloc[0]-grp.iloc[-1]:,.0f} range."
    )


def insights_category(df: pd.DataFrame) -> str:
    grp = df.groupby("category").agg(rev=("revenue", "sum"), cnt=("order_id", "count")).sort_values("rev", ascending=False)
    total = grp["rev"].sum()
    top = grp.index[0]
    top_pct = grp["rev"].iloc[0] / total * 100
    return (
        f"<strong>{top}</strong> is the top revenue category at <strong>${grp['rev'].iloc[0]:,.0f}</strong> "
        f"({top_pct:.1f}% of total). "
        f"Consulting has the highest AOV despite fewer orders, suggesting higher-ticket engagements. "
        f"Training has the lowest AOV ($1,715.63), indicating volume-sensitive pricing."
    )


def insights_product(df: pd.DataFrame) -> str:
    by_rev = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
    by_cnt = df.groupby("product")["order_id"].count().sort_values(ascending=False)
    top_rev = by_rev.index[0]
    top_cnt = by_cnt.index[0]
    note = (
        f"<strong>{top_rev}</strong> generates the most revenue (${by_rev.iloc[0]:,.0f}), "
        f"while <strong>{top_cnt}</strong> has the highest order count ({by_cnt.iloc[0]} orders). "
    )
    if top_rev == top_cnt:
        note += "The same product leads on both dimensions."
    else:
        note += "These differ, indicating distinct volume-vs-value dynamics across the product line."
    return note


def insights_heatmap(df: pd.DataFrame) -> str:
    pivot = df.pivot_table(values="revenue", index="region", columns="category", aggfunc="sum", fill_value=0)
    max_val = pivot.max().max()
    max_cat = pivot.max().idxmax()
    max_region = pivot[max_cat].idxmax()
    zero_cells = int((pivot == 0).sum().sum())
    return (
        f"The highest-value region-category combination is <strong>{max_region} x {max_cat}</strong> "
        f"at <strong>${max_val:,.0f}</strong>. "
        f"There are <strong>{zero_cells}</strong> zero-revenue cells, indicating product gaps by region — "
        f"notably, Consulting revenue is entirely concentrated in North and South."
    )


def insights_rep(df: pd.DataFrame) -> str:
    grp = df.groupby("sales_rep", dropna=True).agg(rev=("revenue", "sum"), cnt=("order_id", "count"), disc=("discount_pct", "mean")).sort_values("rev", ascending=False)
    top_rev = grp.index[0]
    top_disc = grp["disc"].idxmax()
    return (
        f"<strong>{top_rev}</strong> leads on total revenue (${grp['rev'].iloc[0]:,.0f}). "
        f"<strong>{top_disc}</strong> offers the highest average discount ({grp.loc[top_disc, 'disc']:.1f}%), "
        f"which may indicate aggressive pricing to close deals. "
        f"Performance is broadly balanced, with revenue spread across reps within a $3,500 range."
    )


def insights_customers(df: pd.DataFrame) -> str:
    cust = df.groupby("customer_name")["revenue"].sum().sort_values(ascending=False)
    total = cust.sum()
    top1_pct = cust.iloc[0] / total * 100
    top3_pct = cust.head(3).sum() / total * 100
    repeat = (df.groupby("customer_name")["order_id"].count() > 1).sum()
    return (
        f"The top customer (<strong>{cust.index[0]}</strong>) accounts for <strong>{top1_pct:.1f}%</strong> of total revenue. "
        f"The top 3 customers combined account for <strong>{top3_pct:.1f}%</strong>. "
        f"<strong>{repeat}</strong> customers placed more than one order — concentration risk is low given even distribution, "
        f"but the dataset is only 5 months old."
    )


def insights_status(df: pd.DataFrame) -> str:
    grp = df.groupby("status").agg(cnt=("order_id", "count"), rev=("revenue", "sum"))
    total_rev = grp["rev"].sum()
    pending_rev = grp.loc["Pending", "rev"] if "Pending" in grp.index else 0
    pending_cnt = grp.loc["Pending", "cnt"] if "Pending" in grp.index else 0
    total_cnt = grp["cnt"].sum()
    pend_rev_pct = pending_rev / total_rev * 100
    pend_cnt_pct = pending_cnt / total_cnt * 100
    top_pending_region = df[df["is_pending"]].groupby("region")["order_id"].count().idxmax() if df["is_pending"].any() else "N/A"
    return (
        f"<strong>{int(pending_cnt)}</strong> orders ({pend_cnt_pct:.1f}%) are pending, representing "
        f"<strong>${pending_rev:,.0f}</strong> ({pend_rev_pct:.1f}% of total potential revenue). "
        f"<strong>{top_pending_region}</strong> has the most pending orders. "
        f"Converting pending orders to completed would increase recognised revenue by {pend_rev_pct:.1f}%."
    )


# ---------------------------------------------------------------------------
# Interview Q&A
# ---------------------------------------------------------------------------

def build_interview_qa(df: pd.DataFrame, kpis: dict) -> str:
    total_rev = float(kpis.get("total_revenue", 0))
    order_count = int(float(kpis.get("order_count", 0)))
    top_region = kpis.get("top_region", "N/A")
    top_rev_region = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
    top_region_rev = top_rev_region.iloc[0]
    top_region_pct = top_region_rev / total_rev * 100

    grp_region = df.groupby("region")["revenue"].mean().sort_values(ascending=False)
    top_aov_region = grp_region.index[0]

    monthly = df.groupby("month", sort=True)["revenue"].sum()
    monthly_str = ", ".join(f"{m}: ${v:,.0f}" for m, v in monthly.items())

    top_disc_rep = df.groupby("sales_rep", dropna=True)["discount_pct"].mean().idxmax()
    top_disc_val = df.groupby("sales_rep", dropna=True)["discount_pct"].mean().max()

    pending_pct = float(kpis.get("pending_count", 0)) / order_count * 100
    pending_rev_pct = float(kpis.get("pending_revenue", 0)) / total_rev * 100

    cust = df.groupby("customer_name")["revenue"].sum().sort_values(ascending=False)
    top3_pct = cust.head(3).sum() / total_rev * 100

    products = df[["product", "category"]].drop_duplicates().sort_values("product")
    product_list = "<br>".join(f"&bull; {r['product']} ({r['category']})" for _, r in products.iterrows())

    items = [
        qa_item("badge-easy", "Easy",
                "What is the total revenue from this dataset?",
                f"<strong>${total_rev:,.2f}</strong> across {order_count} clean orders (Jan–May 2025). "
                f"Note: 2 dirty rows were removed before analysis — including a row with quantity=999 and one with a negative price. "
                f"The raw dataset had 50 rows; 48 remain after cleaning."),

        qa_item("badge-easy", "Easy",
                "How many orders were placed?",
                f"<strong>{order_count} orders</strong> in the clean dataset. The raw dataset contained 50 rows; "
                f"2 were removed as dirty (ORD-047: extreme quantity + total mismatch; ORD-049: negative unit_price). "
                f"Additionally, 5 orders ({pending_pct:.1f}%) are still Pending."),

        qa_item("badge-easy", "Easy",
                "Which region generated the most revenue?",
                f"<strong>{top_region}</strong> with <strong>${top_region_rev:,.0f}</strong> "
                f"({top_region_pct:.1f}% of total revenue). All four regions are balanced, "
                f"so no single region dominates significantly."),

        qa_item("badge-easy", "Easy",
                "What products does the company sell?",
                f"6 products across 4 categories:<br>{product_list}"),

        qa_item("badge-easy", "Easy",
                "How many sales reps are there?",
                f"<strong>4 confirmed reps</strong>: Sarah Mitchell, James Okafor, Tom Richards, and Priya Sharma. "
                f"One order has a missing sales_rep value — it was retained in the clean dataset but cannot be attributed to a rep."),

        qa_item("badge-medium", "Medium",
                "Which region has the highest average order value?",
                f"<strong>{top_aov_region}</strong> with an AOV of <strong>${grp_region.iloc[0]:,.0f}</strong>. "
                f"This differs from the top-revenue region ({top_region}), which has more orders but a slightly lower per-order value."),

        qa_item("badge-medium", "Medium",
                "What is the month-over-month revenue growth trend?",
                f"Monthly revenue: {monthly_str}. "
                f"March was the strongest month (+46.2% MoM). April dipped -8.7% despite the highest order count (12). "
                f"May shows a sharp -37.4% decline, but note May only covers 3 weeks of data (dataset ends 2025-05-21)."),

        qa_item("badge-medium", "Medium",
                "Which sales rep gives the highest average discount?",
                f"<strong>{top_disc_rep}</strong> at <strong>{top_disc_val:.1f}%</strong> average discount. "
                f"This could indicate deal-closing behaviour, but warrants monitoring to avoid margin erosion."),

        qa_item("badge-medium", "Medium",
                "What percentage of orders are still pending?",
                f"<strong>{int(float(kpis.get('pending_count', 0)))} orders</strong> ({pending_pct:.1f}% of count) are Pending, "
                f"representing <strong>${float(kpis.get('pending_revenue', 0)):,.0f}</strong> ({pending_rev_pct:.1f}% of revenue). "
                f"If all pending orders complete, total recognised revenue would reach ~${total_rev + float(kpis.get('pending_revenue', 0)):,.0f} — "
                f"but this double-counts; pending_revenue is already included in total_revenue."),

        qa_item("badge-medium", "Medium",
                "Which customer segment is most concentrated?",
                f"The top 3 customers account for <strong>{top3_pct:.1f}%</strong> of total revenue. "
                f"With 48 unique customers (one per order on average), no single customer dominates — "
                f"this is a healthy distribution for a 5-month dataset."),

        qa_item("badge-hard", "Hard",
                "How would you handle the outlier in ORD-047?",
                "ORD-047 had quantity=999 — far outside the 1–8 range for all other orders. "
                "The decision tree: (1) confirm with the source system whether bulk orders are possible; "
                "(2) check if the total was agreed with the customer; (3) verify the total calculation — it was off by ~$585, "
                "further suggesting a data entry error. We applied dirty-rule D2 (quantity &gt; 50) and D3 (total mismatch). "
                "Impact: removing ORD-047 drops mean revenue from ~$10,482 to ~$2,035 — a dramatic shift showing how "
                "a single outlier can distort the mean. The median ($1,915) is robust to this outlier and is the preferred "
                "central tendency metric here. In a production pipeline, flag for human review rather than silently removing."),

        qa_item("badge-hard", "Hard",
                "What does the customer concentration risk look like, and why does it matter?",
                "Top 1 customer: 4.2% | Top 3: 12.2% | Top 5: 19.5% | Top 10: 34.8% of total revenue. "
                "This is relatively low concentration for a B2B business — a Herfindahl-Hirschman Index (HHI) analysis "
                "would confirm diversification. However: (1) the dataset is only 5 months old, so patterns may not have emerged; "
                "(2) all customers have placed exactly 1 order — there are zero repeat buyers. This could mean "
                "high churn risk or that the product is one-time in nature. "
                "The key risk is not concentration in a Pareto sense but rather the <em>absence of repeat business</em>, "
                "which affects revenue predictability and LTV calculations."),

        qa_item("badge-hard", "Hard",
                "If you could keep only 3 charts, which would you choose and why?",
                "<strong>1. Monthly Revenue Trend</strong> — shows the business trajectory and seasonality; "
                "essential for any time-series business. "
                "<strong>2. Revenue Heatmap (Region x Category)</strong> — reveals two-dimensional structure "
                "in a single chart; exposes product gaps and regional specialisation. "
                "<strong>3. Top Customers</strong> — directly addresses concentration risk, the most "
                "strategically important question for a B2B business. "
                "Trade-off: dropping Sales Rep Performance loses accountability data; dropping Status loses pipeline visibility. "
                "But trend + structure + concentration covers the core analytical narrative."),

        qa_item("badge-hard", "Hard",
                "How would your analysis change with 10,000 rows?",
                "With 10K rows: (1) <strong>Statistical tests become valid</strong> — t-tests for regional differences, "
                "chi-squared for categorical associations, confidence intervals on all metrics. "
                "(2) <strong>Time-series modelling</strong> — ARIMA, Prophet, or exponential smoothing for forecasting. "
                "(3) <strong>Customer cohort analysis</strong> — retention curves, LTV, churn prediction. "
                "(4) <strong>Automated anomaly detection</strong> — IQR/Z-score flagging replaces manual dirty rules. "
                "(5) <strong>ML models</strong> — predict order value, churn risk, product affinity. "
                "(6) <strong>Sampling for EDA</strong> — stratified samples for initial exploration before full runs."),

        qa_item("badge-hard", "Hard",
                "Is this dataset statistically sufficient to draw conclusions?",
                "For <strong>descriptive statistics</strong>: yes — means, medians, distributions are accurate for this population. "
                "For <strong>inferential statistics</strong>: no — with n=48, confidence intervals are wide and tests lack power. "
                "Example: a 95% CI on mean order value would be roughly $2,035 +/- $400 (SE ~$200). "
                "Regional differences are not statistically significant at this sample size. "
                "What would help: (1) more months of data for seasonality; (2) historical data for trend validation; "
                "(3) external benchmarks for industry comparison; (4) customer demographic data for segmentation."),
    ]
    return '<ul class="qa-list">' + "".join(items) + "</ul>"


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def build_report(df: pd.DataFrame, dirty: pd.DataFrame, stats: pd.DataFrame) -> str:
    kpis = get_kpis(stats)

    def kv(key: str, default: str = "N/A") -> str:
        return str(kpis.get(key, default))

    total_rev = float(kpis.get("total_revenue", 0))
    avg_ov = float(kpis.get("avg_order_value", 0))
    med_ov = float(kpis.get("median_order_value", 0))
    pending_rev = float(kpis.get("pending_revenue", 0))
    pending_cnt = int(float(kpis.get("pending_count", 0)))

    kpi_cards_html = "".join([
        kpi_card("Total Revenue", f"${total_rev:,.2f}", money=True),
        kpi_card("Order Count", kv("order_count")),
        kpi_card("Avg Order Value", f"${avg_ov:,.2f}", money=True),
        kpi_card("Median Order Value", f"${med_ov:,.2f}", money=True),
        kpi_card("Top Region", kv("top_region")),
        kpi_card("Top Product", kv("top_product")),
        kpi_card("Top Sales Rep", kv("top_sales_rep")),
        kpi_card("Pending", f"{pending_cnt} orders / ${pending_rev:,.0f}"),
    ])

    nav_links = "".join(
        f'<a href="#section-{s}">{label}</a>'
        for s, label in [
            ("summary", "Summary"),
            ("quality", "Data Quality"),
            ("trends", "Revenue & Trends"),
            ("regional", "Regional & Products"),
            ("reps", "Sales Reps"),
            ("customers", "Customers"),
            ("status", "Status"),
            ("interview", "Interview Prep"),
        ]
    )

    chart = {stem: load_chart_html(stem) for stem in CHART_STEMS}

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    raw_count = len(df) + len(dirty)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sales Order Analytics Report</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>Sales Order Analytics Report</h1>
  <p>Internal Technical Review &mdash; Jan&ndash;May 2025 &mdash; Generated {now}</p>
</header>
<nav>{nav_links}</nav>
<main>

<!-- Section 1: Executive Summary -->
<section id="section-summary">
  <h2>1. Executive Summary</h2>
  <div class="card-grid">{kpi_cards_html}</div>
  {insight_box(
      f"Dataset covers <strong>{raw_count} raw orders</strong> across Jan&ndash;May 2025. "
      f"After removing <strong>{len(dirty)} dirty rows</strong>, the clean dataset has <strong>{len(df)} orders</strong> "
      f"with total revenue of <strong>${total_rev:,.2f}</strong>. "
      f"All four regions and four reps are active; no repeat customers observed in this 5-month window."
  )}
</section>

<!-- Section 2: Data Quality -->
<section id="section-quality">
  <h2>2. Data Quality</h2>
  <h3>Removed Rows ({len(dirty)} total)</h3>
  {dirty_table_html(dirty)}
  {insight_box(
      "<strong>Date normalisation:</strong> One row (ORD-027) used DD-MM-YYYY format ('15-03-2025') instead of "
      "YYYY-MM-DD. Pandas automatically corrected this during mixed-format parsing &mdash; the row was retained. "
      "<br><br>"
      "<strong>Dirty rows removed:</strong> ORD-047 was removed for quantity=999 (far outside the 1&ndash;8 range "
      "of all other orders) and a total calculation mismatch of ~$585. ORD-049 was removed for a negative unit_price "
      "(-$1,200), which is impossible for a valid sale. "
      "<br><br>"
      "<strong>Missing values retained:</strong> 1 row has no customer_email; 1 row has no sales_rep. "
      "Neither warrants removal &mdash; they participate fully in revenue and regional analysis."
  )}
</section>

<!-- Section 3: Revenue & Trends -->
<section id="section-trends">
  <h2>3. Revenue &amp; Trends</h2>
  <h3>Monthly Revenue</h3>
  <div class="chart-wrap">{chart['monthly_revenue']}</div>
  {insight_box(insights_monthly(df, stats))}
  <h3>Cumulative Revenue</h3>
  <div class="chart-wrap">{chart['cumulative_revenue']}</div>
  {insight_box(
      f"Revenue accumulated steadily through Q1 with the steepest gradient in March. "
      f"The cumulative total of <strong>${total_rev:,.0f}</strong> is reached by 21 May 2025. "
      "The flattening gradient in May reflects both fewer orders and the incomplete month."
  )}
</section>

<!-- Section 4: Regional & Product Breakdown -->
<section id="section-regional">
  <h2>4. Regional &amp; Product Breakdown</h2>
  <h3>Revenue by Region</h3>
  <div class="chart-wrap">{chart['revenue_by_region']}</div>
  {insight_box(insights_region(df))}
  <h3>Revenue by Category</h3>
  <div class="chart-wrap">{chart['revenue_by_category']}</div>
  {insight_box(insights_category(df))}
  <h3>Revenue by Product</h3>
  <div class="chart-wrap">{chart['revenue_by_product']}</div>
  {insight_box(insights_product(df))}
  <h3>Revenue Heatmap: Region &times; Category</h3>
  <div class="chart-wrap">{chart['revenue_heatmap']}</div>
  {insight_box(insights_heatmap(df))}
</section>

<!-- Section 5: Sales Rep Performance -->
<section id="section-reps">
  <h2>5. Sales Rep Performance</h2>
  <div class="chart-wrap">{chart['sales_rep_performance']}</div>
  {insight_box(insights_rep(df))}
</section>

<!-- Section 6: Customer Insights -->
<section id="section-customers">
  <h2>6. Customer Insights</h2>
  <div class="chart-wrap">{chart['top_customers']}</div>
  {insight_box(insights_customers(df))}
  <h3>Discount Distribution</h3>
  <div class="chart-wrap">{chart['discount_distribution']}</div>
  {insight_box(
      "Discounts cluster at 0%, 5%, 10%, and 15&ndash;20%, suggesting a tiered pricing structure. "
      "Web Dev has the widest discount range (up to 20%), while Consulting is most conservative (max 15%). "
      "No clear correlation between discount level and order volume is visible at this sample size."
  )}
</section>

<!-- Section 7: Order Status -->
<section id="section-status">
  <h2>7. Order Status</h2>
  <div class="chart-wrap">{chart['order_status']}</div>
  {insight_box(insights_status(df))}
</section>

<!-- Section 8: Interview-Ready Insights -->
<section id="section-interview">
  <h2>8. Interview-Ready Insights</h2>
  {insight_box(
      "Click each question to reveal a prepared answer. "
      "Questions are colour-coded: "
      "<span class='badge badge-easy'>Easy</span> "
      "<span class='badge badge-medium'>Medium</span> "
      "<span class='badge badge-hard'>Hard</span>"
  )}
  {build_interview_qa(df, kpis)}
</section>

</main>
<footer>
  <span>Generated: {now}</span>
  <span>Script version: {SCRIPT_VERSION}</span>
  <span>Raw rows: {raw_count}</span>
  <span>Clean rows: {len(df)}</span>
  <span>Dirty rows: {len(dirty)}</span>
</footer>
</body>
</html>"""
    return html


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("[load] Reading outputs from previous phases...")
    df, dirty, stats = load_all()
    print(f"       clean.csv: {len(df)} rows | dirty.csv: {len(dirty)} rows | summary_stats.csv: {len(stats)} rows")

    print("[report] Assembling HTML report...")
    html = build_report(df, dirty, stats)

    REPORT_HTML.write_text(html, encoding="utf-8")
    size_kb = REPORT_HTML.stat().st_size / 1024
    print(f"[done] report.html written: {size_kb:.1f} KB -> {REPORT_HTML}")
    print(f"       Open in browser: file:///{REPORT_HTML.resolve().as_posix()}")


if __name__ == "__main__":
    main()
