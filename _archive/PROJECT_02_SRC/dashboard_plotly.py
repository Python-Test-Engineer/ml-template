"""Superstore Analytics Dashboard
Multi-tab Plotly Dash app for PROJECT_02 output folder.
Run: uv run python src/dashboard.py
"""
from __future__ import annotations

import base64
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dash_table, dcc, html

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path("output/PROJECT_02")
PROJECT_NAME = OUTPUT_DIR.name
PORT = 8050

TABLES_DIR = OUTPUT_DIR / "tables"
MODEL_DIR  = OUTPUT_DIR / "model"
PLOTS_DIR  = OUTPUT_DIR / "plots"

# Plotly template that matches the dark theme
TEMPLATE = "plotly_dark"

# ---------------------------------------------------------------------------
# Data loading  (done once at startup)
# ---------------------------------------------------------------------------
def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()

def _read_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path) if path.exists() else pd.DataFrame()

def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else "(file not found)"

def encode_image(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()

# Load all data at startup
pbc     = _read_csv(TABLES_DIR / "profit_by_category.csv")
be      = _read_csv(TABLES_DIR / "discount_breakeven.csv")
rfm     = _read_csv(TABLES_DIR / "rfm_scores.csv")
tests   = _read_csv(TABLES_DIR / "statistical_tests.csv")
cr      = _read_csv(MODEL_DIR  / "classification_report.csv")
dirty   = _read_csv(OUTPUT_DIR / "dirty.csv")
ss      = _read_parquet(OUTPUT_DIR / "superstore_clean.parquet")
report  = _read_text(OUTPUT_DIR / "report.txt")

# Pre-encode all PNGs
plot_images: dict[str, str] = {
    p.stem: encode_image(p)
    for p in sorted(PLOTS_DIR.glob("*.png"))
    if p.exists()
}

# ---------------------------------------------------------------------------
# KPI helpers
# ---------------------------------------------------------------------------
def kpi_card(title: str, value: str, colour: str = "primary") -> dbc.Col:
    return dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.H2(value, className="card-title text-center fw-bold"),
                html.P(title, className="card-text text-center text-muted"),
            ])
        ], color=colour, outline=True),
        xs=12, sm=6, md=3, className="mb-3",
    )

# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def tab_overview() -> html.Div:
    n_clean = len(ss) if not ss.empty else "N/A"
    n_dirty = len(dirty) if not dirty.empty else 0
    loss_rate = f"{ss['is_loss'].mean():.1%}" if "is_loss" in ss.columns else "N/A"
    date_range = (
        f"{pd.to_datetime(ss['Order Date']).min().strftime('%Y-%m-%d')} to {pd.to_datetime(ss['Order Date']).max().strftime('%Y-%m-%d')}"
        if "Order Date" in ss.columns and not ss.empty
        else "N/A"
    )

    LABELS = {
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
    gallery_cards = []
    for stem, label in LABELS.items():
        if stem not in plot_images:
            continue
        gallery_cards.append(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(label, className="fw-semibold text-center"),
                    dbc.CardBody(
                        html.Img(src=plot_images[stem],
                                 style={"width": "100%", "borderRadius": "4px"}),
                        className="p-1",
                    ),
                ], className="mb-3"),
                xs=12, sm=6, lg=4,
            )
        )

    return html.Div([
        html.H4("Project Overview", className="mt-3 mb-3"),
        dbc.Row([
            kpi_card("Clean Rows",        f"{n_clean:,}" if isinstance(n_clean, int) else n_clean, "primary"),
            kpi_card("Dirty Rows Removed", str(n_dirty), "warning"),
            kpi_card("Loss-Making Orders", loss_rate, "danger"),
            kpi_card("Date Range",         date_range, "info"),
        ]),
        html.Hr(),
        html.H5("Report Summary"),
        html.Pre(
            report,
            style={
                "whiteSpace": "pre-wrap",
                "fontFamily": "monospace",
                "fontSize": "0.8rem",
                "backgroundColor": "#1e1e2e",
                "padding": "1rem",
                "borderRadius": "6px",
                "maxHeight": "500px",
                "overflowY": "auto",
            }
        ),
        html.Hr(),
        html.H5("Charts Gallery", className="mt-3 mb-2"),
        html.P(f"{len(gallery_cards)} charts", className="text-muted mb-3"),
        dbc.Row(gallery_cards),
    ])


