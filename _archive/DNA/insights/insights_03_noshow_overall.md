# Insight Report: 03_noshow_overall.jpg

![image](../plots/03_noshow_overall.jpg) 


**Chart type:** Horizontal bar chart
**Variables displayed:** Attendance status (Attended vs No-Show) on y-axis, appointment count on x-axis, with percentage annotations
**Generated:** 2026-03-18

---

## Key Observation

The overall no-show rate is 20.2% (22,314 out of 110,521 appointments). This means roughly 1 in 5 scheduled appointments results in a patient not attending. The 79.8% attendance rate (88,207 appointments) represents the majority class, creating a moderately imbalanced classification target.

## Business / Scientific Implication

A 20% no-show rate represents a significant operational burden: for a clinic running 100 appointments per day, approximately 20 slots go unused daily. This translates directly into wasted physician time, underutilised facilities, and delayed access for other patients who could have filled those slots. Even a modest reduction (e.g., from 20% to 15%) would recover ~5,500 appointment slots across this dataset period — equivalent to approximately 25 additional full clinic-days of capacity. This justifies investment in predictive models and targeted interventions.

## Deeper Analysis

The 80/20 class split is a well-known threshold in classification tasks — it is imbalanced enough that naive accuracy (predicting all "attended") would score 79.8%, making accuracy a misleading metric. Any predictive model must use AUROC, precision-recall, or F1-score to be meaningful. The 20.2% rate is consistent with published no-show rates in public healthcare systems globally (typically 15-30%), suggesting this is a systemic issue rather than a data anomaly. Importantly, this is an appointment-level rate, not a patient-level rate — frequent visitors who always attend pull the aggregate down, while chronic no-showers may have individual rates far exceeding 20%.

## Confidence Assessment

**Confidence:** High
**Rationale:** Simple proportion from a large, clean dataset — virtually no statistical uncertainty at this sample size.

## Suggested Next Steps

1. Calculate the patient-level no-show rate distribution (what fraction of patients have >50% no-show rate?) to identify the chronic non-attenders driving the aggregate
2. Estimate the financial cost per no-show to quantify the ROI of intervention programmes
