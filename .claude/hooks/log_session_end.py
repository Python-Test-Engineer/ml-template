"""
Claude Code hook: Stop
Overwrites the session CSV with the full transcript (including the latest
assistant response) and appends a SESSION_END row.
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


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def flatten(text, limit: int = 300) -> str:
    if not isinstance(text, str):
        text = str(text)
    text = text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    return text[:limit] + "…" if len(text) > limit else text


def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return " ".join(parts)
    return str(content)


def make_row(event_type: str, session_id: str, turn_index: int = -1, **kwargs) -> dict:
    row = {f: "" for f in FIELDNAMES}
    row["event_id"] = str(uuid.uuid4())
    row["session_id"] = session_id
    row["timestamp"] = now()
    row["event_type"] = event_type
    row["turn_index"] = str(turn_index) if turn_index >= 0 else ""
    for k, v in kwargs.items():
        if k in FIELDNAMES and v is not None and v != "":
            row[k] = str(v)
    return row


def write_session_csv(csv_path: Path, session_id: str, transcript: list, stop_reason: str = "") -> None:
    """Overwrite the CSV with SESSION_START + all transcript messages + SESSION_END."""
    rows = [make_row("SESSION_START", session_id)]

    for i, msg in enumerate(transcript):
        role = msg.get("role", "")
        content = flatten(extract_text(msg.get("content", "")))
        conv_len = str(i + 1)

        if role == "user":
            rows.append(make_row(
                "USER_MESSAGE", session_id, turn_index=i,
                message_text_preview=content,
                conversation_length=conv_len,
            ))
        elif role == "assistant":
            rows.append(make_row(
                "LLM_RESPONSE", session_id, turn_index=i,
                response_text_preview=content,
                conversation_length=conv_len,
            ))

    rows.append(make_row("SESSION_END", session_id, stop_reason=stop_reason))

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    data = json.loads(sys.stdin.read())
    session_id = data.get("session_id", "unknown")
    transcript = data.get("transcript", [])
    stop_reason = data.get("stop_reason", "")

    if not _STATE_FILE.exists():
        return
    state = json.loads(_STATE_FILE.read_text(encoding="utf-8"))
    if session_id not in state:
        return

    csv_path = _LOGS_DIR / state[session_id]
    write_session_csv(csv_path, session_id, transcript, stop_reason)


if __name__ == "__main__":
    main()
