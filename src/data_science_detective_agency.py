"""
Lesson 01: Multi-Agent Collaboration Dashboard
Data Science Detective Agency — Educational Shiny App

All processing is local (pandas/Python) — no API calls required:
  - DataCleaner   -> detects nulls, outliers, duplicates
  - Statistician  -> computes mean/std per numeric column
  - Visualizer    -> builds Plotly bar chart + title/insight
  - Reporter      -> assembles Markdown report

Upload any CSV; the agents investigate it autonomously.
Results are assigned display_after timestamps; the UI polls every 1 s.
"""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from typing import Any

import markdown2
import pandas as pd
import plotly.graph_objects as go
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from shiny import App, reactive, render, ui

console = Console()


def _read_csv_smart(path: str) -> pd.DataFrame:
    """Try common encodings until one succeeds."""
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode CSV with any common encoding")


# ---------------------------------------------------------------------------
# 1. Message dataclass
# ---------------------------------------------------------------------------

AGENT_COLORS = {
    "Manager": "#4A90D9",
    "DataCleaner": "#E67E22",
    "Statistician": "#27AE60",
    "Visualizer": "#8E44AD",
    "Reporter": "#C0392B",
    "SYSTEM": "#7F8C8D",
}
AGENT_ICONS = {
    "Manager": "Detective",
    "DataCleaner": "Cleaner",
    "Statistician": "Stats",
    "Visualizer": "Viz",
    "Reporter": "Report",
    "SYSTEM": "System",
}


@dataclass
class AgentMessage:
    sender: str
    recipient: str
    content: str
    msg_type: str  # "task" | "update" | "result" | "complete"
    timestamp: float = field(default_factory=time.time)
    display_after: float = 0.0


# ---------------------------------------------------------------------------
# 3. Shared state
# ---------------------------------------------------------------------------

_message_log: list[AgentMessage] = []
_state_schedule: list[tuple[float, str, str]] = []
_results: dict[str, Any] = {}
_started: bool = False
_done_after: float = 0.0


def _reset_state() -> None:
    global _message_log, _state_schedule, _results, _started, _done_after
    _message_log = []
    _state_schedule = []
    _results = {}
    _started = False
    _done_after = 0.0


_reset_state()


# ---------------------------------------------------------------------------
# 4. Pydantic models
# ---------------------------------------------------------------------------


class DirtyRow(BaseModel):
    index: int
    reason: str


class DataCleanerResult(BaseModel):
    dirty_rows: list[DirtyRow]
    summary: str


class ColumnStat(BaseModel):
    column: str
    mean: float
    std: float


class StatisticianResult(BaseModel):
    column_stats: list[ColumnStat]
    overall_mean: float
    top_column: str
    findings: str


class VisualizerResult(BaseModel):
    chart_title: str
    insight: str


# ---------------------------------------------------------------------------
# 5. Local agent implementations (no API calls)
# ---------------------------------------------------------------------------


def _local_data_cleaner(df: pd.DataFrame) -> DataCleanerResult:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    col_bounds: dict[str, tuple[float, float]] = {}
    for col in numeric_cols:
        vals = df[col].dropna()
        if len(vals) > 1:
            col_bounds[col] = (float(vals.mean()), float(vals.std()))

    dirty: list[DirtyRow] = []
    seen: set[tuple] = set()
    for idx, row in df.iterrows():
        reasons: list[str] = []
        key = tuple(None if pd.isna(v) else v for v in row)
        if key in seen:
            reasons.append("duplicate row")
        else:
            seen.add(key)
        for col in df.columns:
            if pd.isna(row[col]):
                reasons.append(f"missing value in '{col}'")
        for col in numeric_cols:
            val = row[col]
            if pd.notna(val) and col in col_bounds:
                m, s = col_bounds[col]
                if s > 0 and abs(val - m) > 3 * s:
                    reasons.append(f"anomalous value in '{col}' ({val})")
        if reasons:
            dirty.append(DirtyRow(index=int(idx), reason="; ".join(reasons)))

    n = len(dirty)
    summary = (
        f"{n} dirty row(s) found out of {len(df)} total."
        if n > 0
        else f"All {len(df)} rows passed quality checks."
    )
    return DataCleanerResult(dirty_rows=dirty, summary=summary)


def _local_statistician(clean_df: pd.DataFrame) -> StatisticianResult:
    numeric_cols = clean_df.select_dtypes(include="number").columns.tolist()
    analysis_cols = [
        c
        for c in numeric_cols
        if not ("id" in c.lower() and clean_df[c].nunique() == len(clean_df))
    ]
    col_stats: list[ColumnStat] = []
    all_vals: list[float] = []
    for col in analysis_cols:
        vals = clean_df[col].dropna()
        if len(vals) == 0:
            continue
        mean = round(float(vals.mean()), 2)
        std = round(float(vals.std(ddof=1)), 2) if len(vals) > 1 else 0.0
        col_stats.append(ColumnStat(column=col, mean=mean, std=std))
        all_vals.extend(vals.tolist())

    overall_mean = round(float(pd.Series(all_vals).mean()), 2) if all_vals else 0.0
    top = max(col_stats, key=lambda s: s.mean) if col_stats else None
    top_column = top.column if top else ""
    findings = (
        f"Across {len(col_stats)} numeric column(s), the overall mean is {overall_mean}. "
        f"{top_column} has the highest average at {top.mean}."
        if top
        else "No numeric columns found."
    )
    return StatisticianResult(
        column_stats=col_stats,
        overall_mean=overall_mean,
        top_column=top_column,
        findings=findings,
    )


def _local_visualizer(
    means: dict[str, float], overall_mean: float, top_column: str
) -> VisualizerResult:
    top_val = means.get(top_column, 0)
    title = f"Average by Column — {top_column} Leads at {top_val}"[:69]
    spread = (
        round(max(means.values()) - min(means.values()), 2) if len(means) > 1 else 0
    )
    insight = (
        f"{top_column} leads with an average of {top_val}; "
        f"the overall mean is {overall_mean} and values span a range of {spread}."
    )
    return VisualizerResult(chart_title=title, insight=insight)


