# RSI Architecture — Recursive Self-Improvement System

**Created:** 2026-03-19
**Command:** `/rsi [commands|skills|agents|all]`
**Command file:** `.claude/commands/rsi.md`

---

## Purpose

The RSI system closes the *session → improvement* feedback loop. As Claude works across multiple sessions, it makes mistakes, receives corrections, and establishes patterns. Without a mechanism to capture and apply these signals, the same errors recur indefinitely.

`/rsi` reads past `.jsonl` session files, synthesises correction and friction signals across them, proposes targeted edits to the command/skill/agent markdown files that govern Claude's behaviour, gates every change through user approval, and writes an immutable audit log.

---

## Data Flow

```
Session JSONL files (10 most recent)
        │
        ▼
  python3 -c parser (stdlib only)
  • Extracts user + assistant turns
  • Noise filters: system tags, interruptions, trivial messages
  • Truncates to 600 chars per turn
        │
        ▼
  Signal Inventory (Claude synthesis — Opus ultrathink)
  • User Corrections
  • Recurring Errors
  • Prompt Friction
  • Missing Rules
  • Positive Patterns
        │
        ▼
  Findings Table
  • Per-signal: file, severity, proposed fix, session evidence
  • Weak signals (1 session) → flagged, not actioned
        │
        ▼
  Scope Filter
  • commands → .claude/commands/*.md only
  • skills   → .claude/skills/*/SKILL.md only
  • agents   → .claude/agents/*.md only
  • all      → no filter
        │
        ▼
  User Gate (AskUserQuestion)
  • Apply all / Review one-by-one / Cancel
        │
        ▼
  Edit tool — surgical minimal changes
        │
        ▼
  rsi/<TIMESTAMP>.md — change log (always written)
```

---

## Session Parsing

| Parameter | Value |
|-----------|-------|
| Session directory | `C:/Users/mrcra/.claude/projects/C--Users-mrcra-Desktop-data-intelligence-researcher/` |
| File pattern | `*.jsonl` (top-level only, not recursive) |
| Files selected | 10 most recently modified (by `ls -lt`) |
| Parser | `python3 -c` inline script — stdlib only (`json`, `sys`) |
| Max text per turn | 600 characters (truncated) |

### Noise Filters (applied to user messages)

| Filter | Condition |
|--------|-----------|
| System tags | Starts with `<local-command-caveat>` |
| Interrupted requests | Contains `[Request interrupted` |
| Pure command invocations | Starts with `<command-name>` and length < 80 chars |
| Trivial messages | Length < 5 characters |

---

## Signal Categories

| Category | Description | Evidence Threshold |
|----------|-------------|-------------------|
| **User Corrections** | Corrective tone after assistant turn — "no", "don't", "stop", "wrong", "I said" | 2+ sessions to act |
| **Recurring Errors** | Same failure type in 2+ sessions — wrong assumption, missing step, wrong tool | 2+ sessions to act |
| **Prompt Friction** | User re-stated context Claude should know — repeated explanations, re-specifications | 2+ sessions to act |
| **Missing Rules** | Correctable decision pattern — a single rule addition would prevent future recurrence | 2+ sessions to act |
| **Positive Patterns** | Approaches user confirmed without pushback — preserve, do not change | N/A — noted only |

---

## Scope Argument Reference

| Argument | Files in scope |
|----------|---------------|
| `commands` | `.claude/commands/*.md` |
| `skills` | `.claude/skills/*/SKILL.md` |
| `agents` | `.claude/agents/*.md` |
| `all` (default) | All of the above |

---

## Safety Constraints

1. **Surgical edits only** — `Edit` tool with targeted `old_string` / `new_string`. Never rewrite an entire file.
2. **Evidence required** — every proposed change must cite at least one specific session UUID and a user message excerpt.
3. **User gate** — `AskUserQuestion` is called before any write. No silent modifications.
4. **Protected files** — `/rsi` never proposes changes to:
   - `CLAUDE.md`
   - Any file in `src/`
   - Any file in `data/` or `output/`
5. **Weak signal policy** — signals from only 1 session are logged but never actioned. A change requires 2+ session evidence.
6. **Change log always written** — `rsi/<TIMESTAMP>.md` is created every run, even if 0 changes are applied. This provides a complete audit trail.

---

## Change Log Format

Each run writes `rsi/<YYYYMMDD_HHMMSS>.md` containing:

```
# RSI Change Log — <timestamp>

Run metadata: date, scope, sessions analysed, date range, file list

## Signals Found          — table of all signals detected
## Changes Applied        — per-change: file, rationale, type, before, after, evidence
## Changes Skipped        — user-declined or cancelled changes
## Signals Not Actioned   — weak signals (single-session) for monitoring
```

Change log files are **append-only** (each run writes a new file) and serve as the rollback reference — the "Before" sections contain the original text needed to undo any change.

---

## Recommended Cadence

Run `/rsi` every **5–10 sessions** of active work. More frequent runs may lack sufficient signal. Less frequent runs accumulate too many sessions to synthesise effectively.

---

## Model Requirement

`/rsi` uses `model: Opus` (claude-opus-4-6). Signal synthesis across 10 sessions with cross-referencing, pattern matching, and evidence-grounded proposals requires the deepest reasoning available. This matches the model choice in `/planner` and `/insights`.

---

## Future Extensions

| Extension | Description |
|-----------|-------------|
| **Auto-trigger hook** | Configure a `stop` hook in `settings.json` to prompt `/rsi` every N sessions automatically |
| **Memory integration** | Write detected positive patterns to `memory/feedback_*.md` for cross-project retention |
| **Rollback command** | `/rsi-rollback <timestamp>` reads a change log's "Before" sections and reverts edits |
| **Broader scope** | Extend to `CLAUDE.md` sections that don't govern scripts (currently excluded for safety) |
| **Similarity clustering** | Use embeddings to cluster semantically similar signals across many sessions |
