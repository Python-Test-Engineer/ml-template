"""
Claude Code hook: Stop
Appends a SESSION_END row to the active session CSV when Claude finishes a turn.
"""

import csv
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent   # .claude/hooks/
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent       # project root
_LOGS_DIR = _PROJECT_ROOT / "logs"
_STATE_FILE = _LOGS_DIR / ".session_starts.json"

FIELDNAMES = [
    "event_id", "session_id", "timestamp", "event_type", "turn_index", "llm_round",
    "model", "prompt_tokens", "completion_tokens", "stop_reason", "response_text_preview",
    "tool_use_count", "tool_name", "tool_use_id", "tool_args_summary", "result_preview",
    "is_error_result", "file_path", "bytes_written", "lines_written", "write_operation",
    "exec_type", "exec_success", "exec_exit_code", "exec_duration_ms", "exec_output_preview",
    "validation_errors", "code_preview", "web_query", "web_url", "web_result_count",
    "message_text_preview", "slash_command_name", "file_ref_count", "conversation_length",
    "error_message", "error_traceback",
]


def main() -> None:
    data = json.loads(sys.stdin.read())
    session_id = data.get("session_id", "unknown")

    if not _STATE_FILE.exists():
        return
    state = json.loads(_STATE_FILE.read_text(encoding="utf-8"))
    if session_id not in state:
        return

    csv_path = _LOGS_DIR / state[session_id]
    if not csv_path.exists():
        return

    row = {f: "" for f in FIELDNAMES}
    row["event_id"] = str(uuid.uuid4())
    row["session_id"] = session_id
    row["timestamp"] = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    row["event_type"] = "SESSION_END"

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)


if __name__ == "__main__":
    main()
