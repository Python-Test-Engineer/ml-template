"""Phase 1 — Audit: load raw data, profile nulls/types/ranges, save audit.csv."""

from pathlib import Path
import warnings
import pandas as pd

RANDOM_SEED = 42
OUTPUT_DIR = Path("output/PROJECT_01")
DATA_PATH = Path("data/data.csv")

EXPECTED_COLUMNS = [
    "Page Views",
    "Session Duration",
    "Bounce Rate",
    "Traffic Source",
    "Time on Page",
    "Previous Visits",
    "Conversion Rate",
]

NUMERIC_COLUMNS = [
    "Page Views",
    "Session Duration",
    "Bounce Rate",
    "Time on Page",
    "Previous Visits",
    "Conversion Rate",
]


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise ValueError(f"Data file not found: {path}")
    df = pd.read_csv(path)
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")
    return df


def profile_columns(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        series = df[col]
        is_numeric = pd.api.types.is_numeric_dtype(series)
        row: dict = {
            "column": col,
            "dtype": str(series.dtype),
            "total_count": len(series),
            "null_count": series.isna().sum(),
            "null_pct": round(series.isna().mean() * 100, 2),
            "unique_count": series.nunique(),
            "min": series.min() if is_numeric else None,
            "max": series.max() if is_numeric else None,
            "mean": round(series.mean(), 4) if is_numeric else None,
            "std": round(series.std(), 4) if is_numeric else None,
            "p25": round(series.quantile(0.25), 4) if is_numeric else None,
            "p50": round(series.quantile(0.50), 4) if is_numeric else None,
            "p75": round(series.quantile(0.75), 4) if is_numeric else None,
        }
        rows.append(row)
    return pd.DataFrame(rows)


def print_summary(df: pd.DataFrame, profile: pd.DataFrame) -> None:
    print("=" * 60)
    print("PHASE 1 — AUDIT")
    print("=" * 60)
    print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print()
    print(profile[["column", "dtype", "null_count", "null_pct", "unique_count"]].to_string(index=False))
    print()
    print("--- Traffic Source value counts ---")
    vc = df["Traffic Source"].value_counts()
    prop = df["Traffic Source"].value_counts(normalize=True).round(4)
    ts_summary = pd.DataFrame({"count": vc, "proportion": prop})
    print(ts_summary.to_string())
    print()
    print("--- Numeric summary ---")
    print(profile[profile["mean"].notna()][["column", "min", "max", "mean", "std", "p25", "p50", "p75"]].to_string(index=False))
    print()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data(DATA_PATH)
    profile = profile_columns(df)
    print_summary(df, profile)
    out_path = OUTPUT_DIR / "audit.csv"
    profile.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
