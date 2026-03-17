"""Phase 2 — Bivariate EDA
Produces plots 09–18: no-show rate by each feature, plus summary_stats.csv.
"""
import matplotlib
matplotlib.use("Agg")

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

OUTPUT_DIR = Path("output/PROJECT_01")
PLOTS_DIR = OUTPUT_DIR / "plots"
CLEAN_CSV = OUTPUT_DIR / "clean.csv"

DPI = 150
FIG_SIZE = (10, 6)
STYLE = "seaborn-v0_8-whitegrid"

AGE_GROUP_ORDER = ["0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81+"]
LEAD_BUCKET_ORDER = ["same-day", "1-7d", "8-30d", "31-90d", "90d+"]
DOW_ORDER = [0, 1, 2, 3, 4, 5]
DOW_NAMES = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat"}


def assert_inputs() -> None:
    if not CLEAN_CSV.exists():
        raise FileNotFoundError(f"Missing {CLEAN_CSV}. Run phase0_etl.py first.")


def load_clean() -> pd.DataFrame:
    df = pd.read_csv(CLEAN_CSV, parse_dates=["appointment_dt", "scheduled_dt"])
    return df


def noshow_bar(
    ax: plt.Axes,
    groups: list[str],
    rates: list[float],
    overall_rate: float,
    title: str,
    xlabel: str = "",
    color: str = "steelblue",
) -> None:
    """Shared helper: bar chart of no-show rates with reference line and annotations."""
    bars = ax.bar(groups, [r * 100 for r in rates], color=color)
    ax.axhline(overall_rate * 100, color="red", linestyle="--", linewidth=1.2,
               label=f"Overall: {overall_rate*100:.1f}%")
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{rate*100:.1f}%", ha="center", va="bottom", fontsize=9)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("No-Show Rate (%)")
    ax.set_ylim(0, max(r * 100 for r in rates) * 1.2)
    ax.legend()


def plot_noshow_by_gender(df: pd.DataFrame, overall_rate: float) -> None:
    rates = df.groupby("Gender")["noshow_flag"].mean().reindex(["F", "M"])
    fig, ax = plt.subplots(figsize=(7, 5))
    noshow_bar(ax, ["Female (F)", "Male (M)"], rates.values, overall_rate,
               "No-Show Rate by Gender")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "09_noshow_by_gender.png", dpi=DPI)
    plt.close("all")
    print("  Saved 09_noshow_by_gender.png")


def plot_noshow_by_age_group(df: pd.DataFrame, overall_rate: float) -> None:
    rates = df.groupby("age_group", observed=True)["noshow_flag"].mean().reindex(AGE_GROUP_ORDER)
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    noshow_bar(ax, AGE_GROUP_ORDER, rates.values, overall_rate,
               "No-Show Rate by Age Group", xlabel="Age Group")
    plt.xticks(rotation=30)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "10_noshow_by_age_group.png", dpi=DPI)
    plt.close("all")
    print("  Saved 10_noshow_by_age_group.png")


def plot_noshow_by_lead_days(df: pd.DataFrame, overall_rate: float) -> None:
    rates = df.groupby("lead_bucket", observed=True)["noshow_flag"].mean().reindex(LEAD_BUCKET_ORDER)
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    noshow_bar(ax, LEAD_BUCKET_ORDER, rates.values, overall_rate,
               "No-Show Rate by Appointment Lead Time", xlabel="Lead Time Bucket")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "11_noshow_by_lead_days.png", dpi=DPI)
    plt.close("all")
    print("  Saved 11_noshow_by_lead_days.png")


def plot_noshow_by_sms(df: pd.DataFrame, overall_rate: float) -> None:
    rates = df.groupby("SMS_received")["noshow_flag"].mean().reindex([0, 1])
    fig, ax = plt.subplots(figsize=(7, 5))
    noshow_bar(ax, ["No SMS", "SMS Received"], rates.values, overall_rate,
               "No-Show Rate by SMS Reminder Status")
    ax.annotate("Counterintuitive: SMS recipients have higher\nno-show rate due to selection bias\n(reminders sent for long-lead-time appts)",
                xy=(1, rates[1] * 100), xytext=(0.55, rates[1] * 100 + 5),
                fontsize=8, color="darkred",
                arrowprops=dict(arrowstyle="->", color="darkred"))
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "12_noshow_by_sms.png", dpi=DPI)
    plt.close("all")
    print("  Saved 12_noshow_by_sms.png")


