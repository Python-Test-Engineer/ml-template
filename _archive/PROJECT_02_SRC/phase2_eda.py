"""Phase 2 - EDA & Visualisation
Produces 11 EDA charts from clean Superstore and web traffic parquets.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

# -- Constants -----------------------------------------------------------------
OUTPUT_DIR = Path("output/PROJECT_02")
PLOTS_DIR = OUTPUT_DIR / "plots"
RANDOM_SEED = 42
DPI = 150
DEFAULT_FIGSIZE = (10, 6)

sns.set_theme(style="whitegrid")


# -- Helpers -------------------------------------------------------------------
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    ss_path = OUTPUT_DIR / "superstore_clean.parquet"
    wt_path = OUTPUT_DIR / "webtraffic_clean.parquet"
    for p in (ss_path, wt_path):
        if not p.exists():
            raise FileNotFoundError(f"Required input not found: {p}. Run phase1_etl.py first.")
    ss = pd.read_parquet(ss_path)
    wt = pd.read_parquet(wt_path)
    return ss, wt


def save(fig: plt.Figure, name: str) -> None:
    path = PLOTS_DIR / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path.name}")


# -- Charts --------------------------------------------------------------------

def plot_01_profit_distribution(ss: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    sns.histplot(ss["Profit"], bins=60, kde=True, ax=ax, color="steelblue")
    ax.axvline(0, color="red", linestyle="--", linewidth=1.5, label="Break-even (0)")
    ax.fill_betweenx(
        [0, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else 1],
        ss["Profit"].min(), 0,
        alpha=0.07, color="red", label="Loss zone",
    )
    ax.set_title("Profit Distribution")
    ax.set_xlabel("Profit (USD)")
    ax.set_ylabel("Count")
    ax.legend()
    save(fig, "01_profit_distribution.png")


def plot_02_profit_by_category(ss: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    palette = {"Furniture": "#e07b54", "Office Supplies": "#4c9be8", "Technology": "#62c370"}
    sns.boxplot(data=ss, x="Category", y="Profit", palette=palette, ax=ax)
    ax.axhline(0, color="red", linestyle="--", linewidth=1.2, label="Break-even")
    ax.set_title("Profit by Category")
    ax.set_ylabel("Profit (USD)")
    ax.legend()
    save(fig, "02_profit_by_category.png")


def plot_03_profit_by_subcategory(ss: pd.DataFrame) -> None:
    means = ss.groupby("Sub-Category")["Profit"].mean().sort_values(ascending=True)
    colors = ["#d62728" if v < 0 else "#2ca02c" for v in means.values]
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(means.index, means.values, color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title("Mean Profit by Sub-Category")
    ax.set_xlabel("Mean Profit (USD)")
    save(fig, "03_profit_by_subcategory.png")


def plot_04_discount_vs_profit(ss: pd.DataFrame) -> None:
    # Compute approximate breakeven discount
    breakeven = ss.groupby(
        pd.cut(ss["Discount"], bins=10)
    )["Profit"].mean()
    be_disc = None
    for interval, mean_profit in breakeven.items():
        if mean_profit < 0:
            be_disc = interval.mid
            break

    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    sns.regplot(
        data=ss, x="Discount", y="Profit",
        scatter_kws={"alpha": 0.3, "s": 15, "color": "steelblue"},
        line_kws={"color": "orange", "linewidth": 2},
        ax=ax,
    )
    if be_disc is not None:
        ax.axvline(be_disc, color="red", linestyle="--", linewidth=1.5,
                   label=f"Approx. breakeven ~{be_disc:.2f}")
        ax.legend()
    ax.set_title("Discount vs Profit")
    ax.set_xlabel("Discount (fraction)")
    ax.set_ylabel("Profit (USD)")
    save(fig, "04_discount_vs_profit.png")


def plot_05_sales_profit_over_time(ss: pd.DataFrame) -> None:
    ss2 = ss.copy()
    ss2["ym"] = ss2["Order Date"].dt.to_period("M")
    grouped = ss2.groupby("ym").agg(total_sales=("Sales", "sum"), total_profit=("Profit", "sum")).reset_index()
    grouped["ym_dt"] = grouped["ym"].dt.to_timestamp()

    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()
    ax1.plot(grouped["ym_dt"], grouped["total_sales"], color="#4c9be8", label="Sales")
    ax2.plot(grouped["ym_dt"], grouped["total_profit"], color="#e07b54", label="Profit", linestyle="--")
    ax1.set_ylabel("Total Sales (USD)", color="#4c9be8")
    ax2.set_ylabel("Total Profit (USD)", color="#e07b54")
    ax1.set_title("Monthly Sales and Profit Over Time")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    fig.autofmt_xdate()
    save(fig, "05_sales_profit_over_time.png")


def plot_06_region_segment_heatmap(ss: pd.DataFrame) -> None:
    pivot = ss.pivot_table(index="Region", columns="Segment", values="profit_margin", aggfunc="mean")
    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    sns.heatmap(pivot, annot=True, fmt=".3f", cmap="RdYlGn", center=0, ax=ax)
    ax.set_title("Avg Profit Margin: Region x Segment")
    save(fig, "06_region_segment_heatmap.png")


def plot_07_shipmode_profit_violin(ss: pd.DataFrame) -> None:
    order = ss.groupby("Ship Mode")["profit_margin"].median().sort_values().index.tolist()
    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    sns.violinplot(data=ss, x="Ship Mode", y="profit_margin", order=order,
                   palette="muted", ax=ax)
    ax.axhline(0, color="red", linestyle="--", linewidth=1)
    ax.set_title("Profit Margin Distribution by Ship Mode")
    ax.set_ylabel("Profit Margin")
    save(fig, "07_shipmode_profit_violin.png")


def plot_08_top_bottom_products(ss: pd.DataFrame) -> None:
    by_product = ss.groupby("Product Name")["Profit"].sum().sort_values()
    top10 = by_product.tail(10)
    bot10 = by_product.head(10)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    ax1.barh(bot10.index, bot10.values, color="#d62728")
    ax1.set_title("Bottom 10 Products by Profit")
    ax1.set_xlabel("Total Profit (USD)")
    ax2.barh(top10.index, top10.values, color="#2ca02c")
    ax2.set_title("Top 10 Products by Profit")
    ax2.set_xlabel("Total Profit (USD)")
    fig.tight_layout()
    save(fig, "08_top_bottom_products.png")


def plot_09_customer_order_frequency(ss: pd.DataFrame) -> None:
    freq = ss.groupby("Customer ID")["Order ID"].nunique()
    cap = freq.quantile(0.95)
    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    sns.histplot(freq[freq <= cap], bins=30, ax=ax, color="steelblue")
    ax.set_title("Customer Order Frequency (capped at 95th pct)")
    ax.set_xlabel("Number of Orders")
    ax.set_ylabel("Count of Customers")
    save(fig, "09_customer_order_frequency.png")


def plot_10_web_conversion_by_source(wt: pd.DataFrame) -> None:
    agg = wt.groupby("Traffic Source")["Conversion Rate"].agg(["mean", "std"]).reset_index()
    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    palette = sns.color_palette("tab10", n_colors=len(agg))
    bars = ax.bar(agg["Traffic Source"], agg["mean"], yerr=agg["std"],
                  color=palette, capsize=5, error_kw={"elinewidth": 1.5})
    ax.set_title("Mean Conversion Rate by Traffic Source")
    ax.set_ylabel("Mean Conversion Rate")
    ax.set_ylim(0, agg["mean"].max() * 1.3)
    save(fig, "10_web_conversion_by_source.png")


def plot_11_web_bounce_vs_session(wt: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    sources = wt["Traffic Source"].unique()
    palette = dict(zip(sources, sns.color_palette("tab10", n_colors=len(sources))))
    for src in sources:
        sub = wt[wt["Traffic Source"] == src]
        ax.scatter(sub["Bounce Rate"], sub["Session Duration"],
                   alpha=0.5, s=20, label=src, color=palette[src])
    ax.set_title("Bounce Rate vs Session Duration by Traffic Source")
    ax.set_xlabel("Bounce Rate")
    ax.set_ylabel("Session Duration (min)")
    ax.legend(title="Traffic Source", fontsize=8)
    save(fig, "11_web_bounce_vs_session.png")


# -- Main ----------------------------------------------------------------------
def main() -> None:
    print("[Phase 2] Loading clean datasets...")
    ss, wt = load_data()
    print(f"  Superstore: {ss.shape}  |  Web Traffic: {wt.shape}")

    print("[Phase 2] Generating charts...")
    plot_01_profit_distribution(ss)
    plot_02_profit_by_category(ss)
    plot_03_profit_by_subcategory(ss)
    plot_04_discount_vs_profit(ss)
    plot_05_sales_profit_over_time(ss)
    plot_06_region_segment_heatmap(ss)
    plot_07_shipmode_profit_violin(ss)
    plot_08_top_bottom_products(ss)
    plot_09_customer_order_frequency(ss)
    plot_10_web_conversion_by_source(wt)
    plot_11_web_bounce_vs_session(wt)

    print("\n[Phase 2] OK - 11 plots saved to", PLOTS_DIR)


if __name__ == "__main__":
    main()
