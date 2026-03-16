# Technical Spec — Sales CSV Analysis with Shiny

**Plan source:** _plans/test.md
**Dataset(s):** data/sales_dummy.csv
**Output directory:** output/PROJECT_01/
**Date:** 2026-03-02

## 1. Overview
Three scripts process a weekly sales CSV and produce an interactive Shiny for Python dashboard. Phase 1 validates and cleans the data. Phase 2 engineers derived columns and aggregates. Phase 3 builds and writes a self-contained Shiny app that reads the processed data and renders KPI cards, a bar chart, and a line chart with region/product filters.

## 2. Environment
- Python 3.12 via `uv`
- Dependencies to add: `shiny`, `pandas`, `plotly`

## 3. Script Architecture
| Script | Location | Responsibility |
|--------|----------|----------------|
| phase1_eda.py | src/ | Load raw CSV, validate, remove dirty rows, save dirty.csv |
| phase2_features.py | src/ | Compute profit, profit_margin, weekly aggregates, save features.csv |
| phase3_dashboard.py | src/ | Write a self-contained Shiny app to output/PROJECT_01/sales_dashboard.py |

## 4. Data Contract

### Input (`data/sales_dummy.csv`)
| Column | Type | Description | Nullable |
|--------|------|-------------|----------|
| date | string (YYYY-MM-DD) | Week start date | No |
| region | string | Sales region | No |
| product | string | Product name | No |
| units_sold | int | Units sold that week | No |
| revenue | float | Gross revenue ($) | No |
| cost | float | Cost of goods ($) | No |

### Dirty-row rules
Rows are **removed** (never fixed) and written to `output/PROJECT_01/dirty.csv` with a `reason` column when:
- `units_sold` ≤ 0 → reason: `"non_positive_units"`
- `revenue` ≤ 0 → reason: `"non_positive_revenue"`
- `cost` ≤ 0 → reason: `"non_positive_cost"`
- `cost` > `revenue` → reason: `"cost_exceeds_revenue"`
- `date` cannot be parsed as a date → reason: `"invalid_date"`
- Any required column is null → reason: `"missing_required_field"`
- Exact duplicate row → reason: `"duplicate"`

### Output files
| File | Description |
|------|-------------|
| output/PROJECT_01/dirty.csv | Removed rows with `reason` column |
| output/PROJECT_01/features.csv | Clean data with derived columns and aggregates |
| output/PROJECT_01/sales_dashboard.py | Self-contained Shiny for Python app |
| output/PROJECT_01/sales_summary.csv | Aggregated stats (region × product) |

## 5. Phase Specs

### Phase 1 — EDA & Preprocessing (`src/phase1_eda.py`)
**Inputs:** `data/sales_dummy.csv`
**Outputs:** `output/PROJECT_01/dirty.csv`, prints summary to stdout

Steps:
1. Create `output/PROJECT_01/` if it does not exist
2. Load CSV; raise `ValueError` if any expected column is absent
3. Apply dirty-row rules in order; collect removed rows with their `reason`
4. Write removed rows to `output/PROJECT_01/dirty.csv`
5. Drop dirty rows from the working dataframe
6. Print a summary table: total rows, dirty rows removed, clean rows remaining, missing % per column

### Phase 2 — Feature Engineering (`src/phase2_features.py`)
**Inputs:** `data/sales_dummy.csv` (re-loads and re-applies cleaning logic inline, or reads clean rows)
**Outputs:** `output/PROJECT_01/features.csv`, `output/PROJECT_01/sales_summary.csv`

Steps:
1. Load and clean data (same dirty-row rules as Phase 1; do not re-write dirty.csv)
2. Parse `date` as `datetime`
3. Compute `profit = revenue - cost`
4. Compute `profit_margin = profit / revenue` (round to 4 dp)
5. Produce `sales_summary.csv`: group by `region` and `product`, aggregate:
   - `total_revenue` = sum of revenue
   - `total_profit` = sum of profit
   - `total_units` = sum of units_sold
   - `avg_profit_margin` = mean of profit_margin
6. Save full clean + derived dataframe to `output/PROJECT_01/features.csv`

### Phase 3 — Shiny Dashboard (`src/phase3_dashboard.py`)
**Inputs:** none at runtime (dashboard reads `output/PROJECT_01/features.csv` at app startup)
**Outputs:** `output/PROJECT_01/sales_dashboard.py`

This script **writes** a Python source file (`sales_dashboard.py`) to the output directory. It does not run the Shiny app itself.

The generated `sales_dashboard.py` must:
1. Import `shiny`, `pandas`, `plotly.express`
2. On startup, load `output/PROJECT_01/features.csv` relative to its own location
3. Define UI with:
   - `ui.input_checkbox_group("region", ...)` — all 4 regions selected by default
   - `ui.input_checkbox_group("product", ...)` — all 3 products selected by default
   - Three `ui.value_box` KPI cards: **Total Revenue**, **Total Profit**, **Avg Units Sold**
   - `ui.output_plot("revenue_by_region")` — Plotly bar chart
   - `ui.output_plot("revenue_trend")` — Plotly line chart (weekly, coloured by product)
4. Define server with reactive filtering on region and product selections
5. Render KPI values from filtered dataframe
6. Render bar chart: total revenue grouped by region
7. Render line chart: weekly revenue over time, one line per product

## 6. Reproducibility
- `RANDOM_SEED = 42` at the top of each script (even if unused, for consistency)
- All scripts runnable independently in phase order

## 7. Error Handling
- Raise `ValueError` with a clear message if a required input file is missing
- Raise `ValueError` if expected columns are absent from the CSV
- Log a warning (not an error) if dirty.csv would be empty (no dirty rows found)

## 8. Run Order
```bash
uv run python src/phase1_eda.py
uv run python src/phase2_features.py
uv run python src/phase3_dashboard.py
# Then launch the generated app:
uv run shiny run output/PROJECT_01/sales_dashboard.py
```
