"""Phase 4 — HTML Report
Compiles all outputs into a single self-contained report.html with base64-embedded plots.
"""
import base64
import datetime
from pathlib import Path

import pandas as pd
from jinja2 import Environment, BaseLoader

OUTPUT_DIR = Path("output/PROJECT_01")
PLOTS_DIR = OUTPUT_DIR / "plots"

PLOT_FILES = [
    ("01_age_distribution.png", "Age Distribution of Patients"),
    ("02_lead_days_distribution.png", "Days Between Scheduling and Appointment"),
    ("03_noshow_overall.png", "Overall No-Show vs Attended"),
    ("04_binary_flags_prevalence.png", "Prevalence of Patient Condition Flags"),
    ("05_gender_split.png", "Appointment Count by Gender"),
    ("06_top20_neighbourhoods.png", "Top 20 Neighbourhoods by Appointment Volume"),
    ("07_appointments_by_weekday.png", "Appointments by Day of Week"),
    ("08_appointments_over_time.png", "Daily Appointment Volume (Apr–Jun 2016)"),
    ("09_noshow_by_gender.png", "No-Show Rate by Gender"),
    ("10_noshow_by_age_group.png", "No-Show Rate by Age Group"),
    ("11_noshow_by_lead_days.png", "No-Show Rate by Appointment Lead Time"),
    ("12_noshow_by_sms.png", "No-Show Rate by SMS Reminder Status"),
    ("13_noshow_by_conditions.png", "No-Show Rate by Patient Condition"),
    ("14_noshow_by_weekday.png", "No-Show Rate by Day of Week"),
    ("15_noshow_by_neighbourhood.png", "No-Show Rate for Top 30 Neighbourhoods by Volume"),
    ("16_noshow_by_month.png", "No-Show Rate by Appointment Month"),
    ("17_repeat_patient_noshow.png", "Prior No-Show Rate vs Current No-Show"),
    ("18_correlation_heatmap.png", "Correlation Heatmap: Features vs No-Show"),
    ("19_sms_paradox.png", "The SMS Paradox: No-Show Rate by Lead Time and SMS Status"),
    ("20_age_condition_heatmap.png", "No-Show Rate: Age Group × Hypertension Status"),
    ("21_neighbourhood_inequality.png", "No-Show Rate by Neighbourhood (All 81)"),
    ("22_same_day_profile.png", "Profile of Same-Day Appointments"),
    ("23_scholarship_analysis.png", "Scholarship Analysis by Neighbourhood Volume Tercile"),
    ("24_patient_appointment_counts.png", "Patient Appointment Frequency"),
    ("25_weekly_noshow_timeseries.png", "Weekly No-Show Rate and Appointment Volume"),
]

KEY_FINDINGS = [
    "The overall no-show rate is ~20.2%, meaning roughly 1 in 5 appointments is missed.",
    "Longer lead times strongly predict no-shows: same-day appointments have the lowest no-show rate; appointments booked 31+ days ahead have the highest.",
    "Despite intuition, patients who received an SMS reminder had a <em>higher</em> no-show rate. This is a selection-bias artefact: SMS reminders were disproportionately sent for high-lead-time appointments.",
    "Younger patients (11–30 age group) have higher no-show rates; elderly patients (60+) are among the most reliable attenders.",
    "Welfare-programme (Scholarship) recipients have a slightly higher no-show rate, likely reflecting transport or employment constraints.",
    "Day of week matters: Friday appointments have the highest no-show rate; Tuesday and Wednesday appointments are most reliably attended.",
    "Substantial neighbourhood-level variation exists; high-volume central neighbourhoods tend to have lower no-show rates.",
    "Patients with a history of missing appointments are significantly more likely to miss their next appointment — prior behaviour is the strongest single predictor.",
]

