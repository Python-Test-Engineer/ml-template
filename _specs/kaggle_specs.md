# Technical Spec — Medical Appointment No-Show EDA

**Plan source:** _plans/kaggle_plan.md
**Dataset(s):** data/kaggle.csv
**Output directory:** output/PROJECT_01/
**Date:** 2026-03-17

---

## 1. Overview

Five Python scripts execute in phase order to produce a comprehensive EDA of the Brazilian medical appointment no-show dataset (110,527 rows). Phase 0 cleans the data and engineers features. Phases 1–3 produce 25 numbered PNG charts covering univariate, bivariate, and multivariate analyses respectively, plus a `summary_stats.csv`. Phase 4 compiles everything into a single self-contained `report.html` with all plots embedded as base64 and a "Hard Interview Questions" appendix. No predictive model is produced.

---

## 2. Environment

- Python 3.12 via `uv`
- Dependencies to add with `uv add`:
  ```
  pandas matplotlib seaborn jinja2
  ```
- All scripts use `matplotlib` non-interactive backend (`matplotlib.use("Agg")`) — no display required.
- Global style: `plt.style.use("seaborn-v0_8-whitegrid")` at the top of every plotting script.
- Figure DPI: 150 for all saved PNGs. Figure size default: `(10, 6)` unless noted otherwise.

---

## 3. Script Architecture

| Script | Location | Responsibility |
|---|---|---|
| `phase0_etl.py` | `src/` | Load raw CSV, parse dates, engineer `lead_days` and `noshow_flag`, identify and remove dirty rows, save `dirty.csv` + `clean.csv` |
| `phase1_univariate.py` | `src/` | Load `clean.csv`, produce plots 01–08 (univariate distributions) |
| `phase2_bivariate.py` | `src/` | Load `clean.csv`, produce plots 09–18 (no-show rate by each feature) + `summary_stats.csv` |
| `phase3_multivariate.py` | `src/` | Load `clean.csv`, produce plots 19–25 (deep-dive analyses) |
| `phase4_report.py` | `src/` | Load all outputs, render and save `report.html` |

Each script is independently runnable and must be run in phase order.

---

## 4. Data Contract

### 4.1 Raw Input (`data/kaggle.csv`)

| Column | Raw Type | Description | Nullable |
|---|---|---|---|
| PatientId | float64 | Patient identifier (one patient may have multiple rows) | No |
| AppointmentID | int64 | Unique appointment identifier | No |
| Gender | str | "F" or "M" | No |
| ScheduledDay | str | ISO datetime string with UTC offset (e.g. `2016-04-29T18:38:08Z`) | No |
| AppointmentDay | str | ISO date string (`2016-04-29T00:00:00Z`) | No |
| Age | int64 | Patient age in years; valid range 0–115 | No |
| Neighbourhood | str | Name of neighbourhood in Vitória, ES, Brazil (81 unique values) | No |
| Scholarship | int64 | 1 = enrolled in Bolsa Família welfare programme, 0 = not | No |
| Hipertension | int64 | 1 = has hypertension, 0 = does not | No |
| Diabetes | int64 | 1 = has diabetes, 0 = does not | No |
| Alcoholism | int64 | 1 = has alcoholism, 0 = does not | No |
| Handcap | int64 | Disability level 0–4 (0 = none) | No |
| SMS_received | int64 | 1 = received SMS reminder, 0 = did not | No |
| No-show | str | "Yes" = did not attend, "No" = attended | No |

### 4.2 Dirty-Row Rules

Rows are **removed, never fixed**. Each removed row gets a `reason` string.

| Rule | Condition | Reason string |
|---|---|---|
| Negative age | `Age < 0` | `"negative age"` |
| Implausible age | `Age > 115` | `"age > 115"` |
| Impossible lead time | `lead_days < 0` | `"appointment before scheduled date"` |

All three checks are applied independently; a row matching multiple rules uses the first matching reason in the order above.

### 4.3 Engineered Columns (added in Phase 0)

