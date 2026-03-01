---
description: Given a datset, it explores the dataset, creates a report and asks any necessary questions.
allowed-tools: Bash(git diff), Bash(git diff --staged)
---

Your job is to explore a dataset as an experienced data scientist and Oncological researcher.

Goal:
1. Analyse the dataset to gain a comprehensive understanding of what the data refers to.
2. Run both reviewer subagents in parallel on the same diff.
3. Combine their feedback into one unified report, de-duplicating overlap.
4. Produce a proposed edit plan (ordered checklist) to address the feedback.
5. Ask the user for explicit approval BEFORE making any code changes.

Process:
- First, collect the diff:
  - Use `git diff` for unstaged
  - Use `git diff --staged` for staged
  - If both are empty, say so and stop (DO NOT PROCEED).

- Then invoke both subagents in parallel.
  - Provide each agent:
    - the combined diff output
    - brief repo context if needed (tech stack, lint/test commands if available)
  - Tell them to be evidence-based: file paths, line/snippet references, no guessing.
  - Tell them NOT to review any code outside the diff.

- Merge results into:
  1. Summary (max 8 bullets total)
  2. Accessibility findings (Blocker/Major/Minor/Nit)
  3. Code quality findings (Blocker/Major/Minor/Nit)
  4. Combined action plan (ordered checklist)
  5. Questions/uncertainties (anything that needs human intent)

Rules:
- Do NOT edit any files yet.
- Do NOT run formatting-only changes unless they fix a cited issue.

Finish by asking:
"Do you want me to implement the action plan now?"

Wait for user confirmation before making any changes.