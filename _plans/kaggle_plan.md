# Research Plan — Sales Order Analytics & Data Quality Report

**Idea source:** _ideas/kaggle_ideas.md
**Dataset(s):** data/data.csv
**Date:** 2026-03-18

## 1. Research Question

Perform a comprehensive exploratory analysis of a 50-row sales order dataset covering January–May 2025 to uncover revenue trends, regional and product performance patterns, and data quality issues. The output is an interactive HTML report with supporting charts and CSVs, aimed at an internal technical review audience. The analysis should be rigorous enough to withstand interview-style questioning at all difficulty levels.

## 2. Dataset Summary

| Column | Type | Missing % | Notes |
|--------|------|-----------|-------|
| order_id | str | 0% | Unique identifier (ORD-001 to ORD-050), no duplicates |
| date | str | 0% | Mostly YYYY-MM-DD; **one row uses DD-MM-YYYY** (ORD-027: "15-03-2025") |
| customer_name | str | 0% | 26 unique customers |
| customer_email | str | 2% | **1 missing value** |
| region | str | 0% | 4 regions: North (13), South (13), East (12), West (12) |
| product | str | 0% | 6 products, roughly evenly distributed (8–9 each) |
| category | str | 0% | 4 categories: Software (17), Web Dev (16), Training (9), Consulting (8) |
| quantity | int | 0% | Range 1–999; **ORD-047 has quantity=999** (likely data entry error) |
| unit_price | float | 0% | Range -1200 to 2200; **ORD-049 has negative price** (-1200) |
| discount_pct | int | 0% | Range 0–20% |
| total | float | 0% | Range -1200 to 427,657.50; **ORD-047 total also fails validation** (off by ~585) |
| sales_rep | str | 2% | 4 reps + **1 missing**; Sarah Mitchell (13), others ~12 each |
| status | str | 0% | Completed (43), Pending (7) |

### Key Observations

- **50 rows, 13 columns** — small dataset, well-suited for thorough manual inspection.
- **3 dirty rows identified:**
  1. **ORD-027** — date in DD-MM-YYYY format ("15-03-2025"), inconsistent with all other rows.
  2. **ORD-047** — quantity = 999 (extreme outlier, likely data entry error); total also mismatches calculated value by ~585.
  3. **ORD-049** — negative unit_price (-1200) and negative total (-1200).
- **2 missing values:** 1 in `customer_email`, 1 in `sales_rep`.
- **Revenue is heavily skewed** by the ORD-047 outlier (427K vs median ~1,915).
- **Balanced distribution** across regions, products, and sales reps.
- **7 pending orders** — may need separate treatment for revenue analysis (completed vs. pipeline).

## 3. Proposed Phases

### Phase 1 — Data Cleaning & ETL

**Scripts:** `phase1_etl.py`

- Load `data/data.csv`
- Parse dates: detect and normalise the DD-MM-YYYY entry to YYYY-MM-DD
- Identify dirty rows using rules:
  - Negative `unit_price` → dirty
  - Extreme `quantity` (> reasonable threshold, e.g., > 50 for this business) → dirty
  - `total` mismatch with `quantity * unit_price * (1 - discount_pct/100)` beyond ±0.01 → dirty
- Remove dirty rows and save to `output/PROJECT_01/dirty.csv` with a `reason` column
- Handle missing values: flag rows with missing `customer_email` or `sales_rep` (keep in analysis but note)
- Add derived columns:
  - `month` (YYYY-MM)
  - `revenue` (validated total)
  - `is_pending` (boolean from status)
- Save clean dataset to `output/PROJECT_01/clean.csv`

### Phase 2 — Exploratory Data Analysis & Feature Engineering

**Scripts:** `phase2_eda.py`

Focus area: **Revenue & Trends** (primary), with secondary coverage of other dimensions.

**Revenue & Trend Analysis:**
- Monthly revenue trend (line chart)
- Cumulative revenue over time
- Month-over-month growth rate
- Average order value by month

**Regional Analysis:**
- Revenue by region (bar chart)
- Order count by region
- Average order value by region

**Product & Category Analysis:**
- Revenue by product and category (bar charts)
- Quantity distribution by product
- Discount patterns by category

**Sales Rep Performance:**
- Revenue per rep
- Order count and average deal size per rep
- Discount tendencies per rep

**Customer Analysis:**
- Top customers by revenue
- Repeat customers vs. one-time buyers
- Customer concentration (% revenue from top N customers)

**Status Analysis:**
- Completed vs. Pending breakdown
- Pending orders by region/product

**Output:** Summary statistics CSV (`output/PROJECT_01/summary_stats.csv`)

### Phase 3 — Visualisations

