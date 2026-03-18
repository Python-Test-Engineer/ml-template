"""Phase 2 -- EDA & Summaries
Compute statistical summaries and aggregations from clean.csv,
write summary_stats.csv in long format (table, metric_name, metric_value).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RANDOM_SEED = 42
OUTPUT_DIR = Path("output/PROJECT_01")
CLEAN_CSV = OUTPUT_DIR / "clean.csv"
STATS_CSV = OUTPUT_DIR / "summary_stats.csv"


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load_clean() -> pd.DataFrame:
    if not OUTPUT_DIR.exists():
        raise FileNotFoundError("Run phase1_etl.py first")
    if not CLEAN_CSV.exists():
        raise FileNotFoundError(f"clean.csv not found: {CLEAN_CSV}")
    df = pd.read_csv(CLEAN_CSV, parse_dates=["date"])
    df["month"] = df["month"].astype(str)
    print(f"[load] Loaded clean.csv: {len(df)} rows")
    return df


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

def agg_monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    grp = (
        df.groupby("month", sort=True)
        .agg(revenue_sum=("revenue", "sum"), aov=("revenue", "mean"), order_count=("order_id", "count"))
        .reset_index()
    )
    grp["mom_growth_pct"] = grp["revenue_sum"].pct_change() * 100
    return grp


def agg_by_col(df: pd.DataFrame, col: str) -> pd.DataFrame:
    return (
        df.groupby(col, dropna=False)
        .agg(revenue_sum=("revenue", "sum"), aov=("revenue", "mean"), order_count=("order_id", "count"))
        .reset_index()
        .sort_values("revenue_sum", ascending=False)
    )


def agg_sales_rep(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("sales_rep", dropna=False)
        .agg(
            revenue_sum=("revenue", "sum"),
            aov=("revenue", "mean"),
            order_count=("order_id", "count"),
            avg_discount=("discount_pct", "mean"),
        )
        .reset_index()
        .sort_values("revenue_sum", ascending=False)
    )


def agg_top_customers(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("customer_name")
        .agg(revenue_sum=("revenue", "sum"), order_count=("order_id", "count"))
        .reset_index()
        .sort_values("revenue_sum", ascending=False)
        .head(n)
    )


def agg_customer_concentration(df: pd.DataFrame) -> pd.DataFrame:
    total_rev = df["revenue"].sum()
    cust = (
        df.groupby("customer_name")["revenue"].sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    cust["cumulative_revenue"] = cust["revenue"].cumsum()
    rows = []
    for n in [1, 3, 5, 10]:
        top_n_rev = cust.head(n)["revenue"].sum()
        rows.append({"top_n": n, "revenue_sum": top_n_rev, "pct_of_total": top_n_rev / total_rev * 100})
    return pd.DataFrame(rows)


def agg_status_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("status")
        .agg(order_count=("order_id", "count"), revenue_sum=("revenue", "sum"))
        .reset_index()
    )


def agg_region_category_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    pivot = df.pivot_table(values="revenue", index="region", columns="category", aggfunc="sum", fill_value=0)
    # Return as long format for CSV storage
    return pivot.reset_index().melt(id_vars="region", var_name="category", value_name="revenue_sum")


def agg_discount_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("category")
        .agg(avg_discount=("discount_pct", "mean"), max_discount=("discount_pct", "max"), min_discount=("discount_pct", "min"))
        .reset_index()
    )


def compute_kpis(df: pd.DataFrame) -> dict[str, object]:
    total_rev = df["revenue"].sum()
    cust_orders = df.groupby("customer_name")["order_id"].count()

    kpis: dict[str, object] = {
        "total_revenue": round(total_rev, 2),
        "order_count": len(df),
        "avg_order_value": round(df["revenue"].mean(), 2),
        "median_order_value": round(df["revenue"].median(), 2),
        "top_region": df.groupby("region")["revenue"].sum().idxmax(),
        "top_product": df.groupby("product")["revenue"].sum().idxmax(),
        "top_sales_rep": df.groupby("sales_rep")["revenue"].sum().idxmax(),
        "top_customer": df.groupby("customer_name")["revenue"].sum().idxmax(),
        "pending_count": int(df["is_pending"].sum()),
        "pending_revenue": round(df.loc[df["is_pending"], "revenue"].sum(), 2),
        "repeat_customer_count": int((cust_orders > 1).sum()),
        "one_time_customer_count": int((cust_orders == 1).sum()),
    }
    return kpis


# ---------------------------------------------------------------------------
# Long-format serialisation
# ---------------------------------------------------------------------------

def to_long(table_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Convert a wide aggregation table to long format rows."""
    rows = []
    for _, row in df.iterrows():
        # Build a composite metric_name from all non-numeric index columns + metric
        id_cols = [c for c in df.columns if df[c].dtype == object or df[c].dtype.name in ("string", "category", "bool")]
        # Identify the label prefix from id columns
        prefix = " | ".join(str(row[c]) for c in id_cols) if id_cols else ""
        for col in df.columns:
            if col in id_cols:
                continue
            metric_name = f"{prefix} :: {col}" if prefix else col
            rows.append({"table": table_name, "metric_name": metric_name, "metric_value": row[col]})
    return pd.DataFrame(rows)


def kpis_to_long(kpis: dict[str, object]) -> pd.DataFrame:
    rows = [{"table": "kpis", "metric_name": k, "metric_value": v} for k, v in kpis.items()]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    df = load_clean()

    tables = {
        "monthly_revenue": agg_monthly_revenue(df),
        "revenue_by_region": agg_by_col(df, "region"),
        "revenue_by_category": agg_by_col(df, "category"),
        "revenue_by_product": agg_by_col(df, "product"),
        "sales_rep_performance": agg_sales_rep(df),
        "top_customers": agg_top_customers(df),
        "customer_concentration": agg_customer_concentration(df),
        "status_breakdown": agg_status_breakdown(df),
        "region_category_heatmap": agg_region_category_heatmap(df),
        "discount_summary": agg_discount_summary(df),
    }

    kpis = compute_kpis(df)

    # Collect all long-format rows
    long_rows: list[pd.DataFrame] = [kpis_to_long(kpis)]
    for name, tbl in tables.items():
        long_rows.append(to_long(name, tbl))

    stats_df = pd.concat(long_rows, ignore_index=True)
    stats_df.to_csv(STATS_CSV, index=False)
    print(f"[stats] summary_stats.csv written: {len(stats_df)} rows -> {STATS_CSV}")

    # Print KPIs to stdout
    print("\n=== KEY PERFORMANCE INDICATORS ===")
    for k, v in kpis.items():
        if isinstance(v, float):
            print(f"  {k:<30} ${v:,.2f}")
        else:
            print(f"  {k:<30} {v}")

    # Print top-level table summaries
    print("\n=== TABLE SUMMARIES ===")
    for name, tbl in tables.items():
        print(f"\n-- {name} --")
        print(tbl.to_string(index=False))


if __name__ == "__main__":
    main()
