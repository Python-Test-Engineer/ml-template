# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Rules

- Use `src/` for all scripts created; use `output/` for all generated files (plots, CSVs, text reports).
- Always use `uv` and Python 3.12.
- If any data row is not cleanable, DO NOT fix it — remove the row and save it to `output/dirty.csv`.
- Always ask questions to ensure full understanding before implementing.
- results from running code are stored in `outputs` with a subfolder `PROJECT_0X` where the X is the next number e.g. `PROJECT_03`, `PROJECT_04` etc

## Commands

```bash
# Run a script
uv run python src/phase1_eda.py

# Add a dependency
uv add <package>

# Install all dependencies from lockfile
uv sync
```

## Project: Neuroblastoma Genomic Analysis

This is a multi-phase oncology data science project predicting neuroblastoma patient outcomes from gene expression and clinical data.

### Datasets (`data/`)


Data sets are stored here.


### Process

Researchers store their `ideas` of what they want in `_ideas`.

Phase 1: 

`/plan [_ideas/<filename>]`

Create a detailed plan based on the chosen idea and ensure you ask questions so that you fully understand what is required.

Phase 2: 

`/spec [_plan<filename>]`

You create a technical spec of code that will be written This follows best practices for Python.

This is stored in `_specs/<filename>`

Phase 3: You execute the code produced by implementing the spec.

`/execute-spec [_spec/<filename>]`