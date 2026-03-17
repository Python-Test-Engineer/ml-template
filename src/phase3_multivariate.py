"""Phase 3 — Multivariate Deep-Dives
Produces plots 19–25: SMS paradox, age×condition, neighbourhood inequality,
same-day profile, scholarship analysis, patient frequency, weekly time series.
"""
import matplotlib
matplotlib.use("Agg")

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

OUTPUT_DIR = Path("output/PROJECT_01")
PLOTS_DIR = OUTPUT_DIR / "plots"
CLEAN_CSV = OUTPUT_DIR / "clean.csv"

DPI = 150
STYLE = "seaborn-v0_8-whitegrid"
LEAD_BUCKET_ORDER = ["same-day", "1-7d", "8-30d", "31-90d", "90d+"]
AGE_GROUP_ORDER = ["0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81+"]


def assert_inputs() -> None:
    if not CLEAN_CSV.exists():
        raise FileNotFoundError(f"Missing {CLEAN_CSV}. Run phase0_etl.py first.")


def load_clean() -> pd.DataFrame:
    return pd.read_csv(CLEAN_CSV, parse_dates=["appointment_dt", "scheduled_dt"])


def gini_coefficient(values: np.ndarray) -> float:
    """Compute Gini coefficient for an array of values."""
    sorted_vals = np.sort(values)
    n = len(sorted_vals)
    cumsum = np.cumsum(sorted_vals)
    return (2 * np.sum((np.arange(1, n + 1)) * sorted_vals) - (n + 1) * cumsum[-1]) / (n * cumsum[-1])


def plot_sms_paradox(df: pd.DataFrame) -> None:
    pivot = df.groupby(["lead_bucket", "SMS_received"], observed=True)["noshow_flag"].mean().unstack()
    pivot = pivot.reindex(LEAD_BUCKET_ORDER)
    pivot.columns = ["No SMS", "SMS Received"]

    x = np.arange(len(pivot))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))
    bars0 = ax.bar(x - width / 2, pivot["No SMS"] * 100, width, label="No SMS", color="#3498db")
    bars1 = ax.bar(x + width / 2, pivot["SMS Received"] * 100, width, label="SMS Received", color="#e74c3c")
    ax.set_xticks(x)
    ax.set_xticklabels(LEAD_BUCKET_ORDER)
    ax.set_xlabel("Lead Time Bucket")
    ax.set_ylabel("No-Show Rate (%)")
    ax.set_title("The SMS Paradox: No-Show Rate by Lead Time and SMS Status")
    ax.legend()
    ax.text(0.5, -0.14,
            "SMS recipients have higher overall no-show rates because reminders are sent to high-lead-time appointments",
            transform=ax.transAxes, ha="center", fontsize=8, style="italic", color="darkred")
    fig.subplots_adjust(bottom=0.18)
    fig.savefig(PLOTS_DIR / "19_sms_paradox.png", dpi=DPI)
    plt.close("all")
    print("  Saved 19_sms_paradox.png")


def plot_age_condition_heatmap(df: pd.DataFrame) -> None:
    pivot = df.groupby(["age_group", "Hipertension"], observed=True)["noshow_flag"].mean().unstack()
    pivot = pivot.reindex(AGE_GROUP_ORDER)
    pivot.columns = ["No Hypertension", "Hypertension"]

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(pivot, annot=True, fmt=".1%", cmap="YlOrRd", ax=ax,
                linewidths=0.5, vmin=0, vmax=0.4)
    ax.set_title("No-Show Rate: Age Group × Hypertension Status")
    ax.set_xlabel("Hypertension Status")
    ax.set_ylabel("Age Group")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "20_age_condition_heatmap.png", dpi=DPI)
    plt.close("all")
    print("  Saved 20_age_condition_heatmap.png")


