# Insight Report: 07_appointments_by_weekday.jpg

![image](../plots/07_appointments_by_weekday.jpg) 



**Chart type:** Vertical bar chart
**Variables displayed:** Day of week (Mon–Sat) on x-axis, appointment count on y-axis
**Generated:** 2026-03-18

---

## Key Observation

Appointment volume follows a midweek peak pattern: Tuesday (~25,700) and Wednesday (~25,900) carry the highest volume, Monday is slightly lower (~22,700), while Thursday (~17,300) and Friday (~19,000) drop notably. Saturday has near-zero appointments — the system effectively operates on a 5-day week. The Tuesday-Wednesday peak carries roughly 47% of all weekly appointments in just 2 days.

## Business / Scientific Implication

The volume dip on Thursday (~17,300, a 33% drop from Wednesday) is operationally significant and potentially exploitable. If Thursday's lower volume is due to scheduling practices rather than patient demand, redistributing appointments from peak days could smooth capacity utilisation and reduce wait times. The near-zero Saturday volume confirms this is a weekday-only public healthcare system. The Friday volume recovery (~19,000 vs Thursday's ~17,300) suggests Thursday is an anomaly — possibly related to specific clinic closure patterns or administrative schedules.

## Deeper Analysis

The Monday-to-Wednesday ramp-up is consistent with a "start of week scheduling" pattern where patients book on Monday for Tuesday/Wednesday. The Thursday dip is the most analytically interesting feature — in Brazilian public healthcare, some UBS units have reduced Thursday hours for staff training or administrative activities. Alternatively, Thursday may be when many clinics run specialist clinics (fewer general appointments). The absence of Sunday appointments is expected, but the virtual absence of Saturday appointments means weekend acute-care demand likely shifts to emergency departments — a potential hidden cost. When combined with the no-show-by-weekday chart, the key question is whether Thursday and Friday's lower volume is offset by higher or lower no-show rates.

## Confidence Assessment

**Confidence:** High
**Rationale:** Day-of-week counts are exact and the pattern is clear; however, the reason for the Thursday dip requires domain-specific operational knowledge to confirm.

## Suggested Next Steps

1. Investigate whether the Thursday dip is consistent across all neighbourhoods/facilities or is driven by specific clinics closing on Thursdays
2. Compare day-of-week volume with no-show rates to identify whether low-volume days also have different attendance patterns
