---
description: "Translate a research plan from _plans/kaggle_plan.md into a detailed Python technical spec. Usage: /spec _plans/<filename>"
argument-hint: "_plans/<filename>.md"
allowed-tools: Read, Glob, Write, Edit, AskUserQuestion
model: Sonnet
---

**Argument required:** The path to a plan file inside `_plans/`, e.g. ` _plans/kaggle_plan.md`

If no argument was provided, list available plan files and ask the user which to use:

```
Glob: _plans/**/*.md
```

Then stop and ask the user to re-run with the correct file.

Save output file to `_specs/kaggle_specs.md`

---

## Your role

You are an experienced data scientist and oncological researcher acting as a Python software architect. Your job is to translate the research plan into a precise, implementation-ready technical spec that a developer (or `/execute`) can follow without ambiguity.

Do **not** write actual code. Write intent, contracts, and structure.

---

## Step 1 — Read the plan file

Read `$ARGUMENTS` in full. Understand:
- The research question and success criteria
- The dataset(s) and their column contracts (names, types, semantics)
- The proposed phases (EDA, feature engineering, modelling, reporting)
- Any open questions or constraints noted in the plan

Also read `data/` to confirm dataset filenames if referenced.

---

## Step 2 — Determine the output directory

List existing `output/PROJECT_*` folders to find the next project number, e.g. if `PROJECT_01` and `PROJECT_02` exist, the new one is `PROJECT_03`.

Record this as `output_dir = output/PROJECT_XX`.

---

## Step 3 — Ask clarifying questions

Before writing the spec, use `AskUserQuestion` to resolve any remaining ambiguities not settled in the plan, for example:

- Which ML framework is preferred (scikit-learn, XGBoost, PyTorch, lifelines)?
- Should models be persisted to disk?
- Is reproducibility via a fixed random seed required?
- Should the spec cover a single monolithic script or multiple phase scripts?
- Are there runtime or memory constraints?

Only ask if genuinely unclear from the plan.

---

## Step 4 — Write the spec

Save the completed spec to `_specs/kaggle_specs.md` (same stem, `.md` extension).

Use this structure:

```markdown
# Technical Spec — <short title>

**Plan source:** _plans/<filename>
**Dataset(s):** data/<filename(s)>
**Output directory:** output/PROJECT_XX/
**Date:** <today>

## 1. Overview
One paragraph: what this code does and what it produces.

## 2. Environment
- Python 3.12 via `uv`
- Dependencies to add with `uv add`: <list packages>

## 3. Script Architecture
| Script | Location | Responsibility |
|--------|----------|----------------|
| phase1_eda.py | src/ | Load data, profile, produce EDA plots and dirty.csv |
| phase2_features.py | src/ | Feature engineering, produce cleaned dataset |
| phase3_model.py | src/ | Train, evaluate, and persist model |
| phase4_report.py | src/ | Aggregate results into a final report |

One script per phase unless the plan specifies otherwise.

## 4. Data Contract

### Input
| Column | Type | Description | Nullable |
|--------|------|-------------|----------|
| ...    | ...  | ...         | ...      |

### Dirty-row rules
Rows are removed (not fixed) and saved to `output/PROJECT_XX/dirty.csv` when:
- <list each rule>

### Output files
| File | Description |
|------|-------------|
| output/PROJECT_XX/dirty.csv | Removed rows with reason column |
| output/PROJECT_XX/eda_*.png | EDA plots |
| output/PROJECT_XX/model.pkl | Serialised model (if applicable) |
| output/PROJECT_XX/report.txt | Final summary report |

## 5. Phase Specs

### Phase 1 — EDA & Preprocessing (`src/phase1_eda.py`)
**Inputs:** `data/<filename>`
**Outputs:** `output/PROJECT_XX/dirty.csv`, `output/PROJECT_XX/eda_*.png`

Steps:
1. Load dataset; assert expected columns exist
2. Identify dirty rows per dirty-row rules; write to dirty.csv with a `reason` column
3. Drop dirty rows from working dataframe
4. Plot distributions for all numeric columns (histogram + KDE)
5. Plot class balance for target column
6. Plot correlation heatmap
7. Print a summary table (shape, missing %, dtype)

### Phase 2 — Feature Engineering (`src/phase2_features.py`)
**Inputs:** clean dataframe from Phase 1
**Outputs:** `output/PROJECT_XX/features.parquet`

Steps:
1. <specific transformations from the plan>
2. Encode categoricals: <strategy>
3. Scale numerics: <strategy>
4. Save engineered feature matrix

### Phase 3 — Modelling (`src/phase3_model.py`)
**Inputs:** `output/PROJECT_XX/features.parquet`
**Outputs:** `output/PROJECT_XX/model.pkl`, `output/PROJECT_XX/metrics.json`

Steps:
1. Split data: <strategy, e.g. 80/20 stratified, or cross-validation scheme>
2. Train: <algorithm(s), hyperparameter ranges>
3. Evaluate: <metrics — AUROC, C-index, etc.>
4. Persist model and metrics

### Phase 4 — Reporting (`src/phase4_report.py`)
**Inputs:** `output/PROJECT_XX/metrics.json`, plots
**Outputs:** `output/PROJECT_XX/report.txt`

Steps:
1. Load metrics
2. Render a plain-text summary report with all key results
3. Print report to stdout and save to file

## 6. Reproducibility
- Random seed: `RANDOM_SEED = 42` defined at top of each script
- All scripts must be runnable independently in phase order

## 7. Error Handling
- Raise a clear `ValueError` if a required input file is missing
- Log warnings (not errors) for unexpected but non-fatal column issues

## 8. Run Order
```bash
uv run python src/phase1_eda.py
uv run python src/phase2_features.py
uv run python src/phase3_model.py
uv run python src/phase4_report.py
```
```

---

## Step 5 — Confirm with the researcher

After saving the spec, present a short summary:
- Scripts to be written and their responsibilities
- Key design decisions made (algorithm choice, metric, split strategy)
- Output files that will be produced

Then ask: "Does this spec look correct, or would you like to adjust anything before moving to `/execute`?"
