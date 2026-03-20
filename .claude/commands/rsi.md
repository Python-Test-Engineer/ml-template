---
description: "Recursive self-improvement: analyse past Claude sessions to detect patterns and apply targeted improvements to commands, skills, and agents. Usage: /rsi [commands|skills|agents|all]"
argument-hint: "commands | skills | agents | all (default: all)"
allowed-tools: Read, Glob, Bash(ls *), Bash(ls -lt *), Bash(python3 -c *), Bash(mkdir *), Write, Edit, AskUserQuestion
model: Opus
---

> **Model:** This command requires **claude-opus-4-6** (Claude Opus 4.6). Deep cross-session pattern synthesis requires extended reasoning. If not already on Opus, switch with `/model claude-opus-4-6` before invoking.

**Usage:** `/rsi [commands|skills|agents|all]`
Example: `/rsi all` — analyse all session history and propose improvements across commands, skills, and agents.

---

## Step 1 — Parse Arguments

Read `$ARGUMENTS`. Extract:
- `SCOPE` = first token, one of: `commands`, `skills`, `agents`, `all`
- If missing or unrecognised → default to `all`

Announce: `Running /rsi — scope: <SCOPE>`

---

## Step 2 — Locate Session Files

List the 10 most recently modified `.jsonl` session files for this project:

```bash
ls -lt C:/Users/mrcra/.claude/projects/C--Users-mrcra-Desktop-data-intelligence-researcher/*.jsonl
```

Take the **10 most recently modified** files. Record each filename (UUID stem) and its modification timestamp.

If no `.jsonl` files are found, tell the user: "No session files found. Run at least one work session before invoking `/rsi`." and stop.

Tell the user: `Found N session files — analysing the 10 most recent.`

---

## Step 3 — Parse Each Session

For each session file, run the following inline Python script via `Bash` to extract the conversation turns. Substitute the actual file path:

```bash
python3 -c "
import json, sys

path = '<SESSION_FILE_PATH>'
turns = []
try:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            role = obj.get('type', '')
            if role not in ('user', 'assistant'):
                continue

            # Extract text content
            text = ''
            msg = obj.get('message', {})
            content = msg.get('content', [])
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get('type') == 'text':
                        text += part.get('text', '')

            # Noise filters for user messages
            if role == 'user':
                stripped = text.strip()
                # Skip pure command invocations, interrupted requests, system tags
                if stripped.startswith('<local-command-caveat>'):
                    continue
                if '[Request interrupted' in stripped:
                    continue
                if stripped.startswith('<command-name>') and len(stripped) < 80:
                    continue
                if len(stripped) < 5:
                    continue
                if '<command-message>' in stripped:
                    continue
                if len(stripped) > 200 and stripped.startswith('# ') and '## ' in stripped:
                    continue

            # Truncate to 600 chars
            text = text[:600]
            if text:
                turns.append({'role': role, 'text': text})

except Exception as e:
    turns.append({'role': 'error', 'text': str(e)})

print(json.dumps(turns))
"
```

Collect the parsed turns per session. If a session errors or returns empty, note it but continue.

---

## Step 4 — Build Signal Inventory

ultrathink

With all parsed session turns in context, synthesise across sessions to identify signals in **5 categories**:

### Signal Categories

| Category | What to look for |
|----------|-----------------|
| **User Corrections** | User messages with corrective tone after an assistant turn — phrases like "no", "don't", "that's wrong", "I said", "stop doing", "you should have" |
| **Recurring Errors** | The same type of failure appearing in 2 or more sessions — same wrong assumption, missing step, wrong tool choice |
| **Prompt Friction** | User re-stated context or preferences that Claude should already know — repeated explanations, re-specifications of established rules |
| **Missing Rules** | Decisions requiring correction that a single added rule in a command/skill would prevent going forward |
| **Positive Patterns** | Approaches the user confirmed or accepted without pushback — preserve these, do NOT change |

### Weak Signal Policy

- Signals appearing in only **1 session** → flagged in log, **not acted upon**
- Signals appearing in **2+ sessions** → eligible for proposed change

---

## Step 5 — Build Findings Table

For each signal that meets the evidence threshold (2+ sessions), build a findings entry:

| # | Signal Type | Description | Affected File | Severity | Proposed Fix | Sessions |
|---|-------------|-------------|---------------|----------|-------------|---------|
| 1 | ... | ... | ... | High/Medium/Low | ... | UUID1, UUID2 |

