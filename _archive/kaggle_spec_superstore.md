# Technical Spec — Superstore Sales EDA & Analytics

**Plan source:** _plans/kaggle_plan.md
**Dataset(s):** data/kaggle.csv
**Output directory:** output/PROJECT_02/
**Date:** 2026-03-17

---

## 1. Overview

Five scripts executed in order will: clean and profile both raw datasets; produce 11 EDA charts; run statistical tests (ANOVA, chi-square, RFM scoring, STL decomposition, discount breakeven); train and evaluate three classifiers (Logistic Regression, Random Forest, XGBoost) predicting loss-making orders; and aggregate all results into a plain-text summary report. All artefacts land in `output/PROJECT_02/`.

---

## 2. Environment

- Python 3.12 via `uv`
- Dependencies to add: `uv add pandas matplotlib seaborn scipy scikit-learn xgboost statsmodels openpyxl`

---

## 3. Script Architecture

| Script | Location | Responsibility |
|---|---|---|
| `phase1_etl.py` | `src/` | Load both datasets, validate columns, flag & remove dirty rows, parse dates, engineer base derived columns, save clean parquets and dirty.csv |
| `phase2_eda.py` | `src/` | Load clean Superstore data, produce all 9 EDA charts + 2 web-traffic charts, save to `output/PROJECT_02/plots/` |
| `phase3_stats.py` | `src/` | Correlation matrix, ANOVA/Kruskal-Wallis, chi-square, discount breakeven, RFM scoring, STL decomposition; save tables and stat-test plots |
| `phase4_model.py` | `src/` | Feature engineering, train Logistic Regression / Random Forest / XGBoost with stratified 5-fold CV, evaluate, save model artefacts and plots |
| `phase5_report.py` | `src/` | Load all output artefacts, render and save plain-text `report.txt` to `output/PROJECT_02/` |

Each script is independently runnable; all depend only on files produced by earlier phases.

---

## 4. Data Contract

### 4a — Input: data/kaggle.csv (Superstore)

| Column | Type | Description | Nullable |
|---|---|---|---|
| Row ID | int64 | Synthetic row key | No |
| Order ID | str | Groups line items into one order | No |
| Order Date | str (→datetime) | Date order was placed | No |
| Ship Date | str (→datetime) | Date order was shipped | No |
| Ship Mode | str | Shipping tier (4 values) | No |
| Customer ID | str | Unique customer identifier | No |
| Customer Name | str | Customer full name (PII-adjacent) | No |
| Segment | str | Business segment (3 values) | No |
| Country | str | Always "United States" — constant | No |
| City | str | City of delivery | No |
| State | str | US state of delivery | No |
| Postal Code | int64 | Delivery postal code (geo, treat categorical) | No |
| Region | str | Sales region (4 values) | No |
| Product ID | str | Product identifier | No |
| Category | str | Product category (3 values) | No |
| Sub-Category | str | Product sub-category (17 values) | No |
| Product Name | str | Full product name (~1,850 unique) | No |
| Sales | float64 | Revenue per line item (USD) | No |
| Quantity | int64 | Units ordered | No |
| Discount | float64 | Fractional discount applied (0–0.8) | No |
| Profit | float64 | Net profit per line item (USD) | No |

### 4b — Input: data/web_traffic.csv

| Column | Type | Description | Nullable |
|---|---|---|---|
| Page Views | int64 | Number of pages viewed in session | No |
| Session Duration | float64 | Session length in minutes | No |
| Bounce Rate | float64 | Bounce rate (0–1) | No |
| Traffic Source | str | Acquisition channel (5 values) | No |
| Time on Page | float64 | Time on landing page (minutes) | No |
| Previous Visits | int64 | Count of prior visits by this user | No |
| Conversion Rate | float64 | Conversion indicator (mostly 1.0 or <1) | No |

### 4c — Dirty-row rules

Rows are **removed, never fixed**, and appended to `output/PROJECT_02/dirty.csv` with a `reason` column.

**Superstore (kaggle.csv):**
| Rule | reason value |
|---|---|
| `Sales <= 0` | `sales_zero_or_negative` |
| `Profit` is an extreme outlier: absolute z-score > 3 on the full column | `profit_extreme_outlier` |

