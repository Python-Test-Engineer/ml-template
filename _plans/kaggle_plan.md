# Research Plan — Medical Appointment No-Show EDA

**Idea source:** _ideas/kaggle_ideas.md
**Dataset(s):** data/kaggle.csv
**Date:** 2026-03-17

---

## 1. Research Question

This project performs a comprehensive exploratory data analysis of a Brazilian public-health appointments dataset (110,527 records, Vitória municipality, Nov 2015 – Jun 2016) to understand **which patient and appointment factors drive no-shows**. The no-show rate is ~20.2%, creating a meaningful imbalance worth characterising. The outputs — charts, summary tables, and an HTML report — are designed for an internal technical audience and to prepare the researcher to answer a wide range of interview questions about the data.

No predictive model is in scope; the goal is rigorous understanding, not prediction.

---

## 2. Dataset Summary

| Column | Type | Missing % | Notes |
|---|---|---|---|
| PatientId | float64 | 0% | Unique patient ID; one patient may have multiple appointments |
| AppointmentID | int64 | 0% | Unique appointment ID |
| Gender | object | 0% | F (65%), M (35%) |
| ScheduledDay | object→datetime | 0% | Timestamp with timezone; range Nov 2015 – Jun 2016 |
| AppointmentDay | object→datetime | 0% | Date only; range Apr 2016 – Jun 2016 |
| Age | int64 | 0% | 0–115; 1 negative value (-1), 7 values ≥ 100 |
| Neighbourhood | object | 0% | 81 unique Brazilian neighbourhoods |
| Scholarship | int64 | 0% | Bolsa Família welfare recipient (1=yes); 9.8% enrolled |
| Hipertension | int64 | 0% | Hypertension flag; 19.7% positive |
| Diabetes | int64 | 0% | Diabetes flag; 7.2% positive |
| Alcoholism | int64 | 0% | Alcoholism flag; 3.0% positive |
| Handcap | int64 | 0% | Disability level 0–4 (not purely binary); 1.7% non-zero |
| SMS_received | int64 | 0% | SMS reminder sent (1=yes); 32.1% received |
| No-show | object | 0% | **Target** — "Yes" = no-show (20.2%), "No" = attended (79.8%) |

**Key observations:**
- Zero missing values across all columns — data is complete.
- No duplicate rows.
- `ScheduledDay` spans a much wider range than `AppointmentDay`; lead time (days between scheduling and appointment) is a derived feature of high interest.
- `Handcap` has values 0–4; only 16 rows have value ≥ 2 (treat as binary 0/1+ for most analyses).
- Class imbalance: 79.8% show vs 20.2% no-show.
- **Dirty rows to remove:** 1 negative age, 7 ages > 115, 5 appointments scheduled after the appointment day → ~13 rows, saved to `output/PROJECT_XX/dirty.csv`.

---

## 3. Proposed Phases

### Phase 0 — ETL & Cleaning

**Steps:**
1. Load `data/kaggle.csv`.
2. Parse `ScheduledDay` and `AppointmentDay` as datetime (strip timezone from ScheduledDay).
3. Engineer `lead_days` = (`AppointmentDay` − `ScheduledDay.date()`).days.
4. Identify dirty rows:
   - `Age < 0` → reason: "negative age"
   - `Age > 115` → reason: "age > 115"
   - `lead_days < 0` → reason: "appointment before scheduled date"
5. Save dirty rows with `reason` column to `output/PROJECT_XX/dirty.csv`.
6. Drop dirty rows from working dataframe.
7. Encode `No-show` as binary integer (`noshow_flag`: 1=yes, 0=no) for numeric aggregations.
8. Save clean dataframe to `output/PROJECT_XX/clean.csv`.

**Output files:**
- `output/PROJECT_XX/dirty.csv`
- `output/PROJECT_XX/clean.csv`

---

### Phase 1 — Univariate EDA

**Goal:** Understand the distribution of every variable in isolation.

