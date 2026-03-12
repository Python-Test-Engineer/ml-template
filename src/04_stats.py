"""Phase 4 — Statistical Tests: Kruskal-Wallis by Traffic Source, Pearson correlations."""

from pathlib import Path
import pandas as pd
from scipy import stats

RANDOM_SEED = 42
OUTPUT_DIR = Path("output/PROJECT_01")
CLEAN_PATH = OUTPUT_DIR / "clean.csv"

TARGET_COLUMNS = [
    "Session Duration",
    "Bounce Rate",
    "Conversion Rate",
    "Page Views",
    "Time on Page",
]
P_THRESHOLD = 0.05


def load_clean(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise ValueError(f"clean.csv not found: {path}")
    return pd.read_csv(path)


def run_kruskal_wallis(df: pd.DataFrame, target: str) -> dict:
    groups = [group[target].values for _, group in df.groupby("Traffic Source")]
    h_stat, p_value = stats.kruskal(*groups)
    return {
        "target": target,
        "H_stat": round(h_stat, 4),
        "p_value": round(p_value, 4),
        "significant": p_value < P_THRESHOLD,
    }


def print_kw_results(results_df: pd.DataFrame) -> None:
    print("\n--- Kruskal-Wallis H-test (grouped by Traffic Source) ---")
    print(results_df.to_string(index=False))


def print_pearson_correlations(df: pd.DataFrame) -> None:
    numeric_cols = ["Page Views", "Session Duration", "Bounce Rate",
                    "Time on Page", "Previous Visits"]
    print("\n--- Pearson Correlations with Conversion Rate ---")
    for col in numeric_cols:
        r, p = stats.pearsonr(df["Conversion Rate"], df[col])
        sig = "**" if p < P_THRESHOLD else ""
        print(f"  {col:<25} r = {r:+.4f}  p = {p:.4f} {sig}")
    print()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_clean(CLEAN_PATH)

    print("=" * 60)
    print("PHASE 4 — STATISTICAL TESTS")
    print("=" * 60)
    print(f"Loaded clean data: {df.shape[0]} rows")

    results = [run_kruskal_wallis(df, col) for col in TARGET_COLUMNS]
    results_df = pd.DataFrame(results)

    out_path = OUTPUT_DIR / "stats.csv"
    results_df.to_csv(out_path, index=False)

    print_kw_results(results_df)
    print_pearson_correlations(df)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
