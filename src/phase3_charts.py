"""Phase 3 -- Charts
Generate 10 Plotly charts from clean.csv, save each as .html and .png.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

RANDOM_SEED = 42
OUTPUT_DIR = Path("output/PROJECT_01")
CHARTS_DIR = OUTPUT_DIR / "charts"
CLEAN_CSV = OUTPUT_DIR / "clean.csv"
STATS_CSV = OUTPUT_DIR / "summary_stats.csv"

TEMPLATE = "plotly_white"
PNG_WIDTH = 1200
PNG_HEIGHT = 700
PNG_SCALE = 2

CURRENCY = "$"

# Check kaleido availability once
try:
    import kaleido  # noqa: F401
    KALEIDO_OK = True
except ImportError:
    warnings.warn("kaleido not available -- skipping PNG export")
    KALEIDO_OK = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not OUTPUT_DIR.exists():
        raise FileNotFoundError("Run phase1_etl.py first")
    df = pd.read_csv(CLEAN_CSV, parse_dates=["date"])
    df["month"] = df["month"].astype(str)
    stats = pd.read_csv(STATS_CSV)
    print(f"[load] clean.csv: {len(df)} rows | summary_stats.csv: {len(stats)} rows")
    return df, stats


def get_table(stats: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Extract a named aggregation table from the long-format stats CSV."""
    sub = stats[stats["table"] == table_name].copy()
    # Split metric_name into prefix (label) and column parts
    sub[["prefix", "column"]] = sub["metric_name"].str.split(" :: ", n=1, expand=True)
    pivot = sub.pivot_table(index="prefix", columns="column", values="metric_value", aggfunc="first").reset_index()
    pivot.columns.name = None
    return pivot


def save_chart(fig: go.Figure, stem: str) -> None:
    html_path = CHARTS_DIR / f"{stem}.html"
    fig.write_html(str(html_path), full_html=True, include_plotlyjs="cdn")
    print(f"  [html] {html_path.name}")
    if KALEIDO_OK:
        png_path = CHARTS_DIR / f"{stem}.png"
        fig.write_image(str(png_path), width=PNG_WIDTH, height=PNG_HEIGHT, scale=PNG_SCALE)
        print(f"  [png]  {png_path.name}")
    else:
        warnings.warn(f"Skipping PNG for {stem}")


def fmt_currency(val: float) -> str:
    return f"{CURRENCY}{val:,.0f}"


# ---------------------------------------------------------------------------
# Chart 1 -- Monthly Revenue Trend (line + bar combo)
# ---------------------------------------------------------------------------

def chart_monthly_revenue(df: pd.DataFrame) -> None:
    print("\n[chart 1] Monthly Revenue Trend")
    grp = (
        df.groupby("month", sort=True)
        .agg(revenue_sum=("revenue", "sum"), order_count=("order_id", "count"), aov=("revenue", "mean"))
        .reset_index()
    )
    grp["aov_label"] = grp["aov"].apply(fmt_currency)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=grp["month"], y=grp["order_count"], name="Order Count",
            marker_color="rgba(99,110,250,0.3)", hovertemplate="%{x}<br>Orders: %{y}<extra></extra>",
        ),
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(
            x=grp["month"], y=grp["revenue_sum"], mode="lines+markers", name="Revenue",
            line=dict(color="#636EFA", width=3),
            customdata=grp[["aov_label", "order_count"]].values,
            hovertemplate="%{x}<br>Revenue: $%{y:,.0f}<br>AOV: %{customdata[0]}<br>Orders: %{customdata[1]}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.update_layout(
        title="Monthly Revenue Trend (Jan–May 2025)", template=TEMPLATE,
        xaxis_title="Month", legend=dict(x=0.01, y=0.99),
    )
    fig.update_yaxes(title_text="Revenue ($)", secondary_y=False, tickprefix="$", tickformat=",.0f")
    fig.update_yaxes(title_text="Order Count", secondary_y=True)
    save_chart(fig, "monthly_revenue")


# ---------------------------------------------------------------------------
# Chart 2 -- Cumulative Revenue Over Time (area)
# ---------------------------------------------------------------------------

def chart_cumulative_revenue(df: pd.DataFrame) -> None:
    print("\n[chart 2] Cumulative Revenue")
    sorted_df = df.sort_values("date").copy()
    sorted_df["cumulative_revenue"] = sorted_df["revenue"].cumsum()
    total = sorted_df["cumulative_revenue"].iloc[-1]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=sorted_df["date"], y=sorted_df["cumulative_revenue"],
            mode="lines", fill="tozeroy", name="Cumulative Revenue",
            line=dict(color="#EF553B", width=2),
            hovertemplate="%{x|%Y-%m-%d}<br>Cumulative: $%{y:,.0f}<extra></extra>",
        )
    )
    fig.add_annotation(
        x=sorted_df["date"].iloc[-1], y=total,
        text=f"Total: {fmt_currency(total)}",
        showarrow=True, arrowhead=2, ax=-80, ay=-40,
        font=dict(size=12, color="#EF553B"),
    )
    fig.update_layout(
        title="Cumulative Revenue Over Time (Jan–May 2025)", template=TEMPLATE,
        xaxis_title="Date", yaxis_title="Cumulative Revenue ($)",
    )
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")
    save_chart(fig, "cumulative_revenue")