**Scripts:** `phase3_charts.py`

Use **Plotly** for interactive charts saved as standalone HTML snippets and static PNGs:

1. **Monthly Revenue Trend** — line chart with markers, hover showing order count
2. **Revenue by Region** — horizontal bar chart
3. **Revenue by Category** — stacked bar or treemap
4. **Revenue by Product** — bar chart
5. **Sales Rep Performance** — grouped bar (revenue + order count)
6. **Top 10 Customers by Revenue** — horizontal bar
7. **Discount Distribution** — histogram
8. **Order Status Breakdown** — pie/donut chart
9. **Revenue Heatmap** — region × category matrix
10. **Cumulative Revenue Over Time** — area chart

All charts saved to `output/PROJECT_01/charts/` as both `.html` (interactive) and `.png` (static).

### Phase 4 — HTML Report & Interview Preparation

**Scripts:** `phase4_report.py`

Assemble a single interactive HTML report (`output/PROJECT_01/report.html`) containing:

1. **Executive Summary** — key metrics (total revenue, order count, average order value, top region, top product)
2. **Data Quality Section** — dirty rows found, cleaning decisions, missing values
3. **Revenue & Trends** — embedded interactive charts, commentary
4. **Regional & Product Breakdown** — charts with insights
5. **Sales Rep Analysis** — performance comparison
6. **Customer Insights** — concentration, repeat buyers
7. **Interview-Ready Insights** — a section with 10–15 pre-prepared talking points covering:
   - Easy: "What is the total revenue?" / "How many orders were placed?"
   - Medium: "Which region has the highest average order value?" / "What is the MoM growth trend?"
   - Hard: "How would you handle the outlier in ORD-047?" / "What does the customer concentration risk look like?" / "If you could only keep 3 charts, which and why?"

### Output File Manifest

```
output/PROJECT_01/
├── dirty.csv                  # Removed rows with reason column
├── clean.csv                  # Cleaned dataset
├── summary_stats.csv          # Key statistics
├── charts/
│   ├── monthly_revenue.html
│   ├── monthly_revenue.png
│   ├── revenue_by_region.html
│   ├── revenue_by_region.png
│   ├── revenue_by_category.html
│   ├── revenue_by_category.png
│   ├── revenue_by_product.html
│   ├── revenue_by_product.png
│   ├── sales_rep_performance.html
│   ├── sales_rep_performance.png
│   ├── top_customers.html
│   ├── top_customers.png
│   ├── discount_distribution.html
│   ├── discount_distribution.png
│   ├── order_status.html
│   ├── order_status.png
│   ├── revenue_heatmap.html
│   ├── revenue_heatmap.png
│   ├── cumulative_revenue.html
│   └── cumulative_revenue.png
└── report.html                # Full interactive HTML report
```

## 4. Open Questions / Assumptions

- **Assumption:** ORD-047 (quantity=999) is a data entry error, not a legitimate bulk order. Removed as dirty.
- **Assumption:** ORD-049 (negative price) is an error or refund — removed as dirty rather than treated as a credit note.
- **Assumption:** The inconsistent date format on ORD-027 is a one-off typo; the date itself (15-Mar-2025) is valid after parsing.
- **Assumption:** "Pending" orders represent real pipeline — included in order counts but flagged separately for revenue analysis.
- **Assumption:** Missing `customer_email` and `sales_rep` are not grounds for row removal — these rows remain in the clean dataset.

## 5. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Small dataset (50 rows) limits statistical significance | High | Medium | Acknowledge limitations; avoid over-fitting conclusions; use descriptive stats, not inferential |
| Outlier removal changes revenue picture dramatically | Medium | High | Report both with/without outlier totals; document cleaning rationale |
| Mixed date formats cause silent parsing errors | Low | High | Explicit format detection and validation in ETL; assert all dates parse successfully |
| Total column has calculation errors beyond known dirty rows | Low | Medium | Recalculate and validate every row's total in ETL; flag any discrepancy |
| Interview questions may target edge cases not in data | Medium | Low | Include "what-if" discussion points in report (e.g., "what would you do with 10K rows?") |

## 6. Technical Spec Guidance

The `/spec` phase should produce scripts for each phase above with:

- **phase1_etl.py** — Pandas-based cleaning, validation, derived columns, dirty.csv export
- **phase2_eda.py** — Statistical summaries, groupby aggregations, output to CSV
- **phase3_charts.py** — Plotly chart generation (10 charts, HTML + PNG)
- **phase4_report.py** — Jinja2 or string-templated HTML assembly, embedding charts and stats

Dependencies: `pandas`, `plotly`, `kaleido` (for PNG export), `jinja2` (optional for report templating)