def plot_noshow_by_conditions(df: pd.DataFrame, overall_rate: float) -> None:
    flags = ["Scholarship", "Hipertension", "Diabetes", "Alcoholism", "handcap_binary", "SMS_received"]
    titles = ["Scholarship", "Hypertension", "Diabetes", "Alcoholism", "Disability", "SMS Received"]
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    for ax, flag, title in zip(axes.flat, flags, titles):
        rates = df.groupby(flag)["noshow_flag"].mean().reindex([0, 1])
        bars = ax.bar(["No (0)", "Yes (1)"], rates.values * 100, color=["#3498db", "#e74c3c"])
        ax.axhline(overall_rate * 100, color="gray", linestyle="--", linewidth=1, label=f"Overall: {overall_rate*100:.1f}%")
        for bar, rate in zip(bars, rates.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    f"{rate*100:.1f}%", ha="center", va="bottom", fontsize=9)
        ax.set_title(f"No-Show Rate: {title}")
        ax.set_ylabel("No-Show Rate (%)")
        ax.set_ylim(0, max(rates.values) * 100 * 1.25)
        ax.legend(fontsize=7)
    fig.suptitle("No-Show Rate by Patient Condition", fontsize=14, y=1.01)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "13_noshow_by_conditions.png", dpi=DPI, bbox_inches="tight")
    plt.close("all")
    print("  Saved 13_noshow_by_conditions.png")


def plot_noshow_by_weekday(df: pd.DataFrame, overall_rate: float) -> None:
    rates = df.groupby("appointment_dow")["noshow_flag"].mean().reindex(DOW_ORDER)
    labels = [DOW_NAMES[d] for d in DOW_ORDER]
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    noshow_bar(ax, labels, rates.values, overall_rate,
               "No-Show Rate by Day of Week", xlabel="Day of Week")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "14_noshow_by_weekday.png", dpi=DPI)
    plt.close("all")
    print("  Saved 14_noshow_by_weekday.png")


def plot_noshow_by_neighbourhood(df: pd.DataFrame, overall_rate: float) -> None:
    vol = df["Neighbourhood"].value_counts()
    top30 = vol.head(30).index
    sub = df[df["Neighbourhood"].isin(top30)]
    rates = sub.groupby("Neighbourhood")["noshow_flag"].mean().sort_values()

    cmap = matplotlib.colormaps["RdYlGn_r"]
    norm_vals = (rates.values - rates.values.min()) / (rates.values.max() - rates.values.min())
    colors = [cmap(v) for v in norm_vals]

    fig, ax = plt.subplots(figsize=(10, 12))
    ax.barh(rates.index, rates.values * 100, color=colors)
    ax.axvline(overall_rate * 100, color="black", linestyle="--", linewidth=1.2,
               label=f"Overall: {overall_rate*100:.1f}%")
    ax.set_title("No-Show Rate for Top 30 Neighbourhoods by Volume")
    ax.set_xlabel("No-Show Rate (%)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "15_noshow_by_neighbourhood.png", dpi=DPI)
    plt.close("all")
    print("  Saved 15_noshow_by_neighbourhood.png")


def plot_noshow_by_month(df: pd.DataFrame, overall_rate: float) -> None:
    month_map = {4: "April", 5: "May", 6: "June"}
    rates = df.groupby("appointment_month")["noshow_flag"].mean()
    labels = [month_map.get(m, str(m)) for m in rates.index]
    fig, ax = plt.subplots(figsize=(7, 5))
    noshow_bar(ax, labels, rates.values, overall_rate,
               "No-Show Rate by Appointment Month")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "16_noshow_by_month.png", dpi=DPI)
    plt.close("all")
    print("  Saved 16_noshow_by_month.png")


def plot_repeat_patient_noshow(df: pd.DataFrame, overall_rate: float) -> None:
    """Prior no-show rate for each patient (excluding current row) vs current no-show."""
    # Sort by appointment date for chronological ordering
    df_sorted = df.sort_values("appointment_dt").copy()
    df_sorted["cumulative_noshow"] = df_sorted.groupby("PatientId")["noshow_flag"].cumsum()
    df_sorted["cumulative_count"] = df_sorted.groupby("PatientId").cumcount()
    # Prior rate: cumulative up to (but not including) current row
    df_sorted["prior_noshow_rate"] = (
        (df_sorted["cumulative_noshow"] - df_sorted["noshow_flag"]) /
        df_sorted["cumulative_count"].replace(0, np.nan)
    )
    # First appointment has no prior history — drop those
    has_prior = df_sorted["cumulative_count"] > 0
    df_prior = df_sorted[has_prior].copy()

    bins = [-0.001, 0.0, 0.25, 0.50, 0.75, 1.001]
    labels = ["0%", "1-25%", "26-50%", "51-75%", "76-100%"]
    df_prior["prior_bucket"] = pd.cut(df_prior["prior_noshow_rate"], bins=bins, labels=labels)
    rates = df_prior.groupby("prior_bucket", observed=True)["noshow_flag"].mean().reindex(labels)

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    noshow_bar(ax, labels, rates.values, overall_rate,
               "Prior No-Show Rate vs Current No-Show",
               xlabel="Prior No-Show Rate Bucket")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "17_repeat_patient_noshow.png", dpi=DPI)
    plt.close("all")
    print("  Saved 17_repeat_patient_noshow.png")