**Web traffic (web_traffic.csv):**
| Rule | reason value |
|---|---|
| `Page Views == 0` | `zero_page_views` |

### 4d — Output files

| File | Description |
|---|---|
| `output/PROJECT_02/dirty.csv` | All removed rows from both datasets; columns: source_file, all original columns, reason |
| `output/PROJECT_02/superstore_clean.parquet` | Clean Superstore data with derived columns |
| `output/PROJECT_02/webtraffic_clean.parquet` | Clean web traffic data with derived columns |
| `output/PROJECT_02/plots/*.png` | All EDA and model charts (see Phase 2 & 4) |
| `output/PROJECT_02/tables/rfm_scores.csv` | RFM tier per customer |
| `output/PROJECT_02/tables/profit_by_category.csv` | Avg profit and margin per Category/Sub-Category |
| `output/PROJECT_02/tables/discount_breakeven.csv` | Breakeven discount per category |
| `output/PROJECT_02/tables/statistical_tests.csv` | Test name, statistic, p-value, conclusion |
| `output/PROJECT_02/model/classification_report.csv` | Per-model precision, recall, F1, AUROC |
| `output/PROJECT_02/report.txt` | Final human-readable summary |

---

## 5. Phase Specs

### Phase 1 — ETL & Preprocessing (`src/phase1_etl.py`)

**Inputs:** `data/kaggle.csv`, `data/web_traffic.csv`
**Outputs:** `output/PROJECT_02/dirty.csv`, `output/PROJECT_02/superstore_clean.parquet`, `output/PROJECT_02/webtraffic_clean.parquet`

**Constants at top of file:**
```
OUTPUT_DIR = "output/PROJECT_02"
RANDOM_SEED = 42
```

**Steps:**

1. Create `output/PROJECT_02/` and subdirectories `plots/`, `tables/`, `model/` if they do not exist.

2. **Load Superstore:** `pd.read_csv("data/kaggle.csv", encoding="latin-1")`. Assert all 21 expected columns are present; raise `ValueError` if any are missing.

3. **Superstore dirty-row detection:**
   - Flag rows where `Sales <= 0` → reason = `sales_zero_or_negative`
   - Compute z-score of `Profit`; flag rows where `abs(z) > 3` → reason = `profit_extreme_outlier`
   - Collect all flagged rows into a dirty dataframe with a `source_file = "kaggle.csv"` column and `reason` column.
   - Drop flagged rows from working dataframe.

4. **Superstore derived columns** (on clean rows only):
   - Parse `Order Date` and `Ship Date` to datetime using `pd.to_datetime(..., dayfirst=False)`.
   - `days_to_ship = (Ship Date - Order Date).dt.days` (int)
   - `profit_margin = Profit / Sales` (float; set to 0 if Sales == 0 to avoid divide-by-zero — but Sales==0 rows are already removed)
   - `order_month = Order Date.dt.month` (int 1–12)
   - `order_year = Order Date.dt.year` (int)
   - `order_dayofweek = Order Date.dt.dayofweek` (int 0–6, Monday=0)
   - `is_loss = (Profit < 0).astype(int)` (binary target)
   - Drop columns: `Country` (constant), `Row ID` (synthetic key)

5. **Load Web Traffic:** `pd.read_csv("data/web_traffic.csv", encoding="latin-1")`. Assert all 7 expected columns are present.

6. **Web traffic dirty-row detection:**
   - Flag rows where `Page Views == 0` → reason = `zero_page_views`
   - Append to dirty dataframe with `source_file = "web_traffic.csv"`.
   - Drop flagged rows from working dataframe.

7. **Web traffic derived columns:**
   - `converted = (Conversion Rate >= 1.0).astype(int)` (binary)
   - `visits_bin = pd.cut(Previous Visits, bins=[-1, 0, 2, 9], labels=["0", "1-2", "3+"])` (ordinal cohort)

8. Save dirty dataframe to `output/PROJECT_02/dirty.csv` (CSV, include index=False).

9. Save clean Superstore dataframe to `output/PROJECT_02/superstore_clean.parquet`.

10. Save clean web traffic dataframe to `output/PROJECT_02/webtraffic_clean.parquet`.

