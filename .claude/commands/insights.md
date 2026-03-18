---
description: "Analyse images and Python scripts to generate deep business & data insights report. Usage: /insights <image_folder> <python_folder>"
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(uv run python *), AskUserQuestion
hint: "Provide two paths: the image folder and the Python scripts folder, e.g. /insights output/PROJECT_01/plots src"
argument: "Two space-separated paths — image_folder python_folder — REQUIRED"
model: claude-opus-4-6
---

> **Model:** This command requires **claude-opus-4-6** (Claude Opus 4.6). If you are not already running that model, switch with `/model claude-opus-4-6` before invoking.
> **Thinking:** This command uses **ultrathink** — extended thinking with maximum token budget — for each insight synthesis step. Do not skip or abbreviate the thinking phase.

**Arguments required:** `<image_folder> <python_folder>`
Example: `/insights output/PROJECT_01/plots src`

Parse `$ARGUMENTS` as two whitespace-separated tokens:
- `IMAGE_FOLDER` — first token
- `PYTHON_FOLDER` — second token

If either is missing, list available folders under `output/` and `src/` then ask the user to re-run with both paths.

---

## Your role

You are a senior data scientist and business intelligence consultant with expertise in translating analytical visuals into actionable strategy. Your job is to:

1. Read every Python script in `PYTHON_FOLDER` once for context
2. Loop through each image in `IMAGE_FOLDER` **one at a time**, producing an individual insight report per image
3. After all individual reports are written, merge them into a final `insights.md` and `insights.html`

---

## Step 1 — Locate the output folder and create insights subfolder

Find the highest-numbered output folder:

```
Glob: output/PROJECT_*
```

Select the folder with the highest `_XX` suffix. Set `PROJECT_FOLDER` to that path.

Create the insights subfolder:
```
mkdir -p output/PROJECT_XX/insights
```

Set `INSIGHTS_FOLDER` = `output/PROJECT_XX/insights`

---

## Step 2 — Inventory the inputs

**Images** — glob `IMAGE_FOLDER` for:
```
**/*.png  **/*.jpg  **/*.jpeg  **/*.svg  **/*.gif
```

Build a sorted list of all image files: `[filename, file_path]`.

**Python scripts** — glob `PYTHON_FOLDER` for:
```
**/*.py
```

Read every `.py` file in full. Extract and mentally note:
- What data is loaded and from where
- What transformations, feature engineering, or modelling steps are performed
- What metrics, statistics, or model outputs are computed
- What plots are generated and what they are intended to show
- Any domain-specific logic (clinical thresholds, business rules, etc.)

---

## Step 3 — Check for previously completed insights (resume support)

Before starting the loop, glob `INSIGHTS_FOLDER` for existing `insights_*.md` files.

Build a set of already-completed image names. **Skip any image that already has a corresponding insight file.** This allows the command to resume after a context clear without redoing work.

Tell the user:
- Total images found
- How many already have insight files (if any)
- How many remain to process

---

## Step 4 — Per-image insight loop

For **each image** that does not yet have an insight file, in sorted filename order:

### 4a. Read the image

Use the Read tool to read the single image file. Examine it carefully.

### 4b. Deep insight synthesis for this image

ultrathink

**IMPORTANT: Use extended thinking for each image.** Consider:

**What the chart shows:**
- What type of visualisation is this (bar chart, heatmap, time series, etc.)?
- What variables are being displayed and how?
- What are the key data points, trends, or patterns visible?

**Business & strategic lens:**
- What story does this visual tell about the underlying domain?
- Where are the inflection points, anomalies, or asymmetries?
- What decisions could a stakeholder make differently based on this?
- What risks or opportunities are visible?

**Analytical depth lens:**
- Are there confounders, selection biases, or data artefacts?
- What hypotheses does this visual support or challenge?
- What signal is buried in the noise that a casual reader would miss?

**Forward-looking lens:**
- What additional analyses would increase confidence in what this chart shows?
- What unexplored dimensions could yield new findings?

### 4c. Write the individual insight file

Save to `INSIGHTS_FOLDER/insights_<image_name_without_extension>.md`.

**Image embed:** Each individual insight file MUST include the corresponding image as a Markdown image link. Compute the relative path from `INSIGHTS_FOLDER` to the image file. For example, if `INSIGHTS_FOLDER` is `output/PROJECT_01/insights` and the image is at `output/PROJECT_01/plots/01_age_distribution.jpg`, the relative path is `../plots/01_age_distribution.jpg`.

```markdown
# Insight Report: <image_filename>

![image](<relative_path_from_INSIGHTS_FOLDER_to_image_file>)

**Chart type:** [e.g., Bar chart, Heatmap, Time series, etc.]
**Variables displayed:** [What's on each axis / what's being measured]
**Generated:** YYYY-MM-DD

---

## Key Observation

[2-3 sentences: the single most important thing this chart reveals, grounded in specific visual evidence — cite actual values, proportions, or patterns visible in the chart]

## Business / Scientific Implication

[2-3 sentences: what this means for the business, research question, or decision at hand. Be concrete — name the stakeholder action or operational change this implies]

## Deeper Analysis

[3-5 sentences: analytical depth — patterns, anomalies, confounders, surprising findings, what a casual reader would miss. Reference specific data points or regions of the chart]

## Confidence Assessment

**Confidence:** High / Medium / Low
**Rationale:** [One-line justification for the confidence level]

## Suggested Next Steps

1. [Concrete follow-up analysis or action prompted by this chart]
2. [Optional second suggestion if warranted]
```

