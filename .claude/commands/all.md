---
description: "Show how to relaunch Claude with --dangerously-skip-permissions to auto-approve all tool calls"
---

Claude cannot change its own permission mode mid-session. To auto-approve all tool calls without prompts, relaunch from your terminal with:

```bash
claude --dangerously-skip-permissions
```

Or for a one-off command:

```bash
claude --dangerously-skip-permissions -p "your prompt here"
```

**What it does:** bypasses all tool-use confirmation prompts — Bash, file writes, edits, etc. are executed immediately without asking.

**Warning:** only use this in trusted projects where you are confident in the actions Claude will take.
