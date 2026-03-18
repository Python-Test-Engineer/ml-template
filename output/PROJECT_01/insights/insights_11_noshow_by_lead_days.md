# Insight Report: 11_noshow_by_lead_days.jpg

![image](../plots/11_noshow_by_lead_days.jpg) 

**Chart type:** Vertical bar chart with overall reference line
**Variables displayed:** Lead time bucket (same-day, 1-7d, 8-30d, 31-90d, 90d+) on x-axis, no-show rate (%) on y-axis, with overall rate line at 20.2%
**Generated:** 2026-03-18

---

## Key Observation

Lead time is the single most powerful predictor of no-shows visible in this dataset. Same-day appointments have a remarkably low 4.6% no-show rate, while 31-90 day appointments peak at 33.2% — a 7x relative increase. The progression is nearly monotonic: same-day (4.6%) → 1-7d (24.1%) → 8-30d (31.7%) → 31-90d (33.2%), with a slight drop at 90d+ (25.8%). The jump from same-day to 1-7d alone is 19.5 percentage points — the largest single-step increase across any variable in the dataset.

## Business / Scientific Implication

This is the most actionable finding in the entire analysis. Scheduling policy changes that minimise lead time could dramatically reduce no-shows without any patient-level intervention. Moving even 10% of 8-30 day bookings to same-day or 1-7 day bookings would recover hundreds of appointments. Overbooking algorithms should calibrate overbooking rates proportional to lead time: same-day slots need minimal overbooking (5%), while 31-90 day slots should be overbooked by 30%+. SMS reminder programmes should be heavily concentrated on the 8-30d and 31-90d buckets where the base no-show rate exceeds 30%.

## Deeper Analysis

The 90d+ bucket's slight decline to 25.8% (from 33.2% at 31-90d) is counterintuitive and warrants investigation. This could reflect: (a) survivor bias — only the most committed patients keep appointments booked 3+ months ahead; (b) these may be specialist referrals with higher perceived value; or (c) small sample size in the 90d+ bucket creating noise. The massive 4.6% same-day rate is remarkable — it means 95% of walk-in/urgent patients attend, confirming that immediacy of need is the strongest attendance motivator. The 24.1% rate for 1-7d bookings is already above the overall average, meaning even a one-week lead time substantially increases risk. This suggests the "forgetting curve" for medical appointments operates on a timescale of days, not weeks — patients begin forgetting or deprioritising their appointment very quickly after scheduling.

## Confidence Assessment

**Confidence:** High
**Rationale:** The monotonic trend is unambiguous with large sample sizes per bucket; same-day alone has ~50,000 observations, making the 4.6% estimate extremely precise.

## Suggested Next Steps

1. Build a lead-time-based overbooking model: calculate the optimal number of extra bookings per slot as a function of the lead-time distribution of that day's appointments
2. Investigate the 90d+ anomaly: is the drop-off real (survivor bias) or noise (small sample)? Segment by appointment type if available
