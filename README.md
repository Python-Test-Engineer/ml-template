# Agentic ML Template

A structured template for AI-assisted oncology data science using Claude Code. Drop in a dataset, describe what you want to analyse, and follow a three-phase workflow — Claude handles the profiling, planning, coding, and execution.

---

## Prerequisites

- [Claude Code](https://claude.ai/code) installed and authenticated
- [uv](https://docs.astral.sh/uv/) installed (`pip install uv` or see uv docs)

---

## Setup

```bash
uv sync
```

That's it. Claude will install any additional packages it needs automatically as it works.

---

## Workflow

The project follows three phases, each driven by a slash command.

### Phase 1 — Plan
```
/plan _ideas/<filename>
```
Write a short idea file in `_ideas/` describing what you want to explore — it can be rough notes, bullet points, or a few sentences. Claude will read it, profile the dataset, ask any clarifying questions, and produce a structured research plan in `_plans/`.

### Phase 2 — Spec
```
/spec _plans/<filename>
```
Claude reads the plan and writes a detailed technical spec in `_specs/` — covering script architecture, data contracts, dirty-row rules, output files, and the exact run order. Review this before proceeding; it is the contract for what gets built.

### Phase 3 — Execute
```
/execute _specs/<filename>
```
Claude implements all scripts from the spec into `src/`, runs them in order, fixes any errors, and validates that all expected outputs exist in `output/PROJECT_XX/`.

---

## Directory Layout

```
_ideas/      Your research ideas (input to /plan)
_plans/      Research plans produced by /plan (input to /spec)
_specs/      Technical specs produced by /spec (input to /execute)
src/         Python scripts written by /execute
data/        Raw datasets — gitignored, never modified
output/      All generated outputs (plots, CSVs, reports)
  PROJECT_01/
  PROJECT_02/
  ...
.claude/
  commands/  Slash command definitions (/plan, /spec, /execute)
  agents/    Specialist sub-agents (e.g. code-quality-reviewer)
```

---

## Datasets

Place datasets in the `data/` folder. They are **gitignored** — never committed to the repo.

Reference a dataset in your idea file by filename, e.g. `data/neuroblastoma.csv`. Claude will locate and profile it automatically during the plan phase.

---

## Output

Each project run writes to its own subfolder: `output/PROJECT_01`, `output/PROJECT_02`, etc. The next available number is always used automatically.

Every run produces at minimum:
- `dirty.csv` — rows removed during cleaning, with a `reason` column
- Plot files (`.png`)
- A plain-text `report.txt` summarising results

---


## Tips

- **Rough ideas are fine.** The idea file does not need to be structured — a few sentences or bullet points are enough for `/plan` to work with.
- **Review the spec before executing.** The spec phase is your chance to catch misunderstandings before any code is written.
- **Use screenshots.** Paste an image directly into the Claude Code terminal, or reference a saved file with `@filename`. Claude can read charts, error messages, and UI screenshots to help diagnose issues.
- **Just ask.** If you are unsure what to do at any point, describe the situation in plain language and Claude will advise.
