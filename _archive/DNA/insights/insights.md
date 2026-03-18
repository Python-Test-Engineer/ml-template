# Data Intelligence Insights Report

**Project:** PROJECT_01
**Images analysed:** 25
**Scripts analysed:** 6
**Generated:** 2026-03-18

---

## Executive Summary

This analysis of ~110,000 medical appointments in Vitória, Brazil reveals that the 20.2% overall no-show rate masks two fundamentally different populations: same-day walk-ins (45% of volume, 5% no-show) and advance bookings (55% of volume, 29% no-show). Appointment lead time and prior patient no-show history are by far the strongest predictors — together they explain more variance than all demographic and clinical features combined. The SMS reminder system works (reducing no-shows by 6-8pp within lead-time strata) but appears counterproductive in raw data due to Simpson's paradox. Socioeconomic barriers (Scholarship/Bolsa Família recipients) drive a consistent 3.5pp no-show premium that is not explained by geography. The highest-risk micro-segment — hypertensive adolescents — reaches a 35% no-show rate, demanding targeted intervention.

---

## Key Insights

### Insight 1 — Two Healthcare Systems in One: The Same-Day Divide

**Source charts:** 02_lead_days_distribution, 11_noshow_by_lead_days, 22_same_day_profile

**Observation:** 45% of all appointments are same-day (lead_days=0) with a 4.6% no-show rate, while the remaining 55% (advance bookings) have a 29% no-show rate. These two populations differ demographically: same-day patients skew younger and healthier (pediatric acute visits), while advance bookings serve older chronic disease patients with higher hypertension/diabetes prevalence. The overall 20.2% rate is a misleading weighted average of these two distinct systems.

**Implication:** All predictive models, overbooking algorithms, and intervention strategies should be built separately for same-day vs advance booking populations. Targeting same-day patients with reminders is wasteful (5% base rate); all resources should focus on the advance-booking cohort where a 29% base rate offers maximum room for improvement.

**Confidence:** High — based on ~50K same-day and ~60K advance appointments with unambiguous demographic differences.

---

### Insight 2 — Prior Behaviour is the Strongest Crystal Ball

**Source charts:** 17_repeat_patient_noshow, 24_patient_appointment_counts

**Observation:** Patients with 0% prior no-show history miss 17.5% of appointments; those with 51-75% prior history miss 39.7% — a 22.2pp spread, the widest of any single feature. Additionally, highly frequent visitors (10+ appointments) have the lowest no-show rate (16.5%), while mid-frequency patients (6-10 visits) have the highest (22.4%). Past behaviour dominates all demographic predictors.

**Implication:** A patient's prior no-show rate should be the centrepiece feature of any predictive model and the primary basis for intervention tiering. A simple rule — "flag patients with >25% prior no-show rate for enhanced outreach" — would capture most of the at-risk population with minimal model complexity.

**Confidence:** High — the analysis correctly uses only chronologically prior data to avoid leakage, and the monotonic trend is robust.

---

### Insight 3 — The SMS Paradox: When Confounders Reverse the Truth

**Source charts:** 12_noshow_by_sms, 19_sms_paradox, 04_binary_flags_prevalence, 18_correlation_heatmap

**Observation:** Raw data shows SMS recipients have an 11pp *higher* no-show rate (27.6% vs 16.7%). However, when stratified by lead time, SMS *reduces* no-shows by 6-8pp within every stratum where both groups exist. The paradox arises because SMS was selectively sent to long-lead-time appointments (r=0.40 between SMS_received and lead_days), which have inherently higher no-show risk. Only 32% of appointments received SMS.

**Implication:** This is a textbook Simpson's paradox with direct operational consequences. (1) SMS reminders should be expanded to all non-same-day appointments; (2) the estimated 6pp within-stratum effect applied to ~60K advance bookings would recover ~3,600 appointments; (3) any ML model must handle the SMS/lead_days confound explicitly or risk learning a spurious positive association.

