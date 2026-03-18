"""
Data Intelligence Dashboard — Shiny for Python
Auto-discovers the highest PROJECT_XX output folder.
"""

from __future__ import annotations

import base64
import random
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_widget

# ---------------------------------------------------------------------------
# Constants — resolved at startup
# ---------------------------------------------------------------------------
_candidates = sorted(Path("output").glob("PROJECT_*"))
OUTPUT_DIR = _candidates[-1]
PROJECT_NAME = OUTPUT_DIR.name
PORT = random.randint(8000, 8999)

CHARTS_DIR = OUTPUT_DIR / "charts"
CLEAN_CSV = OUTPUT_DIR / "clean.csv"
DIRTY_CSV = OUTPUT_DIR / "dirty.csv"
SUMMARY_CSV = OUTPUT_DIR / "summary_stats.csv"
REPORT_HTML = OUTPUT_DIR / "report.html"

HAS_CHARTS = CHARTS_DIR.exists() and bool(list(CHARTS_DIR.glob("*.png")))
HAS_CLEAN = CLEAN_CSV.exists()
HAS_DIRTY = DIRTY_CSV.exists()
HAS_SUMMARY = SUMMARY_CSV.exists()
HAS_REPORT = REPORT_HTML.exists()

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
df_clean = pd.read_csv(CLEAN_CSV) if HAS_CLEAN else pd.DataFrame()
df_dirty = pd.read_csv(DIRTY_CSV) if HAS_DIRTY else pd.DataFrame()
df_summary = pd.read_csv(SUMMARY_CSV) if HAS_SUMMARY else pd.DataFrame()

dirty_count = len(df_dirty)
chart_count = len(list(CHARTS_DIR.glob("*.png"))) if HAS_CHARTS else 0


def _kpi(name: str, default: str = "N/A") -> str:
    if df_summary.empty:
        return default
    row = df_summary[df_summary["metric_name"] == name]
    if row.empty:
        return default
    val = row.iloc[0]["metric_value"]
    try:
        fval = float(val)
        if fval >= 1_000_000:
            return f"${fval/1_000_000:.1f}M"
        if fval >= 1_000:
            return f"${fval:,.0f}"
        return f"{fval:,.2f}"
    except (ValueError, TypeError):
        return str(val)


