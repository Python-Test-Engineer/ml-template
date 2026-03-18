"""Phase 1 — ETL & Cleaning
Load raw sales CSV, normalise dates, detect and remove dirty rows,
add derived columns, write clean.csv and dirty.csv.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd

RANDOM_SEED = 42
OUTPUT_DIR = Path("output/PROJECT_01")
CHARTS_DIR = OUTPUT_DIR / "charts"
DATA_PATH = Path("data/data.csv")

EXPECTED_COLUMNS = [
    "order_id", "date", "customer_name", "customer_email",
    "region", "product", "category", "quantity", "unit_price",
    "discount_pct", "total", "sales_rep", "status",
]

QTY_THRESHOLD = 50  # D2 dirty rule: quantity > this value -> dirty


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def setup_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[setup] Output dirs ready: {OUTPUT_DIR}, {CHARTS_DIR}")


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load_raw(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"data/data.csv not found at {path.resolve()}")
    df = pd.read_csv(path)
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing expected column(s): {missing_cols}")
    print(f"[load] Loaded {len(df)} rows, {len(df.columns)} columns from {path}")
    return df


# ---------------------------------------------------------------------------
# Date normalisation
# ---------------------------------------------------------------------------

def normalise_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse date column, handling mixed YYYY-MM-DD and DD-MM-YYYY formats."""
    raw = df["date"].copy()
    parsed = pd.to_datetime(raw, format="mixed", dayfirst=False, errors="coerce")

    # Retry unparseable rows with dayfirst=True
    bad_mask = parsed.isna()
    if bad_mask.any():
        retry = pd.to_datetime(raw[bad_mask], format="mixed", dayfirst=True, errors="coerce")
        parsed[bad_mask] = retry

    # Final check
    still_bad = parsed.isna()
    if still_bad.any():
        bad_rows = df.loc[still_bad, ["order_id", "date"]]
        for _, row in bad_rows.iterrows():
            raise ValueError(
                f"Cannot parse date in row {row['order_id']}: '{row['date']}'"
            )

    df = df.copy()
    df["date"] = parsed
    fixed_count = bad_mask.sum()
    if fixed_count:
        print(f"[dates] Normalised {fixed_count} DD-MM-YYYY date(s) to YYYY-MM-DD")
    else:
        print("[dates] All dates in consistent format — no normalisation needed")
    return df


# ---------------------------------------------------------------------------
# Dirty-row detection
# ---------------------------------------------------------------------------

def detect_dirty_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (clean_df, dirty_df) where dirty_df has an added 'reason' column."""
    reasons: dict[int, list[str]] = {i: [] for i in df.index}

    # D1: negative unit_price
    d1 = df["unit_price"] < 0
    for i in df.index[d1]:
        reasons[i].append("negative unit_price")

    # D2: extreme quantity
    d2 = df["quantity"] > QTY_THRESHOLD
    for i in df.index[d2]:
        reasons[i].append(f"quantity exceeds threshold (>{QTY_THRESHOLD})")

    # D3: total mismatch
    calc_total = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)
    d3 = (df["total"] - calc_total).abs() > 0.01
    for i in df.index[d3]:
        reasons[i].append("total_mismatch")

    dirty_mask = d1 | d2 | d3
    dirty_df = df[dirty_mask].copy()
    dirty_df["reason"] = ["; ".join(reasons[i]) for i in dirty_df.index]

    clean_df = df[~dirty_mask].copy()
    return clean_df, dirty_df


# ---------------------------------------------------------------------------
# Derived columns
# ---------------------------------------------------------------------------

def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["revenue"] = df["total"]
    df["is_pending"] = df["status"] == "Pending"
    df["missing_email"] = df["customer_email"].isna()
    df["missing_rep"] = df["sales_rep"].isna()
    return df


# ---------------------------------------------------------------------------
# Post-clean validation
# ---------------------------------------------------------------------------

def validate_clean(df: pd.DataFrame) -> None:
    assert (df["unit_price"] >= 0).all(), "Negative unit_price found in clean dataset"
    assert (df["quantity"] <= QTY_THRESHOLD).all(), "quantity > threshold in clean dataset"
    calc_total = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)
    mismatches = (df["total"] - calc_total).abs() > 0.01
    assert not mismatches.any(), "total_mismatch found in clean dataset"
    assert not df["date"].isna().any(), "NaT values found in date column"
    print("[validate] All post-clean assertions passed")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    setup_dirs()

    df = load_raw(DATA_PATH)
    df = normalise_dates(df)

    clean_df, dirty_df = detect_dirty_rows(df)

    dirty_path = OUTPUT_DIR / "dirty.csv"
    dirty_df.to_csv(dirty_path, index=False)
    print(f"[dirty] Dirty rows removed: {len(dirty_df)} -> {dirty_path}")
    if len(dirty_df):
        for _, row in dirty_df.iterrows():
            print(f"        {row['order_id']}: {row['reason']}")

    clean_df = add_derived_columns(clean_df)
    validate_clean(clean_df)

    clean_path = OUTPUT_DIR / "clean.csv"
    clean_df.to_csv(clean_path, index=False)
    print(f"[clean] Clean dataset: {len(clean_df)} rows -> {clean_path}")

    # Report missing values retained
    missing_email = clean_df["missing_email"].sum()
    missing_rep = clean_df["missing_rep"].sum()
    print(f"[info]  Missing customer_email: {missing_email} row(s) retained")
    print(f"[info]  Missing sales_rep:      {missing_rep} row(s) retained")


if __name__ == "__main__":
    main()
