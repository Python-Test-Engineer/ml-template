# Insight Report: 14_noshow_by_weekday.jpg

![image](../plots/14_noshow_by_weekday.jpg)

**Chart type:** Vertical bar chart with overall reference line
**Variables displayed:** Day of week (Mon–Sat) on x-axis, no-show rate (%) on y-axis, with overall rate line at 20.2%
**Generated:** 2026-03-18

---

## Key Observation

No-show rates show a modest but consistent end-of-week escalation: Saturday peaks at 23.1%, Friday at 21.2%, while midweek days cluster tightly at 19.3-20.1%. The spread between the best day (Thursday 19.3%) and worst (Saturday 23.1%) is 3.8 percentage points. The Monday-to-Thursday range is remarkably narrow (20.6%, 20.1%, 19.7%, 19.3%), showing a gentle midweek improvement before the weekend rise.

## Business / Scientific Implication

The Saturday spike (23.1%) is actionable despite Saturday's near-zero volume — the few Saturday appointments that do exist have the highest no-show risk. More practically, the Friday elevation (21.2%) affects ~19,000 appointments and represents a meaningful operational target. If Friday no-shows could be reduced to Thursday levels (19.3%), approximately 360 additional Friday appointments would be attended. Overbooking algorithms should apply slightly higher overbooking ratios on Fridays and Saturdays. Additionally, patient reminders for Friday/Saturday appointments should be sent earlier in the week to counter end-of-week forgetfulness.

## Deeper Analysis

The gentle midweek improvement (Mon 20.6% → Thu 19.3%) is subtle but consistent — it suggests patients who survive through the week without cancelling become incrementally more committed. The Friday reversal breaks this trend and likely reflects competing weekend plans, travel, or the "Friday effect" seen across many service industries. Saturday's 23.1% is notable but based on very few appointments (chart 07 showed near-zero Saturday volume), so this estimate has wide confidence intervals and should not be over-interpreted. The overall range of 3.8pp across days of week is relatively small compared to lead time (28.6pp range) or age group (10.5pp range), confirming that day of week is a real but secondary predictor.

## Confidence Assessment

**Confidence:** Medium
**Rationale:** The weekday estimates (Mon-Fri) are reliable with ~17K-26K appointments each. The Saturday rate (23.1%) is based on minimal volume and should be treated cautiously.

## Suggested Next Steps

1. Cross-tabulate day of week with lead time to test whether the Friday effect is driven by longer-lead bookings clustering on Fridays
2. Consider day-of-week as a feature in the predictive model but expect low marginal lift compared to lead time and prior history
