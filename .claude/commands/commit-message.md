---
description: Create a commit message by analyzing git diffs
allowed-tools: Bash(git status), Bash(git status --short), Bash(git diff --staged), Bash(git add *), Bash(git commit:*)
---

## Context:

- Current git status: !`git status --short`
- Current git diff (staged): !`git diff --staged`

## Step 1 — Check for unstaged changes

Look at the git status output above. If there are any unstaged or untracked files (lines starting with ` M`, `??`, `M ` with no staged counterpart, etc.), list them clearly and ask the user:

> "The following files have unstaged changes: [list]. Would you like me to stage them before committing?"

If the user says yes, run `git add <file>` for each file they want staged, then re-read the diff.
If the user says no, proceed with only what is already staged.
If nothing is staged and nothing is selected, stop and inform the user there is nothing to commit.

## Step 2 — Analyze and propose commit message

Analyze the staged git changes and create a commit message. Use present tense and explain "why" something has changed, not just "what" has changed.

## Commit types with emojis:
Only use the following emojis: 

- ✨ `feat:` - New feature
- 🐛 `fix:` - Bug fix
- 🔨 `refactor:` - Refactoring code
- 📝 `docs:` - Documentation
- 🎨 `style:` - Styling/formatting
- ✅ `test:` - Tests
- ⚡ `perf:` - Performance

## Format:
Use the following format for making the commit message:

```
<emoji> <type>: <concise_description>
<optional_body_explaining_why>
```

## Output:

1. Show summary of changes currently staged
2. Propose commit message with appropriate emoji
3. Ask for confirmation before committing

DO NOT auto-commit - wait for user approval, and only commit if the user says so.