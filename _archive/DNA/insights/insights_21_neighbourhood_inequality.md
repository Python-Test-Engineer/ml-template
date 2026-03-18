# Insight Report: 21_neighbourhood_inequality.jpg

![image](../plots/21_neighbourhood_inequality.jpg)

**Chart type:** Horizontal bar chart with RdYlGn colour scale, all 81 neighbourhoods, with Gini coefficient
**Variables displayed:** All 81 neighbourhoods on y-axis (sorted by no-show rate), no-show rate (%) on x-axis, with top-3/bottom-3 annotated
**Generated:** 2026-03-18

---

## Key Observation

The full 81-neighbourhood view reveals extreme outliers: **Ilhas Oceânicas de Trindade has a 100% no-show rate**, while Parque Industrial has 0% and Ilha do Boi sits at 8.6%. The Gini coefficient of 0.138 quantifies moderate inequality in no-show rates across neighbourhoods. The bulk of neighbourhoods (positions ~10-70) cluster tightly between 17-23%, but the tails are dramatic. Santos Dumont (28.9%) and Santa Cecília (27.9%) are the worst high-volume outliers after the extreme tail.

## Business / Scientific Implication

The 100% rate for Ilhas Oceânicas de Trindade is almost certainly a data artefact — this is a remote oceanic island ~1,100 km from the Brazilian coast with virtually no civilian population. It likely represents 1-2 appointments from military or research personnel, not a genuine neighbourhood-level pattern. Similarly, Parque Industrial (0%) and Ilha do Boi (8.6%) are very low-volume areas where small sample sizes create extreme rates. The Gini coefficient of 0.138 indicates moderate geographic inequality — meaningful enough to warrant location-based interventions, but not so extreme that a few neighbourhoods dominate the entire no-show problem. The true operational targets are high-volume neighbourhoods with rates above 23%: Itararé, Jesus de Nazareth, Caratoíra, and Andorinhas.

## Deeper Analysis

The tight central clustering (17-23% for ~60 of 81 neighbourhoods) suggests a "baseline" no-show rate of about 20% that is modified by neighbourhood-level factors (income, transport, clinic quality). The extreme tails are driven by sample size — neighbourhoods with <50 appointments should be filtered before drawing conclusions. The green-to-red gradient beautifully visualises the inequality: the bottom third (green) averages ~15-17%, the middle third ~18-21%, and the top third ~22-27% (excluding outliers). The annotation of top-3 lowest rates highlights upscale residential areas (Ilha do Boi, Jardim da Penha) and industrial zones (Parque Industrial), while the worst performers are known lower-income areas — strengthening the socioeconomic hypothesis.

## Confidence Assessment

**Confidence:** Medium
**Rationale:** The overall pattern and Gini coefficient are robust, but extreme values at both tails are unreliable due to very small sample sizes. The Gini metric appropriately summarises the distribution.

## Suggested Next Steps

1. Filter to neighbourhoods with ≥100 appointments and recalculate the Gini coefficient and ranking to remove noise from low-volume areas
2. Overlay census-level socioeconomic data (income, education, transit coverage) to formally test whether neighbourhood no-show variation is explained by deprivation indices
