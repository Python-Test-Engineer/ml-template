"""Phase 1 — ETL & Preprocessing
Loads kaggle.csv and web_traffic.csv, removes dirty rows,
engineers derived columns, saves clean parquets and dirty.csv.
"""
from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd
from scipy import stats

# ── Constants ────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path("output/PROJECT_02")
RANDOM_SEED = 42

SUPERSTORE_COLS = [
    "Row ID", "Order ID", "Order Date", "Ship Date", "Ship Mode",
    "Customer ID", "Customer Name", "Segment", "Country", "City",
    "State", "Postal Code", "Region", "Product ID", "Category",
    "Sub-Category", "Product Name", "Sales", "Quantity", "Discount", "Profit",
]
WEB_TRAFFIC_COLS = [
    "Page Views", "Session Duration", "Bounce Rate", "Traffic Source",
    "Time on Page", "Previous Visits", "Conversion Rate",
]
Z_SCORE_THRESHOLD = 3.0


# ── Helpers ───────────────────────────────────────────────────────────────────
def create_dirs() -> None:
    for sub in ["plots", "tables", "model"]:
        (OUTPUT_DIR / sub).mkdir(parents=True, exist_ok=True)
    print(f"[Phase 1] Output directories ready under {OUTPUT_DIR}")


def load_superstore(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Superstore dataset not found: {path}")
    df = pd.read_csv(path, encoding="latin-1")
    missing = set(SUPERSTORE_COLS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected Superstore columns: {missing}")
    return df


def load_web_traffic(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Web traffic dataset not found: {path}")
    df = pd.read_csv(path, encoding="latin-1")
    missing = set(WEB_TRAFFIC_COLS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected web traffic columns: {missing}")
    return df


def flag_superstore_dirty(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (clean_df, dirty_df) after applying Superstore dirty-row rules."""
    dirty_parts: list[pd.DataFrame] = []

    # Rule 1: Sales <= 0
    mask_sales = df["Sales"] <= 0
    if mask_sales.any():
        part = df[mask_sales].copy()
        part["source_file"] = "kaggle.csv"
        part["reason"] = "sales_zero_or_negative"
        dirty_parts.append(part)

    # Rule 2: Profit extreme outlier (|z| > 3)
    z = stats.zscore(df["Profit"])
    mask_profit = abs(z) > Z_SCORE_THRESHOLD
    # Don't double-count rows already flagged by rule 1
    mask_profit_only = mask_profit & ~mask_sales
    if mask_profit_only.any():
        part = df[mask_profit_only].copy()
        part["source_file"] = "kaggle.csv"
        part["reason"] = "profit_extreme_outlier"
        dirty_parts.append(part)

    combined_dirty_mask = mask_sales | mask_profit
    dirty_df = pd.concat(dirty_parts, ignore_index=True) if dirty_parts else pd.DataFrame(columns=df.columns.tolist() + ["source_file", "reason"])
    clean_df = df[~combined_dirty_mask].copy()

    if len(dirty_df) == 0:
        warnings.warn("Superstore: 0 dirty rows found — verify dirty-row rules are applied correctly.")

    return clean_df, dirty_df


def engineer_superstore(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns and drop unneeded ones."""
    df = df.copy()
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=False)
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], dayfirst=False)
    df["days_to_ship"] = (df["Ship Date"] - df["Order Date"]).dt.days.astype(int)
    df["profit_margin"] = df["Profit"] / df["Sales"]
    df["order_month"] = df["Order Date"].dt.month.astype(int)
    df["order_year"] = df["Order Date"].dt.year.astype(int)
    df["order_dayofweek"] = df["Order Date"].dt.dayofweek.astype(int)
    df["is_loss"] = (df["Profit"] < 0).astype(int)
    df = df.drop(columns=["Country", "Row ID"])
    return df


def flag_webtraffic_dirty(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (clean_df, dirty_df) after applying web traffic dirty-row rules."""
    mask = df["Page Views"] == 0
    dirty_df = df[mask].copy()
    dirty_df["source_file"] = "web_traffic.csv"
    dirty_df["reason"] = "zero_page_views"
    clean_df = df[~mask].copy()

    if len(dirty_df) == 0:
        warnings.warn("Web traffic: 0 dirty rows found — verify dirty-row rules are applied correctly.")

    return clean_df, dirty_df


def engineer_webtraffic(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["converted"] = (df["Conversion Rate"] >= 1.0).astype(int)
    df["visits_bin"] = pd.cut(
        df["Previous Visits"],
        bins=[-1, 0, 2, 9],
        labels=["0", "1-2", "3+"],
    )
    return df


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    create_dirs()

    # ── Superstore ────────────────────────────────────────────────────────────
    print("\n[Phase 1] Loading Superstore (kaggle.csv)…")
    ss_raw = load_superstore(Path("data/kaggle.csv"))
    print(f"  Raw shape: {ss_raw.shape}")

    ss_clean, ss_dirty = flag_superstore_dirty(ss_raw)
    print(f"  After dirty-row removal: {ss_clean.shape}  ({len(ss_dirty)} rows removed)")
    if len(ss_dirty) > 0:
        for reason, cnt in ss_dirty["reason"].value_counts().items():
            print(f"    {reason}: {cnt}")

    ss_clean = engineer_superstore(ss_clean)
    print(f"  Derived columns added. Final shape: {ss_clean.shape}")

    # ── Web Traffic ───────────────────────────────────────────────────────────
    print("\n[Phase 1] Loading Web Traffic (web_traffic.csv)…")
    wt_raw = load_web_traffic(Path("data/web_traffic.csv"))
    print(f"  Raw shape: {wt_raw.shape}")

    wt_clean, wt_dirty = flag_webtraffic_dirty(wt_raw)
    print(f"  After dirty-row removal: {wt_clean.shape}  ({len(wt_dirty)} rows removed)")
    if len(wt_dirty) > 0:
        for reason, cnt in wt_dirty["reason"].value_counts().items():
            print(f"    {reason}: {cnt}")

    wt_clean = engineer_webtraffic(wt_clean)
    print(f"  Derived columns added. Final shape: {wt_clean.shape}")

    # ── Save outputs ──────────────────────────────────────────────────────────
    # Combine dirty rows (align columns)
    all_dirty = pd.concat([ss_dirty, wt_dirty], ignore_index=True)
    dirty_path = OUTPUT_DIR / "dirty.csv"
    all_dirty.to_csv(dirty_path, index=False)
    print(f"\n[Phase 1] dirty.csv saved -> {dirty_path}  ({len(all_dirty)} total rows)")

    ss_path = OUTPUT_DIR / "superstore_clean.parquet"
    ss_clean.to_parquet(ss_path, index=False)
    print(f"[Phase 1] superstore_clean.parquet saved -> {ss_path}")

    wt_path = OUTPUT_DIR / "webtraffic_clean.parquet"
    wt_clean.to_parquet(wt_path, index=False)
    print(f"[Phase 1] webtraffic_clean.parquet saved -> {wt_path}")

    print("\n[Phase 1] OK Complete\n")


if __name__ == "__main__":
    main()
