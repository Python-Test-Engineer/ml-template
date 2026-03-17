"""Superstore Analytics — Shiny for Python Dashboard
Multi-tab dashboard for PROJECT_02 output folder.
Run: uv run python src/dashboard_shiny.py
"""
from __future__ import annotations

import base64
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from shiny import App, render, ui
from shinywidgets import output_widget, render_widget

# ---------------------------------------------------------------------------
# Constants & data loading
# ---------------------------------------------------------------------------
OUTPUT_DIR  = Path("output/PROJECT_02")
PROJECT_NAME = OUTPUT_DIR.name
TABLES_DIR  = OUTPUT_DIR / "tables"
MODEL_DIR   = OUTPUT_DIR / "model"
PLOTS_DIR   = OUTPUT_DIR / "plots"
TEMPLATE    = "plotly_dark"


def _csv(p: Path) -> pd.DataFrame:
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

def _parquet(p: Path) -> pd.DataFrame:
    return pd.read_parquet(p) if p.exists() else pd.DataFrame()

def encode_image(p: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


pbc    = _csv(TABLES_DIR / "profit_by_category.csv")
be     = _csv(TABLES_DIR / "discount_breakeven.csv")
rfm    = _csv(TABLES_DIR / "rfm_scores.csv")
tests  = _csv(TABLES_DIR / "statistical_tests.csv")
cr     = _csv(MODEL_DIR  / "classification_report.csv")
dirty  = _csv(OUTPUT_DIR / "dirty.csv")
ss     = _parquet(OUTPUT_DIR / "superstore_clean.parquet")
report = (OUTPUT_DIR / "report.txt").read_text(encoding="utf-8") if (OUTPUT_DIR / "report.txt").exists() else ""

plot_images: dict[str, str] = {
    p.stem: encode_image(p)
    for p in sorted(PLOTS_DIR.glob("*.png"))
}

GALLERY_LABELS = {
    "01_profit_distribution":      "Profit Distribution",
    "02_profit_by_category":       "Profit by Category",
    "03_profit_by_subcategory":    "Profit by Sub-Category",
    "04_discount_vs_profit":       "Discount vs Profit",
    "05_sales_profit_over_time":   "Sales & Profit Over Time",
    "06_region_segment_heatmap":   "Region x Segment Heatmap",
    "07_shipmode_profit_violin":   "Ship Mode Profit Violin",
    "08_top_bottom_products":      "Top / Bottom Products",
    "09_customer_order_frequency": "Customer Order Frequency",
    "10_web_conversion_by_source": "Web Conversion by Source",
    "11_web_bounce_vs_session":    "Bounce Rate vs Session",
    "12_correlation_heatmap":      "Correlation Heatmap",
    "13_rfm_segments":             "RFM Segments",
    "14_stl_decomposition":        "STL Decomposition",
    "15_feature_importance":       "Feature Importance",
    "16_roc_curves":               "ROC Curves",
}

# Derived KPIs (computed once)
N_CLEAN    = f"{len(ss):,}" if not ss.empty else "N/A"
N_DIRTY    = str(len(dirty)) if not dirty.empty else "0"
LOSS_RATE  = f"{ss['is_loss'].mean():.1%}" if "is_loss" in ss.columns else "N/A"
if "Order Date" in ss.columns and not ss.empty:
    dates = pd.to_datetime(ss["Order Date"])
    DATE_RANGE = f"{dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}"
else:
    DATE_RANGE = "N/A"

CATEGORIES = sorted(pbc["Category"].unique().tolist()) if not pbc.empty else []
RFM_SEGMENTS = sorted(rfm["Segment"].unique().tolist()) if not rfm.empty else []

# ---------------------------------------------------------------------------
# Helper: inline PNG tag
# ---------------------------------------------------------------------------
def img(stem: str, width: str = "100%") -> ui.Tag:
    if stem not in plot_images:
        return ui.p(f"({stem}.png not found)", class_="text-muted")
    return ui.img(src=plot_images[stem], style=f"width:{width};border-radius:6px;")


def section(title: str, *children) -> ui.Tag:
    return ui.div(
        ui.h5(title, class_="mt-4 mb-2 fw-semibold"),
        *children,
    )


def kpi_box(label: str, value: str, theme: str = "primary") -> ui.Tag:
    return ui.value_box(
        title=label,
        value=value,
        theme=theme,
        class_="mb-3",
    )

# ---------------------------------------------------------------------------
# Gallery grid (built once)
# ---------------------------------------------------------------------------
def gallery_grid() -> ui.Tag:
    cols = []
    items = [(s, l) for s, l in GALLERY_LABELS.items() if s in plot_images]
    for i in range(0, len(items), 3):
        row_items = items[i:i+3]
        row_cols = []
        for stem, label in row_items:
            row_cols.append(
                ui.column(4,
                    ui.card(
                        ui.card_header(label),
                        ui.card_body(img(stem), class_="p-1"),
                        class_="mb-3",
                    )
                )
            )
        # pad to 3 columns if needed
        while len(row_cols) < 3:
            row_cols.append(ui.column(4))
        cols.append(ui.row(*row_cols))
    return ui.div(*cols)

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
app_ui = ui.page_navbar(
    # ── Overview ─────────────────────────────────────────────────────────────
    ui.nav_panel("Overview",
        ui.layout_columns(
            kpi_box("Clean Rows",         N_CLEAN,    "primary"),
            kpi_box("Dirty Rows Removed", N_DIRTY,    "warning"),
            kpi_box("Loss-Making Orders", LOSS_RATE,  "danger"),
            kpi_box("Date Range",         DATE_RANGE, "bg-blue"),
            col_widths=[3, 3, 3, 3],
        ),
        ui.hr(),
        ui.h5("Report Summary"),
        ui.pre(report,
               style="white-space:pre-wrap;font-size:0.78rem;"
                     "background:#1e1e2e;color:#cdd6f4;padding:1rem;"
                     "border-radius:6px;max-height:420px;overflow-y:auto;"),
        ui.hr(),
        ui.h5("Charts Gallery", class_="mt-3 mb-3"),
        gallery_grid(),
    ),

    # ── Profitability ─────────────────────────────────────────────────────────
    ui.nav_panel("Profitability",
        ui.layout_sidebar(
            ui.sidebar(
                ui.h6("Filter"),
                ui.input_checkbox_group(
                    "cat_filter", "Category",
                    choices=CATEGORIES,
                    selected=CATEGORIES,
                ),
                width=220,
            ),
            ui.h4("Profitability Analysis"),
            output_widget("fig_profit_bar"),
            output_widget("fig_loss_pct"),
            section("Raw Data Table"),
            ui.output_data_frame("tbl_profit"),
        )
    ),

    # ── Discount ─────────────────────────────────────────────────────────────
    ui.nav_panel("Discount",
        ui.h4("Discount Analysis"),
        ui.layout_columns(
            ui.card(ui.card_header("Discount vs Profit (sample 3,000)"),
                    output_widget("fig_disc_scatter")),
            ui.card(ui.card_header("Discount Distribution by Category"),
                    output_widget("fig_disc_box")),
            col_widths=[7, 5],
        ),
        section("Breakeven Discount by Category"),
        ui.output_data_frame("tbl_breakeven"),
    ),

    # ── RFM ──────────────────────────────────────────────────────────────────
    ui.nav_panel("RFM Segments",
        ui.h4("RFM Customer Segmentation"),
        ui.layout_sidebar(
            ui.sidebar(
                ui.h6("Filter Segment"),
                ui.input_checkbox_group(
                    "rfm_filter", "Segment",
                    choices=RFM_SEGMENTS,
                    selected=RFM_SEGMENTS,
                ),
                width=220,
            ),
            ui.layout_columns(
                ui.card(ui.card_header("Segment Distribution"),
                        output_widget("fig_rfm_pie")),
                ui.card(ui.card_header("Recency vs Monetary"),
                        output_widget("fig_rfm_scatter")),
                col_widths=[5, 7],
            ),
            section("RFM Score Table"),
            ui.output_data_frame("tbl_rfm"),
        )
    ),

    # ── Statistics ───────────────────────────────────────────────────────────
    ui.nav_panel("Statistics",
        ui.h4("Statistical Tests"),
        output_widget("fig_stats_table"),
        output_widget("fig_mean_median"),
        section("Pearson Correlation Heatmap"),
        img("12_correlation_heatmap"),
    ),

    # ── Models ───────────────────────────────────────────────────────────────
    ui.nav_panel("Models",
        ui.h4("Model Evaluation"),
        ui.layout_columns(
            ui.card(ui.card_header("CV AUROC by Model"),   output_widget("fig_auroc")),
            ui.card(ui.card_header("CV F1-Macro by Model"), output_widget("fig_f1")),
            col_widths=[6, 6],
        ),
        section("Full Metrics Table"),
        ui.output_data_frame("tbl_cr"),
        section("Feature Importance (Random Forest)"),
        img("15_feature_importance"),
        section("ROC Curves — All Models"),
        img("16_roc_curves"),
    ),

    title=f"Superstore Analytics — {PROJECT_NAME}",
    bg="#1e1e2e",
    inverse=True,
    fillable=False,
)

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
def server(input, output, session):

    # ── Profitability ─────────────────────────────────────────────────────────
    @render_widget
    def fig_profit_bar():
        cats = list(input.cat_filter()) if input.cat_filter() else CATEGORIES
        df = pbc[pbc["Category"].isin(cats)].sort_values("mean_profit")
        return px.bar(
            df, x="mean_profit", y="Sub-Category", orientation="h",
            color="mean_profit",
            color_continuous_scale=["#d62728", "#f7f7f7", "#2ca02c"],
            color_continuous_midpoint=0,
            facet_col="Category", facet_col_wrap=3,
            title="Mean Profit by Sub-Category",
            labels={"mean_profit": "Mean Profit (USD)"},
            template=TEMPLATE, height=480,
        )

    @render_widget
    def fig_loss_pct():
        cats = list(input.cat_filter()) if input.cat_filter() else CATEGORIES
        df = pbc[pbc["Category"].isin(cats)].sort_values("pct_loss", ascending=False)
        return px.bar(
            df, x="Sub-Category", y="pct_loss", color="Category",
            title="% Loss-Making Orders by Sub-Category",
            labels={"pct_loss": "% Loss Orders"},
            template=TEMPLATE, height=420,
        )

    @render.data_frame
    def tbl_profit():
        cats = list(input.cat_filter()) if input.cat_filter() else CATEGORIES
        df = pbc[pbc["Category"].isin(cats)].round(3)
        return render.DataGrid(df, filters=True, height="350px")

    # ── Discount ─────────────────────────────────────────────────────────────
    @render_widget
    def fig_disc_scatter():
        if ss.empty:
            return go.Figure()
        sample = ss.sample(min(3000, len(ss)), random_state=42)
        fig = px.scatter(
            sample, x="Discount", y="Profit",
            color=sample["is_loss"].map({0: "Profitable", 1: "Loss"}),
            color_discrete_map={"Profitable": "#2ca02c", "Loss": "#d62728"},
            opacity=0.4, trendline="ols",
            labels={"color": "Order Type"},
            template=TEMPLATE, height=460,
        )
        fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.4)
        return fig

    @render_widget
    def fig_disc_box():
        if ss.empty:
            return go.Figure()
        return px.box(
            ss, x="Category", y="Discount", color="Category",
            title="Discount Distribution per Category",
            template=TEMPLATE, height=460,
        )

    @render.data_frame
    def tbl_breakeven():
        return render.DataGrid(be, height="200px")

    # ── RFM ──────────────────────────────────────────────────────────────────
    @render_widget
    def fig_rfm_pie():
        segs = list(input.rfm_filter()) if input.rfm_filter() else RFM_SEGMENTS
        df = rfm[rfm["Segment"].isin(segs)]
        counts = df["Segment"].value_counts().reset_index()
        counts.columns = ["Segment", "Count"]
        return px.pie(
            counts, names="Segment", values="Count",
            color_discrete_sequence=px.colors.qualitative.Bold,
            template=TEMPLATE, height=420,
        )

    @render_widget
    def fig_rfm_scatter():
        segs = list(input.rfm_filter()) if input.rfm_filter() else RFM_SEGMENTS
        df = rfm[rfm["Segment"].isin(segs)]
        return px.scatter(
            df, x="Recency", y="Monetary", size="Frequency", color="Segment",
            title="Recency vs Monetary (size = Frequency)",
            labels={"Recency": "Recency (days)", "Monetary": "Monetary ($)"},
            color_discrete_sequence=px.colors.qualitative.Bold,
            template=TEMPLATE, height=420,
        )

    @render.data_frame
    def tbl_rfm():
        segs = list(input.rfm_filter()) if input.rfm_filter() else RFM_SEGMENTS
        cols = [c for c in ["Customer ID", "Recency", "Frequency", "Monetary",
                             "R", "F", "M", "RFM_Score", "Segment"] if c in rfm.columns]
        df = rfm[rfm["Segment"].isin(segs)][cols].round(2)
        return render.DataGrid(df, filters=True, height="400px")

    # ── Statistics ───────────────────────────────────────────────────────────
    @render_widget
    def fig_stats_table():
        if tests.empty:
            return go.Figure()
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=[f"<b>{c}</b>" for c in tests.columns],
                fill_color="#1e1e2e", font=dict(color="white", size=13),
                align="left",
            ),
            cells=dict(
                values=[tests[c] for c in tests.columns],
                fill_color=[["#2a2a3e" if i % 2 == 0 else "#252540"
                              for i in range(len(tests))]] * len(tests.columns),
                font=dict(color="white", size=12),
                align="left",
            )
        )])
        fig.update_layout(template=TEMPLATE, height=260, margin=dict(t=10, b=10))
        return fig

    @render_widget
    def fig_mean_median():
        if pbc.empty:
            return go.Figure()
        fig = px.bar(
            pbc, x="Sub-Category", y=["mean_profit", "median_profit"],
            barmode="group",
            title="Mean vs Median Profit per Sub-Category",
            template=TEMPLATE, height=440,
        )
        fig.update_xaxes(tickangle=45)
        return fig

    # ── Models ───────────────────────────────────────────────────────────────
    @render_widget
    def fig_auroc():
        if cr.empty:
            return go.Figure()
        fig = px.bar(
            cr, x="model_name", y="cv_auroc_mean", error_y="cv_auroc_std",
            color="model_name",
            labels={"cv_auroc_mean": "Mean CV AUROC", "model_name": "Model"},
            color_discrete_sequence=px.colors.qualitative.Bold,
            template=TEMPLATE, height=380,
        )
        fig.update_yaxes(range=[0.95, 1.0])
        fig.update_layout(showlegend=False)
        return fig

    @render_widget
    def fig_f1():
        if cr.empty:
            return go.Figure()
        fig = px.bar(
            cr, x="model_name", y="cv_f1_mean", error_y="cv_f1_std",
            color="model_name",
            labels={"cv_f1_mean": "Mean CV F1-Macro", "model_name": "Model"},
            color_discrete_sequence=px.colors.qualitative.Bold,
            template=TEMPLATE, height=380,
        )
        fig.update_layout(showlegend=False)
        return fig

    @render.data_frame
    def tbl_cr():
        return render.DataGrid(cr.round(4), height="200px")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
app = App(app_ui, server)

if __name__ == "__main__":
    import uvicorn
    print(f"Shiny dashboard starting on http://127.0.0.1:8051")
    print(f"Output directory: {OUTPUT_DIR.resolve()}")
    uvicorn.run(app, host="127.0.0.1", port=8051)
