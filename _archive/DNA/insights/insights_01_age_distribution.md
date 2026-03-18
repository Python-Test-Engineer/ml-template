# Insight Report: 01_age_distribution.jpg

![image](../plots/01_age_distribution.jpg) 

**Chart type:** Histogram with KDE overlay
**Variables displayed:** Patient age (years) on x-axis, appointment count on y-axis, with median line at 37
**Generated:** 2026-03-18

---

## Key Observation

The age distribution is strikingly bimodal: a massive pediatric spike at ages 0–5 (~12,000 appointments) and a broad second peak around ages 50–60 (~9,500 appointments). A pronounced trough exists for young adults aged 15–25 (~7,000–7,500), representing the lowest utilisation segment outside the elderly. The median age of 37 sits between these two modes, masking the true shape of demand.

## Business / Scientific Implication

Healthcare capacity planning must account for two distinct demand pools: pediatric (driven by vaccination schedules and childhood illness) and middle-aged/elderly (chronic disease management). The young-adult trough (15–25) signals a healthcare access gap or disengagement — this is precisely the demographic most likely to no-show, compounding the underutilisation problem. Targeted outreach programmes for this age band could improve both attendance rates and early disease detection.

## Deeper Analysis

The pediatric spike (0–5 years) is disproportionately large — nearly 12,000 appointments in a single 5-year bin versus ~8,000–9,000 for most other bins. This likely reflects Brazil's mandatory childhood vaccination calendar and well-child visits, where parents schedule on behalf of children. The KDE curve reveals a subtle shoulder around ages 35–45 before the second peak, suggesting a transition zone where patients begin chronic disease management. The long right tail (extending to ~100+) confirms the dataset includes very elderly patients but in small numbers — these bins will have unstable no-show rate estimates. The dip at 40–45 (~7,000) between the two peaks is notable and may reflect a demographic cohort gap or a genuine low-utilisation period before chronic conditions emerge.

## Confidence Assessment

**Confidence:** High
**Rationale:** Histogram patterns are unambiguous with a large sample size (~110K appointments); the bimodal shape is clearly visible and clinically interpretable.

## Suggested Next Steps

1. Stratify no-show rates by the two modal groups (pediatric 0–10 vs. chronic-disease 50–65) to determine if intervention strategies should differ by age cluster
2. Investigate the young-adult trough (15–25): is this low volume due to fewer appointments being scheduled, or are they being scheduled but not attending?