11. Print to stdout: shape before/after cleaning for each dataset, dirty row counts per reason.

---

### Phase 2 — EDA & Visualisation (`src/phase2_eda.py`)

**Inputs:** `output/PROJECT_02/superstore_clean.parquet`, `output/PROJECT_02/webtraffic_clean.parquet`
**Outputs:** 11 PNG files in `output/PROJECT_02/plots/`

**Constants:** `OUTPUT_DIR = "output/PROJECT_02"`, `RANDOM_SEED = 42`

Use `matplotlib` and `seaborn`. Set style `seaborn-v0_8-whitegrid`. All figures `figsize=(10, 6)` unless specified. Save every figure with `dpi=150`, `bbox_inches="tight"`. Close each figure after saving (`plt.close()`).

**Charts:**

| # | Filename | Type | Details |
|---|---|---|---|
| 1 | `plots/01_profit_distribution.png` | Histogram + KDE | `Profit` column; add vertical line at 0; label loss area |
| 2 | `plots/02_profit_by_category.png` | Box plot | x=`Category`, y=`Profit`; colour by category; add horizontal zero line |
| 3 | `plots/03_profit_by_subcategory.png` | Horizontal bar | Mean profit per `Sub-Category`, sorted descending; colour bars red if mean < 0, green if ≥ 0 |
| 4 | `plots/04_discount_vs_profit.png` | Scatter + regression | x=`Discount`, y=`Profit`; use `alpha=0.3`; overlay `seaborn.regplot` line; add vertical line at breakeven discount |
| 5 | `plots/05_sales_profit_over_time.png` | Dual-axis line | Group by year-month; left axis = total `Sales`; right axis = total `Profit`; `figsize=(14, 6)` |
| 6 | `plots/06_region_segment_heatmap.png` | Heatmap | Pivot table: rows=`Region`, cols=`Segment`, values=mean `profit_margin`; annotate cells |
| 7 | `plots/07_shipmode_profit_violin.png` | Violin plot | x=`Ship Mode`, y=`profit_margin`; order by median |
| 8 | `plots/08_top_bottom_products.png` | Horizontal bar (2-panel) | Top 10 and Bottom 10 `Product Name` by total `Profit`; subplots side by side; `figsize=(16, 6)` |
| 9 | `plots/09_customer_order_frequency.png` | Histogram | Count of orders per `Customer ID`; x-axis capped at 95th percentile |
| 10 | `plots/10_web_conversion_by_source.png` | Bar chart | `Traffic Source` vs mean `Conversion Rate`; error bars (std); colour by source |
| 11 | `plots/11_web_bounce_vs_session.png` | Scatter | x=`Bounce Rate`, y=`Session Duration`; colour by `Traffic Source`; `alpha=0.5` |

---

### Phase 3 — Statistical Analysis (`src/phase3_stats.py`)

**Inputs:** `output/PROJECT_02/superstore_clean.parquet`
**Outputs:** `output/PROJECT_02/tables/statistical_tests.csv`, `output/PROJECT_02/tables/profit_by_category.csv`, `output/PROJECT_02/tables/discount_breakeven.csv`, `output/PROJECT_02/tables/rfm_scores.csv`, `output/PROJECT_02/plots/12_correlation_heatmap.png`, `output/PROJECT_02/plots/13_rfm_segments.png`, `output/PROJECT_02/plots/14_stl_decomposition.png`

**Constants:** `OUTPUT_DIR = "output/PROJECT_02"`, `RANDOM_SEED = 42`, `ALPHA = 0.05`

**Steps:**

1. **Correlation matrix:**
   - Compute Pearson correlation of: `Sales`, `Quantity`, `Discount`, `Profit`, `days_to_ship`, `profit_margin`.
   - Plot as annotated heatmap → `plots/12_correlation_heatmap.png`.

2. **Profit by category table:**
   - Group by `Category` and `Sub-Category`; compute count, mean profit, median profit, mean profit_margin, % loss rows.
   - Save to `tables/profit_by_category.csv`.