def _local_reporter(
    dirty_indices: list[int],
    reasons: list[str],
    dc_summary: str,
    overall_mean: float,
    top_column: str,
    means: dict[str, float],
    stds: dict[str, float],
    st_findings: str,
    vz_insight: str,
    clean_df: pd.DataFrame,
    n_total: int,
) -> str:
    # ── Extended per-column stats ──────────────────────────────────────────
    ext: list[tuple] = []  # (col, mean, std, min, max, median, cv)
    high_var: list[str] = []
    for col in means:
        vals = (
            clean_df[col].dropna()
            if col in clean_df.columns
            else pd.Series([], dtype=float)
        )
        if len(vals) == 0:
            continue
        col_min = round(float(vals.min()), 2)
        col_max = round(float(vals.max()), 2)
        col_median = round(float(vals.median()), 2)
        cv = round(stds[col] / means[col] * 100, 1) if means[col] != 0 else 0.0
        ext.append(
            (col, means[col], stds.get(col, 0.0), col_min, col_max, col_median, cv)
        )
        if cv > 40:
            high_var.append((col, cv))

    # ── Data quality breakdown ─────────────────────────────────────────────
    quality_pct = (
        round((1 - len(dirty_indices) / n_total) * 100, 1) if n_total > 0 else 100.0
    )
    issue_counts: dict[str, int] = {}
    for r in reasons:
        for part in r.split("; "):
            key = (
                "missing value"
                if part.startswith("missing")
                else (
                    "anomalous value"
                    if part.startswith("anomalous")
                    else "duplicate row" if part.startswith("duplicate") else part
                )
            )
            issue_counts[key] = issue_counts.get(key, 0) + 1
    issue_lines = (
        "\n".join(f"  - {k}: **{v}** occurrence(s)" for k, v in issue_counts.items())
        or "  - No issues detected"
    )

    # ── Rankings ───────────────────────────────────────────────────────────
    ranked = sorted(means.items(), key=lambda x: x[1], reverse=True)
    top3_lines = "\n".join(
        f"  {i+1}. **{c}** — avg {v}" for i, (c, v) in enumerate(ranked[:3])
    )
    bottom3_lines = "\n".join(
        f"  {i+1}. **{c}** — avg {v}" for i, (c, v) in enumerate(reversed(ranked[-3:]))
    )

    # ── Stats table ────────────────────────────────────────────────────────
    stats_rows = "\n".join(
        f"| {col} | {m} | {s} | {mn} | {mx} | {med} | {cv}% |"
        for col, m, s, mn, mx, med, cv in ext
    )
    stats_table = (
        (
            "| Column | Mean | Std Dev | Min | Max | Median | CV |\n"
            "|--------|------|---------|-----|-----|--------|----|\n" + stats_rows
        )
        if stats_rows
        else "_No numeric columns analysed._"
    )

    # ── Variability section ────────────────────────────────────────────────
    if high_var:
        var_lines = "\n".join(f"- **{c}** (CV: {cv}%)" for c, cv in high_var)
        var_section = (
            "\n## Variability Alert\n"
            "The following columns show high coefficient of variation (CV > 40%), "
            "indicating significant spread or potential data inconsistency:\n"
            + var_lines
        )
    else:
        var_section = ""

    # ── Future work recommendations ────────────────────────────────────────
    future_items: list[str] = []
    if any(k == "missing value" for k in issue_counts):
        future_items.append(
            "**Improve upstream data capture** — missing values suggest gaps in data entry "
            "or collection pipelines. Enforce mandatory fields at source."
        )
    if any(k == "anomalous value" for k in issue_counts):
        future_items.append(
            "**Implement range validation** — anomalous values were detected. Add min/max "
            "constraints at the point of entry or ETL layer."
        )
    if any(k == "duplicate row" for k in issue_counts):
        future_items.append(
            "**Deduplicate at source** — duplicate rows indicate a merging or ingestion "
            "issue. Add unique-key enforcement before loading."
        )
    if high_var:
        future_items.append(
            f"**Investigate high-variance columns** — {', '.join(c for c, _ in high_var)} "
            "show wide spread. Segment by category or time period to understand drivers."
        )
    future_items += [
        f"**Trend analysis** — extend this report with time-series breakdowns of "
        f"**{top_column}** to identify seasonal patterns or growth trajectories.",
        "**Correlation study** — compute pairwise correlations between numeric columns "
        "to surface relationships that may drive the key metric.",
        "**Automated monitoring** — schedule this pipeline to run on new data drops "
        "and alert stakeholders when quality thresholds are breached.",
    ]
    future_lines = "\n".join(f"{i+1}. {item}" for i, item in enumerate(future_items))

    issues_summary = "; ".join(reasons) if reasons else "none"

    return f"""# Case Report: Dataset Investigation

## Executive Summary
This investigation analysed **{n_total}** records across **{len(means)}** numeric column(s). \
After removing **{len(dirty_indices)}** dirty row(s), the clean dataset contains \
**{n_total - len(dirty_indices)}** rows ({quality_pct}% pass rate). \
{st_findings}

---

## Data Quality

- **Total rows ingested:** {n_total}
- **Dirty rows removed:** {len(dirty_indices)} ({round(len(dirty_indices)/n_total*100,1) if n_total else 0}%)
- **Clean rows retained:** {n_total - len(dirty_indices)} ({quality_pct}%)
- **Issues detected:** {issues_summary}

### Issue Breakdown
{issue_lines}

---

## Statistical Analysis

### Summary Table
{stats_table}

### Top Performers (by mean)
{top3_lines}

### Lowest Performers (by mean)
{bottom3_lines}

### Overall
- **Overall mean across all numeric columns:** {overall_mean}
- **Highest average column:** **{top_column}** at {means.get(top_column, '?')}
{var_section}

---

## Key Findings

- {vz_insight}
- Data quality stands at **{quality_pct}%** after cleaning.
- **{top_column}** consistently leads as the strongest numeric signal in this dataset.
{"- High variability detected in: " + ", ".join(f"**{c}**" for c, _ in high_var) + " — warrants deeper investigation." if high_var else "- No alarming variability patterns detected across columns."}

---

## Recommended Next Steps

{future_lines}

---

*— Assembled by the Data Science Detective Agency*"""


