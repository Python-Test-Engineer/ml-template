#!/usr/bin/env python3
"""
Claude Code Status Line - Usage Display
Shows context usage, token counts, cost, and model info.

Install:
  chmod +x ~/.claude/statusline.py

Add to ~/.claude/settings.json:
  {
    "statusLine": {
      "type": "command",
      "command": "~/.claude/statusline.py"
    }
  }
"""

import json
import sys


def make_bar(pct: float, width: int = 10) -> str:
    filled = round(pct / 100 * width)
    return "▓" * filled + "░" * (width - filled)


def color(text: str, pct: float) -> str:
    if pct >= 80:
        code = "\033[31m"   # Red
    elif pct >= 50:
        code = "\033[33m"   # Yellow
    else:
        code = "\033[32m"   # Green
    return f"{code}{text}\033[0m"


def fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(n)


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        print("⚠ No data")
        return

    # ── Model ──────────────────────────────────────────────
    model_raw = (
        data.get("model", {}).get("api_model_id", "")
        or data.get("model", {}).get("name", "")
    )
    if "opus" in model_raw.lower():
        model_label = "Opus"
    elif "sonnet" in model_raw.lower():
        model_label = "Sonnet"
    elif "haiku" in model_raw.lower():
        model_label = "Haiku"
    else:
        model_label = model_raw.split("-")[1].capitalize() if "-" in model_raw else (model_raw or "?")

    # ── Context window ─────────────────────────────────────
    ctx = data.get("context_window", {})
    window_size = ctx.get("context_window_size", 0)
    usage = ctx.get("current_usage") or {}

    input_tok   = usage.get("input_tokens", 0)
    output_tok  = usage.get("output_tokens", 0)
    cache_write = usage.get("cache_creation_input_tokens", 0)
    cache_read  = usage.get("cache_read_input_tokens", 0)

    used_input = input_tok + cache_write + cache_read
    pct = (used_input / window_size * 100) if window_size else 0

    bar = make_bar(pct)
    pct_str = color(f"{pct:5.1f}%", pct)
    bar_str = color(bar, pct)

    used_str  = fmt_tokens(used_input)
    total_str = fmt_tokens(window_size)

    # ── Cost ───────────────────────────────────────────────
    cost_usd = data.get("cost", {}).get("total_cost_usd", 0) or 0
    cost_str = f"${cost_usd:.4f}" if cost_usd else ""

    # ── Assemble line ──────────────────────────────────────
    parts = [f"🤖 {model_label}"]

    if window_size:
        parts.append(f"{bar_str} {pct_str} ({used_str}/{total_str})")
    
    if output_tok:
        parts.append(f"out:{fmt_tokens(output_tok)}")

    if cache_read:
        parts.append(f"💾 cache:{fmt_tokens(cache_read)}")

    if cost_str:
        parts.append(f"💰 {cost_str}")

    print("  |  ".join(parts))


if __name__ == "__main__":
    main()
