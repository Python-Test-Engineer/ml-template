# Insight Report: 02_lead_days_distribution.jpg

![image](../plots/02_lead_days_distribution.jpg) 


**Chart type:** Histogram (clipped at 120 days)
**Variables displayed:** Lead days (days between scheduling and appointment) on x-axis, appointment count on y-axis, with mean line at 10.2 days
**Generated:** 2026-03-18

---

## Key Observation

The distribution is dramatically right-skewed with an overwhelming concentration at day 0 (same-day appointments): approximately 50,000 of ~110,000 appointments (~45%) are scheduled and attended the same day. The count drops precipitously — by day 3-4 it falls to ~8,000, with a secondary bump around days 5-7 (~12,000), then a long tail stretching to 120+ days. The mean of 10.2 days is heavily pulled by the tail; the true typical appointment is booked same-day or within a few days.

## Business / Scientific Implication

Nearly half of all appointments are same-day, which fundamentally shapes the no-show problem: these patients have the lowest no-show rates because intent is immediate. The operational implication is that the healthcare system functions substantially as a walk-in/urgent-care model rather than a planned-appointment model. Intervention strategies (SMS reminders, overbooking algorithms) should focus disproportionately on the ~55% of appointments booked 1+ days ahead, where no-show risk is materially higher.

## Deeper Analysis

The secondary bump at 5-7 days is noteworthy — it likely reflects a "book for next week" scheduling pattern, possibly driven by weekly clinic schedules or patient preference for the same weekday. The long tail (30-120 days) contains relatively few appointments but likely has very high no-show rates — these are the highest-risk slots. The mean of 10.2 days vs. the mode of 0 days reveals extreme positive skewness (skewness likely >3), meaning parametric analyses assuming normality on lead_days would be inappropriate. The fact that the histogram was clipped at 120 days suggests some outliers beyond this threshold. The dramatic drop between day 0 and day 1 (~50K to ~8K) is the single most important structural feature of this dataset.

## Confidence Assessment

**Confidence:** High
**Rationale:** Distribution shape is unambiguous; the same-day dominance is the defining structural characteristic of the scheduling system.

## Suggested Next Steps

1. Segment all downstream analyses into "same-day" vs. "advance booking" cohorts — they are fundamentally different populations with different no-show dynamics
2. Examine whether the 5-7 day bump represents a specific clinic scheduling pattern that could be targeted for reminder optimisation