| Column | Type | Formula | Notes |
|---|---|---|---|
| `scheduled_dt` | datetime (tz-naive) | `pd.to_datetime(ScheduledDay, utc=True).dt.tz_localize(None)` | Used only for lead-time calc |
| `appointment_dt` | datetime (tz-naive) | `pd.to_datetime(AppointmentDay, utc=True).dt.tz_localize(None)` | |
| `lead_days` | int | `(appointment_dt.dt.date - scheduled_dt.dt.date).apply(lambda x: x.days)` | Days between booking and appointment |
| `noshow_flag` | int (0/1) | `1` if `No-show == "Yes"`, else `0` | Numeric target for aggregations |
| `appointment_dow` | int (0=Mon … 6=Sun) | `appointment_dt.dt.dayofweek` | Day of week |
| `appointment_month` | int (1–12) | `appointment_dt.dt.month` | Calendar month |
| `handcap_binary` | int (0/1) | `(Handcap > 0).astype(int)` | Simplified disability flag for binary analyses |
| `age_group` | str | Bin `Age` into `["0-10","11-20","21-30","31-40","41-50","51-60","61-70","71-80","81+"]` using `pd.cut` | |
| `lead_bucket` | str | Bin `lead_days` into `["same-day","1-7d","8-30d","31-90d","90d+"]` with explicit labels | |

### 4.4 Clean Output (`output/PROJECT_01/clean.csv`)

The clean CSV contains all original columns plus all engineered columns listed in §4.3, with dirty rows removed. Column order: original columns first, then engineered columns.

### 4.5 Output Files Summary

| File | Produced by | Description |
|---|---|---|
| `output/PROJECT_01/dirty.csv` | phase0_etl.py | Removed rows + `reason` column |
| `output/PROJECT_01/clean.csv` | phase0_etl.py | Cleaned dataset with engineered columns |
| `output/PROJECT_01/plots/01_age_distribution.png` | phase1_univariate.py | Age histogram + KDE |
| `output/PROJECT_01/plots/02_lead_days_distribution.png` | phase1_univariate.py | Lead time histogram |
| `output/PROJECT_01/plots/03_noshow_overall.png` | phase1_univariate.py | Overall no-show rate bar chart |
| `output/PROJECT_01/plots/04_binary_flags_prevalence.png` | phase1_univariate.py | Prevalence of all binary condition flags |
| `output/PROJECT_01/plots/05_gender_split.png` | phase1_univariate.py | Gender distribution bar chart |
| `output/PROJECT_01/plots/06_top20_neighbourhoods.png` | phase1_univariate.py | Top 20 neighbourhoods by appointment volume |
| `output/PROJECT_01/plots/07_appointments_by_weekday.png` | phase1_univariate.py | Appointment count by day of week |
| `output/PROJECT_01/plots/08_appointments_over_time.png` | phase1_univariate.py | Daily appointment volume line chart |
| `output/PROJECT_01/plots/09_noshow_by_gender.png` | phase2_bivariate.py | No-show rate by gender |
| `output/PROJECT_01/plots/10_noshow_by_age_group.png` | phase2_bivariate.py | No-show rate by age group |
| `output/PROJECT_01/plots/11_noshow_by_lead_days.png` | phase2_bivariate.py | No-show rate by lead time bucket |
| `output/PROJECT_01/plots/12_noshow_by_sms.png` | phase2_bivariate.py | No-show rate by SMS received |
| `output/PROJECT_01/plots/13_noshow_by_conditions.png` | phase2_bivariate.py | No-show rate by each health condition (faceted) |
| `output/PROJECT_01/plots/14_noshow_by_weekday.png` | phase2_bivariate.py | No-show rate by day of week |
| `output/PROJECT_01/plots/15_noshow_by_neighbourhood.png` | phase2_bivariate.py | No-show rate for top-30 neighbourhoods by volume |
| `output/PROJECT_01/plots/16_noshow_by_month.png` | phase2_bivariate.py | No-show rate by appointment month |
| `output/PROJECT_01/plots/17_repeat_patient_noshow.png` | phase2_bivariate.py | Prior no-show rate vs current no-show (patient-level) |
| `output/PROJECT_01/plots/18_correlation_heatmap.png` | phase2_bivariate.py | Correlation heatmap: numeric features vs noshow_flag |
| `output/PROJECT_01/plots/19_sms_paradox.png` | phase3_multivariate.py | SMS × lead bucket × no-show cross-tabulation |
| `output/PROJECT_01/plots/20_age_condition_heatmap.png` | phase3_multivariate.py | No-show rate: age group × hypertension pivot heatmap |
| `output/PROJECT_01/plots/21_neighbourhood_inequality.png` | phase3_multivariate.py | Per-neighbourhood no-show rate bar (all 81, sorted) |
| `output/PROJECT_01/plots/22_same_day_profile.png` | phase3_multivariate.py | Same-day appointment profile: age + condition bars |
| `output/PROJECT_01/plots/23_scholarship_analysis.png` | phase3_multivariate.py | No-show rate: scholarship × neighbourhood volume tercile |
| `output/PROJECT_01/plots/24_patient_appointment_counts.png` | phase3_multivariate.py | Distribution of appointments per patient |
| `output/PROJECT_01/plots/25_weekly_noshow_timeseries.png` | phase3_multivariate.py | Weekly no-show rate time series |
| `output/PROJECT_01/summary_stats.csv` | phase3_multivariate.py | Key aggregated statistics table |
| `output/PROJECT_01/report.html` | phase4_report.py | Self-contained HTML report |