# ---------------------------------------------------------------------------
# Chart 3 -- Revenue by Region (horizontal bar)
# ---------------------------------------------------------------------------

def chart_revenue_by_region(df: pd.DataFrame) -> None:
    print("\n[chart 3] Revenue by Region")
    grp = (
        df.groupby("region")
        .agg(revenue_sum=("revenue", "sum"), aov=("revenue", "mean"), order_count=("order_id", "count"))
        .reset_index()
        .sort_values("revenue_sum", ascending=True)
    )
    grp["aov_label"] = grp["aov"].apply(fmt_currency)

    fig = go.Figure(
        go.Bar(
            x=grp["revenue_sum"], y=grp["region"], orientation="h",
            marker_color="#00CC96",
            customdata=grp[["aov_label", "order_count"]].values,
            hovertemplate="%{y}<br>Revenue: $%{x:,.0f}<br>AOV: %{customdata[0]}<br>Orders: %{customdata[1]}<extra></extra>",
            text=[fmt_currency(v) for v in grp["revenue_sum"]], textposition="outside",
        )
    )
    fig.update_layout(
        title="Revenue by Region", template=TEMPLATE,
        xaxis_title="Revenue ($)", yaxis_title="Region",
        xaxis=dict(tickprefix="$", tickformat=",.0f"),
        margin=dict(l=80, r=120),
    )
    save_chart(fig, "revenue_by_region")


# ---------------------------------------------------------------------------
# Chart 4 -- Revenue by Category (treemap)
# ---------------------------------------------------------------------------

def chart_revenue_by_category(df: pd.DataFrame) -> None:
    print("\n[chart 4] Revenue by Category (Treemap)")
    grp = (
        df.groupby("category")
        .agg(revenue_sum=("revenue", "sum"), order_count=("order_id", "count"))
        .reset_index()
    )
    grp["label"] = grp.apply(
        lambda r: f"{r['category']}<br>${r['revenue_sum']:,.0f}<br>{r['order_count']} orders", axis=1
    )

    fig = px.treemap(
        grp, path=["category"], values="revenue_sum",
        custom_data=["order_count", "revenue_sum"],
        title="Revenue by Category",
        color="revenue_sum",
        color_continuous_scale="Blues",
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Revenue: $%{customdata[1]:,.0f}<br>Orders: %{customdata[0]}<extra></extra>",
        texttemplate="<b>%{label}</b><br>$%{value:,.0f}",
    )
    fig.update_layout(template=TEMPLATE)
    save_chart(fig, "revenue_by_category")


# ---------------------------------------------------------------------------
# Chart 5 -- Revenue by Product (vertical bar)
# ---------------------------------------------------------------------------

def chart_revenue_by_product(df: pd.DataFrame) -> None:
    print("\n[chart 5] Revenue by Product")
    grp = (
        df.groupby(["product", "category"])
        .agg(revenue_sum=("revenue", "sum"), order_count=("order_id", "count"))
        .reset_index()
        .sort_values("revenue_sum", ascending=False)
    )

    fig = px.bar(
        grp, x="product", y="revenue_sum", color="category",
        title="Revenue by Product (coloured by Category)",
        labels={"revenue_sum": "Revenue ($)", "product": "Product", "category": "Category"},
        text=grp["revenue_sum"].apply(fmt_currency),
        template=TEMPLATE,
    )
    fig.update_traces(textposition="outside")
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")
    fig.update_layout(xaxis_tickangle=-20)
    save_chart(fig, "revenue_by_product")


# ---------------------------------------------------------------------------
# Chart 6 -- Sales Rep Performance (grouped bar, dual axis)
# ---------------------------------------------------------------------------

def chart_sales_rep_performance(df: pd.DataFrame) -> None:
    print("\n[chart 6] Sales Rep Performance")
    grp = (
        df.groupby("sales_rep", dropna=False)
        .agg(revenue_sum=("revenue", "sum"), order_count=("order_id", "count"), avg_discount=("discount_pct", "mean"))
        .reset_index()
        .sort_values("revenue_sum", ascending=False)
    )
    grp["sales_rep"] = grp["sales_rep"].fillna("(unknown)")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=grp["sales_rep"], y=grp["revenue_sum"], name="Revenue",
            marker_color="#636EFA",
            hovertemplate="%{x}<br>Revenue: $%{y:,.0f}<extra></extra>",
            text=grp["revenue_sum"].apply(fmt_currency), textposition="outside",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            x=grp["sales_rep"], y=grp["order_count"], name="Order Count",
            marker_color="#EF553B", opacity=0.7,
            hovertemplate="%{x}<br>Orders: %{y}<extra></extra>",
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title="Sales Rep Performance", template=TEMPLATE,
        barmode="group", xaxis_title="Sales Rep",
    )
    fig.update_yaxes(title_text="Revenue ($)", secondary_y=False, tickprefix="$", tickformat=",.0f")
    fig.update_yaxes(title_text="Order Count", secondary_y=True)
    save_chart(fig, "sales_rep_performance")


