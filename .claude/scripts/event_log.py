"""
Event Logger — CSV audit log

All events during a session are written as rows to:
    logs/session_YYYYMMDD_HHMMSS_<8chars-uuid>.csv

Public API:
    init_session()               → str   open log file, write SESSION_START
    close_session()              → None  write SESSION_END, flush & close
    increment_turn()             → None  call once per run_agent() invocation
    increment_llm_round()        → None  call once per stream() call
    log_event(event_type, **kw)  → None  append one row (no-ops if not initialized)
    summarize_args(tool_input)   → str   redacted JSON summary of tool args
"""

import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


_HERE = Path(__file__).resolve().parent   # .claude/scripts/
_PROJECT_ROOT = _HERE.parent.parent       # project root
_LOGS_DIR = _PROJECT_ROOT / "logs"       # <project_root>/logs/

# ---------------------------------------------------------------------------
# Column definitions (37 columns)
# ---------------------------------------------------------------------------

FIELDNAMES = [
    # Universal — present on every row
    "event_id",
    "session_id",
    "timestamp",
    "event_type",
    "turn_index",
    "llm_round",
    # LLM
    "model",
    "prompt_tokens",
    "completion_tokens",
    "stop_reason",
    "response_text_preview",
    "tool_use_count",
    # Tool call (args + result merged into one row)
    "tool_name",
    "tool_use_id",
    "tool_args_summary",
    "result_preview",
    "is_error_result",
    # File write
    "file_path",
    "bytes_written",
    "lines_written",
    "write_operation",
    # Code execution
    "exec_type",
    "exec_success",
    "exec_exit_code",
    "exec_duration_ms",
    "exec_output_preview",
    "validation_errors",
    "code_preview",
    # Web
    "web_query",
    "web_url",
    "web_result_count",
    # User / session
    "message_text_preview",
    "slash_command_name",
    "file_ref_count",
    "conversation_length",
    "error_message",
    "error_traceback",
]

# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------

_session_id: str | None = None
_file_handle = None
_writer = None
_log_path: Path | None = None
_turn_index: int = -1  # incremented to 0 on first increment_turn() call
_llm_round: int = -1  # incremented to 0 on first increment_llm_round() per turn

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _flatten(text: str, limit: int = 300) -> str:
    """Truncate to limit chars and collapse newlines to spaces for CSV safety."""
    if not isinstance(text, str):
        text = str(text)
    text = text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    if len(text) > limit:
        text = text[:limit] + "…"
    return text


def _write_row(event_type: str, **kwargs) -> None:
    """Build and write one CSV row. Only called internally after guard checks."""
    row = {f: "" for f in FIELDNAMES}
    row["event_id"] = str(uuid.uuid4())
    row["session_id"] = _session_id or ""
    row["timestamp"] = _now()
    row["event_type"] = event_type
    row["turn_index"] = str(_turn_index) if _turn_index >= 0 else ""
    row["llm_round"] = str(_llm_round) if _llm_round >= 0 else ""
    for k, v in kwargs.items():
        if k in FIELDNAMES and v is not None and v != "":
            row[k] = str(v)
    _writer.writerow(row)
    _file_handle.flush()


# Keys whose full values are redacted in tool_args_summary
_REDACT_KEYS = {"content", "new_string", "old_string"}
# Key fragments that suggest secrets
_SECRET_PATTERNS = ("_key", "_secret", "_token", "password", "api_key")

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def summarize_args(tool_input: dict) -> str:
    """Return a JSON string summarising tool args with sensitive values redacted."""
    out = {}
    for k, v in tool_input.items():
        if k in _REDACT_KEYS:
            out[k] = f"<{len(v) if isinstance(v, str) else '?'} chars>"
        elif isinstance(v, str) and any(p in k.lower() for p in _SECRET_PATTERNS):
            out[k] = "<redacted>"
        elif isinstance(v, str) and len(v) > 200:
            out[k] = v[:200] + "…"
        else:
            out[k] = v
    return json.dumps(out, ensure_ascii=False)


def get_log_path() -> "Path | None":
    """Return the path of the current session's CSV log file, or None if not initialised."""
    return _log_path


def init_session() -> str:
    """Open a new log file and write a SESSION_START row. Returns the session_id."""
    global _session_id, _file_handle, _writer, _log_path, _turn_index, _llm_round

    _session_id = str(uuid.uuid4())
    _turn_index = -1
    _llm_round = -1

    logs_dir = _LOGS_DIR
    logs_dir.mkdir(exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = _session_id.replace("-", "")[:8]
    _log_path = logs_dir / f"session_{ts}_{short_id}.csv"

    _file_handle = open(_log_path, "w", newline="", encoding="utf-8")
    _writer = csv.DictWriter(_file_handle, fieldnames=FIELDNAMES)
    _writer.writeheader()

    _write_row("SESSION_START")
    return _session_id


def close_session() -> None:
    """Write SESSION_END, flush, and close the log file."""
    global _file_handle, _writer

    if _writer is None:
        return

    _write_row("SESSION_END")
    _file_handle.flush()
    _file_handle.close()
    _file_handle = None
    _writer = None


def increment_turn() -> None:
    """Call once per run_agent() invocation. Resets the llm_round counter."""
    global _turn_index, _llm_round
    _turn_index += 1
    _llm_round = -1


def increment_llm_round() -> None:
    """Call once just before each client.messages.stream() call."""
    global _llm_round
    _llm_round += 1


def log_event(event_type: str, **kwargs) -> None:
    """Append one event row. No-ops silently if the session is not initialized."""
    if _writer is None:
        return
    _write_row(event_type, **kwargs)