def plot_neighbourhood_inequality(df: pd.DataFrame) -> None:
    nb_rates = df.groupby("Neighbourhood")["noshow_flag"].mean().sort_values()
    gini = gini_coefficient(nb_rates.values)
    print(f"  Neighbourhood no-show rate Gini coefficient: {gini:.4f}")

    norm_vals = (nb_rates.values - nb_rates.values.min()) / (nb_rates.values.max() - nb_rates.values.min())
    cmap = plt.colormaps["RdYlGn_r"]
    colors = [cmap(v) for v in norm_vals]

    fig, ax = plt.subplots(figsize=(10, 16))
    ax.barh(nb_rates.index, nb_rates.values * 100, color=colors)

    # Annotate top-3 highest and lowest
    for i, (nb, rate) in enumerate(nb_rates.items()):
        if i < 3:  # lowest
            ax.text(rate * 100 + 0.2, i, f"← {rate*100:.1f}%", va="center", fontsize=7, color="darkgreen")
        if i >= len(nb_rates) - 3:  # highest
            ax.text(rate * 100 + 0.2, i, f"← {rate*100:.1f}%", va="center", fontsize=7, color="darkred")

    ax.set_title(f"No-Show Rate by Neighbourhood (All 81)\nGini coefficient: {gini:.3f}")
    ax.set_xlabel("No-Show Rate (%)")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "21_neighbourhood_inequality.png", dpi=DPI)
    plt.close("all")
    print("  Saved 21_neighbourhood_inequality.png")


def plot_same_day_profile(df: pd.DataFrame) -> None:
    same_day = df[df["lead_days"] == 0]
    rest = df[df["lead_days"] > 0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Profile of Same-Day Appointments", fontsize=14)

    # Left: age distribution overlaid (normalized)
    ax1.hist(same_day["Age"], bins=20, density=True, alpha=0.6, label=f"Same-day (n={len(same_day):,})",
             color="#e74c3c")
    ax1.hist(rest["Age"], bins=20, density=True, alpha=0.5, label=f"Advance booking (n={len(rest):,})",
             color="#3498db")
    ax1.set_title("Age Distribution")
    ax1.set_xlabel("Age (years)")
    ax1.set_ylabel("Density")
    ax1.legend()

    # Right: no-show rate + condition flag comparison
    categories = ["No-Show Rate", "Scholarship", "Hypertension", "Diabetes", "SMS Received"]
    same_vals = [
        same_day["noshow_flag"].mean() * 100,
        same_day["Scholarship"].mean() * 100,
        same_day["Hipertension"].mean() * 100,
        same_day["Diabetes"].mean() * 100,
        same_day["SMS_received"].mean() * 100,
    ]
    rest_vals = [
        rest["noshow_flag"].mean() * 100,
        rest["Scholarship"].mean() * 100,
        rest["Hipertension"].mean() * 100,
        rest["Diabetes"].mean() * 100,
        rest["SMS_received"].mean() * 100,
    ]
    x = np.arange(len(categories))
    width = 0.35
    ax2.bar(x - width / 2, same_vals, width, label="Same-day", color="#e74c3c")
    ax2.bar(x + width / 2, rest_vals, width, label="Advance", color="#3498db")
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, rotation=20, ha="right")
    ax2.set_ylabel("Rate (%)")
    ax2.set_title("Rate Comparison: Same-Day vs Advance")
    ax2.legend()

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "22_same_day_profile.png", dpi=DPI)
    plt.close("all")
    print("  Saved 22_same_day_profile.png")


def plot_scholarship_analysis(df: pd.DataFrame) -> None:
    # Classify neighbourhoods into volume terciles
    nb_vol = df["Neighbourhood"].value_counts()
    terciles = pd.qcut(nb_vol, q=3, labels=["Low Volume", "Medium Volume", "High Volume"])
    nb_tercile_map = terciles.to_dict()
    df2 = df.copy()
    df2["nb_tercile"] = df2["Neighbourhood"].map(nb_tercile_map)
    df2 = df2[df2["nb_tercile"].notna()]

    grouped = df2.groupby(["nb_tercile", "Scholarship"])["noshow_flag"].mean().unstack()
    grouped = grouped.reindex(["Low Volume", "Medium Volume", "High Volume"])
    grouped.columns = ["No Scholarship", "Scholarship"]

    x = np.arange(len(grouped))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width / 2, grouped["No Scholarship"] * 100, width,
           label="No Scholarship", color="#3498db")
    ax.bar(x + width / 2, grouped["Scholarship"] * 100, width,
           label="Scholarship (Bolsa Família)", color="#e74c3c")
    ax.set_xticks(x)
    ax.set_xticklabels(grouped.index)
    ax.set_ylabel("No-Show Rate (%)")
    ax.set_title("No-Show Rate: Welfare Recipients vs Non-Recipients\nby Neighbourhood Volume Tercile")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "23_scholarship_analysis.png", dpi=DPI)
    plt.close("all")
    print("  Saved 23_scholarship_analysis.png")