# ---------------------------------------------------------------------------
# Chart 7 -- Top 10 Customers (horizontal bar)
# ---------------------------------------------------------------------------

def chart_top_customers(df: pd.DataFrame) -> None:
    print("\n[chart 7] Top Customers")
    grp = (
        df.groupby("customer_name")
        .agg(revenue_sum=("revenue", "sum"), order_count=("order_id", "count"))
        .reset_index()
        .sort_values("revenue_sum", ascending=False)
        .head(10)
        .sort_values("revenue_sum", ascending=True)  # ascending for horizontal bar
    )

    fig = go.Figure(
        go.Bar(
            x=grp["revenue_sum"], y=grp["customer_name"], orientation="h",
            marker_color="#AB63FA",
            customdata=grp["order_count"].values,
            hovertemplate="%{y}<br>Revenue: $%{x:,.0f}<br>Orders: %{customdata}<extra></extra>",
            text=grp["revenue_sum"].apply(fmt_currency), textposition="outside",
        )
    )
    fig.update_layout(
        title="Top 10 Customers by Revenue", template=TEMPLATE,
        xaxis_title="Revenue ($)", yaxis_title="Customer",
        xaxis=dict(tickprefix="$", tickformat=",.0f"),
        margin=dict(l=150, r=120),
    )
    save_chart(fig, "top_customers")


# ---------------------------------------------------------------------------
# Chart 8 -- Discount Distribution (histogram with category colour)
# ---------------------------------------------------------------------------

def chart_discount_distribution(df: pd.DataFrame) -> None:
    print("\n[chart 8] Discount Distribution")
    fig = px.histogram(
        df, x="discount_pct", color="category",
        nbins=5, barmode="overlay", opacity=0.75,
        title="Discount % Distribution by Category",
        labels={"discount_pct": "Discount (%)", "category": "Category"},
        template=TEMPLATE,
    )
    fig.update_layout(xaxis_title="Discount (%)", yaxis_title="Order Count")
    save_chart(fig, "discount_distribution")


# ---------------------------------------------------------------------------
# Chart 9 -- Order Status (donut)
# ---------------------------------------------------------------------------

def chart_order_status(df: pd.DataFrame) -> None:
    print("\n[chart 9] Order Status Breakdown")
    grp = (
        df.groupby("status")
        .agg(order_count=("order_id", "count"), revenue_sum=("revenue", "sum"))
        .reset_index()
    )

    fig = go.Figure(
        go.Pie(
            labels=grp["status"], values=grp["order_count"],
            hole=0.45,
            customdata=grp["revenue_sum"].values,
            hovertemplate="%{label}<br>Orders: %{value} (%{percent})<br>Revenue: $%{customdata:,.0f}<extra></extra>",
            marker_colors=["#00CC96", "#FFA15A"],
        )
    )
    fig.update_layout(title="Order Status Breakdown", template=TEMPLATE)
    save_chart(fig, "order_status")


# ---------------------------------------------------------------------------
# Chart 10 -- Revenue Heatmap (region x category)
# ---------------------------------------------------------------------------

def chart_revenue_heatmap(df: pd.DataFrame) -> None:
    print("\n[chart 10] Revenue Heatmap (Region x Category)")
    pivot = df.pivot_table(values="revenue", index="region", columns="category", aggfunc="sum", fill_value=0)
    regions = list(pivot.index)
    categories = list(pivot.columns)
    z_values = pivot.values.tolist()
    text_values = [[fmt_currency(v) for v in row] for row in z_values]

    fig = go.Figure(
        go.Heatmap(
            z=z_values, x=categories, y=regions,
            text=text_values, texttemplate="%{text}",
            colorscale="Blues",
            hovertemplate="Region: %{y}<br>Category: %{x}<br>Revenue: $%{z:,.0f}<extra></extra>",
            showscale=True,
        )
    )
    fig.update_layout(
        title="Revenue Heatmap: Region x Category", template=TEMPLATE,
        xaxis_title="Category", yaxis_title="Region",
    )
    save_chart(fig, "revenue_heatmap")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    df, stats = load_data()

    chart_monthly_revenue(df)
    chart_cumulative_revenue(df)
    chart_revenue_by_region(df)
    chart_revenue_by_category(df)
    chart_revenue_by_product(df)
    chart_sales_rep_performance(df)
    chart_top_customers(df)
    chart_discount_distribution(df)
    chart_order_status(df)
    chart_revenue_heatmap(df)

    html_count = len(list(CHARTS_DIR.glob("*.html")))
    png_count = len(list(CHARTS_DIR.glob("*.png")))
    print(f"\n[done] Charts saved: {html_count} HTML, {png_count} PNG -> {CHARTS_DIR}")


if __name__ == "__main__":
    main()
