# Technical Spec — Sales Order Analytics & Data Quality Report

**Plan source:** _plans/kaggle_plan.md
**Dataset(s):** data/data.csv
**Output directory:** output/PROJECT_01/
**Date:** 2026-03-18

## 1. Overview

Four sequential Python scripts load a 50-row sales order CSV, clean and validate it, compute statistical summaries, generate 10 interactive Plotly charts (saved as both HTML and PNG), and assemble a single self-contained interactive HTML report. The report targets internal technical review and includes an interview-preparation section with pre-written answers at easy, medium, and hard difficulty levels. No ML modelling is performed.

---

## 2. Environment

- Python 3.12 via `uv`
- Add with `uv add`:
  - `pandas`
  - `plotly`
  - `kaleido` (Plotly static PNG export)
  - `jinja2`

---

## 3. Script Architecture

| Script | Location | Responsibility |
|--------|----------|----------------|
| `phase1_etl.py` | `src/` | Load raw CSV, normalise dates, detect & remove dirty rows, add derived columns, write `clean.csv` and `dirty.csv` |
| `phase2_eda.py` | `src/` | Compute statistical summaries and aggregations from `clean.csv`, write `summary_stats.csv` |
| `phase3_charts.py` | `src/` | Generate 10 Plotly charts from `clean.csv`, save each as `.html` and `.png` under `charts/` |
| `phase4_report.py` | `src/` | Load all outputs, render and write self-contained `report.html` |

Scripts run independently in phase order. Each reads its inputs from disk; no in-memory passing between scripts.

---

## 4. Data Contract

### Input: `data/data.csv`

| Column | Expected Type | Description | Nullable |
|--------|--------------|-------------|----------|
| `order_id` | str | Unique order identifier (format `ORD-NNN`) | No |
| `date` | str | Order date; expected YYYY-MM-DD, one known DD-MM-YYYY anomaly | No |
| `customer_name` | str | Company or individual name | No |
| `customer_email` | str | Billing email | Yes (1 known) |
| `region` | str | Sales region: North, South, East, West | No |
| `product` | str | Product name (6 distinct values) | No |
| `category` | str | Product category: Software, Web Dev, Training, Consulting | No |
| `quantity` | int | Units ordered; must be positive integer ≤ 50 to be clean | No |
| `unit_price` | float | Price per unit; must be > 0 to be clean | No |
| `discount_pct` | int | Discount percentage applied (0–100) | No |
| `total` | float | Order total; must match `quantity * unit_price * (1 - discount_pct/100)` within ±0.01 | No |
| `sales_rep` | str | Assigned sales representative | Yes (1 known) |
| `status` | str | Order status: Completed or Pending | No |

### Dirty-row rules

Rows are **removed** (never modified) and written to `output/PROJECT_01/dirty.csv` with a `reason` column when **any** of the following conditions are true:

| Rule ID | Condition | Reason string |
|---------|-----------|---------------|
| D1 | `unit_price < 0` | `"negative unit_price"` |
| D2 | `quantity > 50` | `"quantity exceeds threshold (>50)"` |
| D3 | `abs(total - quantity * unit_price * (1 - discount_pct/100)) > 0.01` | `"total_mismatch"` |

A row matching multiple rules gets all reasons joined with `"; "`.

Note: ORD-027 has a mixed date format but a valid parseable date — it is **not** dirty; it is corrected in place during date normalisation.

### Derived columns added in Phase 1

| Column | Type | Derivation |
|--------|------|-----------|
| `month` | str | `date.dt.to_period('M').astype(str)` → `"YYYY-MM"` |
| `revenue` | float | Copy of validated `total` (post dirty-row removal) |
| `is_pending` | bool | `True` if `status == "Pending"` |
| `missing_email` | bool | `True` if `customer_email` is NaN |
| `missing_rep` | bool | `True` if `sales_rep` is NaN |

### Output files

| File | Description |
|------|-------------|
| `output/PROJECT_01/dirty.csv` | Removed rows with appended `reason` column |
| `output/PROJECT_01/clean.csv` | Validated dataset with derived columns |
| `output/PROJECT_01/summary_stats.csv` | Aggregated statistics (see Phase 2) |
| `output/PROJECT_01/charts/*.html` | 10 interactive Plotly charts |
| `output/PROJECT_01/charts/*.png` | 10 static PNG versions of same charts |
| `output/PROJECT_01/report.html` | Self-contained interactive HTML report |

---

## 5. Phase Specs

---

