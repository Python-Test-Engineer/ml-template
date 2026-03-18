# Insight Report: 22_same_day_profile.jpg

![image](../plots/22_same_day_profile.jpg)

**Chart type:** Two-panel figure — left: overlaid normalised histograms; right: grouped bar chart
**Variables displayed:** Left: age distribution density for same-day (n=38,562) vs advance booking (n=71,959). Right: rate comparison across No-Show Rate, Scholarship, Hypertension, Diabetes, SMS Received
**Generated:** 2026-03-18

---

## Key Observation

Same-day appointments represent a fundamentally different population than advance bookings. Left panel: same-day patients have a much larger pediatric spike (0-5 years), more evenly distributed middle ages, and fewer elderly patients — advance bookings skew strongly toward ages 50-65. Right panel: same-day no-show rate is ~5% vs ~29% for advance bookings (a 6x difference). Same-day patients have lower Scholarship rates, lower Hypertension/Diabetes prevalence, and virtually zero SMS receipt — confirming they are a younger, healthier, non-reminder population.

## Business / Scientific Implication

Same-day and advance-booking appointments are effectively two separate healthcare delivery systems operating within the same infrastructure. Same-day functions as urgent/walk-in care (younger, acute conditions, near-zero no-shows), while advance booking serves chronic disease management (older, hypertensive/diabetic, high no-show risk). This duality means that aggregate statistics are misleading — the overall 20.2% no-show rate is actually a weighted average of ~5% (same-day) and ~29% (advance). All intervention strategies, predictive models, and overbooking algorithms should be built separately for these two populations, not on combined data.

## Deeper Analysis

The most striking finding is the SMS column: same-day patients receive essentially 0% SMS reminders while advance patients receive ~50%. This confirms that SMS is sent based on lead time, not risk — a selection policy that explains the entire SMS paradox. The Scholarship difference (same-day ~11% vs advance ~9.5%) is relatively small, suggesting welfare recipients use both pathways roughly proportionally. The Hypertension gap (same-day ~9% vs advance ~21%) is the most dramatic demographic difference — advance bookings have double the hypertension prevalence, reflecting the chronic disease management pattern. The pediatric spike in same-day appointments (left panel) suggests parents bring sick children as urgent visits rather than scheduling ahead — a rational response to unpredictable childhood illness.

## Confidence Assessment

**Confidence:** High
**Rationale:** Both subgroups have very large sample sizes (38K and 72K). The demographic and behavioural differences are consistent and clinically interpretable.

## Suggested Next Steps

1. Build separate predictive models for same-day vs advance bookings — the same-day model may be unnecessary (5% base rate is already very low), focusing resources on the advance-booking model where the 29% rate offers the most room for improvement
2. Investigate what drives the ~5% same-day no-show rate — are these patients who were seen by triage but left before the consultation?