### 4d. Progress update

After writing each file, briefly tell the user:
```
✓ [N/total] insights_<name>.md — [one-line summary of the key finding]
```

Keep this update to a **single line**. Do not repeat the full insight content.

---

## Step 5 — Merge into `insights.md`

After ALL individual insight files are written, read every `insights_*.md` file from `INSIGHTS_FOLDER` in sorted order.

ultrathink

**IMPORTANT: Use the full extended thinking budget for this merge step.** Now you are synthesising across all charts. Consider:

- What story do these visuals **collectively** tell?
- What cross-cutting patterns emerge only when multiple charts are viewed together?
- What are the top 5+ most impactful insights across all charts?
- What risks and caveats span multiple analyses?
- What are the highest-priority next steps?

Write `INSIGHTS_FOLDER/insights.md` using this structure:

```markdown
# Data Intelligence Insights Report

**Project:** PROJECT_XX
**Images analysed:** N
**Scripts analysed:** N
**Generated:** YYYY-MM-DD

---

## Executive Summary

[3–5 sentence overview of the most important findings and their implications across ALL charts]

---

## Key Insights

### Insight 1 — [Compelling title]

**Source charts:** [List the specific chart filenames that support this insight]

**Observation:** [What the data/visuals show, with specific references to chart names or script outputs]

**Implication:** [What this means for the business, research question, or decision at hand]

**Confidence:** High / Medium / Low — [one-line rationale]

---

### Insight 2 — [Compelling title]
...

[Minimum 5 insights, drawn from and synthesising across the individual reports. These should be HIGHER-LEVEL than the per-chart insights — connect dots across multiple charts]

---

## Patterns Across Analyses

[Cross-cutting observations that emerge only when multiple charts/scripts are viewed together — things invisible in any single view]

---

## Risks & Caveats

| Risk | Affected Insights | Mitigation |
|------|-------------------|------------|
| ...  | ...               | ...        |

---

## Recommended Next Steps

### High Priority
1. **[Analysis name]** — [What to do, what question it answers, what data/tool is needed]
2. ...

### Medium Priority
1. ...

### Exploratory / Speculative
1. ...

---

## Appendix — Individual Chart Insights

[For each chart, include a condensed version: chart name, key observation (1-2 sentences), and confidence level. This serves as a quick-reference index.]

| # | Chart | Key Observation | Confidence |
|---|-------|-----------------|------------|
| 1 | ...   | ...             | ...        |

---

## Appendix — Input Inventory

### Images
| File | Description inferred from content |
|------|------------------------------------|
| ...  | ...                                |

### Python Scripts
| File | Purpose |
|------|---------|
| ...  | ...     |
```

---

## Step 6 — Write `insights.html`

Save to `INSIGHTS_FOLDER/insights.html`.

Produce a **clean, professional, self-contained HTML file** — no external dependencies except Google Fonts and a single inline `<style>` block.

### Design requirements

- **Font:** Inter (Google Fonts CDN) for body; monospace for code blocks
- **Color palette:**
  - Background: `#f8f9fa`
  - Card background: `#ffffff`
  - Primary accent: `#2563eb` (blue)
  - Success/positive: `#16a34a`
  - Warning: `#d97706`
  - Text: `#1e293b` primary, `#64748b` muted
  - Border: `#e2e8f0`
- **Layout:** max-width 900px, centred, generous whitespace
- **Header:** full-width banner with gradient (`#1e3a5f` → `#2563eb`), white title, subtitle line with date and counts
- **Insight cards:** white cards with subtle box-shadow, left border in accent colour, insight number as a large muted badge top-right
- **Confidence badges:** coloured inline badge (green = High, amber = Medium, red = Low)
- **Tables:** clean zebra-stripe, header in `#1e3a5f` with white text
- **Next steps section:** three columns (High / Medium / Exploratory), each with a coloured top border
- **Risks section:** table with colour-coded risk level column
- **Footer:** muted text, generated by Claude Code

### Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Insights Report — PROJECT_XX</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    /* all styles inline here */
  </style>
</head>
<body>
  <!-- hero header -->
  <!-- executive summary card -->
  <!-- insight cards (one per insight) -->
  <!-- patterns section -->
  <!-- risks table -->
  <!-- next steps 3-column grid -->
  <!-- appendix: individual chart insights table -->
  <!-- appendix: input inventory tables -->
  <!-- footer -->
</body>
</html>
```

Embed the full report content from `insights.md` translated into rich HTML — do **not** just reproduce raw markdown inside the HTML.

---

## Step 7 — Confirm and summarise

Tell the user:

- How many images and scripts were analysed
- How many individual insight files were generated
- How many synthesised insights in the final report
- The top 3 insight titles as a quick preview
- Paths to all output files:
  - `INSIGHTS_FOLDER/insights_<name>.md` (individual files)
  - `INSIGHTS_FOLDER/insights.md` (merged report)
  - `INSIGHTS_FOLDER/insights.html` (HTML report)
- The single highest-priority next step recommended

Do **not** repeat the full report in the terminal — the files contain the complete content.
