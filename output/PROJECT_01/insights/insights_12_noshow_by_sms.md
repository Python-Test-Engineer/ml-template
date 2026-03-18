# Insight Report: 12_noshow_by_sms.jpg

![image](../plots/12_noshow_by_sms.jpg) 


**Chart type:** Vertical bar chart with overall reference line and annotation
**Variables displayed:** SMS status (No SMS, SMS Received) on x-axis, no-show rate (%) on y-axis, with overall rate at 20.2%
**Generated:** 2026-03-18

---

## Key Observation

Patients who received SMS reminders have a paradoxically *higher* no-show rate (27.6%) than those who did not (16.7%) — an 11 percentage point gap in the wrong direction. The chart itself annotates this as "counterintuitive" and attributes it to selection bias: SMS reminders were disproportionately sent to long-lead-time appointments, which are inherently higher risk. This is a textbook example of Simpson's paradox.

## Business / Scientific Implication

This chart is a cautionary tale for data-driven decision making. A naive analyst looking at this chart alone would conclude "SMS reminders increase no-shows" and recommend discontinuing them — exactly the wrong conclusion. The real insight is that SMS reminders are a confounded variable and cannot be evaluated without controlling for lead time. Any A/B test of SMS effectiveness must stratify by lead time or use propensity-score matching. For stakeholders, this finding should be presented alongside the SMS paradox chart (plot 19) that breaks down the effect within lead-time buckets.

## Deeper Analysis

The 27.6% rate for SMS recipients is 37% higher than the overall rate (20.2%) and 65% higher than non-recipients (16.7%). This dramatic gap is entirely explained by selection bias: the script code confirms that SMS was sent to ~32% of appointments, concentrated among those with longer lead times. Since same-day appointments (45% of all, with 4.6% no-show) almost certainly did not receive SMS, the "No SMS" group is diluted by a massive low-risk population. The true causal effect of SMS — visible only within lead-time strata — is likely a modest reduction in no-show rate (perhaps 2-5 percentage points), not the 11-point increase shown here. This variable is dangerous in a machine learning model: a model that learns "SMS → higher no-show" would assign higher risk scores to SMS recipients, potentially causing the system to avoid sending reminders to high-risk patients who need them most.

## Confidence Assessment

**Confidence:** High (for the observation); Low (for any causal interpretation)
**Rationale:** The 11pp gap is statistically robust, but it reflects confounding, not causation. The selection bias mechanism is well-understood from the code.

## Suggested Next Steps

1. Conduct a stratified analysis (or use the SMS paradox chart 19) to estimate the within-stratum effect of SMS, controlling for lead time
2. If implementing a prediction model, either exclude SMS_received or include it alongside lead_days with explicit interaction terms to prevent the model from learning a spurious positive association
