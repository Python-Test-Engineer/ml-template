# Insight Report: 17_repeat_patient_noshow.jpg

![image](../plots/17_repeat_patient_noshow.jpg)

**Chart type:** Vertical bar chart with overall reference line
**Variables displayed:** Prior no-show rate bucket (0%, 1-25%, 26-50%, 51-75%, 76-100%) on x-axis, current no-show rate (%) on y-axis, with overall rate line at 20.2%
**Generated:** 2026-03-18

---

## Key Observation

Prior no-show behaviour is the strongest single predictor of future no-shows. Patients with a 0% prior no-show history have just a 17.5% current no-show rate, while those with a 51-75% prior rate reach 39.7% — more than double. The progression is nearly monotonic: 0% (17.5%) → 1-25% (18.7%) → 26-50% (28.2%) → 51-75% (39.7%), with a slight drop at 76-100% (35.3%). The total spread of 22.2 percentage points makes this the widest effect of any individual feature, surpassing even lead time.

## Business / Scientific Implication

This is the single most powerful insight for operational intervention. A patient's history of prior no-shows is a strong, directly observable predictor that should be the centrepiece of any overbooking or reminder strategy. Patients in the 51-75% prior no-show bucket have a nearly 40% probability of missing their next appointment — these patients should receive enhanced outreach (phone calls, not just SMS), flexible rescheduling options, or same-day booking preferences to reduce their lead time. Conversely, patients with 0% prior history (17.5% rate) can be booked with confidence and need minimal intervention resources.

## Deeper Analysis

The slight decline from 51-75% (39.7%) to 76-100% (35.3%) mirrors the 90d+ lead-time anomaly and likely reflects survivor/selection bias: patients who miss 76-100% of prior appointments may have so few total appointments that the current observation is their second or third visit, with wide variance. Alternatively, some patients in this extreme bucket may have experienced a life change (new job, relocation) that simultaneously explains past no-shows and current attendance. The 0% bucket (17.5%) is still notably above zero — even reliable patients miss roughly 1 in 6 appointments, confirming that no-shows have both behavioural (habitual) and situational (unexpected events) components. The jump from 1-25% (18.7%) to 26-50% (28.2%) is the steepest step (+9.5pp), suggesting a critical threshold around 25% prior rate where patients transition from "occasionally unreliable" to "systematically high-risk."

## Confidence Assessment

**Confidence:** High
**Rationale:** The monotonic trend is clear and clinically intuitive; the analysis correctly uses only prior history (not future data) to avoid leakage, as verified in the script code.

## Suggested Next Steps

1. Incorporate prior_noshow_rate as the primary feature in a predictive model — it likely provides more lift than any other single variable
2. Design a tiered intervention programme: light-touch (SMS) for 0-25% history, moderate (phone call + SMS) for 26-50%, intensive (same-day rebooking + community health worker) for 51%+
