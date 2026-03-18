# Insight Report: 08_appointments_over_time.jpg

![image](../plots/08_appointments_over_time.jpg) 


**Chart type:** Line chart (time series)
**Variables displayed:** Date (Apr–Jun 2016) on x-axis, appointments per day on y-axis
**Generated:** 2026-03-18

---

## Key Observation

The time series reveals a strikingly regular weekly sawtooth pattern: weekday volume oscillates between 3,800–4,700 appointments per day, dropping to near-zero on weekends. Peak weekday volumes reach ~4,600 appointments, while the typical weekday range is 3,800–4,500. The pattern is remarkably consistent over the 8-week period shown, with no clear upward or downward trend — the healthcare system appears to be operating at a stable capacity ceiling.

## Business / Scientific Implication

The flat, repeating pattern indicates the system is running at or near maximum capacity — daily volume hits a ceiling around 4,500-4,700 and never exceeds it, suggesting supply-constrained scheduling. This has a critical implication for no-show interventions: if every no-show slot could be filled (overbooking), the system could serve approximately 900 additional patients per day (20% of ~4,500). The absence of any trend over 8 weeks means seasonal adjustments are not needed for this time window, but the dataset only covers April–June, leaving autumn/winter patterns unknown.

## Deeper Analysis

The weekend drops to zero confirm the 5-day operating week seen in the weekday chart. Within each week, there is a subtle mid-week peak visible — volumes tend to be highest on Tuesday-Wednesday (matching chart 07). The sharp drops on some weekdays (e.g., early May around May-10 showing a dip to ~4,000) may coincide with Brazilian public holidays (May 1 is Labour Day). The most notable feature is the absence of any "ramp-up" or "wind-down" at the series boundaries — the system was at full capacity throughout the entire observation window. There are no visible anomalous days where volume spikes above 5,000, reinforcing the capacity ceiling hypothesis.

## Confidence Assessment

**Confidence:** High
**Rationale:** Daily counts are exact; the weekly periodicity is unmistakable and consistent across all 8 weeks shown.

## Suggested Next Steps

1. Overlay daily no-show rates on this time series to test whether high-volume days also have higher no-show rates (capacity pressure hypothesis)
2. Investigate the specific low-volume weekdays to confirm whether they coincide with Brazilian public holidays (May 1, Corpus Christi)
