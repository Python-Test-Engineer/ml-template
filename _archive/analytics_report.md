# Technical Spec — Web Session Analytics

**Plan source:** `_plans/analytics_report.md`
**Dataset(s):** `data/data.csv`
**Output directory:** `output/PROJECT_01/`
**Date:** 2026-03-08

---

## 1. Overview

This pipeline ingests 2,000 web-session records, audits and cleans the data, performs exploratory analysis across all seven session attributes, runs statistical significance tests by traffic source, and produces a final Markdown summary report. There is no modelling phase; all outputs are descriptive. The five scripts run sequentially and produce plots, CSVs, and a report in `output/PROJECT_01/`.

---

## 2. Environment

- Python 3.12 via `uv`
- Dependencies to add with `uv add`:
  - `pandas`
  - `matplotlib`
  - `seaborn`
  - `scipy`
  - `jinja2`

---

## 3. Script Architecture

| Script | Location | Responsibility |
|---|---|---|
| `01_audit.py` | `src/` | Load raw data, profile nulls/types/ranges, save `audit.csv` |
| `02_clean.py` | `src/` | Apply dirty-row rules, save `dirty.csv` + `clean.csv`, derive `converted` flag |
| `03_eda.py` | `src/` | Produce all 11 charts and plots to `output/PROJECT_01/plots/` |
| `04_stats.py` | `src/` | Correlation matrix, ANOVA/Kruskal-Wallis tests, save `stats.csv` |
| `05_report.py` | `src/` | Assemble Markdown summary report from outputs of prior phases |

---

## 4. Data Contract

### 4.1 Input Schema (`data/data.csv`)

| Column | Type | Description | Nullable |
|---|---|---|---|
| `Page Views` | int | Count of pages viewed in session | No |
| `Session Duration` | float | Total session length in minutes | No |
| `Bounce Rate` | float | Proportion of session that bounced (0.0–1.0) | No |
| `Traffic Source` | str | Acquisition channel | No |
| `Time on Page` | float | Time spent on the landing page in minutes | No |
| `Previous Visits` | int | Count of prior visits by this user | No |
| `Conversion Rate` | float | Session-level conversion metric (0.0–1.0) | No |

### 4.2 Dirty-Row Rules

Rows are **removed, never fixed**, and written to `output/PROJECT_01/dirty.csv` with a `reason` column. A row may match multiple rules; record the first-matched reason.

| # | Column(s) | Condition | Reason label |
|---|---|---|---|
| 1 | All | Any null / NaN | `null_value` |
| 2 | `Session Duration` | `< 0.1` (i.e. < 6 seconds) | `session_duration_too_short` |
| 3 | `Time on Page` | `< 0.1` (i.e. < 6 seconds) | `time_on_page_too_short` |
| 4 | `Bounce Rate` | `< 0` or `> 1` | `bounce_rate_out_of_range` |
| 5 | `Conversion Rate` | `< 0` or `> 1` | `conversion_rate_out_of_range` |
| 6 | `Page Views` | `< 1` | `page_views_invalid` |
| 7 | `Traffic Source` | Not in `{Organic, Social, Paid, Direct, Referral}` | `unknown_traffic_source` |

### 4.3 Derived Column

After cleaning, in `02_clean.py`:

- **`converted`** (int, 0 or 1): `1` if `Conversion Rate == 1.0`, else `0`.

This column is appended to `clean.csv` and carried through all downstream scripts.

### 4.4 Output Files

| File | Description |
|---|---|
| `output/PROJECT_01/audit.csv` | Per-column profile: dtype, null count, min, max, mean, percentiles |
| `output/PROJECT_01/dirty.csv` | Removed rows with original data + `reason` column |
| `output/PROJECT_01/clean.csv` | Cleaned data with derived `converted` column |
| `output/PROJECT_01/plots/hist_grid.png` | Histogram + KDE grid for all 6 numeric columns |
| `output/PROJECT_01/plots/bar_traffic_source.png` | Session count by Traffic Source |
| `output/PROJECT_01/plots/box_session_by_source.png` | Session Duration by Traffic Source |
| `output/PROJECT_01/plots/box_bounce_by_source.png` | Bounce Rate by Traffic Source |
| `output/PROJECT_01/plots/box_conversion_by_source.png` | Conversion Rate by Traffic Source |
| `output/PROJECT_01/plots/scatter_duration_vs_bounce.png` | Session Duration vs Bounce Rate, coloured by Traffic Source |
| `output/PROJECT_01/plots/scatter_pageviews_vs_conversion.png` | Page Views vs Conversion Rate, coloured by Traffic Source |
| `output/PROJECT_01/plots/scatter_previous_vs_conversion.png` | Previous Visits vs Conversion Rate, coloured by Traffic Source |
| `output/PROJECT_01/plots/heatmap_correlation.png` | Pearson correlation heatmap of all numeric columns |
| `output/PROJECT_01/plots/bar_metrics_by_source.png` | Grouped bar: mean Session Duration, Bounce Rate, Conversion Rate per source |
| `output/PROJECT_01/plots/violin_previous_vs_duration.png` | Violin: Session Duration by Previous Visits |
| `output/PROJECT_01/stats.csv` | Kruskal-Wallis H-stat and p-value per numeric target, grouped by Traffic Source |
| `output/PROJECT_01/report.md` | Final Markdown summary report |

