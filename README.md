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

You'll get plots, CSVs, and a plain-text report — ready to review.

---

## 🤖 Built-in AI Agents

Alongside the three slash commands, the project ships a specialist sub-agent that Claude activates automatically when needed.

### 🔬 Code Quality Reviewer

```
"Can you review the code before I commit?"
```

After `/execute` writes and runs your scripts, ask Claude to review the code — or it may offer proactively. The **code-quality-reviewer** agent inspects only what changed and checks for issues that genuinely matter in clinical data science:

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

**Trigger it automatically** — it runs after every `/execute` completion.
**Trigger it manually** — just ask: *"review the code"* or *"does this look okay?"*

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
  commands/  ← Slash command definitions (/plan, /spec, /execute)
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

| File | Description |
|------|-------------|
| `dirty.csv` | Rows removed during cleaning, with a `reason` column |
| `*.png` | Plots and visualisations |
| `report.txt` | Plain-English summary of results |

---

## 💡 Tips

- **Rough ideas are fine.** A few bullet points or sentences is all `/plan` needs to get started.
- **Review before you execute.** The spec phase is your chance to catch misunderstandings before any code is written.
- **Use screenshots.** Paste an image directly into Claude Code — it can read charts, error messages, and UI screenshots to diagnose issues.
- **Just ask.** Unsure what to do? Describe the situation in plain language and Claude will advise.
