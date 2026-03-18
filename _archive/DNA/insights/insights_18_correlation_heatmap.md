# Insight Report: 18_correlation_heatmap.jpg

![image](../plots/18_correlation_heatmap.jpg)

**Chart type:** Correlation heatmap (Pearson) with annotated coefficients
**Variables displayed:** 9×9 matrix of Age, lead_days, Scholarship, Hypertension, Diabetes, Alcoholism, handcap_binary, SMS_received, noshow_flag
**Generated:** 2026-03-18

---

## Key Observation

The noshow_flag row reveals that **lead_days (r=0.19)** and **SMS_received (r=0.13)** are the only features with meaningful linear correlations to no-shows. All other features have correlations below |0.06| with the target. The strongest inter-feature correlations are Age↔Hypertension (r=0.50), Hypertension↔Diabetes (r=0.43), and lead_days↔SMS_received (r=0.40) — confirming significant multicollinearity in these pairs.

## Business / Scientific Implication

The correlation structure exposes two critical modelling risks: (1) The SMS_received↔lead_days correlation (r=0.40) confirms the Simpson's paradox — SMS is a proxy for lead time, not an independent predictor. Including both without interaction terms will produce misleading coefficients. (2) The Age↔Hypertension (r=0.50) and Hypertension↔Diabetes (r=0.43) correlations mean these features share substantial information — adding all three to a linear model provides diminishing returns and inflated standard errors. A parsimonious model using just lead_days, age, and prior_noshow_rate (not shown here but the strongest predictor from chart 17) would likely capture most of the available signal.

## Deeper Analysis

The low absolute correlations with noshow_flag (max 0.19) indicate that no single linear feature explains much variance — the no-show problem is inherently multifactorial and likely involves non-linear interactions. The Age↔noshow_flag correlation (r=-0.06) appears weak despite the clear 10.5pp spread seen in the age group bar chart — this is because the relationship is non-linear (U-shaped for pediatric + elderly groups). Tree-based models (XGBoost, Random Forest) will capture this non-linearity far better than linear models. The Scholarship↔Age correlation (r=-0.09) confirms that welfare recipients skew younger, adding another confounding pathway. The near-zero correlations for Alcoholism (r=0.00) and handcap_binary (r=-0.01) with the target confirm these are statistically useless as independent predictors. The overall sparsity of the heatmap (most off-diagonal cells near 0) is actually good news for modelling — it means most features provide somewhat independent information.

## Confidence Assessment

**Confidence:** High
**Rationale:** Pearson correlations are exact for this sample size. However, Pearson only captures linear relationships — non-linear effects (like age) appear weak here but are strong in practice.

## Suggested Next Steps

1. Compute mutual information or Spearman rank correlations to capture non-linear associations that Pearson misses (especially for age and categorical features)
2. Use variance inflation factors (VIF) to formally quantify multicollinearity before building regression models — the Age/Hypertension/Diabetes cluster will likely need dimensionality reduction or feature selection