---

## 5. Phase Specs

---

### Phase 1 — Audit (`src/01_audit.py`)

**Inputs:** `data/data.csv`
**Outputs:** `output/PROJECT_01/audit.csv`; prints summary to stdout

**Steps:**

1. Load `data/data.csv` with pandas. Raise `ValueError` if file not found.
2. Assert the 7 expected columns are present (exact names); raise `ValueError` listing any missing ones.
3. For each column compute: dtype, total count, null count, null %, unique count, min, max, mean (numeric only), std (numeric only), p25, p50, p75.
4. For `Traffic Source`: print value counts and proportions.
5. Save the profile to `output/PROJECT_01/audit.csv` (one row per column).
6. Print a human-readable summary table to stdout (shape, dtypes, null counts).

---

### Phase 2 — Clean (`src/02_clean.py`)

**Inputs:** `data/data.csv`
**Outputs:** `output/PROJECT_01/dirty.csv`, `output/PROJECT_01/clean.csv`

**Steps:**

1. Load `data/data.csv`. Raise `ValueError` if file not found.
2. Apply dirty-row rules in the order listed in §4.2. Tag each dirty row with the first-matched reason string.
3. Write all dirty rows (original columns + `reason`) to `output/PROJECT_01/dirty.csv`.
4. Drop all dirty rows from the working dataframe.
5. Derive the `converted` column: `int(Conversion Rate == 1.0)`.
6. Write the clean dataframe (all original columns + `converted`) to `output/PROJECT_01/clean.csv`.
7. Print to stdout: total rows, rows removed (with breakdown by reason), rows retained.

---

### Phase 3 — EDA Plots (`src/03_eda.py`)

**Inputs:** `output/PROJECT_01/clean.csv`
**Outputs:** 11 PNG files in `output/PROJECT_01/plots/`

**General conventions:**
- Figure DPI: 150. Save as PNG. Use `seaborn` with a clean style (`seaborn-v0_8-whitegrid` or equivalent).
- All axes must have labelled titles, axis labels, and legends where applicable.
- `Traffic Source` colour palette: use a qualitative palette (e.g. `tab10`) consistently across all charts.
- Raise `ValueError` if `clean.csv` is not found.

**Chart specifications:**

| File | Chart type | Details |
|---|---|---|
| `hist_grid.png` | 2×3 histogram + KDE grid | One subplot per numeric column (`Page Views`, `Session Duration`, `Bounce Rate`, `Time on Page`, `Previous Visits`, `Conversion Rate`). Use `bins=30`. |
| `bar_traffic_source.png` | Horizontal bar | Count of sessions per `Traffic Source`, sorted descending. Annotate bars with counts. |
| `box_session_by_source.png` | Box plot | `Session Duration` on y-axis, `Traffic Source` on x-axis. |
| `box_bounce_by_source.png` | Box plot | `Bounce Rate` on y-axis, `Traffic Source` on x-axis. |
| `box_conversion_by_source.png` | Box plot | `Conversion Rate` on y-axis, `Traffic Source` on x-axis. |
| `scatter_duration_vs_bounce.png` | Scatter | x=`Session Duration`, y=`Bounce Rate`, colour=`Traffic Source`. Alpha=0.4. |
| `scatter_pageviews_vs_conversion.png` | Scatter | x=`Page Views`, y=`Conversion Rate`, colour=`Traffic Source`. Alpha=0.4. |
| `scatter_previous_vs_conversion.png` | Scatter | x=`Previous Visits` (jittered ±0.1), y=`Conversion Rate`, colour=`Traffic Source`. Alpha=0.4. |
| `heatmap_correlation.png` | Heatmap | Pearson correlation of all 6 numeric columns + `converted`. Annotate cells with r-values (2 d.p.). Use `coolwarm` colormap, vmin=-1, vmax=1. |
| `bar_metrics_by_source.png` | Grouped bar | Mean of `Session Duration`, `Bounce Rate`, and `Conversion Rate` per `Traffic Source`. Three bar groups per source. Include error bars (std). |
| `violin_previous_vs_duration.png` | Violin plot | x=`Previous Visits`, y=`Session Duration`. Overlay strip plot (alpha=0.3). |

