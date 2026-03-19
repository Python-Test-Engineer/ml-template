"""
Extract conversations from session CSV logs and save to conversation.json.
Merges with any pre-existing conversation.json content.
"""

import csv
import glob
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))   # .claude/scripts/
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))  # project root
LOGS_DIR = os.path.join(_PROJECT_ROOT, "logs")
OUTPUT_FILE = os.path.join(LOGS_DIR, "conversation.json")


def load_existing_json():
    """Load existing conversation.json, normalising to a list of sessions."""
    if not os.path.exists(OUTPUT_FILE):
        return []
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Could be a single session dict or already a list
    if isinstance(data, dict):
        return [data]
    return data


def parse_csv(path):
    """Parse one session CSV and return a session dict (or None if empty)."""
    messages = []
    session_id = None
    start_time = None

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            event = row.get("event_type", "")
            ts = row.get("timestamp", "")

            if not session_id and row.get("session_id"):
                session_id = row["session_id"]

            if event == "SESSION_START":
                start_time = ts

            elif event == "USER_MESSAGE":
                content = row.get("message_text_preview", "").strip()
                messages.append({
                    "type": "user",
                    "timestamp": ts,
                    "content": content,
                })

            elif event == "LLM_RESPONSE":
                content = row.get("response_text_preview", "").strip()
                messages.append({
                    "type": "assistant",
                    "timestamp": ts,
                    "content": content,
                    "tokens_used": {
                        "prompt": row.get("prompt_tokens", ""),
                        "completion": row.get("completion_tokens", ""),
                    },
                    "tool_use_count": row.get("tool_use_count", "0"),
                })

    if not session_id or not messages:
        return None

    return {
        "session_id": session_id,
        "start_time": start_time or "",
        "messages": messages,
    }


def main():
    existing = load_existing_json()
    existing_ids = {s["session_id"] for s in existing}

    csv_files = sorted(glob.glob(os.path.join(LOGS_DIR, "session_*.csv")))
    csv_sessions = []
    for path in csv_files:
        session = parse_csv(path)
        if session and session["session_id"] not in existing_ids:
            csv_sessions.append(session)
            existing_ids.add(session["session_id"])

    # Sort all sessions by start_time, prepend existing (they have earlier dates)
    all_sessions = existing + csv_sessions
    all_sessions.sort(key=lambda s: s.get("start_time") or "")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_sessions, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_sessions)} session(s) to {OUTPUT_FILE}")
    for s in all_sessions:
        print(f"  {s['session_id']}  {s.get('start_time','')}  ({len(s['messages'])} messages)")


if __name__ == "__main__":
    main()
