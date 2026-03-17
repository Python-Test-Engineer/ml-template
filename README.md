# 🧠 Data Intelligence Researcher

> **AI-assisted data science — you bring the ideas, Claude does the heavy lifting.**

---

## ⚡ TL;DR — It's This Simple

**Got a dataset and a research question? Here's all you do:**

```
1.  Write your idea (rough notes are fine!)  →  _ideas/my-idea.md
2.  /plan  _ideas/my-idea.md
3.  /spec  _plans/my-idea.md
4.  /execute  _specs/my-idea.md
```

That's it. Claude profiles your data, writes the code, runs it, and saves the results. No boilerplate. No setup. Just answers.

---

## 🗺️ The Workflow at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   📝 You write a brain dump          _ideas/my-idea.md         │
│      (bullet points, rough notes,                               │
│       a few sentences — anything!)                              │
│                                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼  /plan _ideas/my-idea.md
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   🔍 Claude reads your idea, profiles    _plans/my-idea.md     │
│      the dataset, asks questions,                               │
│      and writes a research plan                                 │
│                                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼  /spec _plans/my-idea.md
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   🏗️  Claude turns the plan into a      _specs/my-idea.md      │
│      detailed technical spec — scripts,                         │
│      data rules, outputs, run order                             │
│                                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼  /execute _specs/my-idea.md
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   🚀 Claude writes every script, runs    output/PROJECT_XX/    │
│      them in order, fixes errors, and                           │
│      delivers plots, CSVs, and a report                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✍️ Step 0 — Write Your Idea

Create a file in `_ideas/`. It can be as rough as you like:

```markdown
# Survival Analysis

I want to know which gene expression features best predict
patient survival in the neuroblastoma dataset.

- Try Kaplan-Meier curves
- Maybe a Cox proportional hazards model?
- Compare high-risk vs low-risk groups
- Dataset: data/neuroblastoma.csv
```

That's genuinely all you need. Claude will figure out the rest.

---

## 🔍 Step 1 — `/plan` (Claude thinks it through)

```
/plan _ideas/my-idea.md
```

Claude will:
- 📂 Read your idea file
- 📊 Profile the dataset (shape, columns, missing values, distributions)
- 💬 Ask any clarifying questions
- 📋 Save a structured research plan to `_plans/my-idea.md`

**Review the plan** — this is where you steer the direction before any code is written.

---

## 🏗️ Step 2 — `/spec` (Claude architects the solution)

```
/spec _plans/my-idea.md
```

Claude will:
- 🗂️ Design the script architecture
- 📐 Define data contracts and cleaning rules
- 📁 List every output file that will be produced
- 💾 Save a detailed technical spec to `_specs/my-idea.md`

**Review the spec** — this is the blueprint. Catch any issues here before code is written.

---

## 🚀 Step 3 — `/execute` (Claude builds and runs everything)

```
/execute _specs/my-idea.md
```

Claude will:
- 💻 Write all Python scripts into `src/`
- ▶️ Run them in the correct order
- 🔧 Fix any errors automatically
- ✅ Validate that all expected outputs exist
- 📁 Save everything to `output/PROJECT_XX/`

You'll get plots, CSVs, and a report — ready to review.

---

## 🛠️ All Skills Reference

All slash commands available in this project:

### Core Research Pipeline

| Skill | Usage | What it does |
|-------|-------|--------------|
| `/plan` | `/plan _ideas/<file>` | Reads idea file, profiles dataset, asks clarifying questions, saves structured research plan to `_plans/` |
| `/spec` | `/spec _plans/<file>` | Translates a research plan into a detailed Python technical spec (scripts, data contracts, outputs) saved to `_specs/` |
| `/execute` | `/execute _specs/<file>` | Implements all scripts, runs them in phase order, fixes errors, validates all outputs in `output/PROJECT_XX/` |

### Output & Presentation

| Skill | Usage | What it does |
|-------|-------|--------------|
| `/dashboard` | `/dashboard output/PROJECT_XX` | Builds and launches an interactive Shiny Dash dashboard from a completed project output folder |
| `/style` | `/style` | Select and apply an output style for the current conversation |

### Code Quality & Review

| Skill | Usage | What it does |
|-------|-------|--------------|
| `code-quality-reviewer` | *automatic after `/execute`, or ask "review the code"* | Inspects the diff for reproducibility, data contracts, clinical safety, code correctness, error handling, and output validation. Reports issues with severity levels (Critical / High / Medium / Low) |
| `/simplify` | `/simplify` | Reviews changed code for reuse, quality, and efficiency, then fixes any issues found |

### Environment & Configuration

| Skill | Usage | What it does |
|-------|-------|--------------|
| `/uv` | `/uv` | Runs `uv sync` and activates the virtual environment |
| `/update-config` | `/update-config` | Configures Claude Code settings (hooks, permissions, env vars, automated behaviours) via `settings.json` |
| `/keybindings-help` | `/keybindings-help` | Customise keyboard shortcuts and rebind keys in `~/.claude/keybindings.json` |
| `/all` | `/all` | Shows how to relaunch Claude with `--dangerously-skip-permissions` to auto-approve all tool calls |