---

### Phase 4 — Statistical Tests (`src/04_stats.py`)

**Inputs:** `output/PROJECT_01/clean.csv`
**Outputs:** `output/PROJECT_01/stats.csv`; prints results to stdout

**Steps:**

1. Load `clean.csv`. Raise `ValueError` if not found.
2. For each numeric target column (`Session Duration`, `Bounce Rate`, `Conversion Rate`, `Page Views`, `Time on Page`):
   - Group rows by `Traffic Source` (5 groups).
   - Run **Kruskal-Wallis H-test** (`scipy.stats.kruskal`) across the 5 groups.
   - Record: target column, H-statistic (4 d.p.), p-value (4 d.p.), significant (bool, threshold p < 0.05).
3. Save all results to `output/PROJECT_01/stats.csv` (columns: `target`, `H_stat`, `p_value`, `significant`).
4. Print a formatted summary table to stdout.
5. Additionally, compute and print Pearson correlation coefficients between `Conversion Rate` and all other numeric columns.

---

### Phase 5 — Report (`src/05_report.py`)

**Inputs:** `output/PROJECT_01/audit.csv`, `output/PROJECT_01/dirty.csv`, `output/PROJECT_01/clean.csv`, `output/PROJECT_01/stats.csv`, all PNGs in `output/PROJECT_01/plots/`
**Outputs:** `output/PROJECT_01/report.md`

**Steps:**

1. Raise `ValueError` if any required input file is missing.
2. Load audit, dirty, clean, and stats CSVs.
3. Compute derived summary values:
   - Total raw rows, dirty rows removed (with breakdown by reason), clean rows retained.
   - Overall mean/median for each numeric column (on clean data).
   - Per-`Traffic Source` means for `Session Duration`, `Bounce Rate`, `Conversion Rate`.
   - Best-converting source (highest mean `Conversion Rate`).
   - Lowest-bounce source (lowest mean `Bounce Rate`).
   - Highest-engagement source (highest mean `Session Duration`).
   - Conversion rate for new vs returning visitors (`Previous Visits == 0` vs `> 0`).
4. Render `output/PROJECT_01/report.md` using the following structure:

```
# Web Session Analytics — Summary Report
**Generated:** <date>
**Dataset:** data/data.csv | **Clean rows:** N | **Dirty rows removed:** N

## 1. Data Quality
- Table: dirty row breakdown by reason
- Key finding sentence

## 2. Dataset Overview
- Table: overall numeric summary (mean, median, std, min, max)

## 3. Traffic Source Analysis
- Table: per-source mean Session Duration, Bounce Rate, Conversion Rate
- Best source for conversion, engagement, lowest bounce

## 4. Conversion Insights
- New vs returning visitor conversion rates
- Top correlated features with Conversion Rate (from stats.csv)

## 5. Statistical Significance
- Table: Kruskal-Wallis results per target column
- Interpretation: which differences across sources are statistically significant?

## 6. Key Findings
- Bullet list of top 5 actionable insights

## 7. Plots
- Inline Markdown image links to all 11 PNGs (relative paths)
```

---

## 6. Reproducibility

- `RANDOM_SEED = 42` defined at the top of every script (even where not used, for consistency).
- Scripts must be runnable independently in phase order; each re-reads its inputs from disk.
- No script mutates `data/data.csv`.

---

## 7. Error Handling

- Raise `ValueError` with a clear message if any required input file is missing.
- Raise `ValueError` if expected columns are absent from the loaded dataframe.
- Use `warnings.warn()` for non-fatal issues (e.g. unexpected `Traffic Source` values that pass the clean rule).

---

## 8. Run Order

```bash
uv run python src/01_audit.py
uv run python src/02_clean.py
uv run python src/03_eda.py
uv run python src/04_stats.py
uv run python src/05_report.py
```