# ---------------------------------------------------------------------------
# 6. Investigation runner — all local processing
# ---------------------------------------------------------------------------

MSG_STYLE = {
    "task": ("bold blue", "[TASK]"),
    "update": ("yellow", "[UPDATE]"),
    "result": ("bold green", "[RESULT]"),
    "complete": ("bold magenta", "[DONE]"),
}
AGENT_RICH_COLORS = {
    "Manager": "bright_blue",
    "DataCleaner": "dark_orange",
    "Statistician": "green",
    "Visualizer": "magenta",
    "Reporter": "red",
    "SYSTEM": "grey62",
}


def _run_investigation(df: pd.DataFrame, interval: float = 1.0) -> None:
    """Run all agents locally; stream messages to the UI via shared globals."""
    global _state_schedule, _results, _done_after

    t0 = time.time()
    delay = 0.0
    first_msg = True

    def emit(msg: AgentMessage) -> None:
        nonlocal delay, first_msg
        msg.display_after = t0 + delay
        _message_log.append(msg)
        style, label = MSG_STYLE.get(msg.msg_type, ("white", msg.msg_type.upper()))
        sender_color = AGENT_RICH_COLORS.get(msg.sender, "white")
        console.print(
            f"  [dim]+{delay:5.1f}s[/]  [{sender_color}]{msg.sender:<12}[/]"
            f"[dim]-> {msg.recipient:<12}[/]  [{style}]{label}[/]  [white]{msg.content}[/]"
        )
        if first_msg:
            first_msg = False
        else:
            delay += interval

    def state_now(agent: str, state: str) -> None:
        _state_schedule.append((t0 + delay, agent, state))

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    n_rows, n_cols = df.shape
    col_summary = f"{n_rows} rows x {n_cols} columns ({len(numeric_cols)} numeric)"
    console.print(f"\n[bold]Dataset:[/] {col_summary}\n")

    # Manager intro
    emit(
        AgentMessage("SYSTEM", "ALL", "Investigation started! Manager online.", "task")
    )
    emit(
        AgentMessage(
            "Manager",
            "ALL",
            f"Dataset loaded: {col_summary}. Columns: {', '.join(df.columns.tolist())}. "
            "Dispatching sub-agents...",
            "update",
        )
    )

    # DataCleaner
    state_now("DataCleaner", "working")
    emit(
        AgentMessage(
            "Manager", "DataCleaner", "Find all dirty rows in the dataset.", "task"
        )
    )
    emit(
        AgentMessage(
            "DataCleaner",
            "ALL",
            "Scanning for nulls, outliers, duplicates...",
            "update",
        )
    )

    dc: DataCleanerResult = _local_data_cleaner(df)
    dirty_indices = [r.index for r in dc.dirty_rows]
    reasons = [r.reason for r in dc.dirty_rows]
    clean_df = df.drop(index=dirty_indices).reset_index(drop=True)

    emit(
        AgentMessage(
            "DataCleaner",
            "Manager",
            f"Found {len(dirty_indices)} dirty row(s). {dc.summary} Rows flagged for removal.",
            "result",
        )
    )
    state_now("DataCleaner", "done")
    emit(
        AgentMessage(
            "DataCleaner",
            "ALL",
            f"Done. Clean dataset: {len(clean_df)} rows.",
            "complete",
        )
    )

    # Statistician
    emit(
        AgentMessage(
            "Manager", "ALL", "DataCleaner done. Dispatching Statistician...", "update"
        )
    )
    state_now("Statistician", "working")
    emit(
        AgentMessage(
            "Manager",
            "Statistician",
            "Compute summary statistics on the clean dataset.",
            "task",
        )
    )
    emit(
        AgentMessage(
            "Statistician",
            "ALL",
            "Computing mean and std per numeric column...",
            "update",
        )
    )

    st: StatisticianResult = _local_statistician(clean_df)
    means = {s.column: s.mean for s in st.column_stats}
    stds = {s.column: s.std for s in st.column_stats}
    top_column = st.top_column
    overall_mean = st.overall_mean

    stats_table = Table("Column", "Mean", "Std", box=box.SIMPLE, style="dim")
    for s in st.column_stats:
        stats_table.add_row(s.column, str(s.mean), str(s.std))
    console.print(stats_table)

    emit(
        AgentMessage(
            "Statistician",
            "Manager",
            f"Overall mean: {overall_mean}. Top column: {top_column} (avg {means.get(top_column, '?')}). {st.findings}",
            "result",
        )
    )
    state_now("Statistician", "done")
    emit(AgentMessage("Statistician", "ALL", "Statistics complete!", "complete"))

    # Visualizer
    emit(
        AgentMessage(
            "Manager", "ALL", "Stats ready. Dispatching Visualizer...", "update"
        )
    )
    state_now("Visualizer", "working")
    emit(
        AgentMessage(
            "Manager",
            "Visualizer",
            "Build a bar chart of average values per column.",
            "task",
        )
    )
    emit(AgentMessage("Visualizer", "ALL", "Designing chart...", "update"))

    vz: VisualizerResult = _local_visualizer(means, overall_mean, top_column)

    bar_colors = [
        "#4A90D9",
        "#E67E22",
        "#27AE60",
        "#8E44AD",
        "#C0392B",
        "#1ABC9C",
        "#E74C3C",
        "#3498DB",
        "#F39C12",
        "#9B59B6",
    ]
    cols_ordered = list(means.keys())
    fig = go.Figure(
        go.Bar(
            x=cols_ordered,
            y=[means[c] for c in cols_ordered],
            marker_color=bar_colors[: len(cols_ordered)],
            text=[f"{means[c]:.1f}" for c in cols_ordered],
            textposition="outside",
        )
    )
    y_max = max(means.values()) * 1.15 if means else 110
    fig.update_layout(
        title=vz.chart_title,
        xaxis_title="Column",
        yaxis_title="Average Value",
        yaxis_range=[0, y_max],
        plot_bgcolor="white",
        paper_bgcolor="#F8F9FA",
        font=dict(family="monospace", size=13),
        title_font_size=16,
        margin=dict(t=60, b=40, l=40, r=20),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E0E0E0")
    _results["fig"] = fig

    emit(
        AgentMessage(
            "Visualizer",
            "Manager",
            f"Chart ready: '{vz.chart_title}'. {vz.insight}",
            "result",
        )
    )
    state_now("Visualizer", "done")
    emit(AgentMessage("Visualizer", "ALL", "Visualization complete!", "complete"))

    # Reporter
    emit(
        AgentMessage(
            "Manager", "ALL", "All data ready. Dispatching Reporter...", "update"
        )
    )
    state_now("Reporter", "working")
    emit(
        AgentMessage(
            "Manager", "Reporter", "Assemble the final investigation report.", "task"
        )
    )
    emit(AgentMessage("Reporter", "ALL", "Reviewing all findings...", "update"))

    report_text = _local_reporter(
        dirty_indices=dirty_indices,
        reasons=reasons,
        dc_summary=dc.summary,
        overall_mean=overall_mean,
        top_column=top_column,
        means=means,
        stds=stds,
        st_findings=st.findings,
        vz_insight=vz.insight,
        clean_df=clean_df,
        n_total=len(df),
    )
    _results["report"] = report_text

    emit(
        AgentMessage(
            "Reporter", "Manager", "Final report assembled and ready.", "result"
        )
    )
    state_now("Reporter", "done")
    emit(
        AgentMessage(
            "Reporter", "ALL", "Investigation complete! Case closed.", "complete"
        )
    )
    emit(
        AgentMessage(
            "Manager", "ALL", "All agents done. Investigation closed!", "complete"
        )
    )

    _done_after = _message_log[-1].display_after
    console.print(f"[green]Done! {len(_message_log)} messages over {delay:.0f} s.[/]")


# ---------------------------------------------------------------------------
# 7. UI helpers
# ---------------------------------------------------------------------------


def _badge(status: str) -> ui.Tag:
    colors = {"waiting": "#95A5A6", "working": "#F39C12", "done": "#27AE60"}
    labels = {"waiting": "Waiting", "working": "Working", "done": "Done"}
    return ui.tags.span(
        labels.get(status, status),
        style=(
            f"background:{colors.get(status, '#95A5A6')};color:white;"
            "padding:3px 10px;border-radius:12px;font-size:0.8em;font-weight:bold;"
        ),
    )


TASK_DESCRIPTIONS = {
    "DataCleaner": "Find dirty/missing rows",
    "Statistician": "Compute summary statistics",
    "Visualizer": "Produce bar chart",
    "Reporter": "Assemble final report",
}


def _message_bubble(msg: AgentMessage) -> ui.Tag:
    color = AGENT_COLORS.get(msg.sender, "#555")
    type_labels = {
        "task": "TASK",
        "update": "UPDATE",
        "result": "RESULT",
        "complete": "DONE",
    }
    ts = time.strftime("%H:%M:%S", time.localtime(msg.timestamp))
    return ui.div(
        ui.div(
            ui.tags.span(f"{msg.sender}", style=f"font-weight:bold;color:{color};"),
            ui.tags.span(f" -> {msg.recipient}", style="color:#888;font-size:0.85em;"),
            ui.tags.span(
                f"  [{type_labels.get(msg.msg_type, msg.msg_type)}]",
                style=f"color:{color};font-size:0.75em;margin-left:6px;",
            ),
            ui.tags.span(f"  {ts}", style="color:#aaa;font-size:0.75em;float:right;"),
            style="margin-bottom:4px;",
        ),
        ui.div(msg.content, style="color:var(--text);font-size:0.9em;line-height:1.4;"),
        style=(
            f"background:var(--bubble-bg);border-left:4px solid {color};"
            "border-radius:8px;padding:10px 14px;margin-bottom:8px;"
            "box-shadow:0 1px 3px rgba(0,0,0,0.07);"
        ),
    )


def _agent_status_card(agent: str, status: str) -> ui.Tag:
    color = AGENT_COLORS.get(agent, "#555")
    roles = {
        "DataCleaner": "Finds dirty rows & anomalies",
        "Statistician": "Computes summary statistics",
        "Visualizer": "Produces charts & figures",
        "Reporter": "Assembles the final report",
    }
    return ui.div(
        ui.div(
            ui.tags.span(
                agent, style=f"font-weight:bold;color:{color};font-size:0.95em;"
            ),
            style="margin-bottom:3px;",
        ),
        ui.div(
            roles.get(agent, ""), style="color:#777;font-size:0.75em;margin-bottom:6px;"
        ),
        _badge(status),
        style=(
            "background:var(--card-bg);border:1px solid var(--border-light);border-radius:10px;"
            f"padding:8px 12px;margin-bottom:8px;border-left:4px solid {color};"
        ),
    )


# ---------------------------------------------------------------------------
# 8. Shiny app
# ---------------------------------------------------------------------------

app_ui = ui.page_fluid(
    ui.busy_indicators.use(spinners=False, pulse=False, fade=False),
    ui.tags.script(
        """
        setInterval(function() {
            if (window.Shiny && Shiny.setInputValue) {
                Shiny.setInputValue('_keepalive', Date.now());
            }
        }, 20000);
    """
    ),
    ui.tags.script(
        """
        (function() {
            var scrolled = false;
            var observer = new MutationObserver(function() {
                if (scrolled) return;
                if (!document.querySelector('.results-panel')) return;
                scrolled = true;
                observer.disconnect();
                setTimeout(function() {
                    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                }, 200);
            });
            observer.observe(document.body, { childList: true, subtree: true });
        })();
    """
    ),
    ui.tags.style(
        """
        :root {
            --bg:              antiquewhite;
            --surface:         #FDF8F0;
            --surface-alt:     #FAF5EB;
            --border:          #DDD0B3;
            --border-light:    #E0E0E0;
            --text:            #333;
            --text-muted:      #777;
            --text-faint:      #aaa;
            --panel-title:     #333;
            --panel-border:    #E0E0E0;
            --bubble-bg:       #ffffff;
            --card-bg:         #ffffff;
            --results-bg:      #ffffff;
            --preview-th:      #EDE3D0;
            --preview-td-bdr:  #F0F0F0;
            --report-bg:       #FDF8F0;
            --report-th:       #EDE3D0;
            --report-th-bdr:   #C8B89A;
            --report-td-bdr:   #DDD0B3;
            --report-td-alt:   #F5EFE3;
            --report-h1:       #1A1A2E;
            --report-h2:       #333;
            --report-strong:   #1A1A2E;
            --upload-bg:       #FDF8F0;
            --upload-border:   #C8B89A;
            --msg-wait:        #aaa;
        }
        body.dark {
            --bg:              #111827;
            --surface:         #1A2235;
            --surface-alt:     #1E2840;
            --border:          #2E4070;
            --border-light:    #2E4070;
            --text:            #D8DCE8;
            --text-muted:      #8A90A8;
            --text-faint:      #555E78;
            --panel-title:     #B8C4E0;
            --panel-border:    #2E4070;
            --bubble-bg:       #1E2840;
            --card-bg:         #1E2840;
            --results-bg:      #1A2235;
            --preview-th:      #1C3060;
            --preview-td-bdr:  #2A3A5C;
            --report-bg:       #1A2235;
            --report-th:       #1C3060;
            --report-th-bdr:   #2A4080;
            --report-td-bdr:   #2A3A5C;
            --report-td-alt:   #1C2840;
            --report-h1:       #82B4F0;
            --report-h2:       #B8C4E0;
            --report-strong:   #82B4F0;
            --upload-bg:       #1A2235;
            --upload-border:   #2E4070;
            --msg-wait:        #556;
        }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; transition: background 0.3s, color 0.3s; }
        .recalculating { opacity: 1 !important; }
        .shiny-busy-indicator { display: none !important; }
        .header-bar {
            background: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%);
            color: white; padding: 0 30px; margin-bottom: 24px;
            border-radius: 0 0 16px 16px;
            display: flex; align-items: center; min-height: 72px;
        }
        .header-bar h2 { margin: 0; font-size: 1.6em; flex: 1; text-align: center; }
        #theme-toggle {
            background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.25);
            border-radius: 50%; width: 40px; height: 40px; cursor: pointer;
            font-size: 1.25em; display: flex; align-items: center; justify-content: center;
            transition: background 0.2s; flex-shrink: 0; color: white;
        }
        #theme-toggle:hover { background: rgba(255,255,255,0.22); }
        .panel-title {
            font-weight: bold; font-size: 0.95em; color: var(--panel-title);
            text-transform: uppercase; letter-spacing: 0.05em;
            padding-bottom: 8px; margin-bottom: 14px;
            border-bottom: 2px solid var(--panel-border);
        }
        .upload-zone {
            background: var(--upload-bg); border: 2px dashed var(--upload-border); border-radius: 12px;
            padding: 16px 20px; margin: 0 16px 16px;
            display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
        }
        .upload-zone .shiny-input-container { margin-bottom: 0 !important; }
        .upload-zone label { color: var(--text) !important; }
        .data-preview {
            background: var(--surface); border-radius: 10px; border: 1px solid var(--border);
            padding: 12px 16px; margin: 0 16px 16px; font-size: 0.82em;
            font-family: monospace; overflow-x: auto; color: var(--text);
        }
        .data-preview table { border-collapse: collapse; width: 100%; }
        .data-preview th {
            background: var(--preview-th); padding: 4px 10px;
            border: 1px solid var(--border); text-align: left; font-size: 0.9em;
        }
        .data-preview td {
            padding: 3px 10px; border: 1px solid var(--preview-td-bdr);
            white-space: nowrap; max-width: 160px; overflow: hidden;
            text-overflow: ellipsis;
        }
        .msg-log { height: 420px; overflow-y: auto; padding: 4px 0; }
        .results-panel {
            background: var(--results-bg); border-radius: 12px;
            border: 1px solid var(--border-light); padding: 20px; margin-top: 20px;
        }
        .report-text {
            background: var(--report-bg); border-radius: 8px; padding: 16px;
            font-family: 'Segoe UI', sans-serif; font-size: 0.88em;
            border: 1px solid var(--border-light); line-height: 1.7; color: var(--text);
        }
        .report-text h1 { font-size: 1.2em; margin: 0 0 10px; color: var(--report-h1); }
        .report-text h2 { font-size: 1.0em; margin: 14px 0 6px; color: var(--report-h2);
                          border-bottom: 1px solid var(--border); padding-bottom: 3px; }
        .report-text ul { margin: 4px 0 8px 18px; padding: 0; }
        .report-text li { margin-bottom: 2px; }
        .report-text strong { color: var(--report-strong); }
        .report-text table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 0.9em; }
        .report-text th { background: var(--report-th); padding: 5px 10px; border: 1px solid var(--report-th-bdr); text-align: left; }
        .report-text td { padding: 4px 10px; border: 1px solid var(--report-td-bdr); }
        .report-text tr:nth-child(even) td { background: var(--report-td-alt); }
        .start-btn {
            background: #27AE60 !important; color: white !important;
            font-weight: bold !important; font-size: 1.1em !important;
            padding: 10px 32px !important; border-radius: 8px !important;
            border: none !important; cursor: pointer !important;
        }
        .clear-btn {
            background: #95A5A6 !important; color: white !important;
            font-weight: bold !important; font-size: 1.1em !important;
            padding: 10px 24px !important; border-radius: 8px !important;
            border: none !important; cursor: pointer !important;
        }
        .toolbar-row .shiny-input-container {
            margin-bottom: 0 !important;
            margin-left: 10px !important;
        }
        .toolbar-row select { background: var(--surface); color: var(--text); border-color: var(--border); }
        /* ── Agent intro modal ──────────────────────────────────── */
        #agent-intro-overlay {
            position: fixed; inset: 0; z-index: 9999;
            background: rgba(10,10,20,0.82);
            display: flex; align-items: center; justify-content: center;
            animation: fadeInOverlay 0.4s ease;
        }
        @keyframes fadeInOverlay { from { opacity:0; } to { opacity:1; } }
        #agent-intro-overlay.fade-out {
            animation: fadeOutOverlay 0.5s ease forwards;
            pointer-events: none;
        }
        @keyframes fadeOutOverlay { from { opacity:1; } to { opacity:0; } }
        #agent-intro-card {
            background: white; border-radius: 24px;
            width: 720px; max-width: 96vw;
            padding: 52px 56px 40px;
            box-shadow: 0 32px 80px rgba(0,0,0,0.5);
            text-align: center; position: relative;
            animation: introSlideUp 0.35s ease;
        }
        @keyframes introSlideUp {
            from { transform: translateY(30px); opacity:0; }
            to   { transform: translateY(0);    opacity:1; }
        }
        .intro-skip {
            position: absolute; top: 18px; right: 24px;
            color: #aaa; font-size: 1.0em; cursor: pointer;
            text-decoration: underline; background: none; border: none; padding: 0;
        }
        .intro-skip:hover { color: #555; }
        .intro-icon { font-size: 5.8em; margin-bottom: 12px; display: block; }
        .intro-agent-name {
            font-size: 2.2em; font-weight: bold; margin-bottom: 8px;
        }
        .intro-badge {
            display: inline-block; font-size: 1.05em; font-weight: bold;
            color: white; padding: 5px 18px; border-radius: 20px;
            margin-bottom: 22px; text-transform: uppercase; letter-spacing: 0.06em;
        }
        .intro-bio {
            font-size: 1.05em; color: #888; font-style: italic;
            margin-bottom: 14px; line-height: 1.5;
        }
        .intro-desc {
            font-size: 1.25em; color: #444; line-height: 1.7;
            margin-bottom: 30px; min-height: 90px;
        }
        .intro-dots {
            display: flex; justify-content: center; gap: 10px; margin-bottom: 24px;
        }
        .intro-dot {
            width: 12px; height: 12px; border-radius: 50%;
            background: #ddd; transition: background 0.3s;
        }
        .intro-next-btn {
            padding: 14px 48px; border-radius: 10px; border: none;
            font-size: 1.3em; font-weight: bold; cursor: pointer;
            color: white; transition: opacity 0.2s;
        }
        .intro-next-btn:hover { opacity: 0.85; }
        .intro-progress-wrap {
            height: 4px; background: #eee; border-radius: 2px;
            margin-top: 26px; overflow: hidden;
        }
        .intro-progress-bar { height: 100%; width: 0%; border-radius: 2px; }
    """
    ),
    ui.div(
        ui.tags.h2("The Data Science Detective Agency"),
        ui.tags.button("🌙", id="theme-toggle", title="Toggle light/dark mode"),
        class_="header-bar",
    ),
    ui.tags.script("""
(function() {
    function apply(dark) {
        document.body.classList.toggle('dark', dark);
        var btn = document.getElementById('theme-toggle');
        if (btn) btn.textContent = dark ? '\u2600\ufe0f' : '\U0001F319';
        localStorage.setItem('theme', dark ? 'dark' : 'light');
    }
    var saved = localStorage.getItem('theme') === 'dark';
    // Run after DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            apply(saved);
            document.getElementById('theme-toggle').addEventListener('click', function() {
                apply(!document.body.classList.contains('dark'));
            });
        });
    } else {
        apply(saved);
        var btn = document.getElementById('theme-toggle');
        if (btn) btn.addEventListener('click', function() {
            apply(!document.body.classList.contains('dark'));
        });
    }
})();
    """),
    # Upload zone
    ui.div(
        ui.div(
            ui.input_file(
                "csv_file",
                "Upload a CSV file to investigate:",
                accept=[".csv"],
                button_label="Browse...",
                placeholder="No file selected",
                width="340px",
            ),
            style="flex:1;",
        ),
        ui.output_ui("file_info"),
        class_="upload-zone",
    ),
    # Data preview
    ui.output_ui("data_preview"),
    # Toolbar
    ui.div(
        ui.input_action_button("start_btn", "Start Investigation", class_="start-btn"),
        ui.input_action_button("clear_btn", "Clear", class_="clear-btn"),
        ui.input_select(
            "interval",
            None,
            choices={
                "1": "1 s / message",
                "2": "2 s / message",
                "3": "3 s / message",
                "4": "4 s / message",
                "5": "5 s / message",
            },
            selected="1",
            width="140px",
        ),
        ui.output_text("status_text"),
        class_="toolbar-row",
        style="padding: 0 16px 16px; display:flex; align-items:center; gap:12px;",
    ),
    ui.layout_columns(
        ui.div(
            ui.div("Live Message Log", class_="panel-title"),
            ui.div(ui.output_ui("message_log"), class_="msg-log", id="msg-log-div"),
            ui.tags.script(
                """
                (function() {
                    var d = document.getElementById('msg-log-div');
                    if (!d) return;
                    var pinned = true;
                    d.addEventListener('scroll', function() {
                        pinned = (d.scrollHeight - d.scrollTop - d.clientHeight) < 80;
                    });
                    var observer = new MutationObserver(function() {
                        if (pinned) d.scrollTop = d.scrollHeight;
                    });
                    observer.observe(d, { childList: true, subtree: true });
                })();
            """
            ),
            style="background:#FAF5EB;border-radius:12px;padding:16px;border:1px solid #DDD0B3;",
        ),
        ui.div(
            ui.div("Agent Status", class_="panel-title"),
            ui.output_ui("agent_cards"),
            style="background:#FAF5EB;border-radius:12px;padding:16px;border:1px solid #DDD0B3;",
        ),
        col_widths=[9, 3],
    ),
    ui.output_ui("results_panel"),
    ui.tags.script(
        """
        (function() {
            var AGENTS = [
                { name: "Manager",      role: "Orchestrator",    icon: "🕵️",  color: "#4A90D9",
                  bio: "Age 42 · Favourite drink: triple-shot espresso · Once solved a mystery dataset at 2 am in his dressing gown",
                  desc: "Runs the whole operation — loads your data, briefs every agent, and keeps the pipeline moving from start to finish. Nothing happens without his sign-off." },
                { name: "DataCleaner",  role: "Quality Guard",   icon: "🧹",  color: "#E67E22",
                  bio: "Age 29 · Allergic to NaN · Owns 14 different kinds of broom (she says it's not a metaphor)",
                  desc: "Scans every single row for missing values, statistical outliers more than 3 standard deviations from the mean, and sneaky exact duplicates. She's never let a dirty row slip past her. Ever." },
                { name: "Statistician", role: "Number Cruncher", icon: "📊",  color: "#27AE60",
                  bio: "Age 35 · Reads textbooks for fun · Once argued with a calculator — and won",
                  desc: "Computes mean, standard deviation, min, max, and median for every numeric column on the cleaned dataset. Ranks them, spots the outliers, and tells you what the numbers actually mean." },
                { name: "Visualizer",   role: "Chart Builder",   icon: "📈",  color: "#8E44AD",
                  bio: "Age 31 · Colour theory enthusiast · Has opinions about pie charts (they're wrong)",
                  desc: "Translates raw statistics into a clear bar chart with a punchy title and a one-sentence insight. Believes every dataset deserves a good-looking chart." },
                { name: "Reporter",     role: "Case Writer",     icon: "📝",  color: "#C0392B",
                  bio: "Age 38 · Former investigative journalist · Still types at 120 wpm despite the RSI",
                  desc: "Pulls every finding together into a full structured report: executive summary, data quality breakdown, statistical analysis, key findings, and recommended next steps. Then hands you a download button." },
            ];

            var DURATION = 4500;
            var current = 0;
            var timer = null;
            var rafId = null;
            var startTime = null;

            var overlay  = document.createElement('div');  overlay.id = 'agent-intro-overlay';
            var card     = document.createElement('div');  card.id = 'agent-intro-card';
            var skipBtn  = document.createElement('button'); skipBtn.className = 'intro-skip'; skipBtn.textContent = 'Skip intro';
            var iconEl   = document.createElement('span');  iconEl.className = 'intro-icon';
            var nameEl   = document.createElement('div');   nameEl.className = 'intro-agent-name';
            var badgeEl  = document.createElement('span');  badgeEl.className = 'intro-badge';
            var bioEl    = document.createElement('div');   bioEl.className = 'intro-bio';
            var descEl   = document.createElement('div');   descEl.className = 'intro-desc';
            var dotsEl   = document.createElement('div');   dotsEl.className = 'intro-dots';
            var nextBtn  = document.createElement('button'); nextBtn.className = 'intro-next-btn';
            var progWrap = document.createElement('div');   progWrap.className = 'intro-progress-wrap';
            var progBar  = document.createElement('div');   progBar.className = 'intro-progress-bar';

            AGENTS.forEach(function(_, i) {
                var d = document.createElement('div');
                d.className = 'intro-dot' + (i === 0 ? ' active' : '');
                dotsEl.appendChild(d);
            });

            progWrap.appendChild(progBar);
            card.append(skipBtn, iconEl, nameEl, badgeEl, bioEl, descEl, dotsEl, nextBtn, progWrap);
            overlay.appendChild(card);

            skipBtn.addEventListener('click', dismiss);
            nextBtn.addEventListener('click', advance);

            function showSlide(i) {
                var a = AGENTS[i];
                iconEl.textContent  = a.icon;
                nameEl.textContent  = a.name;  nameEl.style.color = a.color;
                badgeEl.textContent = a.role;  badgeEl.style.background = a.color;
                bioEl.textContent   = a.bio;
                descEl.textContent  = a.desc;
                nextBtn.textContent = (i === AGENTS.length - 1) ? 'All set! →' : 'Next →';
                nextBtn.style.background = a.color;
                progBar.style.background = a.color;

                dotsEl.querySelectorAll('.intro-dot').forEach(function(d, idx) {
                    d.style.background = idx === i ? a.color : '#ddd';
                });

                clearTimeout(timer);
                cancelAnimationFrame(rafId);
                progBar.style.transition = 'none';
                progBar.style.width = '0%';
                startTime = performance.now();

                function tick(now) {
                    var pct = Math.min(((now - startTime) / DURATION) * 100, 100);
                    progBar.style.width = pct + '%';
                    if (pct < 100) { rafId = requestAnimationFrame(tick); }
                }
                rafId = requestAnimationFrame(tick);
                timer = setTimeout(advance, DURATION);
            }

            function advance() {
                clearTimeout(timer); cancelAnimationFrame(rafId);
                current++;
                if (current >= AGENTS.length) { dismiss(); } else { showSlide(current); }
            }

            function dismiss() {
                clearTimeout(timer); cancelAnimationFrame(rafId);
                overlay.classList.add('fade-out');
                setTimeout(function() { overlay.remove(); }, 500);
            }

            document.addEventListener('DOMContentLoaded', function() {
                document.body.appendChild(overlay);
                showSlide(0);
            });
        })();
        """
    ),
    style="max-width:1400px;margin:0 auto;padding:0 16px 40px;",
)


def app_server(input, output, session):

    clock = reactive.Value(0)
    active_df: reactive.Value[pd.DataFrame | None] = reactive.Value(None)

    @reactive.effect
    def _tick():
        reactive.invalidate_later(float(input.interval()))
        with reactive.isolate():
            clock.set(clock() + 1)

    @reactive.effect
    @reactive.event(input.csv_file)
    def _on_upload():
        f = input.csv_file()
        if not f:
            return
        try:
            df = _read_csv_smart(f[0]["datapath"])
            active_df.set(df)
        except Exception as exc:
            console.print(f"[red]Error reading uploaded file: {exc}[/]")

    @output
    @render.ui
    def file_info():
        df = active_df()
        if df is None:
            return ui.div()
        n_rows, n_cols = df.shape
        numeric = df.select_dtypes(include="number").shape[1]
        return ui.tags.span(
            f"{n_rows} rows, {n_cols} cols, {numeric} numeric",
            style=(
                "background:#27AE60;color:white;padding:4px 12px;"
                "border-radius:20px;font-size:0.82em;font-weight:bold;"
            ),
        )

    @output
    @render.ui
    def data_preview():
        df = active_df()
        if df is None:
            return ui.div()
        preview = df.head(5)
        header = "".join(f"<th>{c}</th>" for c in preview.columns)
        rows_html = ""
        for _, row in preview.iterrows():
            cells = "".join(
                f"<td>{'' if pd.isna(row[c]) else row[c]}</td>" for c in preview.columns
            )
            rows_html += f"<tr>{cells}</tr>"
        table_html = (
            f"<table><thead><tr>{header}</tr></thead><tbody>{rows_html}</tbody></table>"
        )
        n_rows = len(df)
        suffix = f" ({n_rows} rows total)" if n_rows > 5 else ""
        return ui.div(
            ui.div(
                f"Data Preview - first 5 rows{suffix}",
                style="font-weight:bold;font-size:0.85em;color:#555;margin-bottom:8px;font-family:'Segoe UI',sans-serif;",
            ),
            ui.HTML(table_html),
            class_="data-preview",
        )

    def _visible_msgs() -> list[AgentMessage]:
        now = time.time()
        return [m for m in list(_message_log) if m.display_after <= now]

    def _current_states() -> dict[str, str]:
        now = time.time()
        states = {
            a: "waiting"
            for a in ["DataCleaner", "Statistician", "Visualizer", "Reporter"]
        }
        for ts, agent, state in list(_state_schedule):
            if ts <= now:
                states[agent] = state
        return states

    def _is_complete() -> bool:
        return _done_after > 0 and time.time() >= _done_after

    def _still_running() -> bool:
        return _started and not _is_complete()

    @output
    @render.ui
    def message_log():
        clock()
        visible = _visible_msgs()
        if not visible:
            return ui.div(
                "Waiting for investigation to start...",
                style="color:#aaa;font-style:italic;padding:20px;text-align:center;",
            )
        return ui.div(*[_message_bubble(m) for m in visible])

    @output
    @render.ui
    def agent_cards():
        clock()
        return ui.div(
            *[
                _agent_status_card(a, _current_states()[a])
                for a in ["DataCleaner", "Statistician", "Visualizer", "Reporter"]
            ]
        )

    @output
    @render.text
    def status_text():
        clock()
        if _still_running():
            return "Investigation in progress..."
        if _is_complete():
            return "Investigation complete!"
        return ""

    @output
    @render.ui
    def results_panel():
        clock()
        if not _is_complete():
            return ui.div()
        report_md = _results.get("report", "")
        report_html = markdown2.markdown(
            report_md, extras=["tables", "fenced-code-blocks"]
        )
        import base64

        b64 = base64.b64encode(report_md.encode()).decode()
        download_js = (
            f"var a=document.createElement('a');"
            f"a.href='data:text/markdown;base64,{b64}';"
            f"a.download='investigation_report.md';a.click();"
        )
        return ui.div(
            ui.div(
                "Investigation Results", class_="panel-title", style="font-size:1.1em;"
            ),
            ui.div(
                ui.tags.button(
                    "Download Report (.md)",
                    onclick=download_js,
                    style=(
                        "float:right;background:#4A90D9;color:white;border:none;"
                        "border-radius:7px;padding:7px 18px;font-size:0.88em;"
                        "font-weight:bold;cursor:pointer;margin-bottom:10px;"
                    ),
                ),
                ui.div(
                    "Final Report",
                    style="font-weight:bold;margin-bottom:10px;color:var(--text);",
                ),
                ui.div(ui.HTML(report_html), class_="report-text"),
                style="clear:both;",
            ),
            class_="results-panel",
        )

    @reactive.effect
    @reactive.event(input.start_btn)
    def _start():
        global _started
        if _started:
            return

        df = active_df()
        if df is None:
            console.print("[red]No file loaded — upload a CSV first.[/]")
            return

        _started = True
        interval = float(input.interval())

        def _run():
            try:
                _run_investigation(df, interval)
            except Exception:
                console.print_exception()

        threading.Thread(target=_run, daemon=True).start()

    @reactive.effect
    @reactive.event(input.clear_btn)
    def _clear():
        _reset_state()
        console.print("[dim]-- Page cleared, ready to run again --[/]")


app = App(app_ui, app_server)

if __name__ == "__main__":
    import uvicorn

    console.print("Starting Data Science Detective Agency on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
