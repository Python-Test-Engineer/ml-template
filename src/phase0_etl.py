"""Phase 0 — ETL & Cleaning
Loads raw kaggle.csv, engineers features, removes dirty rows, saves clean.csv + dirty.csv.
"""
import matplotlib
matplotlib.use("Agg")

from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path("output/PROJECT_01")
PLOTS_DIR = OUTPUT_DIR / "plots"
DATA_FILE = Path("data/kaggle.csv")

EXPECTED_COLUMNS = [
    "PatientId", "AppointmentID", "Gender", "ScheduledDay",
    "AppointmentDay", "Age", "Neighbourhood", "Scholarship",
    "Hipertension", "Diabetes", "Alcoholism", "Handcap",
    "SMS_received", "No-show",
]

AGE_BINS = [-1, 10, 20, 30, 40, 50, 60, 70, 80, 200]
AGE_LABELS = ["0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81+"]

LEAD_BINS = [-1, 0, 7, 30, 90, 10000]
LEAD_LABELS = ["same-day", "1-7d", "8-30d", "31-90d", "90d+"]


def assert_file_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}. Ensure data/kaggle.csv is present.")


def assert_columns(df: pd.DataFrame, expected: list[str]) -> None:
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")


def load_raw(path: Path) -> pd.DataFrame:
    print(f"Loading {path} ...")
    df = pd.read_csv(path)
    assert_columns(df, EXPECTED_COLUMNS)
    print(f"  Raw shape: {df.shape}")
    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["scheduled_dt"] = pd.to_datetime(df["ScheduledDay"], utc=True).dt.tz_localize(None)
    df["appointment_dt"] = pd.to_datetime(df["AppointmentDay"], utc=True).dt.tz_localize(None)
    return df


def compute_lead_days(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    sched_dates = df["scheduled_dt"].dt.date
    appt_dates = df["appointment_dt"].dt.date
    df["lead_days"] = (appt_dates - sched_dates).apply(lambda x: x.days)
    return df


def identify_dirty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return dataframe of dirty rows with a 'reason' column (first matching rule wins)."""
    reasons = pd.Series("", index=df.index)
    reasons[df["Age"] < 0] = "negative age"
    reasons[(reasons == "") & (df["Age"] > 115)] = "age > 115"
    reasons[(reasons == "") & (df["lead_days"] < 0)] = "appointment before scheduled date"
    dirty_mask = reasons != ""
    dirty = df[dirty_mask].copy()
    dirty["reason"] = reasons[dirty_mask]
    return dirty


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["noshow_flag"] = (df["No-show"] == "Yes").astype(int)
    df["appointment_dow"] = df["appointment_dt"].dt.dayofweek
    df["appointment_month"] = df["appointment_dt"].dt.month
    df["handcap_binary"] = (df["Handcap"] > 0).astype(int)
    df["age_group"] = pd.cut(df["Age"], bins=AGE_BINS, labels=AGE_LABELS, right=True)
    df["lead_bucket"] = pd.cut(df["lead_days"], bins=LEAD_BINS, labels=LEAD_LABELS, right=True)
    return df


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    assert_file_exists(DATA_FILE)
    df = load_raw(DATA_FILE)
    df = parse_dates(df)
    df = compute_lead_days(df)

    dirty = identify_dirty_rows(df)
    print(f"\n--- Dirty rows: {len(dirty)} ---")
    if len(dirty) > 0:
        print(dirty[["PatientId", "Age", "lead_days", "reason"]].to_string())

    # Save dirty rows (original columns + reason; exclude engineered cols not yet added)
    dirty_out = dirty[[c for c in EXPECTED_COLUMNS] + ["reason"]].copy()
    dirty_out.to_csv(OUTPUT_DIR / "dirty.csv", index=False)
    print(f"  Saved {len(dirty_out)} dirty rows to {OUTPUT_DIR / 'dirty.csv'}")

    # Drop dirty rows
    clean = df[~df.index.isin(dirty.index)].copy()
    print(f"\n  Rows retained: {len(clean)} (removed {len(dirty)})")

    # Engineer features on clean data
    clean = engineer_features(clean)

    # Save clean CSV: original columns first, then engineered
    engineered_cols = [
        "scheduled_dt", "appointment_dt", "lead_days", "noshow_flag",
        "appointment_dow", "appointment_month", "handcap_binary", "age_group", "lead_bucket",
    ]
    col_order = EXPECTED_COLUMNS + engineered_cols
    clean[col_order].to_csv(OUTPUT_DIR / "clean.csv", index=False)

    print(f"\n=== Phase 0 Complete ===")
    print(f"  Total raw rows    : {len(df)}")
    print(f"  Dirty rows removed: {len(dirty)}")
    print(f"  Clean rows saved  : {len(clean)}")
    print(f"  lead_days range   : {clean['lead_days'].min()} – {clean['lead_days'].max()}")
    print(f"  Output: {OUTPUT_DIR / 'clean.csv'}")


if __name__ == "__main__":
    main()
