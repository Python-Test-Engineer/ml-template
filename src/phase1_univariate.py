"""Phase 1 — Univariate EDA
Produces plots 01–08: distributions of each variable in isolation.
"""
import matplotlib
matplotlib.use("Agg")

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

OUTPUT_DIR = Path("output/PROJECT_01")
PLOTS_DIR = OUTPUT_DIR / "plots"
CLEAN_CSV = OUTPUT_DIR / "clean.csv"

DPI = 150
FIG_SIZE = (10, 6)
STYLE = "seaborn-v0_8-whitegrid"

DOW_NAMES = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}


def assert_inputs() -> None:
    if not CLEAN_CSV.exists():
        raise FileNotFoundError(
            f"Missing {CLEAN_CSV}. Run phase0_etl.py first."
        )


def load_clean() -> pd.DataFrame:
    df = pd.read_csv(CLEAN_CSV, parse_dates=["appointment_dt", "scheduled_dt"])
    return df


def plot_age_distribution(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    sns.histplot(df["Age"], bins=20, kde=True, ax=ax, color="steelblue")
    median_age = df["Age"].median()
    ax.axvline(median_age, color="red", linestyle="--", label=f"Median: {median_age:.0f}")
    ax.set_title("Age Distribution of Patients")
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Count")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "01_age_distribution.png", dpi=DPI)
    plt.close("all")
    print("  Saved 01_age_distribution.png")


def plot_lead_days_distribution(df: pd.DataFrame) -> None:
    clipped = df[df["lead_days"] <= 120]["lead_days"]
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.hist(clipped, bins=50, color="steelblue", edgecolor="white")
    mean_lead = df["lead_days"].mean()
    ax.axvline(mean_lead, color="red", linestyle="--", label=f"Mean: {mean_lead:.1f}d")
    ax.set_title("Days Between Scheduling and Appointment")
    ax.set_xlabel("Lead Days (clipped at 120)")
    ax.set_ylabel("Count")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "02_lead_days_distribution.png", dpi=DPI)
    plt.close("all")
    print("  Saved 02_lead_days_distribution.png")


def plot_noshow_overall(df: pd.DataFrame) -> None:
    counts = df["No-show"].value_counts().reindex(["No", "Yes"])
    labels = ["Attended (No)", "No-Show (Yes)"]
    total = counts.sum()
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(labels, counts.values, color=["#2ecc71", "#e74c3c"])
    for bar, count in zip(bars, counts.values):
        pct = count / total * 100
        ax.text(bar.get_width() + total * 0.005, bar.get_y() + bar.get_height() / 2,
                f"{count:,} ({pct:.1f}%)", va="center", fontsize=11)
    ax.set_title("Overall No-Show vs Attended")
    ax.set_xlabel("Count")
    ax.set_xlim(0, total * 1.15)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "03_noshow_overall.png", dpi=DPI)
    plt.close("all")
    print("  Saved 03_noshow_overall.png")


def plot_binary_flags_prevalence(df: pd.DataFrame) -> None:
    flags = ["Scholarship", "Hipertension", "Diabetes", "Alcoholism", "handcap_binary", "SMS_received"]
    labels = ["Scholarship", "Hypertension", "Diabetes", "Alcoholism", "Disability", "SMS Received"]
    pcts = [df[f].mean() * 100 for f in flags]
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    bars = ax.bar(labels, pcts, color="steelblue")
    for bar, pct in zip(bars, pcts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{pct:.1f}%", ha="center", va="bottom", fontsize=10)
    ax.set_title("Prevalence of Patient Condition Flags")
    ax.set_ylabel("% of Appointments")
    ax.set_ylim(0, max(pcts) * 1.15)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "04_binary_flags_prevalence.png", dpi=DPI)
    plt.close("all")
    print("  Saved 04_binary_flags_prevalence.png")


def plot_gender_split(df: pd.DataFrame) -> None:
    counts = df["Gender"].value_counts().reindex(["F", "M"])
    total = counts.sum()
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(["Female (F)", "Male (M)"], counts.values, color=["#9b59b6", "#3498db"])
    for bar, count in zip(bars, counts.values):
        pct = count / total * 100
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + total * 0.003,
                f"{count:,}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=11)
    ax.set_title("Appointment Count by Gender")
    ax.set_ylabel("Count")
    ax.set_ylim(0, counts.max() * 1.15)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "05_gender_split.png", dpi=DPI)
    plt.close("all")
    print("  Saved 05_gender_split.png")


def plot_top20_neighbourhoods(df: pd.DataFrame) -> None:
    top20 = df["Neighbourhood"].value_counts().head(20).sort_values()
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(top20.index, top20.values, color="steelblue")
    ax.set_title("Top 20 Neighbourhoods by Appointment Volume")
    ax.set_xlabel("Number of Appointments")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "06_top20_neighbourhoods.png", dpi=DPI)
    plt.close("all")
    print("  Saved 06_top20_neighbourhoods.png")


def plot_appointments_by_weekday(df: pd.DataFrame) -> None:
    dow_counts = df["appointment_dow"].value_counts().sort_index()
    dow_labels = [DOW_NAMES.get(i, str(i)) for i in dow_counts.index]
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.bar(dow_labels, dow_counts.values, color="steelblue")
    ax.set_title("Appointments by Day of Week")
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "07_appointments_by_weekday.png", dpi=DPI)
    plt.close("all")
    print("  Saved 07_appointments_by_weekday.png")


def plot_appointments_over_time(df: pd.DataFrame) -> None:
    daily = df.set_index("appointment_dt").resample("D")["AppointmentID"].count()
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.plot(daily.index, daily.values, color="steelblue", linewidth=1.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b-%d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45)
    ax.set_title("Daily Appointment Volume (Apr–Jun 2016)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Appointments per Day")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "08_appointments_over_time.png", dpi=DPI)
    plt.close("all")
    print("  Saved 08_appointments_over_time.png")


def main() -> None:
    plt.style.use(STYLE)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    assert_inputs()

    print("Loading clean.csv ...")
    df = load_clean()
    print(f"  Shape: {df.shape}")

    print("\n--- Generating univariate plots ---")
    plot_age_distribution(df)
    plot_lead_days_distribution(df)
    plot_noshow_overall(df)
    plot_binary_flags_prevalence(df)
    plot_gender_split(df)
    plot_top20_neighbourhoods(df)
    plot_appointments_by_weekday(df)
    plot_appointments_over_time(df)

    print("\n=== Phase 1 Complete — 8 plots saved ===")


if __name__ == "__main__":
    main()