QA_PAIRS = [
    (
        "Why does SMS_received correlate positively with no-shows, when you'd expect reminders to help?",
        """SMS reminders appear counterproductive at first glance, but this is a <strong>selection-bias artefact</strong>.
        Reminders were disproportionately sent to patients with longer lead-time appointments.
        Since lead time is the dominant predictor of no-show, patients who received SMS are already at higher baseline risk.
        When you control for lead time (see Plot 19 — SMS Paradox), the SMS effect is reduced or reversed within each
        lead-time bucket. The lesson: never interpret a raw correlation without considering confounders.""",
    ),
    (
        "What is the effect of appointment lead time on attendance?",
        """Lead time shows a near-<strong>monotonic relationship</strong> with no-show rate.
        Same-day appointments have the lowest no-show rates (patients are motivated and remember their appointment).
        The rate rises steadily through 1–7 days, 8–30 days, 31–90 days, reaching 30%+ for appointments booked
        more than 90 days ahead. Practically, this suggests scheduling systems should minimise lead times where possible,
        and should prioritise reminder systems for long-lead appointments.""",
    ),
    (
        "Which patient segments are at highest risk of not attending?",
        """The highest-risk segments are:
        <ul>
        <li><strong>Young adults (11–30)</strong>: highest no-show rate across age groups</li>
        <li><strong>Long lead-time appointments (31d+)</strong>: strong monotonic effect</li>
        <li><strong>Patients with prior no-show history</strong>: strongest single predictor — past behaviour predicts future behaviour</li>
        <li><strong>Scholarship (welfare) recipients</strong>: slightly elevated rate, likely socioeconomic barriers</li>
        <li><strong>Friday appointments</strong>: highest no-show rate by day of week</li>
        <li><strong>Certain neighbourhoods</strong>: substantial geographic variation in no-show rate</li>
        </ul>""",
    ),
    (
        "How would you build a no-show prediction model from this data?",
        """<strong>Target:</strong> Binary classification — noshow_flag (1 = missed).
        <br><strong>Features:</strong> lead_days, prior_noshow_rate (computed from patient history),
        age, appointment_dow, handcap_binary, Scholarship, Hipertension, Diabetes, neighbourhood (encoded).
        <br><strong>Class imbalance (80/20):</strong> Use class_weight='balanced' or SMOTE; evaluate with AUROC
        (not accuracy, which is misleading on imbalanced data).
        <br><strong>Algorithm:</strong> Start with logistic regression as interpretable baseline;
        then gradient boosting (XGBoost/LightGBM) for performance.
        <br><strong>Cross-validation:</strong> Time-based split (train on earlier months, test on later) to
        avoid data leakage — never use random splits when temporal order matters.
        <br><strong>Leakage risk:</strong> prior_noshow_rate must be computed using only past appointments,
        not future ones.""",
    ),
    (
        "What are the ethical considerations of using neighbourhood or scholarship status as features?",
        """These features are <strong>proxies for socioeconomic status</strong> and potentially ethnicity.
        Using them in an automated system risks:
        <ul>
        <li><strong>Proxy discrimination</strong>: deprioritising patients from poorer neighbourhoods who may already have worse health access</li>
        <li><strong>Feedback loops</strong>: a model trained on biased outcomes may perpetuate existing inequalities</li>
        <li><strong>Regulatory risk</strong>: Brazil's LGPD (Lei Geral de Proteção de Dados) and general data protection principles require fairness considerations</li>
        </ul>
        Mitigations: audit for demographic parity, use fairness-aware ML, ensure human oversight of automated decisions,
        and consider whether features improve <em>individual</em> or only <em>aggregate</em> predictions.""",
    ),
    (
        "What are the limitations of this dataset?",
        """<ul>
        <li><strong>Geographic scope</strong>: Single city (Vitória, ES, Brazil) — results may not generalise</li>
        <li><strong>Temporal scope</strong>: ~7 months (Nov 2015 – Jun 2016) — no seasonal patterns, no trend analysis</li>
        <li><strong>No reason for no-show</strong>: We can predict but not explain — patients may have rescheduled, recovered, or had emergencies</li>
        <li><strong>No appointment type</strong>: Specialty, urgency, and provider are not captured; these likely matter significantly</li>
        <li><strong>PatientId precision issue</strong>: Stored as float64 — possible precision loss for large IDs affecting patient-level analysis</li>
        <li><strong>No socioeconomic depth</strong>: Neighbourhood is a coarse proxy; income, transport access, and employment are not available</li>
        <li><strong>Handcap column</strong>: Multi-level (0–4) but treated as binary due to tiny sample sizes at levels 2–4</li>
        </ul>""",
    ),
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Medical Appointment No-Show — EDA Report</title>
  <style>
    body { font-family: Arial, sans-serif; background: #fff; color: #222;
           max-width: 1100px; margin: 0 auto; padding: 20px 30px; }
    h1 { color: #1a1a2e; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }
    h2 { color: #16213e; border-bottom: 1px solid #ccc; padding-bottom: 6px; margin-top: 40px; }
    h3 { color: #0f3460; }
    p.meta { color: #666; font-size: 0.9em; }
    table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 0.9em; }
    th { background: #1a1a2e; color: #fff; padding: 8px 12px; text-align: left; }
    td { padding: 7px 12px; border-bottom: 1px solid #eee; }
    tr:nth-child(even) td { background: #f8f8f8; }
    img { max-width: 100%; height: auto; border: 1px solid #ddd;
          border-radius: 4px; margin: 10px 0; display: block; }
    .plot-section { margin-bottom: 30px; }
    .plot-caption { font-size: 0.85em; color: #555; font-style: italic; margin-top: 4px; }
    ul.findings li { margin: 8px 0; line-height: 1.6; }
    details { margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; padding: 2px; }
    summary { cursor: pointer; font-weight: bold; padding: 10px 14px;
              background: #f0f4f8; border-radius: 4px; color: #1a1a2e; }
    summary:hover { background: #dce8f0; }
    details[open] summary { border-bottom: 1px solid #ccc; border-radius: 4px 4px 0 0; }
    .qa-answer { padding: 12px 16px; line-height: 1.7; }
    section { margin-bottom: 40px; }
  </style>
</head>
<body>
  <h1>Medical Appointment No-Show — EDA Report</h1>
  <p class="meta">Dataset: data/kaggle.csv &nbsp;|&nbsp; Generated: {{ date }} &nbsp;|&nbsp; Rows after cleaning: {{ n_clean }}</p>

  <section id="dataset-summary">
    <h2>1. Dataset Summary</h2>
    {{ stats_table }}
    <p>Dirty rows removed: <strong>{{ n_dirty }}</strong> (saved to dirty.csv with reason column)</p>
  </section>

  <section id="key-findings">
    <h2>2. Key Findings</h2>
    <ul class="findings">
      {% for finding in key_findings %}
      <li>{{ finding }}</li>
      {% endfor %}
    </ul>
  </section>

  <section id="univariate">
    <h2>3. Univariate Analysis</h2>
    {% for filename, caption in univariate_plots %}
    <div class="plot-section">
      <img src="data:image/png;base64,{{ plot_data[filename] }}" alt="{{ caption }}">
      <p class="plot-caption">{{ caption }}</p>
    </div>
    {% endfor %}
  </section>

  <section id="bivariate">
    <h2>4. Bivariate Analysis — No-Show Drivers</h2>
    {% for filename, caption in bivariate_plots %}
    <div class="plot-section">
      <img src="data:image/png;base64,{{ plot_data[filename] }}" alt="{{ caption }}">
      <p class="plot-caption">{{ caption }}</p>
    </div>
    {% endfor %}
  </section>

  <section id="multivariate">
    <h2>5. Multivariate &amp; Deep-Dive Analyses</h2>
    {% for filename, caption in multivariate_plots %}
    <div class="plot-section">
      <img src="data:image/png;base64,{{ plot_data[filename] }}" alt="{{ caption }}">
      <p class="plot-caption">{{ caption }}</p>
    </div>
    {% endfor %}
  </section>

  <section id="interview-qa">
    <h2>6. Hard Interview Questions — Q&amp;A</h2>
    <p>Click each question to expand the answer.</p>
    {% for question, answer in qa_pairs %}
    <details>
      <summary>Q: {{ question }}</summary>
      <div class="qa-answer">{{ answer }}</div>
    </details>
    {% endfor %}
  </section>

</body>
</html>
"""


def assert_inputs() -> None:
    missing = []
    for filename, _ in PLOT_FILES:
        p = PLOTS_DIR / filename
        if not p.exists():
            missing.append(str(p))
    if missing:
        raise FileNotFoundError(
            f"Missing {len(missing)} plot file(s). Run phases 1–3 first.\n" + "\n".join(missing)
        )
    for f in [OUTPUT_DIR / "summary_stats.csv", OUTPUT_DIR / "dirty.csv"]:
        if not f.exists():
            raise FileNotFoundError(f"Missing {f}. Run earlier phases first.")


def encode_plot(path: Path) -> str:
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode("utf-8")


def load_stats_html() -> str:
    df = pd.read_csv(OUTPUT_DIR / "summary_stats.csv")
    return df.to_html(index=False, border=0, classes="")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    assert_inputs()

    print("Encoding plots ...")
    plot_data: dict[str, str] = {}
    for filename, _ in PLOT_FILES:
        plot_data[filename] = encode_plot(PLOTS_DIR / filename)
        print(f"  Encoded {filename}")

    dirty_df = pd.read_csv(OUTPUT_DIR / "dirty.csv")
    clean_df = pd.read_csv(OUTPUT_DIR / "clean.csv")
    n_dirty = len(dirty_df)
    n_clean = len(clean_df)

    stats_table = load_stats_html()
    date_str = datetime.date.today().strftime("%Y-%m-%d")

    univariate_plots = PLOT_FILES[:8]
    bivariate_plots = PLOT_FILES[8:18]
    multivariate_plots = PLOT_FILES[18:]

    env = Environment(loader=BaseLoader())
    template = env.from_string(HTML_TEMPLATE)
    html = template.render(
        date=date_str,
        n_clean=f"{n_clean:,}",
        n_dirty=n_dirty,
        stats_table=stats_table,
        key_findings=KEY_FINDINGS,
        univariate_plots=univariate_plots,
        bivariate_plots=bivariate_plots,
        multivariate_plots=multivariate_plots,
        plot_data=plot_data,
        qa_pairs=QA_PAIRS,
    )

    report_path = OUTPUT_DIR / "report.html"
    report_path.write_text(html, encoding="utf-8")
    size_mb = report_path.stat().st_size / 1024 / 1024
    print(f"\n  Saved report.html ({size_mb:.1f} MB)")
    print("\n=== Phase 4 Complete — report.html saved ===")


if __name__ == "__main__":
    main()
