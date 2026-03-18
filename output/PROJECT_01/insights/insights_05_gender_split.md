# Insight Report: 05_gender_split.jpg

![image](../plots/05_gender_split.jpg)

**Chart type:** Vertical bar chart
**Variables displayed:** Gender (Female, Male) on x-axis, appointment count on y-axis, with count and percentage annotations
**Generated:** 2026-03-18

---

## Key Observation

Females account for 65.0% of appointments (71,836) versus 35.0% for males (38,685) — a nearly 2:1 ratio. This substantial gender skew means the dataset and any derived models are predominantly reflecting female healthcare-seeking behaviour. Brazil's population is approximately 51% female, so the 65% appointment share represents a significant over-representation.

## Business / Scientific Implication

The 2:1 female-to-male appointment ratio reflects a well-documented global pattern: women utilise primary care services more frequently due to reproductive healthcare, greater health-seeking behaviour, and caregiving roles (bringing children to appointments). For no-show prediction, this imbalance means a model optimised on aggregate data will disproportionately reflect female attendance patterns. Male patients — who are the minority but may have different no-show drivers (e.g., employment constraints, cultural attitudes) — risk being underserved by a one-size-fits-all intervention.

## Deeper Analysis

The 65/35 split is more extreme than Brazil's population gender ratio (~51/49), indicating that the gap is driven by utilisation differences, not demographics. Part of this is explained by the pediatric spike seen in the age distribution — mothers scheduling children's appointments count as female-initiated visits. The magnitude of this skew also means that any gender-specific no-show rate differences will contribute unevenly to the overall rate: even if males had a substantially higher no-show rate, their smaller volume (35%) limits their impact on the aggregate. This is a classic Simpson's paradox setup where subgroup-level patterns may not be reflected in the overall rate.

## Confidence Assessment

**Confidence:** High
**Rationale:** Simple count data from the full dataset; gender coding is binary and complete with no missing values.

## Suggested Next Steps

1. Examine whether the gender skew varies by age group — specifically, does the female over-representation concentrate in reproductive ages (20-40) and pediatric proxy visits (0-10)?
2. Develop gender-stratified no-show models to test whether predictive features differ between male and female patients