**Confidence:** High — the within-stratum reversal is consistent across 3 lead-time buckets with large samples.

---

### Insight 4 — Age as a Lifecycle Predictor with a Dangerous Interaction

**Source charts:** 01_age_distribution, 10_noshow_by_age_group, 20_age_condition_heatmap

**Observation:** No-show rates follow a clear lifecycle gradient: adolescents/young adults (11-20: 25.2%, 21-30: 24.6%) are highest risk; elderly patients (61-70: 14.7%) are most reliable — a 10.5pp spread. The age × hypertension interaction reveals an extreme outlier: hypertensive adolescents hit 35.0%, the highest rate of any identifiable subgroup. The bimodal age distribution (pediatric spike + chronic-disease peak) confirms two distinct patient populations using the system.

**Implication:** Age-specific intervention design is essential: digital nudges for 11-30, transport/mobility support for 81+, and minimal intervention for the reliable 50-70 cohort. The hypertensive adolescent micro-segment (35% no-show) demands targeted outreach — these are medically critical patients whose conditions require consistent monitoring.

**Confidence:** High for the main age effect; Medium for the hypertensive adolescent cell (small sample size needs confidence interval verification).

---

### Insight 5 — Socioeconomic Barriers Trump Geography

**Source charts:** 13_noshow_by_conditions, 23_scholarship_analysis, 15_noshow_by_neighbourhood, 21_neighbourhood_inequality

**Observation:** Bolsa Família (Scholarship) recipients have a consistent ~3.5pp no-show premium (23.5% vs 19.8%) that persists identically across low-volume, medium-volume, and high-volume neighbourhoods. Meanwhile, patients with chronic conditions (Hypertension, Diabetes) actually have *lower* no-show rates than healthy patients, by 2-4pp. Neighbourhood-level rates vary by 11pp across the top 30 (Itararé ~27%, Santa Martha ~16%), with a Gini coefficient of 0.138.

**Implication:** The Scholarship effect is socioeconomic, not geographic — it does not shrink in well-connected central areas. Interventions should address personal barriers (lost wages, childcare, transport cost) rather than simply placing clinics closer. The protective effect of chronic conditions means "sicker patients attend better" — a finding that challenges the intuition that clinical complexity increases no-shows.

**Confidence:** High — the Scholarship effect's consistency across 3 independent neighbourhood terciles is strong evidence of a genuine independent effect.

---

### Insight 6 — Temporal Stability: A Persistent Structural Problem

**Source charts:** 08_appointments_over_time, 16_noshow_by_month, 25_weekly_noshow_timeseries, 07_appointments_by_weekday, 14_noshow_by_weekday

**Observation:** The system operates at a stable capacity ceiling of ~4,500 appointments/day with a regular weekly sawtooth pattern. Monthly no-show variation is only 2.3pp (April 19.6%, May 20.8%, June 18.5%). Weekly fluctuations are within ±1.5pp of the mean. Day-of-week effects are modest: Friday/Saturday are worst (21-23%), Thursday best (19.3%).

**Implication:** The no-show problem is structural and persistent, not episodic. There are no "crisis weeks" or seasonal shocks — the 20% rate is baked into the system's operating characteristics. This stability is actually good news for modelling: a prediction system trained on any month should generalise well to others. Overbooking algorithms can use a steady-state assumption with minor day-of-week adjustments.

**Confidence:** High for stability within this window; limited confidence for extrapolation beyond April–June due to dataset scope.

---

### Insight 7 — The Correlation Paradox: Weak Linear Signals, Strong Non-Linear Effects

**Source charts:** 18_correlation_heatmap, 09_noshow_by_gender

**Observation:** Pearson correlations with noshow_flag are universally weak: lead_days (r=0.19) and SMS_received (r=0.13) are the only features above |0.06|. Age correlates at just r=-0.06 despite a 10.5pp spread across age groups. Gender is a complete non-predictor (20.3% vs 20.0%). Significant multicollinearity exists: Age↔Hypertension (r=0.50), Hypertension↔Diabetes (r=0.43), lead_days↔SMS (r=0.40).