def tab_profitability() -> html.Div:
    if pbc.empty:
        return html.Div("profit_by_category.csv not found.")

    categories = sorted(pbc["Category"].unique())
    options    = [{"label": c, "value": c} for c in categories]

    fig_bar = px.bar(
        pbc.sort_values("mean_profit"),
        x="mean_profit", y="Sub-Category", orientation="h",
        color="mean_profit",
        color_continuous_scale=["#d62728", "#f7f7f7", "#2ca02c"],
        color_continuous_midpoint=0,
        facet_col="Category",
        title="Mean Profit by Sub-Category",
        labels={"mean_profit": "Mean Profit (USD)"},
        template=TEMPLATE, height=500,
    )

    fig_loss = px.bar(
        pbc.sort_values("pct_loss", ascending=False),
        x="Sub-Category", y="pct_loss",
        color="Category",
        title="% Loss-Making Orders by Sub-Category",
        labels={"pct_loss": "% Loss Orders"},
        template=TEMPLATE, height=450,
    )
    fig_loss.update_xaxes(tickangle=45)

    return html.Div([
        html.H4("Profitability Analysis", className="mt-3 mb-3"),
        dcc.Graph(figure=fig_bar),
        dcc.Graph(figure=fig_loss),
        html.H5("Raw Data", className="mt-4"),
        dash_table.DataTable(
            data=pbc.round(3).to_dict("records"),
            columns=[{"name": c, "id": c} for c in pbc.columns],
            filter_action="native", sort_action="native",
            page_size=17,
            style_table={"overflowX": "auto"},
            style_cell={"backgroundColor": "#2a2a3e", "color": "white", "fontSize": "0.82rem"},
            style_header={"backgroundColor": "#1e1e2e", "fontWeight": "bold"},
            style_data_conditional=[
                {"if": {"filter_query": "{mean_profit} < 0"}, "color": "#ff6b6b"},
            ],
        ),
    ])


def tab_discount() -> html.Div:
    if ss.empty:
        return html.Div("superstore_clean.parquet not found.")

    sample = ss.sample(min(3000, len(ss)), random_state=42)
    fig = px.scatter(
        sample, x="Discount", y="Profit",
        color=sample["is_loss"].map({0: "Profitable", 1: "Loss"}),
        color_discrete_map={"Profitable": "#2ca02c", "Loss": "#d62728"},
        opacity=0.4, trendline="ols",
        title="Discount vs Profit (sample of 3,000 orders)",
        labels={"color": "Order Type"},
        template=TEMPLATE, height=500,
    )
    fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.4)

    return html.Div([
        html.H4("Discount Analysis", className="mt-3 mb-3"),
        dcc.Graph(figure=fig),
        html.Hr(),
        html.H5("Breakeven Discount by Category"),
        dash_table.DataTable(
            data=be.to_dict("records"),
            columns=[{"name": c, "id": c} for c in be.columns],
            style_table={"overflowX": "auto"},
            style_cell={"backgroundColor": "#2a2a3e", "color": "white"},
            style_header={"backgroundColor": "#1e1e2e", "fontWeight": "bold"},
        ),
        html.Hr(),
        html.H5("Discount Distribution by Category"),
        dcc.Graph(figure=px.box(
            ss, x="Category", y="Discount", color="Category",
            title="Discount Distribution per Category",
            template=TEMPLATE, height=400,
        )),
    ])


def tab_rfm() -> html.Div:
    if rfm.empty:
        return html.Div("rfm_scores.csv not found.")

    seg_counts = rfm["Segment"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Count"]

    fig_pie = px.pie(
        seg_counts, names="Segment", values="Count",
        title="Customer Segments (RFM)",
        color_discrete_sequence=px.colors.qualitative.Bold,
        template=TEMPLATE, height=420,
    )

    fig_scatter = px.scatter(
        rfm, x="Recency", y="Monetary",
        size="Frequency", color="Segment",
        title="RFM Space: Recency vs Monetary (size = Frequency)",
        labels={"Recency": "Recency (days)", "Monetary": "Monetary ($)"},
        color_discrete_sequence=px.colors.qualitative.Bold,
        template=TEMPLATE, height=480,
    )

    table_cols = ["Customer ID", "Recency", "Frequency", "Monetary", "R", "F", "M", "RFM_Score", "Segment"]
    display_cols = [c for c in table_cols if c in rfm.columns]

    return html.Div([
        html.H4("RFM Customer Segmentation", className="mt-3 mb-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_pie), md=5),
            dbc.Col(dcc.Graph(figure=fig_scatter), md=7),
        ]),
        html.H5("RFM Score Table", className="mt-4"),
        dash_table.DataTable(
            data=rfm[display_cols].round(2).to_dict("records"),
            columns=[{"name": c, "id": c} for c in display_cols],
            filter_action="native", sort_action="native",
            page_size=15,
            style_table={"overflowX": "auto"},
            style_cell={"backgroundColor": "#2a2a3e", "color": "white", "fontSize": "0.8rem"},
            style_header={"backgroundColor": "#1e1e2e", "fontWeight": "bold"},
            style_data_conditional=[
                {"if": {"filter_query": '{Segment} = "Champions"'}, "color": "#ffd700"},
                {"if": {"filter_query": '{Segment} = "At Risk"'},   "color": "#ff6b6b"},
                {"if": {"filter_query": '{Segment} = "Loyal"'},     "color": "#90ee90"},
            ],
        ),
    ])


