---
description: "Build and launch an interactive Shiny dashboard from a PROJECT_XX output folder. Usage: /dashboard"
allowed-tools: Read, Glob, Grep, Bash(uv run python *), Bash(uv add *), Write, AskUserQuestion
---

Create a dashboard file in `src/dashboard.py` using **Shiny for Python only**.

Auto-discover the most recent project output folder by globbing `output/PROJECT_*` and selecting the one with the highest `_XX` number.

---

## Your role

You are an experienced data visualisation engineer. Your job is to:

1. Inspect the output folder at `$ARGUMENTS`
2. Discover all available data files (CSVs, PNGs, report HTML/txt, parquets, summary stats)
3. Install any missing dependencies
4. Write a production-quality **Shiny for Python** multi-page dashboard in `src/dashboard.py`
5. Run it and confirm it launches successfully

---

## Step 1 — Discover the output folder contents

Scan `$ARGUMENTS` for:
- `plots/*.png` — static chart images
- `*.csv` — data tables (summary_stats, dirty, etc.)
- `*.parquet` — clean datasets
- `report.html` or `report.txt` — narrative summary
- `tables/*.csv` — structured sub-tables
- `model/*.csv` — model metrics

Build a manifest of what is available. Adapt tabs to what actually exists — skip tabs for missing data.

---

## Step 2 — Install dependencies

```bash
uv add shiny shinyswatch shinywidgets plotly pandas pyarrow
```

Install all of the above. `plotly` and `shinywidgets` are only used where Shiny has no native equivalent — do not add Plotly charts where Shiny's built-in components (`render.DataGrid`, `ui.tags.img`, `ui.tags.iframe`, `ui.HTML`) are sufficient.

---

## Step 3 — Write `src/dashboard.py`

### Constants at top of file

Resolve the output folder at script startup by finding the highest-numbered `PROJECT_XX` folder:

```python
from pathlib import Path

_candidates = sorted(Path("output").glob("PROJECT_*"))
OUTPUT_DIR   = _candidates[-1]          # highest PROJECT_XX
PROJECT_NAME = OUTPUT_DIR.name          # e.g. "PROJECT_01"
PORT         = random.randint(8000, 8999)
```

### Architecture

Use `shiny.ui.page_navbar()` as the top-level layout with:

- A **brand title** on the left: `f"{PROJECT_NAME} — Data Intelligence Dashboard"`
- A **dark/light mode toggle** icon button in the navbar header (top-right)
- One `ui.nav_panel()` per data domain (see tab table below)

### Dark / Light mode toggle

Add Bootstrap Icons via CDN in `ui.head_content()`. Use a single `ui.input_action_button` with an id of `"toggle_theme"` styled as an icon-only button, showing a **moon icon** in light mode and a **sun icon** in dark mode. Implement via a `reactive.Value` that tracks the current theme and a `@render.ui` that injects a `<link>` tag swapping between `bootswatch` Flatly (light) and Darkly (dark) stylesheets. The button label must update reactively to show the correct icon.

```python
# Head content — Bootstrap Icons CDN
ui.head_content(
    ui.tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"
    )
)

# In server:
theme_dark = reactive.Value(True)   # start in dark mode

@reactive.effect
@reactive.event(input.toggle_theme)
def _flip_theme():
    theme_dark.set(not theme_dark.get())

@render.ui
def theme_link():
    if theme_dark.get():
        href = "https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/darkly/bootstrap.min.css"
    else:
        href = "https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/flatly/bootstrap.min.css"
    return ui.tags.link(rel="stylesheet", href=href)

@render.ui
def toggle_icon():
    icon = "bi-sun-fill" if theme_dark.get() else "bi-moon-fill"
    return ui.tags.i(class_=f"bi {icon}", style="font-size:1.3rem;")
```

Place `ui.output_ui("theme_link")` inside `ui.head_content()` and the toggle button in the navbar's `header=` argument:

```python
header=ui.div(
    ui.output_ui("toggle_icon", inline=True),
    ui.input_action_button(
        "toggle_theme", "",
        class_="btn btn-outline-secondary btn-sm ms-2",
        style="border:none; background:transparent;"
    ),
    style="display:flex; align-items:center; margin-left:auto; padding-right:1rem;"
)
```