**Implication:** Linear models (logistic regression) will underperform — the no-show problem is fundamentally non-linear with important interaction effects (age × condition, SMS × lead_time). Tree-based models (XGBoost, Random Forest) are strongly preferred. Feature engineering (prior_noshow_rate, same-day flag) will provide more lift than adding raw demographic features. The multicollinearity clusters (Age/Hypertension/Diabetes and lead_days/SMS) must be handled through feature selection or regularisation.

**Confidence:** High — Pearson values are exact; the mismatch between linear correlation and actual effect sizes confirms non-linearity.

---

## Patterns Across Analyses

1. **The lead-time thread runs through everything.** It directly predicts no-shows (chart 11), confounds the SMS effect (chart 12/19), drives the same-day population split (chart 22), and correlates with SMS receipt (chart 18). Lead time is the single most important variable in the entire analysis — it touches every other finding.

2. **Age and chronic conditions form a tightly coupled system.** Age correlates with Hypertension (r=0.50) and Diabetes (r=0.43), both of which appear protective for no-shows — but this is largely because they serve as proxies for the elderly cohort that attends reliably. The true independent effects are weaker than raw rates suggest.

3. **Confounding is pervasive.** SMS ↔ lead_time, age ↔ chronic conditions, Scholarship ↔ age ↔ neighbourhood — nearly every bivariate relationship in this dataset has at least one confounding pathway. Naive single-variable analysis would produce misleading conclusions in at least 3 of 25 charts. The SMS paradox (chart 12 vs 19) is the most dramatic example but not the only one.

4. **Volume concentration creates intervention leverage.** The top 5 neighbourhoods hold ~25% of all appointments. Combined with the same-day/advance split (chart 22), a targeted intervention in just 5 neighbourhoods for advance-booking patients only could reach ~15% of total volume with ~30% of total no-shows.

5. **The dataset has two hidden populations that should never be merged.** Same-day (young, acute, 5% no-show, no SMS) vs advance (older, chronic, 29% no-show, SMS sent). Every aggregate statistic in this report is a misleading blend of these two groups. This is the most important structural insight for anyone building on this analysis.

---

## Risks & Caveats

| Risk | Affected Insights | Mitigation |
|------|-------------------|------------|
| **Simpson's paradox** — confounded variables produce misleading aggregate effects | Insights 3 (SMS), 4 (age × conditions), 5 (Scholarship) | Always stratify by lead time before interpreting any other variable |
| **Small sample sizes in tails** — extreme neighbourhood rates, rare conditions, elderly subgroups | Insights 4 (hypertensive adolescents), 6 (neighbourhood inequality) | Filter to ≥100 observations per cell; report confidence intervals |
| **Single-city, 3-month snapshot** — no seasonal, geographic, or temporal generalisability | All insights | Validate on a second city or time period before deploying interventions |
| **No appointment type data** — specialty, urgency, provider identity unavailable | Insights 1, 2, 6 | Collect appointment type in future data; it is likely a strong predictor |
| **Observational data, not experimental** — causal claims about SMS, scheduling are tentative | Insight 3 (SMS effectiveness) | Design A/B tests stratified by lead time to confirm causal effects |
| **Data truncation in June** — potential boundary effects on final weeks | Insight 6 (June rate decline) | Verify whether the dataset ends mid-June by checking the latest appointment date |

---

## Recommended Next Steps

### High Priority
1. **Build a segmented prediction model** — Separate models for same-day vs advance bookings, using prior_noshow_rate, lead_days, age, and neighbourhood as primary features. Use XGBoost with AUROC evaluation. Estimated lift: 5-10pp improvement in targeting efficiency over uniform overbooking.
2. **Expand SMS to all advance bookings** — Currently only 32% receive SMS; the within-stratum effect of 6-8pp reduction justifies universal deployment for any appointment with lead_days ≥ 1. Estimated recovery: ~3,600 appointments per period.
3. **Implement lead-time-proportional overbooking** — Same-day: no overbooking (5% base). 1-7d: 5% overbooking. 8-30d: 15%. 31-90d: 20%. This matches the empirical no-show rate curve from chart 11.

