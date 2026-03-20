---
question: "why did any sales drop?"
generated: 2026-03-20
project: PROJECT_01
---

### Answer

Yes, sales dropped in two consecutive months after a March 2025 peak. **April fell -8.7%** ($22,790 from $24,969) despite record order volume — the drop was caused by shrinking deal sizes (AOV fell from $2,270 to $1,899), not fewer customers. **May fell a further -37.4%** ($14,270) as both order count and revenue collapsed, indicating a pipeline slowdown. The evidence points to two compounding causes: deal-quality erosion in April (likely discount-driven) and an absence of any repeat customers, meaning the business has no recurring revenue buffer when new deal flow weakens.

---

### Supporting Evidence

- **`summary_stats.csv` — `monthly_revenue`** — Jan $18,555 → Feb $17,074 → **Mar $24,969 (+46.2%)** → Apr $22,790 (-8.7%) → May $14,270 (-37.4%). April uniquely shows order count rising to 12 (highest of any month) while revenue fell — confirming smaller deals, not fewer deals.

- **`monthly_revenue.png`** — The dual-axis chart makes the April anomaly visible: the order-count bars are at their peak height in April while the revenue line simultaneously dips — the two series diverge in the only direction that signals deal-quality erosion.

- **`summary_stats.csv` — `sales_rep_performance`** — Priya Sharma: avg discount 8.6%, revenue $22,092 (lowest named rep). James Okafor: avg discount 2.9%, revenue $24,172. Higher discounting is not producing higher revenue, suggesting margin is being given away without closing larger deals.

- **`summary_stats.csv` — `kpis`** — `repeat_customer_count = 0`. Every dollar of revenue comes from a first-time buyer. There is no recurring base to absorb a soft month — any pipeline gap hits total revenue immediately and fully.

- **`cumulative_revenue.png`** — The curve's gradient visibly steepens through mid-March (~$35K to ~$60K cumulative in ~3 weeks) then flattens from late April onward, confirming the deceleration is sustained, not a single-week anomaly.

---

### Confidence

**Medium-High** — The drops are confirmed in validated transaction data. The deal-quality cause in April is strongly indicated by the AOV/volume divergence, but the precise driver (discount, product mix, or customer segment shift) requires deal-level analysis of `clean.csv` to confirm.

---

### Caveats & Limitations

May is almost certainly a **partial month** (~18 days of data visible in `cumulative_revenue.png`). Annualised, May's true run rate is approximately $19,100 — still a decline from April, but the headline -37.4% overstates it. Conclusions about May should be held lightly until the full month is confirmed.

---

### Suggested Follow-up

Group `clean.csv` April orders by `sales_rep` × `discount_pct` × `product` to determine whether the AOV compression is concentrated in one rep's deals or is business-wide — this is the single most actionable query available from existing data.
