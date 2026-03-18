# Insight Report: 20_age_condition_heatmap.jpg

![image](../plots/20_age_condition_heatmap.jpg)

**Chart type:** Heatmap (2-column) with annotated percentages
**Variables displayed:** Age group (9 bins) on y-axis, Hypertension status (No/Yes) on x-axis, cell values = no-show rate (%), colour scale from yellow (low) to dark red (high)
**Generated:** 2026-03-18

---

## Key Observation

The interaction between age and hypertension reveals a dramatic outlier: **hypertensive adolescents (11-20) have a 35.0% no-show rate** — the highest cell in the entire matrix and nearly double the overall 20.2% rate. This is 10pp higher than non-hypertensive 11-20 year-olds (25.2%). In contrast, for ages 21-50, hypertensive patients actually have *lower* no-show rates than their non-hypertensive peers (by 2-3pp). The effect reverses again in the elderly (61+), where hypertensive patients have slightly higher rates.

## Business / Scientific Implication

The 11-20 hypertensive cell (35%) represents the single highest-risk identifiable subgroup in the entire dataset. While numerically small (hypertension in adolescents is rare), these patients are medically critical — adolescent hypertension often signals serious underlying conditions (renal disease, obesity-related metabolic syndrome) requiring consistent follow-up. A targeted intervention for this micro-segment (possibly involving parental engagement, school-based scheduling, or paediatric cardiology coordination) could address both the highest no-show risk and the highest clinical need simultaneously.

## Deeper Analysis

The age-dependent direction change of the hypertension effect is the most analytically interesting finding here. For young patients (0-20), hypertension *increases* no-show risk — possibly because hypertension in youth is often asymptomatic and diagnosed incidentally, reducing the patient's/parent's perceived urgency. For middle-aged patients (21-50), hypertension *decreases* risk — these patients are likely symptomatic, medicated, and engaged in active disease management. For the elderly (61+), the effect is nearly neutral (13.8% vs 15.6% for 61-70), suggesting that age-related reliability overwhelms the condition effect. The 0-10 hypertension cell (22.2%) represents children with hypertension — an extremely rare and serious condition, yet their parents still miss 1 in 5 appointments. The overall No Hypertension column shows the clean age gradient from chart 10, confirming age is the dominant driver.

## Confidence Assessment

**Confidence:** Medium
**Rationale:** The overall pattern is clear, but several cells (especially 11-20 Hypertension, 0-10 Hypertension, 81+ both) likely have small sample sizes, making individual cell estimates uncertain. The 35.0% outlier should be confirmed with a confidence interval.

## Suggested Next Steps

1. Calculate sample sizes and confidence intervals for each cell, particularly the 11-20 Hypertension cell, to assess whether the 35% rate is statistically distinct from the 25.2% non-hypertensive rate
2. Extend this interaction analysis to other conditions (Diabetes × Age, Scholarship × Age) to identify additional high-risk micro-segments