3. **ANOVA / Kruskal-Wallis tests** (use Kruskal-Wallis as default — does not assume normality):
   - Test 1: Does mean `Profit` differ across `Region`? (4 groups)
   - Test 2: Does mean `Profit` differ across `Segment`? (3 groups)
   - Test 3: Does mean `Profit` differ across `Category`? (3 groups)
   - For each: run `scipy.stats.kruskal`; record test name, H-statistic, p-value, and conclusion ("significant" if p < ALPHA else "not significant").

4. **Chi-square test:**
   - Contingency table: `Segment` × `Ship Mode`.
   - Run `scipy.stats.chi2_contingency`; record chi2, p-value, dof, conclusion.

5. Save all 4 test results to `tables/statistical_tests.csv` (columns: test_name, statistic, p_value, dof, conclusion).

6. **Discount breakeven analysis:**
   - Bin `Discount` into 10 equal-width buckets (0–0.1, 0.1–0.2, …, 0.7–0.8).
   - For each bucket × `Category`, compute mean `Profit`.
   - Identify the lowest discount bucket where mean profit first turns negative per category.
   - Save to `tables/discount_breakeven.csv` (columns: Category, breakeven_discount_bucket, mean_profit_at_breakeven).

7. **RFM scoring:**
   - Reference date = max(`Order Date`) + 1 day.
   - Per `Customer ID`: Recency = days since last order; Frequency = count of distinct `Order ID`; Monetary = sum of `Sales`.
   - Assign quartile scores 1–4 for each dimension (4 = best: lowest recency, highest frequency, highest monetary).
   - Concatenate into `RFM_Score = str(R) + str(F) + str(M)`.
   - Assign segment label based on score (Champions ≥ "444", Loyal ≥ "334", At Risk ≤ "222", others = "Mid-tier").
   - Save to `tables/rfm_scores.csv` (columns: Customer ID, Recency, Frequency, Monetary, R, F, M, RFM_Score, Segment).
   - Plot segment distribution bar chart → `plots/13_rfm_segments.png`.

8. **STL decomposition:**
   - Aggregate `Sales` by year-month (period index, monthly frequency).
   - Run `statsmodels.tsa.seasonal.STL(series, period=12).fit()`.
   - Plot 4-panel figure (observed, trend, seasonal, residual) → `plots/14_stl_decomposition.png`.

---

### Phase 4 — Feature Engineering & Modelling (`src/phase4_model.py`)

**Inputs:** `output/PROJECT_02/superstore_clean.parquet`
**Outputs:** `output/PROJECT_02/model/classification_report.csv`, `output/PROJECT_02/plots/15_feature_importance.png`, `output/PROJECT_02/plots/16_roc_curves.png`

**Constants:** `OUTPUT_DIR = "output/PROJECT_02"`, `RANDOM_SEED = 42`

**Target:** `is_loss` (binary: 1 if Profit < 0)

**Feature matrix construction:**

Categorical features (one-hot encode with `drop="first"`, `handle_unknown="ignore"`):
- `Ship Mode`, `Segment`, `Category`, `Sub-Category`, `Region`

Numeric features (pass through as-is — do NOT include `profit_margin` to avoid leakage from `Profit`):
- `Sales`, `Quantity`, `Discount`, `days_to_ship`, `order_month`, `order_year`, `order_dayofweek`

Columns to explicitly exclude:
- `Row ID` (already dropped), `Order ID`, `Customer ID`, `Customer Name` (dropped), `City`, `State`, `Postal Code`, `Product ID`, `Product Name`, `Order Date`, `Ship Date`, `Profit`, `profit_margin`, `is_loss` (target), `converted`, `visits_bin`

Use `sklearn.compose.ColumnTransformer` + `sklearn.pipeline.Pipeline`.

**Models:**

| Name | Class | Key hyperparameters |
|---|---|---|
| Logistic Regression | `sklearn.linear_model.LogisticRegression` | `max_iter=1000`, `C=1.0`, `class_weight="balanced"`, `random_state=RANDOM_SEED` |
| Random Forest | `sklearn.ensemble.RandomForestClassifier` | `n_estimators=200`, `max_depth=None`, `class_weight="balanced"`, `random_state=RANDOM_SEED` |
| XGBoost | `xgboost.XGBClassifier` | `n_estimators=200`, `max_depth=6`, `learning_rate=0.1`, `scale_pos_weight=<ratio of negatives/positives>`, `random_state=RANDOM_SEED`, `eval_metric="logloss"` |