### Medium Priority
4. **Pilot tiered outreach for high-risk patients** — Patients with >25% prior no-show rate get phone calls (not just SMS); patients with >50% get community health worker outreach or same-day rebooking preference.
5. **Investigate the Scholarship population** — Cross-tabulate Bolsa Família recipients with age, lead time, and specific neighbourhoods to design a targeted support programme (transport vouchers, flexible scheduling, childcare).
6. **Audit neighbourhood-level data quality** — Remove neighbourhoods with <50 appointments from rate comparisons; recalculate the inequality metrics.

### Exploratory / Speculative
7. **Join external socioeconomic data** — Overlay census income, transit coverage, and facility location data to test whether geographic deprivation indices predict neighbourhood-level no-show rates.
8. **Test appointment-type effects** — If specialty or provider data can be obtained, add to the model — appointment type is likely a top-5 predictor based on healthcare literature.
9. **Temporal expansion** — Acquire 12+ months of data to decompose seasonal patterns and test whether the system is on a long-term trend.

---

## Appendix — Individual Chart Insights

| # | Chart | Key Observation | Confidence |
|---|-------|-----------------|------------|
| 1 | 01_age_distribution | Bimodal: pediatric spike (0-5, ~12K) + chronic-disease peak (50-60); median 37 | High |
| 2 | 02_lead_days_distribution | 45% same-day; extreme right skew; mean 10.2d masks mode of 0 | High |
| 3 | 03_noshow_overall | 20.2% overall (22,314 missed); 80/20 class imbalance | High |
| 4 | 04_binary_flags_prevalence | SMS sent to 32%; Hypertension 19.7%; low-prevalence flags need caution | High |
| 5 | 05_gender_split | 65/35 F/M; 2:1 ratio exceeds population demographics | High |
| 6 | 06_top20_neighbourhoods | Jardim Camburi dominates (~7,700); top 3 = 16% of volume | High |
| 7 | 07_appointments_by_weekday | Tue-Wed peak (47% of weekly volume); Thursday dip of 33% | High |
| 8 | 08_appointments_over_time | Stable weekly sawtooth at 3,800-4,700/day; capacity ceiling | High |
| 9 | 09_noshow_by_gender | Gender is a non-predictor: 20.3% F vs 20.0% M (0.3pp) | High |
| 10 | 10_noshow_by_age_group | Clear age gradient: 11-20 peak 25.2%, 61-70 trough 14.7% | High |
| 11 | 11_noshow_by_lead_days | #1 modifiable predictor: 4.6% same-day → 33.2% at 31-90d | High |
| 12 | 12_noshow_by_sms | Simpson's paradox: SMS recipients 27.6% vs 16.7% — confounded | High (obs) / Low (causal) |
| 13 | 13_noshow_by_conditions | Chronic conditions protective (-2-4pp); Scholarship +3.9pp | Medium |
| 14 | 14_noshow_by_weekday | End-of-week rise: Sat 23.1%, Fri 21.2% vs Thu 19.3% | Medium |
| 15 | 15_noshow_by_neighbourhood | 11pp spread across top 30; Itararé worst (~27%) | High |
| 16 | 16_noshow_by_month | Month is a non-predictor: only 2.3pp range across Apr-Jun | Medium |
| 17 | 17_repeat_patient_noshow | #1 predictor overall: 0% history → 17.5%, 51-75% → 39.7% | High |
| 18 | 18_correlation_heatmap | Weak linear signals (max r=0.19); multicollinearity in Age/Hyp/Dia | High |
| 19 | 19_sms_paradox | Paradox resolved: SMS reduces no-shows 6-8pp within strata | High |
| 20 | 20_age_condition_heatmap | Hypertensive adolescents 35% — highest micro-segment rate | Medium |
| 21 | 21_neighbourhood_inequality | Gini 0.138; extreme outliers from tiny samples (100% Trindade) | Medium |
| 22 | 22_same_day_profile | Two populations: same-day (young, 5%) vs advance (older, 29%) | High |
| 23 | 23_scholarship_analysis | Scholarship premium ~3.5pp persists across all neighbourhood terciles | High |
| 24 | 24_patient_appointment_counts | Most patients 1-2 visits; 10+ visits = most reliable (16.5%) | Medium |
| 25 | 25_weekly_noshow_timeseries | Inverted-V: peaks ~21.4% mid-May, declines to ~18.1% mid-June | Medium |