### Phase 1 — ETL & Cleaning (`src/phase1_etl.py`)

**Inputs:** `data/data.csv`
**Outputs:** `output/PROJECT_01/dirty.csv`, `output/PROJECT_01/clean.csv`

**Steps:**

1. **Setup:** Create `output/PROJECT_01/` and `output/PROJECT_01/charts/` directories if they do not exist. Define `OUTPUT_DIR = "output/PROJECT_01"`.

2. **Load:** Read `data/data.csv` with `pandas.read_csv()`. Assert that all 13 expected columns are present; raise `ValueError` with a descriptive message if any are missing.

3. **Date normalisation:**
   - Attempt to parse `date` column with `format="mixed"` and `dayfirst=False`.
   - For any row that fails standard parsing, retry with `dayfirst=True`.
   - Assert that every row now has a valid parsed date; raise `ValueError` if any remain unparseable.
   - Overwrite the `date` column with the normalised `datetime64` values.

4. **Dirty-row detection:**
   - Apply rules D1, D2, D3 (see Data Contract).
   - Collect dirty rows into a separate DataFrame; append a `reason` column with concatenated reason strings.
   - Write dirty rows to `output/PROJECT_01/dirty.csv` (index=False).
   - Print a summary: `f"Dirty rows removed: {n} → output/PROJECT_01/dirty.csv"`.

5. **Drop dirty rows** from the working DataFrame.

6. **Add derived columns:** `month`, `revenue`, `is_pending`, `missing_email`, `missing_rep` (see Derived columns table).

7. **Validation assertions (post-clean):**
   - Assert no remaining negative `unit_price`.
   - Assert no remaining `quantity > 50`.
   - Assert no `total` mismatches (within ±0.01).
   - Assert `date` column has no NaT values.
   - Print: `f"Clean dataset: {len(df)} rows → output/PROJECT_01/clean.csv"`.

8. **Write** clean DataFrame to `output/PROJECT_01/clean.csv` (index=False).

---

### Phase 2 — EDA & Summaries (`src/phase2_eda.py`)

**Inputs:** `output/PROJECT_01/clean.csv`
**Outputs:** `output/PROJECT_01/summary_stats.csv`

**Steps:**

1. **Load** `clean.csv`; parse `date` as datetime, `month` as str.

2. **Compute the following aggregation tables** and collect them into an ordered dict `{table_name: DataFrame}`:

   | Table name | Groupby | Metrics |
   |-----------|---------|---------|
   | `monthly_revenue` | `month` | `revenue.sum()`, `revenue.mean()` (AOV), `order_count` (row count), `mom_growth_pct` (pct change of revenue sum) |
   | `revenue_by_region` | `region` | `revenue.sum()`, `revenue.mean()` (AOV), `order_count` |
   | `revenue_by_category` | `category` | `revenue.sum()`, `revenue.mean()`, `order_count` |
   | `revenue_by_product` | `product` | `revenue.sum()`, `revenue.mean()`, `order_count` |
   | `sales_rep_performance` | `sales_rep` | `revenue.sum()`, `revenue.mean()`, `order_count`, `discount_pct.mean()` |
   | `top_customers` | `customer_name` | `revenue.sum()`, `order_count` — sort descending by revenue, take top 10 |
   | `customer_concentration` | derived | cumulative revenue share of top 1, 3, 5, 10 customers as `pct_of_total` |
   | `status_breakdown` | `status` | `order_count`, `revenue.sum()` |
   | `region_category_heatmap` | `region` × `category` | `revenue.sum()` — pivot table |
   | `discount_summary` | `category` | `discount_pct.mean()`, `discount_pct.max()`, `discount_pct.min()` |

3. **Global KPIs** (scalar values, stored as a single-row DataFrame `kpis`):

   | KPI | Calculation |
   |-----|-------------|
   | `total_revenue` | `revenue.sum()` |
   | `order_count` | `len(df)` |
   | `avg_order_value` | `revenue.mean()` |
   | `median_order_value` | `revenue.median()` |
   | `top_region` | region with highest revenue sum |
   | `top_product` | product with highest revenue sum |
   | `top_sales_rep` | rep with highest revenue sum |
   | `top_customer` | customer with highest revenue sum |
   | `pending_count` | `is_pending.sum()` |
   | `pending_revenue` | revenue of pending orders |
   | `repeat_customer_count` | customers with order_count > 1 |
   | `one_time_customer_count` | customers with order_count == 1 |

