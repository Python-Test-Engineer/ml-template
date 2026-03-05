"""
Lesson 01: Multi-Agent Collaboration Dashboard
Data Science Detective Agency — Educational Shiny App

Agent logic runs synchronously and assigns future display_after timestamps.
The UI polls every 1s and reveals messages as time passes — no async needed.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any

import markdown2
import pandas as pd
import plotly.graph_objects as go
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from shiny import App, reactive, render, ui

console = Console()


# ---------------------------------------------------------------------------
# 1. Synthetic dataset
# ---------------------------------------------------------------------------

SUBJECTS = ["Math", "Science", "English", "History", "Art"]
STUDENT_NAMES = [
    "Alice", "Bob", "Carol", "David", "Eva", "Frank", "Grace", "Hiro",
    "Iris", "Jake", "Kira", "Leo", "Mia", "Noah", "Olivia", "Pete",
    "Quinn", "Rosa", "Sam", "Tina", "Uma", "Vince", "Wendy", "Xander",
    "Yara", "Zoe", "Amir", "Bella", "Caden", "Dana",
]


def generate_grades_df() -> pd.DataFrame:
    random.seed(42)
    rows = []
    for i, name in enumerate(STUDENT_NAMES):
        row: dict[str, Any] = {"student_id": i + 1, "name": name}
        for subj in SUBJECTS:
            grade = random.randint(50, 100)
            if name in ("Frank", "Pete") and subj == "Math":
                grade = None
            if name == "Xander" and subj == "Science":
                grade = 999
            if name == "Zoe":
                row["name"] = None
            row[subj] = grade
        rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. Message dataclass
# ---------------------------------------------------------------------------

AGENT_COLORS = {
    "Manager":     "#4A90D9",
    "DataCleaner": "#E67E22",
    "Statistician":"#27AE60",
    "Visualizer":  "#8E44AD",
    "Reporter":    "#C0392B",
    "SYSTEM":      "#7F8C8D",
}
AGENT_ICONS = {
    "Manager":     "🕵️",
    "DataCleaner": "🧹",
    "Statistician":"📊",
    "Visualizer":  "🎨",
    "Reporter":    "📝",
}


@dataclass
class AgentMessage:
    sender:       str
    recipient:    str
    content:      str
    msg_type:     str   # "task" | "update" | "result" | "complete"
    timestamp:    float = field(default_factory=time.time)
    display_after: float = 0.0   # wall-clock time when this message becomes visible


# ---------------------------------------------------------------------------
# 3. Shared state
# ---------------------------------------------------------------------------

_message_log:       list[AgentMessage] = []
_state_schedule:    list[tuple[float, str, str]] = []  # (time, agent, state)
_results:           dict[str, Any] = {}
_started:           bool = False
_done_after:        float = 0.0   # time when last message appears


def _reset_state() -> None:
    global _message_log, _state_schedule, _results, _started, _done_after
    _message_log    = []
    _state_schedule = []
    _results        = {}
    _started        = False
    _done_after     = 0.0


_reset_state()


# ---------------------------------------------------------------------------
# 4. Investigation runner — synchronous, assigns display timestamps
# ---------------------------------------------------------------------------

MSG_STYLE = {
    "task":     ("bold blue",    "📋 TASK"),
    "update":   ("yellow",       "💬 UPDATE"),
    "result":   ("bold green",   "📤 RESULT"),
    "complete": ("bold magenta", "🏁 DONE"),
}
AGENT_RICH_COLORS = {
    "Manager":     "bright_blue",
    "DataCleaner": "dark_orange",
    "Statistician":"green",
    "Visualizer":  "magenta",
    "Reporter":    "red",
    "SYSTEM":      "grey62",
}


def _run_investigation(interval: float = 1.0) -> None:
    """Compute everything instantly; stagger display via display_after times."""
    global _message_log, _state_schedule, _results, _done_after

    console.print(Panel(
        f"[bold white]🕵️  Data Science Detective Agency[/]\n"
        f"[dim]Generating investigation plan — messages stream every {interval:.0f} s[/]",
        style="on dark_blue", border_style="bright_blue"
    ))

    t0    = time.time()
    msgs: list[AgentMessage] = []
    sched: list[tuple[float, str, str]] = []
    delay = 0.0

    def emit(msg: AgentMessage) -> None:
        nonlocal delay
        msg.display_after = t0 + delay
        msgs.append(msg)
        style, label = MSG_STYLE.get(msg.msg_type, ("white", msg.msg_type.upper()))
        sender_color = AGENT_RICH_COLORS.get(msg.sender, "white")
        console.print(
            f"  [dim]+{delay:5.1f}s[/]  [{sender_color}]{AGENT_ICONS.get(msg.sender,'🤖')} {msg.sender:<12}[/]"
            f"[dim]→ {msg.recipient:<12}[/]  [{style}]{label}[/]  [white]{msg.content}[/]"
        )
        delay += interval

    def state_now(agent: str, state: str) -> None:
        sched.append((t0 + delay, agent, state))
        icons = {"working": "⚡", "done": "✅"}
        console.print(f"  [dim]       [/]  [dim italic]{agent} → {icons.get(state,'')} {state.upper()}[/]")

    df = generate_grades_df()
    console.print(f"\n[bold]Dataset:[/] {len(df)} rows × {len(SUBJECTS)} subjects generated\n")

    # ── Manager intro ───────────────────────────────────────────────────────
    emit(AgentMessage("SYSTEM",   "ALL", "🚀 Investigation started! Manager Agent is online.", "task"))
    emit(AgentMessage("Manager",  "ALL",
         f"Dataset loaded: {len(df)} students, {len(SUBJECTS)} subjects. Dispatching sub-agents...", "update"))

    # ── DataCleaner ─────────────────────────────────────────────────────────
    console.print("\n[bold dark_orange]── DataCleaner Phase ──[/]")
    state_now("DataCleaner", "working")
    emit(AgentMessage("Manager",     "DataCleaner",
         "Investigate the dataset for missing values and anomalies.", "task"))
    emit(AgentMessage("DataCleaner", "ALL",
         "Starting data quality scan on 30-row dataset...", "update"))

    dirty_rows: list[int] = []
    reasons:    list[str] = []
    for idx, row in df.iterrows():
        row_reasons: list[str] = []
        if pd.isna(row.get("name")):
            row_reasons.append("missing name")
        for subj in SUBJECTS:
            val = row.get(subj)
            if pd.isna(val):
                row_reasons.append(f"missing {subj} grade")
            elif isinstance(val, (int, float)) and val > 100:
                row_reasons.append(f"invalid {subj} grade ({val})")
        if row_reasons:
            dirty_rows.append(idx)
            reasons.append("; ".join(row_reasons))

    console.print(f"  [dim]Dirty rows found: {len(dirty_rows)} — {'; '.join(reasons) if reasons else 'none'}[/]")
    clean_df = df.drop(index=dirty_rows).reset_index(drop=True)
    emit(AgentMessage("DataCleaner", "Manager",
         f"Found {len(dirty_rows)} dirty row(s): {', '.join(reasons)}. Flagging for removal.", "result"))
    state_now("DataCleaner", "done")
    emit(AgentMessage("DataCleaner", "ALL",
         f"Done. Clean dataset has {len(clean_df)} rows.", "complete"))

    # ── Statistician ────────────────────────────────────────────────────────
    console.print("\n[bold green]── Statistician Phase ──[/]")
    emit(AgentMessage("Manager", "ALL", "DataCleaner done. Dispatching Statistician...", "update"))
    state_now("Statistician", "working")
    emit(AgentMessage("Manager",      "Statistician",
         "Compute summary statistics on the clean dataset.", "task"))
    emit(AgentMessage("Statistician", "ALL", "Crunching numbers...", "update"))

    numeric      = clean_df[SUBJECTS]
    means        = numeric.mean().round(2).to_dict()
    stds         = numeric.std().round(2).to_dict()
    top_subject  = max(means, key=lambda k: means[k])
    overall_mean = round(float(numeric.values.mean()), 2)

    stats_table = Table("Subject", "Mean", "Std", box=box.SIMPLE, style="dim")
    for subj in SUBJECTS:
        stats_table.add_row(subj, str(means[subj]), str(stds[subj]))
    console.print(stats_table)
    console.print(f"  [green]Overall mean: {overall_mean}  |  Top subject: {top_subject}[/]")

    emit(AgentMessage("Statistician", "Manager",
         f"Overall mean grade: {overall_mean}. Top subject: {top_subject} "
         f"(avg {means[top_subject]}). Means: "
         + ", ".join(f"{s}={v}" for s, v in means.items()), "result"))
    state_now("Statistician", "done")
    emit(AgentMessage("Statistician", "ALL", "Statistics complete!", "complete"))

    # ── Visualizer ──────────────────────────────────────────────────────────
    console.print("\n[bold magenta]── Visualizer Phase ──[/]")
    emit(AgentMessage("Manager", "ALL", "Stats ready. Dispatching Visualizer...", "update"))
    state_now("Visualizer", "working")
    emit(AgentMessage("Manager",    "Visualizer",
         "Produce a bar chart of average grades per subject.", "task"))
    emit(AgentMessage("Visualizer", "ALL", "Building Plotly figure...", "update"))

    bar_colors = ["#4A90D9", "#E67E22", "#27AE60", "#8E44AD", "#C0392B"]
    fig = go.Figure(go.Bar(
        x=list(means.keys()),
        y=list(means.values()),
        marker_color=bar_colors,
        text=[f"{v:.1f}" for v in means.values()],
        textposition="outside",
    ))
    fig.update_layout(
        title="Average Grade by Subject",
        xaxis_title="Subject", yaxis_title="Average Grade",
        yaxis_range=[0, 110], plot_bgcolor="white", paper_bgcolor="#F8F9FA",
        font=dict(family="monospace", size=13), title_font_size=16,
        margin=dict(t=60, b=40, l=40, r=20),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E0E0E0")
    console.print("  [magenta]Plotly bar chart built[/]")

    emit(AgentMessage("Visualizer", "Manager",
         "Chart ready — bar chart of subject averages generated.", "result"))
    state_now("Visualizer", "done")
    emit(AgentMessage("Visualizer", "ALL", "Visualization complete!", "complete"))

    # ── Reporter ────────────────────────────────────────────────────────────
    console.print("\n[bold red]── Reporter Phase ──[/]")
    emit(AgentMessage("Manager", "ALL", "All data ready. Dispatching Reporter...", "update"))
    state_now("Reporter", "working")
    emit(AgentMessage("Manager",  "Reporter",
         "Assemble the final investigation report from all findings.", "task"))
    emit(AgentMessage("Reporter", "ALL",
         "Reviewing findings from DataCleaner, Statistician, and Visualizer...", "update"))

    report_lines = [
        "# Case Report: Student Grades Investigation",
        "",
        "## Data Quality",
        f"- **{len(dirty_rows)} dirty row(s)** were removed before analysis.",
        "- Issues: " + ("; ".join(reasons) if reasons else "none"),
        "",
        "## Statistical Findings",
        f"- **Overall mean grade:** {overall_mean}",
        f"- **Top-performing subject:** {top_subject} (avg {means[top_subject]})",
        "- **Subject averages:**",
    ]
    for subj, avg in means.items():
        report_lines.append(f"  - {subj}: {avg} (std ±{stds.get(subj, '?')})")
    report_lines += [
        "",
        "## Conclusion",
        f"Students perform best in **{top_subject}**. "
        "Data quality was good overall with only minor anomalies detected. "
        "Recommend reviewing missing grades with class teachers.",
        "",
        "*— Assembled by the Data Science Detective Agency*",
    ]
    report_text = "\n".join(report_lines)

    emit(AgentMessage("Reporter", "Manager", "Final report assembled and ready.", "result"))
    state_now("Reporter", "done")
    emit(AgentMessage("Reporter", "ALL", "Investigation complete! Case closed. 🎉", "complete"))
    emit(AgentMessage("Manager",  "ALL",
         "All agents have completed their tasks. Investigation closed! 🎉", "complete"))

    # Commit to shared state
    _message_log    = msgs
    _state_schedule = sched
    _results["fig"]    = fig
    _results["report"] = report_text
    _done_after = t0 + delay

    console.print(Panel(
        f"[bold green]✅ Plan complete![/]  {len(msgs)} messages scheduled over {delay:.0f} s\n"
        f"[dim]Results will appear in browser after the final message at +{delay-1:.0f}s[/]",
        style="on dark_green", border_style="green"
    ))


# ---------------------------------------------------------------------------
# 5. UI helpers
# ---------------------------------------------------------------------------

def _badge(status: str) -> ui.Tag:
    colors = {"waiting": "#95A5A6", "working": "#F39C12", "done": "#27AE60"}
    labels = {"waiting": "⏳ Waiting", "working": "⚡ Working", "done": "✅ Done"}
    return ui.tags.span(
        labels.get(status, status),
        style=(
            f"background:{colors.get(status, '#95A5A6')};color:white;"
            "padding:3px 10px;border-radius:12px;font-size:0.8em;font-weight:bold;"
        )
    )


TASK_DESCRIPTIONS = {
    "DataCleaner":  "Find dirty/missing rows",
    "Statistician": "Compute summary statistics",
    "Visualizer":   "Produce bar chart",
    "Reporter":     "Assemble final report",
}


def _task_card(agent: str, status: str) -> ui.Tag:
    icon  = AGENT_ICONS.get(agent, "🤖")
    color = AGENT_COLORS.get(agent, "#555")
    return ui.div(
        ui.div(
            ui.tags.span(f"{icon} {agent}", style=f"font-weight:bold;color:{color};"),
            ui.tags.span(f" — {TASK_DESCRIPTIONS[agent]}", style="color:#555;font-size:0.85em;"),
            style="margin-bottom:6px;"
        ),
        _badge(status),
        style=(
            "background:white;border:1px solid #E0E0E0;border-radius:10px;"
            f"padding:10px 14px;margin-bottom:8px;border-left:4px solid {color};"
        )
    )


def _message_bubble(msg: AgentMessage) -> ui.Tag:
    color = AGENT_COLORS.get(msg.sender, "#555")
    icon  = AGENT_ICONS.get(msg.sender, "🤖")
    type_labels = {"task": "📋 TASK", "update": "💬 UPDATE", "result": "📤 RESULT", "complete": "🏁 DONE"}
    ts = time.strftime("%H:%M:%S", time.localtime(msg.timestamp))
    return ui.div(
        ui.div(
            ui.tags.span(f"{icon} {msg.sender}", style=f"font-weight:bold;color:{color};"),
            ui.tags.span(f" → {msg.recipient}", style="color:#888;font-size:0.85em;"),
            ui.tags.span(f"  [{type_labels.get(msg.msg_type, msg.msg_type)}]",
                         style=f"color:{color};font-size:0.75em;margin-left:6px;"),
            ui.tags.span(f"  {ts}", style="color:#aaa;font-size:0.75em;float:right;"),
            style="margin-bottom:4px;"
        ),
        ui.div(msg.content, style="color:#333;font-size:0.9em;line-height:1.4;"),
        style=(
            f"background:white;border-left:4px solid {color};"
            "border-radius:8px;padding:10px 14px;margin-bottom:8px;"
            "box-shadow:0 1px 3px rgba(0,0,0,0.07);"
        )
    )


def _agent_status_card(agent: str, status: str) -> ui.Tag:
    icon  = AGENT_ICONS.get(agent, "🤖")
    color = AGENT_COLORS.get(agent, "#555")
    roles = {
        "DataCleaner":  "Finds dirty rows & anomalies",
        "Statistician": "Computes summary statistics",
        "Visualizer":   "Produces charts & figures",
        "Reporter":     "Assembles the final report",
    }
    return ui.div(
        ui.div(
            ui.tags.span(icon, style="font-size:1.3em;margin-right:6px;"),
            ui.tags.span(agent, style=f"font-weight:bold;color:{color};font-size:0.95em;"),
            style="margin-bottom:3px;"
        ),
        ui.div(roles.get(agent, ""), style="color:#777;font-size:0.75em;margin-bottom:6px;"),
        _badge(status),
        style=(
            "background:white;border:1px solid #E0E0E0;border-radius:10px;"
            f"padding:8px 12px;margin-bottom:8px;border-left:4px solid {color};"
        )
    )


# ---------------------------------------------------------------------------
# 6. Shiny app
# ---------------------------------------------------------------------------

app_ui = ui.page_fluid(
    ui.busy_indicators.use(spinners=False, pulse=False, fade=False),
    ui.tags.style("""
        body { background: #F0F2F5; font-family: 'Segoe UI', sans-serif; }
        /* Suppress Shiny's recalculating fade */
        .recalculating { opacity: 1 !important; }
        .shiny-busy-indicator { display: none !important; }
        .header-bar {
            background: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%);
            color: white; padding: 20px 30px; margin-bottom: 24px;
            border-radius: 0 0 16px 16px;
        }
        .header-bar h2 { margin: 0; font-size: 1.5em; }
        .header-bar p  { margin: 6px 0 0; opacity: 0.75; font-size: 0.9em; }
        .panel-title {
            font-weight: bold; font-size: 0.95em; color: #333;
            text-transform: uppercase; letter-spacing: 0.05em;
            padding-bottom: 8px; margin-bottom: 14px;
            border-bottom: 2px solid #E0E0E0;
        }
        .msg-log { height: 420px; overflow-y: auto; padding: 4px 0; }
        .results-panel {
            background: white; border-radius: 12px;
            border: 1px solid #E0E0E0; padding: 20px; margin-top: 20px;
        }
        .report-text {
            background: #F8F9FA; border-radius: 8px; padding: 16px;
            font-family: 'Segoe UI', sans-serif; font-size: 0.88em;
            border: 1px solid #E0E0E0; line-height: 1.7;
        }
        .report-text h1 { font-size: 1.2em; margin: 0 0 10px; color: #1A1A2E; }
        .report-text h2 { font-size: 1.0em; margin: 14px 0 6px; color: #333;
                          border-bottom: 1px solid #ddd; padding-bottom: 3px; }
        .report-text ul { margin: 4px 0 8px 18px; padding: 0; }
        .report-text li { margin-bottom: 2px; }
        .report-text strong { color: #1A1A2E; }
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
            margin-left: 10px !important;
        }
    """),

    ui.div(
        ui.tags.h2("🕵️ Data Science Detective Agency"),
        ui.tags.p("Lesson 01: Multi-Agent Collaboration — Watch sub-agents solve a mystery dataset together"),
        class_="header-bar"
    ),

    ui.div(
        ui.input_action_button("start_btn", "▶ Start Investigation", class_="start-btn"),
        ui.input_action_button("clear_btn", "✕ Clear", class_="clear-btn"),
        ui.tags.span(
            ui.input_select(
                "interval", None,
                choices={"1": "1 s / message", "2": "2 s / message",
                         "3": "3 s / message", "4": "4 s / message", "5": "5 s / message"},
                selected="1",
                width="140px",
            ),
            style="display:inline-block;vertical-align:middle;margin-left:14px;"
        ),
        ui.output_text("status_text"),
        style="padding: 0 16px 16px; display:flex; align-items:center; gap:0;"
    ),

    ui.layout_columns(
        ui.div(
            ui.div("📋 Task Queue", class_="panel-title"),
            ui.output_ui("task_queue"),
            style="background:#F8F9FA;border-radius:12px;padding:16px;border:1px solid #E0E0E0;"
        ),
        ui.div(
            ui.div("💬 Live Message Log", class_="panel-title"),
            ui.div(ui.output_ui("message_log"), class_="msg-log", id="msg-log-div"),
            ui.tags.script("""
                (function() {
                    var d = document.getElementById('msg-log-div');
                    if (!d) return;

                    // True when user is near the bottom (or hasn't scrolled at all)
                    var pinned = true;

                    // Update pinned state when user scrolls manually
                    d.addEventListener('scroll', function() {
                        pinned = (d.scrollHeight - d.scrollTop - d.clientHeight) < 80;
                    });

                    // Scroll immediately after Shiny injects new content
                    var observer = new MutationObserver(function() {
                        if (pinned) d.scrollTop = d.scrollHeight;
                    });
                    observer.observe(d, { childList: true, subtree: true });
                })();
            """),
            style="background:#F8F9FA;border-radius:12px;padding:16px;border:1px solid #E0E0E0;"
        ),
        ui.div(
            ui.div("🤖 Agent Status", class_="panel-title"),
            ui.output_ui("agent_cards"),
            style="background:#F8F9FA;border-radius:12px;padding:16px;border:1px solid #E0E0E0;"
        ),
        col_widths=[3, 6, 3],
    ),

    ui.output_ui("results_panel"),

    style="max-width:1400px;margin:0 auto;padding:0 16px 40px;"
)


def app_server(input, output, session):

    # Single shared clock — all outputs depend on this one reactive, so they
    # all re-render together in the same flush, eliminating staggered jank.
    # isolate() prevents _tick from subscribing to clock (avoids infinite loop).
    clock = reactive.Value(0)

    @reactive.effect
    def _tick():
        reactive.invalidate_later(float(input.interval()))
        with reactive.isolate():
            clock.set(clock() + 1)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _visible_msgs() -> list[AgentMessage]:
        now = time.time()
        return [m for m in _message_log if m.display_after <= now]

    def _current_states() -> dict[str, str]:
        now = time.time()
        states = {a: "waiting" for a in ["DataCleaner", "Statistician", "Visualizer", "Reporter"]}
        for ts, agent, state in _state_schedule:
            if ts <= now:
                states[agent] = state
        return states

    def _is_complete() -> bool:
        return _done_after > 0 and time.time() >= _done_after

    def _still_running() -> bool:
        return _started and not _is_complete()

    # ── outputs ──────────────────────────────────────────────────────────────

    @output
    @render.ui
    def task_queue():
        clock()   # subscribe to shared clock
        return ui.div(*[_task_card(a, _current_states()[a])
                        for a in ["DataCleaner", "Statistician", "Visualizer", "Reporter"]])

    @output
    @render.ui
    def message_log():
        clock()
        visible = _visible_msgs()
        if not visible:
            return ui.div(
                "Waiting for investigation to start...",
                style="color:#aaa;font-style:italic;padding:20px;text-align:center;"
            )
        return ui.div(*[_message_bubble(m) for m in visible])

    @output
    @render.ui
    def agent_cards():
        clock()
        return ui.div(*[_agent_status_card(a, _current_states()[a])
                        for a in ["DataCleaner", "Statistician", "Visualizer", "Reporter"]])

    @output
    @render.text
    def status_text():
        clock()
        if _still_running():
            return "   ⚡ Investigation in progress..."
        if _is_complete():
            return "   ✅ Investigation complete!"
        return ""

    @output
    @render.ui
    def results_panel():
        clock()
        if not _is_complete():
            return ui.div()
        report_html = markdown2.markdown(_results.get("report", ""))
        fig_html = _results["fig"].to_html(full_html=False, include_plotlyjs="cdn")
        return ui.div(
            ui.div("📊 Investigation Results", class_="panel-title", style="font-size:1.1em;"),
            ui.layout_columns(
                ui.div(ui.HTML(fig_html)),
                ui.div(
                    ui.div("📝 Final Report",
                           style="font-weight:bold;margin-bottom:10px;color:#333;"),
                    ui.div(ui.HTML(report_html), class_="report-text"),
                ),
                col_widths=[6, 6],
            ),
            class_="results-panel"
        )

    # ── actions ──────────────────────────────────────────────────────────────

    @reactive.effect
    @reactive.event(input.start_btn)
    def _start():
        global _started
        if _started:
            return
        _started = True
        _run_investigation(float(input.interval()))

    @reactive.effect
    @reactive.event(input.clear_btn)
    def _clear():
        _reset_state()
        console.print("[dim]── Page cleared, ready to run again ──[/]")


app = App(app_ui, app_server)

if __name__ == "__main__":
    import uvicorn
    console.print(Panel(
        "[bold white]🕵️  Data Science Detective Agency[/]\n"
        "[dim]Lesson 01: Multi-Agent Collaboration[/]\n\n"
        "[bright_blue]http://127.0.0.1:8000[/]  ← open in browser\n"
        "[dim]Click [bold]▶ Start Investigation[/dim] to begin",
        title="[bold]Starting server[/]",
        border_style="bright_blue",
    ))
    uvicorn.run(app, host="127.0.0.1", port=8000)