def tab_statistics() -> html.Div:
    children = [html.H4("Statistical Tests", className="mt-3 mb-3")]

    if not tests.empty:
        fig = go.Figure(data=[
            go.Table(
                header=dict(
                    values=[f"<b>{c}</b>" for c in tests.columns],
                    fill_color="#1e1e2e", font=dict(color="white", size=13),
                    align="left",
                ),
                cells=dict(
                    values=[tests[c] for c in tests.columns],
                    fill_color=[
                        ["#2a2a3e" if i % 2 == 0 else "#1e2a3e" for i in range(len(tests))]
                    ] * len(tests.columns),
                    font=dict(color="white", size=12),
                    align="left",
                )
            )
        ])
        fig.update_layout(template=TEMPLATE, height=280, margin=dict(t=10, b=10))
        children.append(dcc.Graph(figure=fig))

    # Profit by category breakdown (interactive)
    if not pbc.empty:
        fig2 = px.bar(
            pbc, x="Sub-Category", y=["mean_profit", "median_profit"],
            barmode="group",
            title="Mean vs Median Profit per Sub-Category",
            template=TEMPLATE, height=450,
        )
        fig2.update_xaxes(tickangle=45)
        children += [html.Hr(), dcc.Graph(figure=fig2)]

    # Correlation heatmap PNG
    if "12_correlation_heatmap" in plot_images:
        children += [
            html.Hr(),
            html.H5("Pearson Correlation Heatmap"),
            html.Img(src=plot_images["12_correlation_heatmap"],
                     style={"maxWidth": "100%", "borderRadius": "6px"}),
        ]

    return html.Div(children)


def tab_models() -> html.Div:
    children = [html.H4("Model Evaluation", className="mt-3 mb-3")]

    if not cr.empty:
        fig_auroc = px.bar(
            cr, x="model_name", y="cv_auroc_mean",
            error_y="cv_auroc_std",
            color="model_name",
            title="CV AUROC by Model",
            labels={"cv_auroc_mean": "Mean CV AUROC", "model_name": "Model"},
            color_discrete_sequence=px.colors.qualitative.Bold,
            template=TEMPLATE, height=420,
        )
        fig_auroc.update_yaxes(range=[0.95, 1.0])

        fig_f1 = px.bar(
            cr, x="model_name", y="cv_f1_mean",
            error_y="cv_f1_std",
            color="model_name",
            title="CV F1-Macro by Model",
            labels={"cv_f1_mean": "Mean CV F1-Macro", "model_name": "Model"},
            color_discrete_sequence=px.colors.qualitative.Bold,
            template=TEMPLATE, height=420,
        )

        children += [
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_auroc), md=6),
                dbc.Col(dcc.Graph(figure=fig_f1), md=6),
            ]),
            html.H5("Full Metrics Table", className="mt-3"),
            dash_table.DataTable(
                data=cr.round(4).to_dict("records"),
                columns=[{"name": c, "id": c} for c in cr.columns],
                sort_action="native",
                style_table={"overflowX": "auto"},
                style_cell={"backgroundColor": "#2a2a3e", "color": "white", "fontSize": "0.8rem"},
                style_header={"backgroundColor": "#1e1e2e", "fontWeight": "bold"},
            ),
        ]

    # Feature importance + ROC curve PNGs
    for key, title in [
        ("15_feature_importance", "Random Forest Feature Importances"),
        ("16_roc_curves", "ROC Curves — All Models"),
    ]:
        if key in plot_images:
            children += [
                html.Hr(),
                html.H5(title),
                html.Img(src=plot_images[key],
                         style={"maxWidth": "100%", "borderRadius": "6px"}),
            ]

    return html.Div(children)




# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title=f"Superstore Analytics — {PROJECT_NAME}",
)

app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(
            html.H2(
                f"Superstore Analytics Dashboard — {PROJECT_NAME}",
                className="text-center py-3 fw-bold",
            )
        )
    ),
    dbc.Tabs(
        [
            dbc.Tab(label="Overview",        tab_id="overview"),
            dbc.Tab(label="Profitability",   tab_id="profit"),
            dbc.Tab(label="Discount",        tab_id="discount"),
            dbc.Tab(label="RFM Segments",    tab_id="rfm"),
            dbc.Tab(label="Statistics",      tab_id="stats"),
            dbc.Tab(label="Models",          tab_id="models"),
        ],
        id="tabs",
        active_tab="overview",
        className="mb-2",
    ),
    html.Div(id="tab-content"),
], fluid=True)


@app.callback(Output("tab-content", "children"), Input("tabs", "active_tab"))
def render_tab(active_tab: str) -> html.Div:
    return {
        "overview": tab_overview,
        "profit":   tab_profitability,
        "discount": tab_discount,
        "rfm":      tab_rfm,
        "stats":    tab_statistics,
        "models":   tab_models,
    }.get(active_tab, tab_overview)()


if __name__ == "__main__":
    print(f"Dashboard starting on http://127.0.0.1:{PORT}")
    print(f"Output directory: {OUTPUT_DIR.resolve()}")
    app.run(debug=False, port=PORT, host="127.0.0.1")