def plot_correlation_heatmap(df: pd.DataFrame) -> None:
    cols = ["Age", "lead_days", "Scholarship", "Hipertension", "Diabetes",
            "Alcoholism", "handcap_binary", "SMS_received", "noshow_flag"]
    corr = df[cols].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                square=True, linewidths=0.5, ax=ax)
    ax.set_title("Correlation Heatmap: Features vs No-Show")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "18_correlation_heatmap.png", dpi=DPI)
    plt.close("all")
    print("  Saved 18_correlation_heatmap.png")


def build_summary_stats(df: pd.DataFrame, overall_rate: float) -> pd.DataFrame:
    rows: list[dict] = []

    rows.append({"metric": "Total appointments (after cleaning)", "value": len(df)})
    rows.append({"metric": "Total unique patients", "value": df["PatientId"].nunique()})
    rows.append({"metric": "Overall no-show rate (%)", "value": f"{overall_rate*100:.2f}"})

    for gender in ["F", "M"]:
        rate = df[df["Gender"] == gender]["noshow_flag"].mean()
        rows.append({"metric": f"No-show rate — Gender {gender} (%)", "value": f"{rate*100:.2f}"})

    for bucket in ["same-day", "1-7d", "8-30d", "31-90d", "90d+"]:
        sub = df[df["lead_bucket"] == bucket]
        if len(sub) > 0:
            rate = sub["noshow_flag"].mean()
            rows.append({"metric": f"No-show rate — Lead bucket {bucket} (%)", "value": f"{rate*100:.2f}"})

    for sms in [0, 1]:
        rate = df[df["SMS_received"] == sms]["noshow_flag"].mean()
        label = "No SMS" if sms == 0 else "SMS received"
        rows.append({"metric": f"No-show rate — {label} (%)", "value": f"{rate*100:.2f}"})

    rows.append({"metric": "Mean lead_days", "value": f"{df['lead_days'].mean():.1f}"})
    rows.append({"metric": "Median lead_days", "value": f"{df['lead_days'].median():.0f}"})

    most_common_nb = df["Neighbourhood"].value_counts().idxmax()
    rows.append({"metric": "Most common neighbourhood", "value": most_common_nb})

    nb_stats = df.groupby("Neighbourhood").agg(
        count=("noshow_flag", "count"),
        rate=("noshow_flag", "mean")
    )
    nb_filtered = nb_stats[nb_stats["count"] >= 50]
    rows.append({"metric": "Neighbourhood with highest no-show rate (min 50 appts)",
                 "value": f"{nb_filtered['rate'].idxmax()} ({nb_filtered['rate'].max()*100:.1f}%)"})
    rows.append({"metric": "Neighbourhood with lowest no-show rate (min 50 appts)",
                 "value": f"{nb_filtered['rate'].idxmin()} ({nb_filtered['rate'].min()*100:.1f}%)"})

    return pd.DataFrame(rows)


def main() -> None:
    plt.style.use(STYLE)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    assert_inputs()

    print("Loading clean.csv ...")
    df = load_clean()
    print(f"  Shape: {df.shape}")
    overall_rate = df["noshow_flag"].mean()
    print(f"  Overall no-show rate: {overall_rate*100:.2f}%")

    print("\n--- Generating bivariate plots ---")
    plot_noshow_by_gender(df, overall_rate)
    plot_noshow_by_age_group(df, overall_rate)
    plot_noshow_by_lead_days(df, overall_rate)
    plot_noshow_by_sms(df, overall_rate)
    plot_noshow_by_conditions(df, overall_rate)
    plot_noshow_by_weekday(df, overall_rate)
    plot_noshow_by_neighbourhood(df, overall_rate)
    plot_noshow_by_month(df, overall_rate)
    plot_repeat_patient_noshow(df, overall_rate)
    plot_correlation_heatmap(df)

    print("\n--- Building summary_stats.csv ---")
    stats = build_summary_stats(df, overall_rate)
    stats.to_csv(OUTPUT_DIR / "summary_stats.csv", index=False)
    print(f"  Saved summary_stats.csv ({len(stats)} rows)")

    print("\n=== Phase 2 Complete — 10 plots + summary_stats.csv saved ===")


if __name__ == "__main__":
    main()
