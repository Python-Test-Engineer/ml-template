# Insight Report: 04_binary_flags_prevalence.jpg

![image](../plots/04_binary_flags_prevalence.jpg) 


**Chart type:** Vertical bar chart
**Variables displayed:** Six binary patient flags on x-axis (Scholarship, Hypertension, Diabetes, Alcoholism, Disability, SMS Received), prevalence as % of appointments on y-axis
**Generated:** 2026-03-18

---

## Key Observation

SMS Received is the most common flag at 32.1% of appointments, followed by Hypertension (19.7%) and Scholarship/welfare (9.8%). The clinical conditions Diabetes (7.2%), Alcoholism (3.0%), and Disability (2.0%) are relatively rare. Notably, Hypertension affects nearly 1 in 5 appointments, consistent with Brazil's high cardiovascular disease burden, while SMS reminders were sent to roughly a third of all appointments — not universally.

## Business / Scientific Implication

The non-universal SMS coverage (only 32.1%) represents an immediate operational lever: if SMS reminders are effective at reducing no-shows, extending coverage from 32% to 100% could yield significant attendance improvements. The high hypertension prevalence (19.7%) means this condition alone defines a substantial subpopulation whose appointment behaviour will influence aggregate statistics. The low prevalence of Alcoholism (3.0%) and Disability (2.0%) means any no-show rate analysis for these subgroups will have wide confidence intervals — conclusions about these groups should be treated cautiously.

## Deeper Analysis

The Scholarship flag (9.8%) is a proxy for Bolsa Família welfare recipients, marking socioeconomically vulnerable patients. This nearly 10% subpopulation may face transportation, childcare, or employment barriers that affect attendance — their no-show patterns require separate analysis. The fact that SMS was sent to only 32.1% raises the question of the selection mechanism: the scripts reveal that SMS reminders were preferentially sent to longer-lead-time appointments, creating a confounding relationship between SMS receipt and no-show risk. Hypertension and Diabetes prevalences (19.7% and 7.2%) skew heavily toward older age groups, meaning these flags are correlated with age — any model using both age and condition flags must account for multicollinearity.

## Confidence Assessment

**Confidence:** High
**Rationale:** Simple proportions from a large dataset; prevalence figures are precise and directly readable from the chart.

## Suggested Next Steps

1. Cross-tabulate SMS_received with lead_days to confirm the selection bias hypothesis before interpreting SMS effectiveness
2. Test for multicollinearity between age and condition flags (Hypertension, Diabetes) to determine if both should be included as independent features in a predictive model