---

## Appendix — Input Inventory

### Images
| File | Description inferred from content |
|------|------------------------------------|
| 01_age_distribution.jpg | Histogram + KDE of patient age with median line |
| 02_lead_days_distribution.jpg | Histogram of scheduling lead time, clipped at 120d |
| 03_noshow_overall.jpg | Horizontal bar chart: attended vs no-show counts |
| 04_binary_flags_prevalence.jpg | Bar chart of 6 binary flag prevalence rates |
| 05_gender_split.jpg | Bar chart of appointment volume by gender |
| 06_top20_neighbourhoods.jpg | Horizontal bar chart of top 20 neighbourhoods by volume |
| 07_appointments_by_weekday.jpg | Bar chart of daily appointment volume Mon-Sat |
| 08_appointments_over_time.jpg | Daily time series of appointment volume Apr-Jun 2016 |
| 09_noshow_by_gender.jpg | No-show rate by gender with overall reference line |
| 10_noshow_by_age_group.jpg | No-show rate across 9 age groups |
| 11_noshow_by_lead_days.jpg | No-show rate across 5 lead-time buckets |
| 12_noshow_by_sms.jpg | No-show rate by SMS status with confound annotation |
| 13_noshow_by_conditions.jpg | 2×3 grid: no-show rate by 6 binary condition flags |
| 14_noshow_by_weekday.jpg | No-show rate by day of week |
| 15_noshow_by_neighbourhood.jpg | No-show rate for top 30 neighbourhoods, colour-coded |
| 16_noshow_by_month.jpg | No-show rate by month (Apr, May, Jun) |
| 17_repeat_patient_noshow.jpg | No-show rate by prior no-show history bucket |
| 18_correlation_heatmap.jpg | 9×9 Pearson correlation matrix of features vs target |
| 19_sms_paradox.jpg | Grouped bar: no-show by lead time × SMS status |
| 20_age_condition_heatmap.jpg | Heatmap: no-show rate by age group × hypertension |
| 21_neighbourhood_inequality.jpg | All 81 neighbourhoods ranked with Gini coefficient |
| 22_same_day_profile.jpg | Dual-panel: age distributions + rate comparison for same-day vs advance |
| 23_scholarship_analysis.jpg | Grouped bar: Scholarship effect by neighbourhood volume tercile |
| 24_patient_appointment_counts.jpg | Dual-panel: visit frequency histogram + no-show rate by frequency |
| 25_weekly_noshow_timeseries.jpg | Dual-axis: weekly no-show rate + volume time series |

### Python Scripts
| File | Purpose |
|------|---------|
| phase0_etl.py | Load raw CSV, parse dates, compute lead_days, remove dirty rows, engineer features, save clean.csv |
| phase1_univariate.py | Generate plots 01-08: distributions of individual variables |
| phase2_bivariate.py | Generate plots 09-18: no-show rate by each feature, correlation heatmap, summary stats |
| phase3_multivariate.py | Generate plots 19-25: SMS paradox, age×condition, neighbourhood inequality, deep-dives |
| phase4_report.py | Compile all outputs into self-contained HTML report with base64-embedded plots |
| dashboard.py | Shiny for Python interactive dashboard with KPIs, gallery, explorer, and statistics tabs |