4. **Write** all tables to `output/PROJECT_01/summary_stats.csv` using a labelled multi-section format: prepend each table with a header row `## TABLE: <table_name>` so Phase 4 can parse sections. Alternatively, write a single CSV with a `table` column that identifies each row's source aggregation.

   > **Preferred format:** Single CSV with columns `table, metric_name, metric_value` (long format). This makes Phase 4 parsing simple with `df[df.table == "kpis"]`.

5. **Print** all KPIs to stdout for immediate review.

---

### Phase 3 — Charts (`src/phase3_charts.py`)

**Inputs:** `output/PROJECT_01/clean.csv`, `output/PROJECT_01/summary_stats.csv`
**Outputs:** `output/PROJECT_01/charts/<name>.html` and `output/PROJECT_01/charts/<name>.png` for each of 10 charts

**General conventions:**
- All charts use Plotly with a consistent colour palette: `plotly_white` template.
- All charts have a descriptive `title` and labelled axes.
- HTML export: `fig.write_html(path, full_html=True, include_plotlyjs="cdn")` — CDN so files stay small.
- PNG export: `fig.write_image(path, width=1200, height=700, scale=2)` via kaleido.
- All monetary axis labels formatted as `£{value:,.0f}` (or `${value:,.0f}` — use `$` consistently throughout).

**Chart specifications:**

| # | Filename stem | Chart type | Data | Key config |
|---|--------------|-----------|------|-----------|
| 1 | `monthly_revenue` | Line + markers | `monthly_revenue` table: x=month, y=revenue_sum | Secondary y-axis: order_count as bar; hover shows AOV |
| 2 | `cumulative_revenue` | Filled area | `clean.csv` sorted by date: x=date, y=cumulative revenue | Show a reference annotation for the total |
| 3 | `revenue_by_region` | Horizontal bar | `revenue_by_region`: x=revenue_sum, y=region | Sorted descending; annotate bars with AOV |
| 4 | `revenue_by_category` | Treemap | `revenue_by_category`: path=[category], values=revenue_sum | Label each tile with revenue and order count |
| 5 | `revenue_by_product` | Vertical bar | `revenue_by_product`: x=product, y=revenue_sum | Sort descending; colour by category if available |
| 6 | `sales_rep_performance` | Grouped bar | `sales_rep_performance`: x=sales_rep; bars for revenue_sum and order_count | Dual axis: revenue left, order_count right |
| 7 | `top_customers` | Horizontal bar | `top_customers` (top 10): x=revenue_sum, y=customer_name | Sorted descending; annotate with order_count |
| 8 | `discount_distribution` | Histogram | `clean.csv` discount_pct column | Bin width=5; overlay KDE line; colour by category |
| 9 | `order_status` | Donut chart | `status_breakdown`: labels=status, values=order_count | Show both count and revenue in hover |
| 10 | `revenue_heatmap` | Heatmap | `region_category_heatmap` pivot: x=category, y=region, z=revenue_sum | Annotate each cell with formatted revenue value |

**Error handling:** If kaleido is not available, log a warning and skip PNG export without failing the script.

---

### Phase 4 — HTML Report (`src/phase4_report.py`)

**Inputs:**
- `output/PROJECT_01/clean.csv`
- `output/PROJECT_01/dirty.csv`
- `output/PROJECT_01/summary_stats.csv`
- `output/PROJECT_01/charts/*.html` (all 10 chart files)

**Outputs:** `output/PROJECT_01/report.html`

**Report structure (HTML sections):**

Build the report as a single self-contained HTML string using Python string templating or Jinja2. Inline all chart HTML by reading each chart `.html` file and embedding its `<div>` and script tags. Use a clean CSS stylesheet (dark header, white cards, responsive layout).

**Section 1 — Executive Summary**

A 2×4 KPI card grid showing:
- Total Revenue
- Order Count
- Average Order Value
- Median Order Value
- Top Region
- Top Product
- Top Sales Rep
- Pending Orders (count + revenue)

**Section 2 — Data Quality**

A table listing the 3 dirty rows (from `dirty.csv`) with columns: `order_id`, `date`, `product`, `unit_price`, `quantity`, `total`, `reason`.

Below the table, a prose paragraph explaining:
- How dates were normalised (ORD-027)
- Why negative prices and extreme quantities were removed
- The 2 missing values retained in the clean dataset

**Section 3 — Revenue & Trends**

Embed charts: `monthly_revenue`, `cumulative_revenue`.

