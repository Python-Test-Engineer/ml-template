"""
Claude Code hook: UserPromptSubmit
Rewrites the session CSV with the full transcript on every user turn.
Saved to <project_root>/logs/session_YYYYMMDD_HHMMSS_<id>.csv
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
    """Handle both string content and list-of-blocks content."""
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


def load_state() -> dict:
    if _STATE_FILE.exists():
        return json.loads(_STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict) -> None:
    _STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def get_csv_path(session_id: str, state: dict) -> Path:
    """Return the CSV path for this session, creating a state entry on first call."""
    if session_id not in state:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_id = session_id.replace("-", "")[:8]
        state[session_id] = f"session_{ts}_{short_id}.csv"
        save_state(state)
    return _LOGS_DIR / state[session_id]


def write_session_csv(csv_path: Path, session_id: str, transcript: list) -> None:
    """Overwrite the CSV with SESSION_START + all transcript messages."""
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

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    _LOGS_DIR.mkdir(exist_ok=True)
    data = json.loads(sys.stdin.read())
    session_id = data.get("session_id", "unknown")
    prompt = data.get("prompt", "")
    transcript = data.get("transcript", [])

    # Save last prompt for status line display
    if prompt:
        prompt_file = Path.home() / ".claude" / f"last_prompt_{session_id}.txt"
        try:
            prompt_file.write_text(prompt, encoding="utf-8")
        except Exception:
            pass

    state = load_state()
    csv_path = get_csv_path(session_id, state)

    # Append the current prompt so it is logged as a USER_MESSAGE row.
    # At UserPromptSubmit time, `transcript` only contains the *previous* history;
    # the current message is only available in `prompt`.
    if prompt:
        transcript = list(transcript) + [{"role": "user", "content": prompt}]

    write_session_csv(csv_path, session_id, transcript)


if __name__ == "__main__":
    main()
