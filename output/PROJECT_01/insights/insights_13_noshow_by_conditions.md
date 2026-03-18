# Insight Report: 13_noshow_by_conditions.jpg

![image](../plots/13_noshow_by_conditions.jpg)

**Chart type:** 2×3 grid of paired bar charts with overall reference lines
**Variables displayed:** Six binary flags (Scholarship, Hypertension, Diabetes, Alcoholism, Disability, SMS Received) — each subplot compares no-show rate for flag=No vs flag=Yes
**Generated:** 2026-03-18

---

## Key Observation

The six condition flags split into three distinct groups by effect size: (1) **SMS Received** dominates with an 11pp gap (16.7% → 27.6%) but is confounded; (2) **Scholarship** shows a meaningful 3.9pp increase (19.8% → 23.7%); (3) **Hypertension, Diabetes, Alcoholism, and Disability** all show negligible or slightly *lower* no-show rates for affected patients (Hypertension: 20.9% → 17.3%, Diabetes: 20.4% → 18.0%, Alcoholism: 20.2% → 20.1%, Disability: 20.2% → 18.1%).

## Business / Scientific Implication

The pattern tells a clear story: patients with chronic medical conditions are actually *more* reliable attenders, not less. Hypertension patients are 3.6pp more likely to attend than non-hypertensive patients, and diabetes patients 2.4pp more likely. This makes clinical sense — these patients need ongoing medication management and monitoring, creating a strong incentive to attend. The only flag associated with *increased* no-shows is Scholarship (welfare recipients), which reflects socioeconomic barriers rather than health attitudes. This means intervention resources should target socioeconomic accessibility (transport, flexible scheduling) rather than health education for chronic disease patients.

## Deeper Analysis

The chronic-condition protective effect (Hypertension -3.6pp, Diabetes -2.4pp, Disability -2.1pp) is almost certainly confounded by age: these conditions are prevalent in older patients, who independently have lower no-show rates. A proper analysis would need to control for age to isolate the true condition effect. Alcoholism shows essentially zero effect (0.1pp) but has a very small sample (3% prevalence = ~3,300 appointments), so this null result has limited statistical power. The Scholarship effect (+3.9pp) is the most interesting from a policy perspective — it identifies a vulnerable population that could benefit from targeted support. The SMS panel (bottom-right) uses a different y-axis scale (0-30% vs 0-25%), which visually exaggerates its already-confounded effect — a potential misinterpretation risk for report readers.

## Confidence Assessment

**Confidence:** Medium
**Rationale:** The direction of effects is reliable, but magnitude estimates are confounded by age. The Scholarship effect is the most robust finding as it operates independently of the age-condition correlation.

## Suggested Next Steps

1. Run age-adjusted logistic regressions for each condition flag to isolate the true independent effect from the age confound
2. Deep-dive into the Scholarship subgroup: what are their lead-time distributions, neighbourhood patterns, and age profiles compared to non-Scholarship patients?
