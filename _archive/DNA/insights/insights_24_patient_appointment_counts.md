# Insight Report: 24_patient_appointment_counts.jpg

![image](../plots/24_patient_appointment_counts.jpg)

**Chart type:** Two-panel figure — left: histogram of appointments per patient; right: bar chart of no-show rate by visit frequency bucket
**Variables displayed:** Left: number of appointments (1-21+) vs number of patients. Right: frequency bucket (1 appt, 2-5, 6-10, 10+) vs no-show rate (%), with overall rate line at 20.2%
**Generated:** 2026-03-18

---

## Key Observation

The patient frequency distribution is extremely right-skewed: ~38,000 patients have only 1 appointment, ~14,000 have 2, and the count drops steeply — by 5 appointments, fewer than 1,000 patients remain. The no-show rate by frequency shows a non-monotonic pattern: single-visit patients have 18.8%, rising to 22.4% for 6-10 visits, then dropping sharply to 16.5% for 10+ visits. The most frequent visitors (10+ appointments) are the most reliable attenders.

## Business / Scientific Implication

The 10+ visit group's low 16.5% no-show rate identifies a "loyal patient" segment — these are chronic disease patients with established healthcare routines who attend more reliably than average. Conversely, the 6-10 visit mid-frequency group (22.4%) represents patients who engage with the system regularly but inconsistently — they are above average risk and may be the most responsive to intervention, as they clearly intend to use healthcare but face recurring attendance barriers. The massive single-visit population (~38,000 patients) may include one-time visitors, new patients, or patients who no-showed and never returned — understanding this group's composition is critical.

## Deeper Analysis

The non-monotonic pattern (18.8% → 21.0% → 22.4% → 16.5%) is analytically rich. The initial rise from 1-appointment to 6-10 appointments seems counterintuitive — shouldn't more engaged patients attend better? The explanation is likely survivor bias in the 1-visit group: some of these patients attended their only appointment (0% personal no-show rate) while others no-showed and were never seen again. The 1-visit group is a mixture of perfectly reliable one-time visitors and total dropouts, averaging to 18.8%. The 6-10 group has enough history to reveal habitual patterns — these are patients with moderate engagement who sometimes attend and sometimes don't. The 10+ group has self-selected into consistent healthcare engagement, and their 16.5% rate represents the floor achievable through patient loyalty. The left panel's steep drop-off (38K at 1 visit, 14K at 2, 5K at 3) means the median patient has only 1-2 appointments — most "patients" in this dataset are essentially strangers to the system.

## Confidence Assessment

**Confidence:** Medium
**Rationale:** The frequency-rate pattern is clear but the interpretation of the 1-visit group is ambiguous without knowing whether these are new patients, one-time needs, or dropouts. The 10+ group's low rate is robust but based on a small number of patients with many appointments each.

## Suggested Next Steps

1. Classify single-visit patients into "attended once" vs "no-showed and never returned" to understand whether the 1-visit group's 18.8% masks a dropout problem
2. Use visit frequency as a feature in the predictive model, but be cautious of data leakage — frequency should be computed from prior visits only, not future ones
