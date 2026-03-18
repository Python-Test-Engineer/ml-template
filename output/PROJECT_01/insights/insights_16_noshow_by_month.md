# Insight Report: 16_noshow_by_month.jpg

![image](../plots/16_noshow_by_month.jpg)

**Chart type:** Vertical bar chart with overall reference line
**Variables displayed:** Appointment month (April, May, June) on x-axis, no-show rate (%) on y-axis, with overall rate line at 20.2%
**Generated:** 2026-03-18

---

## Key Observation

Monthly no-show rates are remarkably stable: April 19.6%, May 20.8%, June 18.5%. The total spread is just 2.3 percentage points across three months. May is the only month above the overall average (20.2%), while June shows a slight improvement. There is no evidence of a meaningful temporal trend within this 3-month window.

## Business / Scientific Implication

The stability of monthly rates is reassuring for predictive modelling — it means a model trained on one month's data should generalise well to subsequent months within this seasonal window. Month-of-year is unlikely to add predictive power in a model already containing lead time, age, and neighbourhood. However, this dataset only spans April–June (late autumn into winter in the Southern Hemisphere), so seasonal effects across the full calendar year remain unknown. The slight May peak (20.8%) may coincide with Brazilian public holidays (Labour Day on May 1, possibly others) creating scheduling disruption.

## Deeper Analysis

The 2.3pp range across months is the smallest effect size of any variable examined — smaller than gender (0.3pp), weekday (3.8pp), age (10.5pp), or lead time (28.6pp). This effectively confirms that month is a non-predictor in this dataset. June's lower rate (18.5%) could reflect either a genuine seasonal effect (patients more diligent in cooler weather) or a data truncation artefact — if June data is incomplete, the most recently scheduled appointments (which have shorter lead times) would be over-represented, mechanically lowering the no-show rate. The absence of a trend is itself informative: it suggests the no-show problem is structural and persistent rather than worsening or improving over time in this period.

## Confidence Assessment

**Confidence:** Medium
**Rationale:** Monthly aggregates are based on very large samples (~30K+ per month), but only 3 months are available, making it impossible to assess seasonality or long-term trends. June may have truncation effects.

## Suggested Next Steps

1. Check whether June data is complete (does the dataset end mid-June?) to rule out truncation bias in the June rate
2. If a full 12-month dataset were available, seasonal decomposition would be valuable — particularly to test whether winter months (Jun-Aug in Brazil) differ from summer
