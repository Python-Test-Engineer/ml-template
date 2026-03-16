"""Phase 2 — Clean: apply dirty-row rules, save dirty.csv + clean.csv, derive converted flag."""

from pathlib import Path
import pandas as pd

RANDOM_SEED = 42
OUTPUT_DIR = Path("output/PROJECT_01")
DATA_PATH = Path("data/data.csv")

VALID_TRAFFIC_SOURCES = {"Organic", "Social", "Paid", "Direct", "Referral"}


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise ValueError(f"Data file not found: {path}")
    return pd.read_csv(path)


def tag_dirty_rows(df: pd.DataFrame) -> pd.Series:
    """Return a Series of reason strings; empty string means row is clean."""
    reason = pd.Series("", index=df.index)

    # Rule 1 — any null
    null_mask = df.isnull().any(axis=1) & (reason == "")
    reason[null_mask] = "null_value"

    # Rule 2 — Session Duration < 0.1
    mask = (df["Session Duration"] < 0.1) & (reason == "")
    reason[mask] = "session_duration_too_short"

    # Rule 3 — Time on Page < 0.1
    mask = (df["Time on Page"] < 0.1) & (reason == "")
    reason[mask] = "time_on_page_too_short"

    # Rule 4 — Bounce Rate out of range
    mask = ((df["Bounce Rate"] < 0) | (df["Bounce Rate"] > 1)) & (reason == "")
    reason[mask] = "bounce_rate_out_of_range"

    # Rule 5 — Conversion Rate out of range
    mask = ((df["Conversion Rate"] < 0) | (df["Conversion Rate"] > 1)) & (reason == "")
    reason[mask] = "conversion_rate_out_of_range"

    # Rule 6 — Page Views < 1
    mask = (df["Page Views"] < 1) & (reason == "")
    reason[mask] = "page_views_invalid"

    # Rule 7 — Unknown Traffic Source
    mask = (~df["Traffic Source"].isin(VALID_TRAFFIC_SOURCES)) & (reason == "")
    reason[mask] = "unknown_traffic_source"

    return reason


def print_summary(total: int, dirty: pd.DataFrame, clean: pd.DataFrame) -> None:
    print("=" * 60)
    print("PHASE 2 — CLEAN")
    print("=" * 60)
    print(f"Total rows loaded : {total}")
    print(f"Dirty rows removed: {len(dirty)}")
    if len(dirty) > 0:
        breakdown = dirty["reason"].value_counts()
        for reason, count in breakdown.items():
            print(f"  {reason}: {count}")
    print(f"Clean rows retained: {len(clean)}")
    print()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data(DATA_PATH)
    total = len(df)

    reason = tag_dirty_rows(df)

    dirty_mask = reason != ""
    dirty_df = df[dirty_mask].copy()
    dirty_df["reason"] = reason[dirty_mask]

    clean_df = df[~dirty_mask].copy()
    clean_df["converted"] = (clean_df["Conversion Rate"] == 1.0).astype(int)

    dirty_path = OUTPUT_DIR / "dirty.csv"
    clean_path = OUTPUT_DIR / "clean.csv"
    dirty_df.to_csv(dirty_path, index=False)
    clean_df.to_csv(clean_path, index=False)

    print_summary(total, dirty_df, clean_df)
    print(f"Saved: {dirty_path}")
    print(f"Saved: {clean_path}")


if __name__ == "__main__":
    main()