def plot_patient_appointment_counts(df: pd.DataFrame) -> None:
    patient_counts = df.groupby("PatientId").size()

    # Bin: 1, 2-5, 6-10, 10+
    bins_hist = list(range(1, 22)) + [patient_counts.max() + 1]
    labels_hist = [str(i) for i in range(1, 21)] + ["21+"]

    # No-show rate by frequency bucket
    freq_bins = [0, 1, 5, 10, patient_counts.max() + 1]
    freq_labels = ["1 appt", "2-5 appts", "6-10 appts", "10+ appts"]
    patient_freq = patient_counts.reset_index()
    patient_freq.columns = ["PatientId", "appt_count"]
    patient_freq["freq_bucket"] = pd.cut(patient_freq["appt_count"], bins=freq_bins, labels=freq_labels, right=True)

    df2 = df.merge(patient_freq[["PatientId", "freq_bucket"]], on="PatientId", how="left")
    freq_noshow = df2.groupby("freq_bucket", observed=True)["noshow_flag"].mean().reindex(freq_labels)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Patient Appointment Frequency", fontsize=14)

    # Left: histogram of appointment count per patient
    count_vals = patient_counts.values
    ax1.hist(np.clip(count_vals, 1, 21), bins=range(1, 23), color="steelblue", edgecolor="white", align="left")
    ax1.set_title("Appointments per Patient")
    ax1.set_xlabel("Number of Appointments")
    ax1.set_ylabel("Number of Patients")
    ax1.set_xticks(range(1, 22))
    ax1.set_xticklabels([str(i) for i in range(1, 21)] + ["21+"], rotation=45, fontsize=8)

    # Right: no-show rate by frequency bucket
    bars = ax2.bar(freq_labels, freq_noshow.values * 100, color="#e74c3c")
    overall_rate = df["noshow_flag"].mean()
    ax2.axhline(overall_rate * 100, color="black", linestyle="--", label=f"Overall: {overall_rate*100:.1f}%")
    for bar, rate in zip(bars, freq_noshow.values):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                 f"{rate*100:.1f}%", ha="center", va="bottom", fontsize=9)
    ax2.set_title("No-Show Rate by Visit Frequency")
    ax2.set_ylabel("No-Show Rate (%)")
    ax2.legend()

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "24_patient_appointment_counts.png", dpi=DPI)
    plt.close("all")
    print("  Saved 24_patient_appointment_counts.png")


def plot_weekly_noshow_timeseries(df: pd.DataFrame) -> None:
    df2 = df.set_index("appointment_dt")
    weekly_rate = df2["noshow_flag"].resample("W").mean() * 100
    weekly_vol = df2["AppointmentID"].resample("W").count()

    mean_rate = weekly_rate.mean()
    std_rate = weekly_rate.std()
    anomaly_weeks = weekly_rate[weekly_rate > mean_rate + 1.5 * std_rate]

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    ax1.plot(weekly_rate.index, weekly_rate.values, color="#e74c3c", linewidth=2,
             label="No-Show Rate (%)", marker="o", markersize=4)
    ax2.bar(weekly_vol.index, weekly_vol.values, width=5, color="#3498db", alpha=0.3,
            label="Weekly Volume")

    for week in anomaly_weeks.index:
        ax1.axvline(week, color="darkred", linestyle="--", alpha=0.7, linewidth=1.2)
        ax1.text(week, weekly_rate[week] + 0.5, f"↑{weekly_rate[week]:.1f}%",
                 fontsize=7, color="darkred", rotation=45)

    ax1.set_title("Weekly No-Show Rate and Appointment Volume (Apr–Jun 2016)")
    ax1.set_xlabel("Week")
    ax1.set_ylabel("No-Show Rate (%)", color="#e74c3c")
    ax2.set_ylabel("Appointment Volume", color="#3498db")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b-%d"))
    plt.xticks(rotation=45)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "25_weekly_noshow_timeseries.png", dpi=DPI)
    plt.close("all")
    print("  Saved 25_weekly_noshow_timeseries.png")


def main() -> None:
    plt.style.use(STYLE)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    assert_inputs()

    print("Loading clean.csv ...")
    df = load_clean()
    print(f"  Shape: {df.shape}")

    print("\n--- Generating multivariate plots ---")
    plot_sms_paradox(df)
    plot_age_condition_heatmap(df)
    plot_neighbourhood_inequality(df)
    plot_same_day_profile(df)
    plot_scholarship_analysis(df)
    plot_patient_appointment_counts(df)
    plot_weekly_noshow_timeseries(df)

    print("\n=== Phase 3 Complete — 7 plots saved ===")


if __name__ == "__main__":
    main()