---

## 5. Phase Specs

### Phase 0 — ETL & Cleaning (`src/phase0_etl.py`)

**Inputs:** `data/kaggle.csv`
**Outputs:** `output/PROJECT_01/dirty.csv`, `output/PROJECT_01/clean.csv`

**Pre-conditions:** Assert that `data/kaggle.csv` exists; raise `FileNotFoundError` with clear message if not.

**Steps:**
1. Create `output/PROJECT_01/` and `output/PROJECT_01/plots/` directories (`exist_ok=True`).
2. Load CSV with `pd.read_csv`.
3. Assert all 14 expected columns are present; raise `ValueError` listing any missing ones.
4. Parse `ScheduledDay` and `AppointmentDay` as UTC datetime, then strip timezone info (`.dt.tz_localize(None)`), storing as `scheduled_dt` and `appointment_dt`.
5. Compute `lead_days` as integer days (see §4.3).
6. Identify dirty rows using the three rules in §4.2 (evaluate all rules, tag first matching reason).
7. Write dirty rows (all original columns + `reason`) to `output/PROJECT_01/dirty.csv`.
8. Drop dirty rows; print count removed and count retained.
9. Add all engineered columns in §4.3 to the clean dataframe.
10. Write clean dataframe to `output/PROJECT_01/clean.csv` (index=False).
11. Print a completion summary: total rows, dirty rows removed, clean rows saved, `lead_days` range.

---

### Phase 1 — Univariate EDA (`src/phase1_univariate.py`)

**Inputs:** `output/PROJECT_01/clean.csv`
**Outputs:** plots 01–08 in `output/PROJECT_01/plots/`

**Pre-conditions:** Assert `clean.csv` exists.

**Plot specifications:**

| Plot file | Type | X / Y | Title | Notes |
|---|---|---|---|---|
| `01_age_distribution.png` | Histogram + KDE | Age | "Age Distribution of Patients" | bins=20; use `seaborn.histplot(kde=True)`; annotate median age with vertical dashed line |
| `02_lead_days_distribution.png` | Histogram | lead_days | "Days Between Scheduling and Appointment" | bins=50; clip x-axis to [0, 120] to reduce distortion from long tail; annotate mean with vertical line |
| `03_noshow_overall.png` | Horizontal bar | Count / % | "Overall No-Show vs Attended" | Two bars: "Attended (No)" and "No-Show (Yes)"; annotate each bar with count and percentage |
| `04_binary_flags_prevalence.png` | Grouped bar | Flag name / % positive | "Prevalence of Patient Condition Flags" | Flags: Scholarship, Hipertension, Diabetes, Alcoholism, handcap_binary, SMS_received; one bar per flag; annotate with percentage |
| `05_gender_split.png` | Bar chart | Gender / Count | "Appointment Count by Gender" | Annotate each bar with count and percentage |
| `06_top20_neighbourhoods.png` | Horizontal bar | Neighbourhood / Count | "Top 20 Neighbourhoods by Appointment Volume" | Sort descending; figure height `(8, 6)` |
| `07_appointments_by_weekday.png` | Bar chart | Day name / Count | "Appointments by Day of Week" | Use ordered day names (Mon–Sat; note Sun should be 0 in data) |
| `08_appointments_over_time.png` | Line chart | Date / Count | "Daily Appointment Volume (Apr–Jun 2016)" | Resample to daily; x-axis formatted as month-day |

---

### Phase 2 — Bivariate EDA (`src/phase2_bivariate.py`)

