"""Phase 3 — EDA Plots: produce 11 charts to output/PROJECT_01/plots/."""

from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

matplotlib.use("Agg")

RANDOM_SEED = 42
OUTPUT_DIR = Path("output/PROJECT_01")
PLOTS_DIR = OUTPUT_DIR / "plots"
CLEAN_PATH = OUTPUT_DIR / "clean.csv"

DPI = 150
PALETTE = "tab10"

NUMERIC_COLS = [
    "Page Views",
    "Session Duration",
    "Bounce Rate",
    "Time on Page",
    "Previous Visits",
    "Conversion Rate",
]

rng = np.random.default_rng(RANDOM_SEED)


def load_clean(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise ValueError(f"clean.csv not found: {path}")
    return pd.read_csv(path)


def save(fig: plt.Figure, name: str) -> None:
    path = PLOTS_DIR / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_hist_grid(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.suptitle("Numeric Column Distributions", fontsize=14, fontweight="bold")
    for ax, col in zip(axes.flat, NUMERIC_COLS):
        sns.histplot(df[col], bins=30, kde=True, ax=ax, color="steelblue")
        ax.set_title(col)
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
    fig.tight_layout()
    save(fig, "hist_grid.png")


def plot_bar_traffic_source(df: pd.DataFrame) -> None:
    counts = df["Traffic Source"].value_counts().sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(counts.index, counts.values, color=sns.color_palette(PALETTE, len(counts)))
    ax.set_title("Session Count by Traffic Source")
    ax.set_xlabel("Sessions")
    ax.set_ylabel("Traffic Source")
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=9)
    fig.tight_layout()
    save(fig, "bar_traffic_source.png")


def plot_box(df: pd.DataFrame, y_col: str, filename: str, title: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    order = df.groupby("Traffic Source")[y_col].median().sort_values().index.tolist()
    sns.boxplot(data=df, x="Traffic Source", y=y_col, order=order,
                palette=PALETTE, ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Traffic Source")
    ax.set_ylabel(y_col)
    fig.tight_layout()
    save(fig, filename)


def plot_scatter(df: pd.DataFrame, x_col: str, y_col: str, filename: str,
                 title: str, jitter: bool = False) -> None:
    plot_df = df.copy()
    if jitter:
        plot_df[x_col] = plot_df[x_col] + rng.uniform(-0.1, 0.1, size=len(plot_df))
    fig, ax = plt.subplots(figsize=(9, 6))
    sources = plot_df["Traffic Source"].unique()
    palette = dict(zip(sources, sns.color_palette(PALETTE, len(sources))))
    for source, group in plot_df.groupby("Traffic Source"):
        ax.scatter(group[x_col], group[y_col], label=source,
                   color=palette[source], alpha=0.4, s=20)
    ax.set_title(title)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.legend(title="Traffic Source", bbox_to_anchor=(1.01, 1), loc="upper left")
    fig.tight_layout()
    save(fig, filename)


def plot_heatmap_correlation(df: pd.DataFrame) -> None:
    corr_cols = NUMERIC_COLS + ["converted"]
    corr = df[corr_cols].corr(method="pearson")
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                vmin=-1, vmax=1, ax=ax, square=True, linewidths=0.5)
    ax.set_title("Pearson Correlation Heatmap")
    fig.tight_layout()
    save(fig, "heatmap_correlation.png")


def plot_bar_metrics_by_source(df: pd.DataFrame) -> None:
    metrics = ["Session Duration", "Bounce Rate", "Conversion Rate"]
    grouped = df.groupby("Traffic Source")[metrics].agg(["mean", "std"]).reset_index()
    sources = grouped["Traffic Source"].tolist()
    x = np.arange(len(sources))
    width = 0.25
    colors = sns.color_palette(PALETTE, len(metrics))

    fig, ax = plt.subplots(figsize=(11, 6))
    for i, metric in enumerate(metrics):
        means = grouped[(metric, "mean")]
        stds = grouped[(metric, "std")]
        ax.bar(x + i * width, means, width, label=metric,
               color=colors[i], yerr=stds, capsize=3, alpha=0.85)

    ax.set_xticks(x + width)
    ax.set_xticklabels(sources, rotation=15)
    ax.set_title("Mean Session Metrics by Traffic Source")
    ax.set_ylabel("Mean Value")
    ax.set_xlabel("Traffic Source")
    ax.legend(title="Metric")
    fig.tight_layout()
    save(fig, "bar_metrics_by_source.png")


def plot_violin_previous_vs_duration(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    order = sorted(df["Previous Visits"].unique())
    sns.violinplot(data=df, x="Previous Visits", y="Session Duration",
                   order=order, palette=PALETTE, ax=ax, inner=None)
    sns.stripplot(data=df, x="Previous Visits", y="Session Duration",
                  order=order, color="black", alpha=0.3, size=2, ax=ax)
    ax.set_title("Session Duration by Previous Visits")
    ax.set_xlabel("Previous Visits")
    ax.set_ylabel("Session Duration (min)")
    fig.tight_layout()
    save(fig, "violin_previous_vs_duration.png")


def main() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_clean(CLEAN_PATH)

    print("=" * 60)
    print("PHASE 3 — EDA PLOTS")
    print("=" * 60)
    print(f"Loaded clean data: {df.shape[0]} rows")

    try:
        plt.style.use("seaborn-v0_8-whitegrid")
    except OSError:
        warnings.warn("seaborn-v0_8-whitegrid style not available, using default.")

    print("Generating plots...")
    plot_hist_grid(df)
    plot_bar_traffic_source(df)
    plot_box(df, "Session Duration", "box_session_by_source.png",
             "Session Duration by Traffic Source")
    plot_box(df, "Bounce Rate", "box_bounce_by_source.png",
             "Bounce Rate by Traffic Source")
    plot_box(df, "Conversion Rate", "box_conversion_by_source.png",
             "Conversion Rate by Traffic Source")
    plot_scatter(df, "Session Duration", "Bounce Rate",
                 "scatter_duration_vs_bounce.png",
                 "Session Duration vs Bounce Rate")
    plot_scatter(df, "Page Views", "Conversion Rate",
                 "scatter_pageviews_vs_conversion.png",
                 "Page Views vs Conversion Rate")
    plot_scatter(df, "Previous Visits", "Conversion Rate",
                 "scatter_previous_vs_conversion.png",
                 "Previous Visits vs Conversion Rate", jitter=True)
    plot_heatmap_correlation(df)
    plot_bar_metrics_by_source(df)
    plot_violin_previous_vs_duration(df)

    print(f"\nAll 11 plots saved to {PLOTS_DIR}")


if __name__ == "__main__":
    main()