**Steps:**
1. **Age distribution** — histogram (bins=20) with KDE; note infant (age=0) cluster and elderly tail.
2. **Lead time distribution** — histogram of `lead_days`; note same-day appointments (lead=0) and long-wait outliers.
3. **No-show rate overall** — bar chart showing 79.8% / 20.2% split.
4. **Binary flags** — grouped bar chart showing prevalence of Scholarship, Hypertension, Diabetes, Alcoholism, Handicap, SMS_received.
5. **Gender split** — pie or bar chart.
6. **Neighbourhood counts** — horizontal bar chart of top 20 neighbourhoods by appointment volume.
7. **Appointment day of week** — bar chart; extract from `AppointmentDay`.
8. **Appointments over time** — line chart of daily appointment volume (April–June 2016).

**Output files:**
- `output/PROJECT_XX/plots/01_age_distribution.png`
- `output/PROJECT_XX/plots/02_lead_days_distribution.png`
- `output/PROJECT_XX/plots/03_noshow_overall.png`
- `output/PROJECT_XX/plots/04_binary_flags_prevalence.png`
- `output/PROJECT_XX/plots/05_gender_split.png`
- `output/PROJECT_XX/plots/06_top20_neighbourhoods.png`
- `output/PROJECT_XX/plots/07_appointments_by_weekday.png`
- `output/PROJECT_XX/plots/08_appointments_over_time.png`

---

### Phase 2 — Bivariate EDA (No-Show Drivers)

**Goal:** Identify which factors are associated with higher/lower no-show rates.

**Steps:**
1. **No-show rate by Gender** — grouped bar chart.
2. **No-show rate by Age group** — bin age into 0–10, 11–20, …, 80+; bar chart of no-show rate per bin.
3. **No-show rate by Lead time bucket** — bin lead_days: 0, 1–7, 8–30, 31–90, 90+; bar chart.
4. **No-show rate by SMS received** — bar chart; note the counterintuitive expected result (SMS correlates with no-show due to selection bias).
5. **No-show rate by each binary condition** — faceted bar chart for Scholarship, Hypertension, Diabetes, Alcoholism, Handicap.
6. **No-show rate by Day of Week** — bar chart; expect higher no-shows on Fridays/Mondays.
7. **No-show rate by Neighbourhood** — horizontal bar chart (top 30 by volume, coloured by rate); identify high-risk neighbourhoods.
8. **No-show rate by Month** — aggregate by appointment month.
9. **Repeat patient behaviour** — compute per-patient appointment count and prior no-show rate; plot relationship between past no-show history and current appointment outcome.
10. **Correlation heatmap** — numeric columns (age, lead_days, binary flags) vs noshow_flag; seaborn heatmap.

**Output files:**
- `output/PROJECT_XX/plots/09_noshow_by_gender.png`
- `output/PROJECT_XX/plots/10_noshow_by_age_group.png`
- `output/PROJECT_XX/plots/11_noshow_by_lead_days.png`
- `output/PROJECT_XX/plots/12_noshow_by_sms.png`
- `output/PROJECT_XX/plots/13_noshow_by_conditions.png`
- `output/PROJECT_XX/plots/14_noshow_by_weekday.png`
- `output/PROJECT_XX/plots/15_noshow_by_neighbourhood.png`
- `output/PROJECT_XX/plots/16_noshow_by_month.png`
- `output/PROJECT_XX/plots/17_repeat_patient_noshow.png`
- `output/PROJECT_XX/plots/18_correlation_heatmap.png`

---

### Phase 3 — Multivariate & Deep-Dive Analyses

**Goal:** Answer the harder interview-style questions about the data.

**Steps:**
1. **SMS paradox deep-dive** — cross-tabulate SMS × lead_days × no-show to explain why SMS recipients show *higher* no-show rates (they are more likely given to high-lead-time appointments).
2. **Age × Condition interactions** — pivot table of no-show rate by age group × hypertension; are older hypertensive patients more reliable?
3. **Neighbourhood inequality** — compute Gini coefficient of no-show rate across neighbourhoods; identify top-3 highest and lowest no-show-rate neighbourhoods.
4. **Same-day appointments** — isolate lead_days=0 subset; profile who books same-day (age, conditions, no-show rate).
5. **Scholarship (welfare) analysis** — compare no-show rates for Bolsa Família recipients vs non-recipients, stratified by neighbourhood poverty proxy (appointment volume as proxy).
6. **Patient-level vs appointment-level analysis** — aggregate to patient level; plot distribution of number of appointments per patient; identify frequent fliers.
7. **Time-series anomaly** — are there specific weeks with unusually high no-shows? (e.g. public holidays, extreme weather).