**Severity guidelines:**
- **High** — causes task failure or requires significant user correction
- **Medium** — causes friction, redundant effort, or user confusion
- **Low** — minor style or wording improvement

For each proposed fix, determine the **target file** from the scope:
- Commands → `.claude/commands/*.md`
- Skills → `.claude/skills/*/SKILL.md`
- Agents → `.claude/agents/*.md`

**Safety guardrails — never propose changes to:**
- `CLAUDE.md`
- Any file in `src/`
- Any file in `data/` or `output/`

---

## Step 6 — Filter by Scope

Discard any findings whose target file falls outside `SCOPE`:
- `commands` → keep only `.claude/commands/*.md` targets
- `skills` → keep only `.claude/skills/*/SKILL.md` targets
- `agents` → keep only `.claude/agents/*.md` targets
- `all` → keep all findings

If no findings remain after filtering, tell the user: "No actionable signals found within scope `<SCOPE>`. Either no recurring patterns were detected, or all signals were weak (single-session). See the change log for weak signals noted." Then write the change log (Step 8) and stop.

---

## Step 7 — Present Proposals and Gate

Present the full findings table to the user. Then for each proposed change, show:

```
Change N — <target file>
Severity: High / Medium / Low
Signal: <1-sentence description>
Sessions: <UUID list>

BEFORE:
  <exact lines to be replaced>

AFTER:
  <replacement lines>

Evidence: "<user message excerpt>" — session <UUID>
```

Then call `AskUserQuestion` with:

```
I found N proposed changes. How would you like to proceed?

1. Apply all — apply every proposed change immediately
2. Review one-by-one — I'll show each change and ask for confirmation before applying
3. Cancel — discard all proposals (change log will still be written with findings)
```

### If "Apply all"
Proceed directly to Step 8 with all proposed changes approved.

### If "Review one-by-one"
For each change in order:
- Present the before/after diff
- Call `AskUserQuestion`: "Apply this change? (yes / skip / cancel all)"
- `yes` → mark approved
- `skip` → mark skipped
- `cancel all` → stop applying, mark remaining as skipped

### If "Cancel"
Mark all changes as skipped. Proceed to Step 8 (write log only).

---

## Step 8 — Apply Edits and Write Change Log

### Apply Approved Changes

For each approved change:
1. Read the target file with `Read` tool
2. Apply the **surgical minimal edit** using `Edit` tool — never rewrite the entire file
3. Verify the edit was applied correctly

### Get Timestamp

```bash
python3 -c "from datetime import datetime; print(datetime.now().strftime('%Y%m%d_%H%M%S'))"
```

Set `TIMESTAMP` to the output.

### Write Change Log

Ensure the `logs/` directory exists:

```bash
mkdir -p C:/Users/mrcra/Desktop/data-intelligence-researcher/logs
```

Write `logs/rsi_<TIMESTAMP>.md` with the following structure:

```markdown
# RSI Change Log — <TIMESTAMP>

**Run date:** <YYYY-MM-DD HH:MM:SS>
**Scope:** <commands|skills|agents|all>
**Sessions analysed:** <N>
**Session date range:** <oldest to newest modification date>
**Session files:**
- <UUID1>.jsonl
- <UUID2>.jsonl
...

---

## Signals Found

| # | Type | Description | Sessions | Severity |
|---|------|-------------|----------|----------|
| 1 | ... | ... | ... | ... |

---

## Changes Applied

### Change N — <file path>

**Rationale:** <why this change addresses the signal>
**Type:** Addition | Clarification | Rule | Removal
**Before:**
```
<exact lines before>
```
**After:**
```
<exact lines after>
```
**Signal source:** Session <UUID> — "<user message excerpt>"

---

## Changes Skipped / Deferred

| # | File | Reason skipped |
|---|------|----------------|
| 1 | ...  | User skipped / User cancelled |

---

## Signals Noted But Not Actioned (Weak — Single Session)

| # | Type | Description | Session | Notes |
|---|------|-------------|---------|-------|
| 1 | ... | ... | ... | Appears in only 1 session — monitor for recurrence |
```

> **Always write the change log**, even if 0 changes were applied. The log is the audit trail.

### Final Summary

Tell the user:
- Sessions analysed: N
- Signals found: N (breakdown by category)
- Changes applied: N
- Changes skipped: N
- Weak signals logged: N
- Change log saved to: `logs/rsi_<TIMESTAMP>.md`

If changes were applied, list each modified file with a one-line description of what changed.