total_revenue = _kpi("total_revenue")
order_count = _kpi("order_count")
avg_order_value = _kpi("avg_order_value")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def encode_png(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def kpi_card(title: str, value: str, icon: str = "bi-bar-chart-fill", color: str = "primary"):
    return ui.div(
        ui.div(
            ui.tags.i(class_=f"bi {icon}", style="font-size:2rem;"),
            ui.h2(value, class_="mt-1 mb-0 fw-bold"),
            ui.p(title, class_="text-muted mb-0 small"),
            class_="card-body text-center py-3",
        ),
        class_=f"card border-{color} shadow-sm mb-3",
        style="border-width:2px;",
    )


# ---------------------------------------------------------------------------
# Tab UI builders
# ---------------------------------------------------------------------------
def overview_ui():
    if HAS_REPORT:
        report_content = ui.tags.iframe(
            src="report.html",
            style="width:100%;height:600px;border:1px solid #444;border-radius:6px;",
        )
    else:
        report_content = ui.p("No report found.", class_="text-muted")

    return ui.div(
        ui.h4(f"{PROJECT_NAME} — Overview", class_="mb-4 mt-2"),
        ui.row(
            ui.column(3, kpi_card("Total Revenue", total_revenue, "bi-currency-dollar", "success")),
            ui.column(3, kpi_card("Orders", order_count, "bi-bag-check-fill", "primary")),
            ui.column(3, kpi_card("Avg Order Value", avg_order_value, "bi-receipt", "info")),
            ui.column(3, kpi_card("Dirty Rows Removed", str(dirty_count), "bi-trash3-fill", "danger")),
        ),
        ui.row(
            ui.column(3, kpi_card("Charts Generated", str(chart_count), "bi-image-fill", "warning")),
        ),
        ui.hr(),
        ui.h5("Narrative Report", class_="mb-3"),
        report_content,
        class_="p-3",
    )


def gallery_ui():
    if not HAS_CHARTS:
        return ui.p("No charts found.", class_="text-muted p-3")

    pngs = sorted(CHARTS_DIR.glob("*.png"))
    rows = []
    for i in range(0, len(pngs), 3):
        chunk = pngs[i: i + 3]
        cols = []
        for p in chunk:
            label = p.stem.replace("_", " ").title()
            cols.append(
                ui.column(
                    4,
                    ui.div(
                        ui.tags.img(
                            src=encode_png(p),
                            style="width:100%;border-radius:6px;",
                            alt=label,
                        ),
                        ui.p(label, class_="text-center small mt-1 mb-0 text-muted"),
                        class_="mb-4",
                    ),
                )
            )
        rows.append(ui.row(*cols))

    return ui.div(
        ui.h4("Charts Gallery", class_="mb-4 mt-2"),
        *rows,
        class_="p-3",
    )


def tables_ui():
    panels = []
    if HAS_CLEAN:
        panels.append(
            ui.nav_panel("Clean Data", ui.output_data_frame("tbl_clean"))
        )
    if HAS_DIRTY:
        panels.append(
            ui.nav_panel("Dirty Rows", ui.output_data_frame("tbl_dirty"))
        )
    if not panels:
        return ui.p("No CSV files found.", class_="text-muted p-3")
    return ui.div(
        ui.h4("Data Tables", class_="mb-4 mt-2"),
        ui.navset_tab(*panels, id="data_tabs"),
        class_="p-3",
    )


def statistics_ui():
    if not HAS_SUMMARY:
        return ui.p("No summary_stats.csv found.", class_="text-muted p-3")
    return ui.div(
        ui.h4("Summary Statistics", class_="mb-4 mt-2"),
        output_widget("stats_chart"),
        ui.hr(),
        ui.output_data_frame("tbl_summary"),
        class_="p-3",
    )


def dirty_ui():
    if not HAS_DIRTY:
        return ui.p("No dirty.csv found.", class_="text-muted p-3")
    return ui.div(
        ui.h4("Dirty Data Analysis", class_="mb-4 mt-2"),
        output_widget("dirty_chart"),
        ui.hr(),
        ui.output_data_frame("tbl_dirty2"),
        class_="p-3",
    )


# ---------------------------------------------------------------------------
# Assemble nav panels
# ---------------------------------------------------------------------------
_nav_panels = [
    ui.nav_panel("Overview", overview_ui()),
    ui.nav_panel("Charts Gallery", gallery_ui()),
    ui.nav_panel("Data Tables", tables_ui()),
]
if HAS_SUMMARY:
    _nav_panels.append(ui.nav_panel("Statistics", statistics_ui()))
if HAS_DIRTY:
    _nav_panels.append(ui.nav_panel("Dirty Data", dirty_ui()))

# ---------------------------------------------------------------------------
# App UI
# ---------------------------------------------------------------------------
app_ui = ui.page_navbar(
    ui.head_content(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
        ),
        ui.output_ui("theme_link"),
    ),
    *_nav_panels,
    title=f"{PROJECT_NAME} — Data Intelligence",
    header=ui.div(
        ui.output_ui("toggle_icon", inline=True),
        ui.input_action_button(
            "toggle_theme",
            "",
            class_="btn btn-sm ms-2",
            style="border:none; background:transparent; cursor:pointer;",
        ),
        style="display:flex; align-items:center; margin-left:auto; padding-right:1rem;",
    ),
    id="navbar",
    bg="#222",
    inverse=True,
)


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
def server(input, output, session):
    theme_dark = reactive.Value(True)

    @reactive.effect
    @reactive.event(input.toggle_theme)
    def _flip_theme():
        theme_dark.set(not theme_dark.get())

    @render.ui
    def theme_link():
        href = (
            "https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/darkly/bootstrap.min.css"
            if theme_dark.get()
            else "https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/flatly/bootstrap.min.css"
        )
        return ui.tags.link(rel="stylesheet", href=href)

    @render.ui
    def toggle_icon():
        icon = "bi-sun-fill" if theme_dark.get() else "bi-moon-fill"
        return ui.tags.i(class_=f"bi {icon}", style="font-size:1.3rem; color:#f0ad4e;")

    # --- Data Tables ---
    if HAS_CLEAN:
        @render.data_frame
        def tbl_clean():
            return render.DataGrid(df_clean, filters=True, height="500px")

    if HAS_DIRTY:
        @render.data_frame
        def tbl_dirty():
            return render.DataGrid(df_dirty, filters=True)

        @render.data_frame
        def tbl_dirty2():
            return render.DataGrid(df_dirty, filters=True)

    # --- Statistics ---
    if HAS_SUMMARY:
        @render.data_frame
        def tbl_summary():
            return render.DataGrid(df_summary, filters=True, height="400px")

        @render_widget
        def stats_chart():
            template = "plotly_dark" if theme_dark.get() else "plotly_white"
            kpi_df = df_summary[df_summary["table"] == "kpis"].copy()
            if kpi_df.empty:
                kpi_df = df_summary.head(20).copy()
            kpi_df["metric_value"] = pd.to_numeric(kpi_df["metric_value"], errors="coerce")
            kpi_df = kpi_df.dropna(subset=["metric_value"])
            fig = px.bar(
                kpi_df,
                x="metric_name",
                y="metric_value",
                color="metric_value",
                color_continuous_scale="Viridis",
                title="Key Metrics",
                labels={"metric_name": "Metric", "metric_value": "Value"},
                template=template,
            )
            fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-30)
            return fig

    # --- Dirty Data ---
    if HAS_DIRTY:
        @render_widget
        def dirty_chart():
            template = "plotly_dark" if theme_dark.get() else "plotly_white"
            if "reason" not in df_dirty.columns or df_dirty.empty:
                fig = go.Figure()
                fig.update_layout(title="No reason data", template=template)
                return fig

            reasons = (
                df_dirty["reason"]
                .str.split(";")
                .explode()
                .str.strip()
                .value_counts()
                .reset_index()
            )
            reasons.columns = ["reason", "count"]
            fig = px.bar(
                reasons,
                x="count",
                y="reason",
                orientation="h",
                title=f"Dirty Row Reasons ({dirty_count} rows removed)",
                labels={"count": "Count", "reason": "Reason"},
                color="count",
                color_continuous_scale="Reds",
                template=template,
            )
            fig.update_layout(
                coloraxis_showscale=False,
                yaxis={"categoryorder": "total ascending"},
            )
            return fig


app = App(app_ui, server)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=PORT)