**Inputs:** `output/PROJECT_01/clean.csv`
**Outputs:** plots 09–18, `output/PROJECT_01/summary_stats.csv`

**Pre-conditions:** Assert `clean.csv` exists.

**Shared pattern for no-show rate bar charts:** Compute `noshow_rate = noshow_flag.mean()` per group. Plot as bar chart with y-axis 0–100% (multiply by 100). Annotate each bar with the rate value. Include a dashed horizontal line at the overall no-show rate (20.2%) as a reference.

**Plot specifications:**

| Plot file | Grouping | Title | Notes |
|---|---|---|---|
| `09_noshow_by_gender.png` | Gender | "No-Show Rate by Gender" | Two bars: F, M |
| `10_noshow_by_age_group.png` | age_group | "No-Show Rate by Age Group" | Ordered age groups on x-axis |
| `11_noshow_by_lead_days.png` | lead_bucket | "No-Show Rate by Appointment Lead Time" | Ordered buckets on x-axis |
| `12_noshow_by_sms.png` | SMS_received | "No-Show Rate by SMS Reminder Status" | Two bars: No SMS, SMS received; add annotation noting the counterintuitive result |
| `13_noshow_by_conditions.png` | Each condition flag | "No-Show Rate by Patient Condition" | Faceted: 2×3 subplots, one per flag (Scholarship, Hipertension, Diabetes, Alcoholism, handcap_binary, SMS_received); each subplot has two bars (0/1); figure size `(14, 8)` |
| `14_noshow_by_weekday.png` | appointment_dow | "No-Show Rate by Day of Week" | Ordered Mon–Sat |
| `15_noshow_by_neighbourhood.png` | Neighbourhood | "No-Show Rate for Top 30 Neighbourhoods by Volume" | Filter to top 30 by volume; bars coloured by rate using a diverging colormap centred on overall mean; figure size `(10, 12)` horizontal bar |
| `16_noshow_by_month.png` | appointment_month | "No-Show Rate by Appointment Month" | Months: April, May, June |
| `17_repeat_patient_noshow.png` | Patient history | "Prior No-Show Rate vs Current No-Show" | For each patient compute: prior no-show rate (excluding current appointment, sorted by appointment date); bin into 5 buckets [0%, 1–25%, 26–50%, 51–75%, 76–100%]; bar chart of no-show rate per bucket |
| `18_correlation_heatmap.png` | — | "Correlation Heatmap: Features vs No-Show" | Columns: Age, lead_days, Scholarship, Hipertension, Diabetes, Alcoholism, handcap_binary, SMS_received, noshow_flag; `seaborn.heatmap` with `annot=True`, `fmt=".2f"`, diverging palette; figure size `(10, 8)` |

**`summary_stats.csv` contents:**
A long-format CSV with columns `[metric, value]` containing:
- Total appointments (after cleaning)
- Total unique patients
- Overall no-show rate (%)
- No-show rate by gender (F, M)
- No-show rate by lead bucket (5 buckets)
- No-show rate by SMS status (0, 1)
- Mean lead_days
- Median lead_days
- Most common neighbourhood
- Neighbourhood with highest no-show rate (min 50 appointments)
- Neighbourhood with lowest no-show rate (min 50 appointments)

---

### Phase 3 — Multivariate Deep-Dives (`src/phase3_multivariate.py`)

**Inputs:** `output/PROJECT_01/clean.csv`
**Outputs:** plots 19–25

**Pre-conditions:** Assert `clean.csv` exists.

**Analysis specifications:**

**Plot 19 — SMS Paradox (`19_sms_paradox.png`)**
- Compute no-show rate cross-tabulated by: `SMS_received` (0/1) × `lead_bucket` (5 buckets).
- Display as grouped bar chart: x-axis = lead_bucket, two bars per group (SMS=0, SMS=1).
- Title: "The SMS Paradox: No-Show Rate by Lead Time and SMS Status"
- Add a subtitle/annotation: "SMS recipients have higher overall no-show rates because reminders are sent to high-lead-time appointments"

**Plot 20 — Age × Condition Heatmap (`20_age_condition_heatmap.png`)**
- Pivot table: rows = `age_group` (ordered), columns = `Hipertension` (0/1), values = `noshow_flag` mean.
- Display as `seaborn.heatmap` with `annot=True`, `fmt=".1%"`, colormap `YlOrRd`.
- Title: "No-Show Rate: Age Group × Hypertension Status"