### Domain Knowledge

| Skill | Usage | What it does |
|-------|-------|--------------|
| `neuroblastoma-domain` | *activated automatically* | Provides neuroblastoma domain knowledge to inform analysis decisions |
| `clinical-data-quality` | *activated automatically* | Applies clinical data quality rules specific to neuroblastoma datasets |

### Development Utilities

| Skill | Usage | What it does |
|-------|-------|--------------|
| `/commit-message` | `/commit-message` | Analyses git diffs and creates a descriptive commit message |
| `/loop` | `/loop 5m /some-skill` | Runs a skill or command on a recurring interval (default: 10 min) |
| `/claude-api` | `/claude-api` | Builds apps using the Claude API / Anthropic SDK |
| `/frontend-design` | `/frontend-design` | Creates distinctive, production-grade frontend interfaces with high design quality |

---

## 🤖 Built-in AI Agents

### 🔬 Code Quality Reviewer

After `/execute` writes and runs your scripts, ask Claude to review the code — or it may offer proactively.

```
┌─────────────────────────────────────────────────────────────────┐
│  What it checks                                                 │
├─────────────────────────────────────────────────────────────────┤
│  ✅ Reproducibility   — random seeds, deterministic outputs     │
│  ✅ Data contracts    — column names, dirty.csv written          │
│  ✅ Clinical safety   — correct metrics, no data leakage        │
│  ✅ Code correctness  — pandas ops, train/test separation       │
│  ✅ Error handling    — clear failures, no silent drops         │
│  ✅ Output validation — all files written, plots saved to disk  │
└─────────────────────────────────────────────────────────────────┘
```

Issues are reported with **severity levels** (Critical / High / Medium / Low) and a suggested fix for each. The agent only reviews the diff — it won't speculate about code it hasn't seen.

**Trigger automatically** — runs after every `/execute` completion.
**Trigger manually** — just ask: *"review the code"* or *"does this look okay?"*

---

## 📁 Directory Layout

```
_ideas/      ← Start here: your research ideas
_plans/      ← Claude's research plans (output of /plan)
_specs/      ← Claude's technical specs (output of /spec)
src/         ← Python scripts (written by /execute)
data/        ← Your datasets (gitignored, never modified)
output/      ← All results, organised by run
  PROJECT_01/
  PROJECT_02/
  ...
.claude/
  commands/  ← Slash command definitions (/plan, /spec, /execute, ...)
  agents/    ← Specialist sub-agents (code-quality-reviewer, ...)
```

---

## 🛠️ Setup

**Prerequisites:** [Claude Code](https://claude.ai/code) + [uv](https://docs.astral.sh/uv/)

```bash
uv sync
```

Done. Claude installs any extra packages it needs automatically as it works.

---

## 📦 What You Get in `output/PROJECT_XX/`

Every run produces at minimum:

| File / Folder | Description |
|---------------|-------------|
| `dirty.csv` | Rows removed during cleaning, each with a `reason` column explaining why |
| `clean.csv` | Cleaned dataset ready for analysis |
| `plots/` | All visualisations as numbered PNG files (e.g. `01_age_distribution.png`) |
| `summary_stats.csv` | Per-variable summary statistics (mean, std, percentiles, etc.) |
| `report.html` | Self-contained HTML report with embedded plots, key findings, and an interview Q&A appendix |
| `model/` | *(when modelling phase is included)* classification reports, feature importance tables, ROC data |
| `tables/` | *(when statistical phase is included)* pivot tables, test results, segment breakdowns |

### Cleaning rules (always enforced)

- Dirty rows are **removed, never fixed**
- Every removed row is saved to `dirty.csv` with a `reason` column
- Output subfolders are named `PROJECT_01`, `PROJECT_02`, etc. — always the next available number

### Plot naming convention

Plots are zero-padded and numbered in phase order:

```
01_<description>.png   ← Phase 0/1 ETL & univariate
09_<description>.png   ← Phase 2 bivariate
19_<description>.png   ← Phase 3 multivariate / deep-dive
```

---

## 💡 Tips

- **Rough ideas are fine.** A few bullet points or sentences is all `/plan` needs to get started.
- **Review before you execute.** The spec phase is your chance to catch misunderstandings before any code is written.
- **Use screenshots.** Paste an image directly into Claude Code — it can read charts, error messages, and UI screenshots to diagnose issues.
- **Just ask.** Unsure what to do? Describe the situation in plain language and Claude will advise.
- **Launch a dashboard.** After `/execute` completes, run `/dashboard output/PROJECT_XX` to explore results interactively.
- **Commit cleanly.** Use `/commit-message` to get a well-structured commit message from the diff.
