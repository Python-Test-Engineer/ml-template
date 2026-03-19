# CLAUDE.md

## Output Style: Markdown Focused

Structure all responses using comprehensive markdown for optimal readability:

- Use **headers** (`##`, `###`, `####`) to create clear hierarchy; separate major sections with `---`
- `inline code` for commands, file names, function names, variables, and file paths
- **Bold** for important concepts, warnings, key points; *italics* for technical terms and emphasis
- > Blockquotes for important notes, tips, warnings, or key insights
- Tables for comparisons, options, configurations, or any tabular data
- Numbered lists for sequential steps; bulleted lists for related items
- Code blocks with language identifiers for all code and command sequences

Style file: `.claude/output-styles/markdown-focused.md`

---

## Rules

- All scripts go in `src/`; all generated files (plots, CSVs, reports) go in `output/PROJECT_XX/`.
- Always use `uv` and Python 3.12.
- Dirty rows must be **removed, never fixed**, and saved to `output/PROJECT_XX/dirty.csv` with a `reason` column.
- Output subfolders are named `PROJECT_01`, `PROJECT_02`, etc. — always use the next available number.

## Shell Commands

```bash
uv run python src/<script>.py   # run a script
uv add <package>                # add a dependency
uv sync                         # install from lockfile
```

## Project: Neuroblastoma Genomic Analysis

Multi-phase oncology data science project predicting neuroblastoma patient outcomes from gene expression and clinical data.

## Directory Layout

```
_ideas/      Researcher idea files (input to /plan)
_plans/      Research plans (output of /plan, input to /spec)
_specs/      Technical specs (output of /spec, input to /execute)
src/         Python scripts (written by /execute)
data/        Raw datasets (read-only)
output/      All generated outputs, one subfolder per project run
```

## Workflow

**Phase 1 — Plan**
```
/plan _ideas/<filename>
```
Reads the idea file, profiles the dataset, asks clarifying questions, and saves a structured research plan to `_plans/<filename>`.

**Phase 2 — Spec**
```
/spec _plans/<filename>
```
Translates the plan into a detailed Python technical spec (scripts, data contracts, output files) and saves it to `_specs/<filename>`.

**Phase 3 — Execute**
```
/execute _specs/<filename>
```
Implements every script in the spec, runs them in phase order, fixes errors, and validates all outputs in `output/PROJECT_XX/`.
