# Insight Report: 25_weekly_noshow_timeseries.jpg

![image](../plots/25_weekly_noshow_timeseries.jpg)

**Chart type:** Dual-axis line+bar chart (time series)
**Variables displayed:** Week (Apr–Jun 2016) on x-axis, no-show rate (%) on left y-axis (red line), weekly appointment volume on right y-axis (blue bars)
**Generated:** 2026-03-18

---

## Key Observation

The no-show rate shows a clear inverted-V pattern over the 8-week window: rising from ~19.6% in late April to a peak of ~21.4% around May 15-22, then declining steadily to ~18.1% by mid-June. Weekly volume is relatively stable at ~18,000-21,000 appointments per week, with a dip in late May (~May 22 week) and the final June-15 week. The rate and volume appear to move somewhat independently — the highest no-show rate (~21.4%) coincides with peak volume weeks, while the June decline in rate occurs alongside sustained volume.

## Business / Scientific Implication

The mid-May peak aligns with a period that includes several Brazilian public holidays and cultural events (Labour Day recovery period, potential bridge holidays). The steady June decline — dropping from ~21.4% to ~18.1% (a 3.3pp improvement) — could reflect seasonal effects (cooler weather improving attendance), calendar effects (fewer competing events), or a data boundary artefact (June appointments with very long lead times not yet occurred). If the decline is genuine, it suggests that no-show rates have a seasonal component that could inform dynamic overbooking algorithms: overbook more aggressively in May, less in June.

## Deeper Analysis

The y-axis range on the no-show rate (18.0-21.7%) is relatively narrow, magnifying visual variation — the actual week-to-week fluctuation is only ~3pp, which is modest for weekly aggregates of ~20,000 appointments. The volume dip around May 22 may coincide with a holiday week, and the slight rate increase during that same week suggests that patients who keep holiday-week appointments are offset by a higher proportion of no-shows among those who scheduled before knowing about the holiday. The final week (Jun-15) shows the lowest rate (~18.1%) and reduced volume — this is likely a truncated week at the end of the dataset, and the lower rate may partially reflect the lead-time composition effect (truncated data over-represents recently scheduled, short-lead appointments which have inherently lower no-show rates). The absence of any anomaly markers (no weeks exceeded mean + 1.5 SD) confirms that week-to-week variation is within normal bounds — there are no "shock" events in this period.

## Confidence Assessment

**Confidence:** Medium
**Rationale:** The overall trend is visible but the narrow range (3pp) and short window (8 weeks) make it difficult to distinguish genuine seasonality from noise. The final week's low rate may be a truncation artefact.

## Suggested Next Steps

1. Test whether the June rate decline persists after controlling for lead-time composition — if truncated data over-represents short-lead appointments, the decline is mechanical rather than behavioural
2. If a longer time series were available (12+ months), decompose the series into trend, seasonal, and residual components to quantify true seasonality