**Output files:**
- `output/PROJECT_XX/plots/19_sms_paradox.png`
- `output/PROJECT_XX/plots/20_age_condition_heatmap.png`
- `output/PROJECT_XX/plots/21_neighbourhood_inequality.png`
- `output/PROJECT_XX/plots/22_same_day_profile.png`
- `output/PROJECT_XX/plots/23_scholarship_analysis.png`
- `output/PROJECT_XX/plots/24_patient_appointment_counts.png`
- `output/PROJECT_XX/plots/25_weekly_noshow_timeseries.png`
- `output/PROJECT_XX/summary_stats.csv`

---

### Phase 4 — HTML Report

**Goal:** Compile all findings into a single self-contained HTML report.

**Steps:**
1. Use `jinja2` (or `pandas` + inline HTML) to generate an HTML report that:
   - Summarises the dataset (shape, cleaning decisions)
   - Embeds all plots as base64 PNG images (no external dependencies)
   - Includes an executive summary section with 5–8 key findings in plain language
   - Includes a "Hard Interview Questions" appendix with Q&A pairs covering:
     - Why does SMS_received correlate positively with no-shows?
     - What is the effect of lead time on attendance?
     - Which patient segments are highest risk?
     - How would you build a no-show prediction model from this data?
     - What are the ethical considerations of using neighbourhood or scholarship status?
     - What are the limitations of this dataset?
2. Save as `output/PROJECT_XX/report.html`.

**Output files:**
- `output/PROJECT_XX/report.html`

---

## 4. Open Questions / Assumptions

- **Assumption:** `ScheduledDay` timestamp represents the exact moment the appointment was booked; timezone stripped for lead-time calculation.
- **Assumption:** `Handcap` values 2, 3, 4 (n=199) are treated as "disabled" (=1) for binary analyses; the multi-level nature is noted but not deeply analysed given tiny sample sizes.
- **Assumption:** Age=0 is valid (infants/neonates) and is retained.
- **Open question:** Are `PatientId` values stable across appointments? (float64 type is unusual — may be a precision artefact from the source system.) This is noted but not corrected.
- **Open question:** The dataset covers only one Brazilian city (Vitória, Espírito Santo). Generalisability to other contexts is limited.

---

## 5. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Negative age (-1) | Removed; saved to dirty.csv with reason "negative age" |
| Ages > 115 (7 rows) | Removed; likely data entry errors |
| Appointments before scheduled date (5 rows) | Removed; lead_days < 0 is impossible |
| SMS selection bias misleading narrative | Explicitly analysed in Phase 3 SMS paradox section |
| Neighbourhood encoding (81 categories) | Used for visualisation only; no one-hot encoding required for EDA |
| Class imbalance (80/20) | Noted prominently; not a concern for pure EDA but flagged for any future modelling |
| `ScheduledDay` timezone | Stripped before lead-time calculation to avoid off-by-one errors |

---

## 6. Technical Spec Notes (for `/spec`)

The spec should define these scripts in `src/`:

| Script | Phase | Purpose |
|---|---|---|
| `phase0_etl.py` | 0 | Load, clean, engineer features, save dirty.csv + clean.csv |
| `phase1_univariate.py` | 1 | Generate plots 01–08 |
| `phase2_bivariate.py` | 2 | Generate plots 09–18 + summary_stats.csv |
| `phase3_multivariate.py` | 3 | Generate plots 19–25 |
| `phase4_report.py` | 4 | Compile HTML report with embedded plots |

All scripts read from `output/PROJECT_XX/clean.csv` (except phase0 which reads raw data).
All plots use `matplotlib`/`seaborn` with a consistent style (e.g. `seaborn-v0_8-whitegrid`).
Report uses `jinja2` with base64-encoded plot embeds.