**Plot 21 — Neighbourhood Inequality (`21_neighbourhood_inequality.png`)**
- Compute per-neighbourhood no-show rate for all 81 neighbourhoods.
- Sort ascending by no-show rate.
- Horizontal bar chart; colour bars using a continuous colormap (low=green, high=red).
- Annotate the top-3 highest and top-3 lowest explicitly.
- Also compute and print the Gini coefficient of the no-show rate distribution to stdout.
- Figure size: `(10, 16)`.
- Title: "No-Show Rate by Neighbourhood (All 81)"

**Plot 22 — Same-Day Profile (`22_same_day_profile.png`)**
- Isolate `lead_days == 0` subset.
- 2-panel figure:
  - Left: Age distribution histogram for same-day vs rest (overlaid, normalized).
  - Right: Bar chart comparing no-show rate for same-day vs rest + condition flag prevalence comparison.
- Title: "Profile of Same-Day Appointments"

**Plot 23 — Scholarship Analysis (`23_scholarship_analysis.png`)**
- Classify each neighbourhood into tercile by appointment volume: low, medium, high volume (as a proxy for neighbourhood socioeconomic activity).
- For each tercile, plot no-show rate for Scholarship=0 vs Scholarship=1.
- Display as grouped bar chart with 3 group pairs.
- Title: "No-Show Rate: Welfare Recipients vs Non-Recipients by Neighbourhood Volume Tercile"

**Plot 24 — Patient Appointment Counts (`24_patient_appointment_counts.png`)**
- Aggregate to patient level: count appointments per `PatientId`.
- Histogram of appointment count per patient (bins up to ~20, then "20+" bucket).
- Also plot: no-show rate for patients with 1 appointment vs 2–5 vs 6–10 vs 10+ appointments.
- 2-panel figure (side by side).
- Title: "Patient Appointment Frequency"

**Plot 25 — Weekly No-Show Time Series (`25_weekly_noshow_timeseries.png`)**
- Resample by ISO week (using `appointment_dt`); compute weekly no-show rate and weekly appointment count.
- Dual-axis line chart: left y-axis = no-show rate (%); right y-axis = appointment volume.
- Annotate any week where no-show rate is > 1.5 standard deviations from the mean with a vertical dashed line.
- Title: "Weekly No-Show Rate and Appointment Volume (Apr–Jun 2016)"

---

### Phase 4 — HTML Report (`src/phase4_report.py`)

**Inputs:** All 25 PNG plots in `output/PROJECT_01/plots/`, `output/PROJECT_01/summary_stats.csv`, `output/PROJECT_01/dirty.csv`
**Outputs:** `output/PROJECT_01/report.html`

**Pre-conditions:** Assert all 25 plot files exist; raise `FileNotFoundError` listing any missing ones.

**Report structure (rendered via Jinja2 template defined inline as a Python string):**

```
<html>
  <head>
    <title>Medical Appointment No-Show — EDA Report</title>
    <style>  [see §5.4.1 below]  </style>
  </head>
  <body>
    <h1>Medical Appointment No-Show — EDA Report</h1>
    <p class="meta">Dataset: data/kaggle.csv | Generated: {date} | Rows after cleaning: {n_clean}</p>

    <section id="dataset-summary">
      <h2>1. Dataset Summary</h2>
      [HTML table from summary_stats.csv]
      <p>Dirty rows removed: {n_dirty} (saved to dirty.csv)</p>
    </section>

    <section id="key-findings">
      <h2>2. Key Findings</h2>
      <ul>
        [5–8 bullet points — see §5.4.2]
      </ul>
    </section>

    <section id="univariate">
      <h2>3. Univariate Analysis</h2>
      [Plots 01–08, each with a caption]
    </section>

    <section id="bivariate">
      <h2>4. Bivariate Analysis — No-Show Drivers</h2>
      [Plots 09–18, each with a caption]
    </section>

    <section id="multivariate">
      <h2>5. Multivariate & Deep-Dive Analyses</h2>
      [Plots 19–25, each with a caption]
    </section>

    <section id="interview-qa">
      <h2>6. Hard Interview Questions — Q&A</h2>
      [See §5.4.3]
    </section>
  </body>
</html>
```

**§5.4.1 — CSS style:** Clean, minimal styling. White background, max-width 1100px, centered. H2 headings with a bottom border. Images max-width 100%. `<details>/<summary>` used for each Q&A pair so they are collapsible.