### Tabs — adapt to available files

| Tab | Condition | Content | Rendering approach |
|-----|-----------|---------|-------------------|
| **Overview** | always | KPI cards (total rows, dirty rows removed, number of plots, date of run). Render `report.html` in a `ui.tags.iframe` or `report.txt` in a `ui.tags.pre` block. | **Shiny only** — `ui.HTML`, `ui.tags.*`, `ui.output_ui` |
| **Charts Gallery** | `charts/*.png` exist | Responsive image grid — encode each PNG as base64 inline. Group in rows of 3 using Bootstrap grid (`col-md-4`). | **Shiny only** — `ui.tags.img` with base64 src |
| **Data Tables** | any `*.csv` or `*.parquet` | Tabbed sub-panels, one per file. Sorting and filtering enabled. | **Shiny only** — `ui.output_data_frame` / `render.DataGrid` |
| **Statistics** | `summary_stats.csv` exists | Render the CSV as a styled DataGrid. Add a Plotly bar chart **only** for numeric KPI comparison where a chart genuinely adds over the table. | **Shiny** for table; **Plotly** for chart only if it adds value |
| **Dirty Data** | `dirty.csv` exists | Show removed-rows count by reason as a bar chart; render full dirty table. | **Plotly** bar chart (no Shiny native equivalent) + **Shiny** DataGrid |

### PNG embedding helper

```python
import base64

def encode_png(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()
```

### Plotly charts

All interactive charts must use `plotly.express` or `plotly.graph_objects`. Render them with `@render_widget` from `shinywidgets`:

```python
from shinywidgets import output_widget, render_widget
import plotly.express as px

# In UI:
output_widget("my_chart")

# In server:
@render_widget
def my_chart():
    fig = px.bar(df, x="col_a", y="col_b", title="My Chart")
    fig.update_layout(template="plotly_dark" if theme_dark.get() else "plotly_white")
    return fig
```

Always pass `template="plotly_dark"` or `"plotly_white"` based on `theme_dark.get()` so charts match the current theme.

### KPI card helper

```python
def kpi_card(title: str, value: str, icon: str = "bi-bar-chart-fill", color: str = "primary"):
    return ui.div(
        ui.div(
            ui.tags.i(class_=f"bi {icon}", style="font-size:2rem;"),
            ui.h2(value, class_="mt-1 mb-0"),
            ui.p(title, class_="text-muted mb-0"),
            class_="card-body text-center"
        ),
        class_=f"card border-{color} mb-3"
    )
```

### Full layout skeleton

```python
app_ui = ui.page_navbar(
    ui.head_content(
        ui.tags.link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"),
        ui.output_ui("theme_link"),
    ),
    # --- nav panels go here ---
    ui.nav_panel("Overview",       overview_ui()),
    ui.nav_panel("Charts Gallery", gallery_ui()),
    ui.nav_panel("Data Tables",    tables_ui()),
    # add / remove panels based on available files
    title=f"{PROJECT_NAME} — Data Intelligence",
    header=ui.div(
        ui.output_ui("toggle_icon", inline=True),
        ui.input_action_button(
            "toggle_theme", "",
            class_="btn btn-sm ms-2",
            style="border:none; background:transparent; cursor:pointer;"
        ),
        style="display:flex; align-items:center; margin-left:auto; padding-right:1rem;"
    ),
    id="navbar",
    bg="#222" ,        # overridden by the dynamic theme link anyway
    inverse=True,
)

app = App(app_ui, server)
```

---

## Step 4 — Run the dashboard

```bash
uv run python src/dashboard.py
```

The app should start and print something like:
```
Uvicorn running on http://127.0.0.1:8000
```

Run in **background** so it does not block. Then open in the browser:

- Windows: `start http://127.0.0.1:8000`
- macOS: `open http://127.0.0.1:8000`
- Linux: `xdg-open http://127.0.0.1:8000`

---

## Step 5 — Confirm and report

Tell the user:
- URL: `http://127.0.0.1:8000`
- Which tabs are active and what data each shows
- Script location: `src/dashboard.py`
- Any files that were missing and skipped
- How to toggle dark/light mode (the icon button top-right of the navbar)

If the app fails to start, read the full traceback, fix the root cause, and re-run once. Do not retry the same failing command more than twice.