Beneath each chart, a 2–3 sentence automated insight generated from the summary stats:
- e.g., "Revenue peaked in [month] at $[value], representing [X]% of total revenue."
- MoM growth: "The strongest month-over-month growth was [X]% from [month A] to [month B]."

**Section 4 — Regional & Product Breakdown**

Embed charts: `revenue_by_region`, `revenue_by_category`, `revenue_by_product`, `revenue_heatmap`.

Automated insights for each:
- Top region and its share of total revenue.
- Top category and its share.
- Highest-revenue product vs. highest-volume product (if different).
- Heatmap: identify the region×category cell with highest revenue.

**Section 5 — Sales Rep Performance**

Embed chart: `sales_rep_performance`.

Automated insights:
- Top rep by revenue and by order count (may differ).
- Average discount tendency per rep (who gives the most discount?).

**Section 6 — Customer Insights**

Embed chart: `top_customers`.

Automated insights:
- Top customer's share of total revenue.
- Concentration: "Top 3 customers account for [X]% of revenue."
- Repeat vs. one-time buyers: "[N] customers placed more than one order."

**Section 7 — Order Status**

Embed chart: `order_status`.

Automated insights:
- Pending count and pending revenue as % of total potential revenue.
- Which region/product has most pending orders.

**Section 8 — Interview-Ready Insights**

A styled accordion or collapsible list of 15 Q&A pairs, colour-coded by difficulty:

*Easy (green badge):*
1. Q: "What is the total revenue from this dataset?" → A: computed value + caveat about dirty row removal
2. Q: "How many orders were placed?" → A: clean count + total incl. dirty
3. Q: "Which region generated the most revenue?" → A: top region + value + % share
4. Q: "What products does the company sell?" → A: list all 6 with category
5. Q: "How many sales reps are there?" → A: 4 confirmed + 1 missing

*Medium (amber badge):*
6. Q: "Which region has the highest average order value?" → A: computed from summary_stats
7. Q: "What is the month-over-month revenue growth trend?" → A: monthly values + observation
8. Q: "Which sales rep gives the highest average discount?" → A: computed value
9. Q: "What percentage of orders are still pending?" → A: count % + revenue %
10. Q: "Which customer segment is most concentrated?" → A: top-3 concentration %

*Hard (red badge):*
11. Q: "How would you handle the outlier in ORD-047?" → A: explain dirty-row rule, impact on mean vs. median, when you might keep it (bulk order scenario)
12. Q: "What does the customer concentration risk look like, and why does it matter?" → A: Herfindahl-style discussion, top-N share, business risk narrative
13. Q: "If you could keep only 3 charts, which would you choose and why?" → A: justify monthly_revenue (trend), revenue_heatmap (2D breakdown), top_customers (concentration) — explain trade-offs
14. Q: "How would your analysis change with 10,000 rows?" → A: sampling, inferential stats, automated anomaly detection, time-series modelling, customer cohort analysis
15. Q: "Is this dataset statistically sufficient to draw conclusions?" → A: n=47 (post-clean) is descriptive only; CIs would be wide; note what additional data would help

**Footer:** Report generation timestamp, script version, dataset row counts (raw/clean/dirty).

---

## 6. Reproducibility

- `RANDOM_SEED = 42` defined at top of each script (unused in this project but included for consistency).
- All scripts runnable independently in phase order.
- Output directory created by Phase 1; all subsequent scripts assume it exists and raise `FileNotFoundError` if it does not.
- No hardcoded absolute paths — all paths relative to the project root.

---

## 7. Error Handling

| Condition | Response |
|-----------|----------|
| `data/data.csv` not found | `raise FileNotFoundError("data/data.csv not found")` |
| Expected column missing from input | `raise ValueError(f"Missing expected column: {col}")` |
| Unparseable date after both format attempts | `raise ValueError(f"Cannot parse date in row {order_id}: {raw_value}")` |
| `output/PROJECT_01/` missing when Phase 2/3/4 runs | `raise FileNotFoundError("Run phase1_etl.py first")` |
| kaleido not installed (Phase 3) | `warnings.warn("kaleido not available — skipping PNG export")` |
| Chart HTML file missing when Phase 4 embeds it | `warnings.warn(f"Chart file not found: {path} — section will be empty")` |

---

## 8. Run Order

```bash
uv run python src/phase1_etl.py
uv run python src/phase2_eda.py
uv run python src/phase3_charts.py
uv run python src/phase4_report.py
```

Expected final output: `output/PROJECT_01/report.html` — open in any browser.