**§5.4.2 — Key Findings bullet points** (hardcoded from known analysis results):
1. The overall no-show rate is ~20.2%, meaning roughly 1 in 5 appointments is missed.
2. Longer lead times strongly predict no-shows: same-day appointments have the lowest no-show rate; appointments booked 31+ days ahead have the highest.
3. Despite intuition, patients who received an SMS reminder had a *higher* no-show rate. This is a selection-bias artefact: SMS reminders were disproportionately sent for high-lead-time appointments.
4. Younger patients (11–30 age group) have higher no-show rates; elderly patients (60+) are among the most reliable attenders.
5. Welfare-programme (Scholarship) recipients have a slightly higher no-show rate, likely reflecting transport or employment constraints.
6. Day of week matters: Friday appointments have the highest no-show rate; appointments on Tuesday and Wednesday are most reliably attended.
7. Substantial neighbourhood-level variation exists (Gini > 0.10 expected); high-volume central neighbourhoods tend to have lower no-show rates.
8. Patients with a history of missing appointments are significantly more likely to miss their next appointment — prior behaviour is the strongest single predictor.

**§5.4.3 — Interview Q&A pairs** (6 questions, each as `<details><summary>Q: …</summary><p>A: …</p></details>`):

1. **Q: Why does SMS_received correlate positively with no-shows, when you'd expect reminders to help?**
   A: Explain selection bias — SMS reminders were sent to patients with longer lead times. Lead time is the dominant predictor of no-show, so controlling for lead time eliminates or reverses the SMS effect. Show reference to Plot 19.

2. **Q: What is the effect of appointment lead time on attendance?**
   A: Discuss the monotonic relationship — same-day near-zero no-show rate rising to 30%+ for 90+ day lead times. Discuss scheduling system implications.

3. **Q: Which patient segments are at highest risk of not attending?**
   A: Young adults (11–30), welfare recipients, long-lead-time appointments, patients with prior no-show history, Friday appointments.

4. **Q: How would you build a no-show prediction model from this data?**
   A: Define target (binary), discuss features (lead_days, prior_noshow_rate, age, conditions, dow, neighbourhood), discuss class imbalance strategies (SMOTE, class weights), recommended algorithms (logistic regression baseline, gradient boosting), evaluation metric (AUROC > accuracy due to imbalance), cross-validation approach (time-based split to avoid data leakage).

5. **Q: What are the ethical considerations of using neighbourhood or scholarship status as features?**
   A: Discuss proxy discrimination — these features correlate with socioeconomic status and ethnicity. Using them in an automated system could entrench inequality (e.g. deprioritising patients from poorer areas). Discuss regulatory frameworks (LGPD in Brazil), fairness metrics (demographic parity), and human-oversight requirements.

6. **Q: What are the limitations of this dataset?**
   A: Single city (Vitória, ES) — limited generalisability. No information on appointment type, department, or doctor. No reason for no-show captured. PatientId float64 precision issue. 7-month window may not capture seasonal patterns. No socioeconomic or transport data to explain neighbourhood effects.

**Embedding plots:** For each PNG file, read as bytes, base64-encode, and embed as `<img src="data:image/png;base64,{encoded}">`. This makes the HTML fully self-contained.

---

## 6. Reproducibility

- No random operations in this project (pure EDA, no train/test splits, no sampling).
- All scripts produce deterministic output given the same input CSV.
- Output directory is hardcoded as `OUTPUT_DIR = Path("output/PROJECT_01")` at the top of each script.

---

## 7. Error Handling

- Each script asserts its input files exist at startup; raises `FileNotFoundError` with a message stating which file is missing and which phase should be run first.
- Each script asserts expected columns are present in loaded dataframes; raises `ValueError` listing missing columns.
- `output/PROJECT_01/` and `output/PROJECT_01/plots/` directories are created with `mkdir(parents=True, exist_ok=True)` in phase0; all subsequent scripts also call this defensively.
- Matplotlib figures are always explicitly closed after saving (`plt.close("all")`) to prevent memory leaks across 25 plots.

---

## 8. Run Order

```bash
uv run python src/phase0_etl.py
uv run python src/phase1_univariate.py
uv run python src/phase2_bivariate.py
uv run python src/phase3_multivariate.py
uv run python src/phase4_report.py
```