**Cross-validation:**
- `sklearn.model_selection.StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)`
- For each fold: fit pipeline on train, predict proba on val, collect AUROC and F1 (threshold=0.5).
- After CV: refit each model on full dataset for feature importance extraction.

**Metrics to record per model:**
- Mean CV AUROC (±std)
- Mean CV F1-macro (±std)
- Full-dataset classification report: precision, recall, F1 per class + support
- Confusion matrix values (TP, FP, TN, FN)

Save all metrics to `model/classification_report.csv` (columns: model_name, cv_auroc_mean, cv_auroc_std, cv_f1_mean, cv_f1_std, precision_0, recall_0, f1_0, precision_1, recall_1, f1_1).

**Plots:**

- `plots/15_feature_importance.png`: Horizontal bar chart of top-20 feature importances from Random Forest (use `feature_importances_` attribute). Sort descending.
- `plots/16_roc_curves.png`: Overlay ROC curves for all 3 models on a single axes. Use full-dataset predicted probas (refit models). Label each curve with model name and AUROC. Include diagonal reference line.

---

### Phase 5 — Reporting (`src/phase5_report.py`)

**Inputs:** `output/PROJECT_02/tables/*.csv`, `output/PROJECT_02/model/classification_report.csv`
**Outputs:** `output/PROJECT_02/report.txt`

**Constants:** `OUTPUT_DIR = "output/PROJECT_02"`

**Steps:**

1. Load `tables/profit_by_category.csv`, `tables/discount_breakeven.csv`, `tables/statistical_tests.csv`, `tables/rfm_scores.csv`, `model/classification_report.csv`.

2. Render the following sections to a string, then save to `output/PROJECT_02/report.txt` and also print to stdout:

```
=== SUPERSTORE SALES — ANALYSIS REPORT ===
Generated: <datetime>

--- 1. DATASET OVERVIEW ---
  Superstore: <N_clean> rows after removing <N_dirty> dirty rows
  Date range: 2014-01-03 to 2017-12-30

--- 2. PROFITABILITY BY CATEGORY ---
  <table: Category | Sub-Category | Mean Profit | % Loss rows>
  Top 3 most profitable sub-categories: ...
  Bottom 3 least profitable sub-categories: ...

--- 3. DISCOUNT BREAKEVEN ---
  <table: Category | Breakeven Discount Bucket>
  Insight: Discounts above X% drive losses in Furniture; Y% in Technology.

--- 4. STATISTICAL TESTS ---
  <table: Test | Statistic | p-value | Conclusion>

--- 5. RFM CUSTOMER SEGMENTS ---
  <table: Segment | Count | % of customers>

--- 6. MODEL RESULTS ---
  <table: Model | CV AUROC | CV F1-macro>
  Best model by AUROC: <name> (<score>)
  Key predictors (top 5 features from Random Forest): ...

--- 7. KEY FINDINGS ---
  1. ...
  2. ...
  3. ...
```

Section 7 should contain 3–5 bullet findings derived programmatically from the loaded data (e.g. "Tables sub-category has the highest % loss rows at X%", "Discount is the strongest predictor of loss (feature rank #1)").

---

## 6. Reproducibility

- `RANDOM_SEED = 42` defined at the top of every script.
- All scripts must be runnable independently in phase order.
- No script modifies `data/` — all writes go to `output/PROJECT_02/`.
- Parquet files are the interchange format between phases (not CSV), to preserve dtypes.

---

## 7. Error Handling

- Each script raises `FileNotFoundError` with a clear message if a required input file does not exist.
- Each script raises `ValueError` with a clear message if expected columns are missing from a loaded dataframe.
- Warn (via `warnings.warn`) if dirty row count is 0 — may indicate a dirty-row rule was silently skipped.

---

## 8. Run Order

```bash
uv run python src/phase1_etl.py
uv run python src/phase2_eda.py
uv run python src/phase3_stats.py
uv run python src/phase4_model.py
uv run python src/phase5_report.py
```
