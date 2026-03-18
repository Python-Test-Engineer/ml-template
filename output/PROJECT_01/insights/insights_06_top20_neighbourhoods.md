# Insight Report: 06_top20_neighbourhoods.jpg

![image](../plots/06_top20_neighbourhoods.jpg) 

**Chart type:** Horizontal bar chart (sorted ascending)
**Variables displayed:** Neighbourhood names on y-axis, number of appointments on x-axis, for the top 20 by volume
**Generated:** 2026-03-18

---

## Key Observation

Appointment volume is heavily concentrated: Jardim Camburi alone accounts for ~7,700 appointments (roughly 7% of total), nearly 3x the volume of the 20th-ranked neighbourhood Romão (~2,200). The top 3 neighbourhoods (Jardim Camburi, Maria Ortiz, Resistência) collectively represent ~18,000 appointments (~16% of the dataset). The distribution follows a long-tail power-law shape with a steep drop-off after the top 5.

## Business / Scientific Implication

The geographic concentration means that interventions deployed in just 3-5 neighbourhoods could reach a disproportionate share of total appointment volume. Jardim Camburi's dominance (~7,700 appointments) makes it the single highest-leverage target for any no-show reduction pilot — if that neighbourhood's no-show rate dropped by 5 percentage points, it would eliminate ~385 missed appointments. Conversely, the 61 neighbourhoods outside the top 20 collectively have smaller volumes, making per-neighbourhood interventions less cost-effective there.

## Deeper Analysis

The steep gradient (7,700 for #1 vs. 2,200 for #20) suggests that healthcare infrastructure (clinic locations, capacity) is not evenly distributed across Vitória. Jardim Camburi is known as the most populous neighbourhood in Vitória, so high volume is expected — but 7,700 appointments over ~7 months (~37/day) may indicate one or more high-volume UBS (Unidade Básica de Saúde) health units serving as a regional hub. The mid-range cluster (positions 6-10: Centro, Tabuazeiro, Santa Martha, Jesus de Nazareth, Bonfim) is tightly packed around 2,800-3,300 appointments, suggesting similar-capacity facilities. Centro's presence at #6 rather than #1 is interesting — central business districts often have lower residential populations despite high economic activity.

## Confidence Assessment

**Confidence:** High
**Rationale:** Count data from a complete dataset across 81 neighbourhoods; ranking is unambiguous.

## Suggested Next Steps

1. Cross-reference neighbourhood appointment volume with no-show rates to identify high-volume, high-no-show "hot spots" where intervention ROI would be maximised
2. Map neighbourhood locations to assess whether geographic distance from health facilities correlates with no-show rates
