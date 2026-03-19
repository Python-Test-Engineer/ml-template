---
description: "Select and apply an output style for this conversation. Usage: /style"
allowed-tools: AskUserQuestion
---

Use `AskUserQuestion` to present the available output styles and let the user pick one.

Ask this single question:

- question: "Which output style would you like to apply for this conversation?"
- header: "Output style"
- multiSelect: false
- options (exactly these 8, in this order):

  1. label: "Ultra Concise"
     description: "Minimum words, direct actions only, no filler — best for focused building sessions"

  2. label: "Bullet Points"
     description: "Hierarchical bullet points for quick scanning — great for lists and step-by-step work"

  3. label: "Markdown Focused"
     description: "Full markdown features — headers, tables, bold, blockquotes — maximum readability"

  4. label: "Table Based"
     description: "Markdown tables wherever possible — ideal for comparisons and structured data"

  5. label: "YAML Structured"
     description: "Responses as valid YAML — task, details, files, commands, status, next_steps"

  6. label: "HTML Structured"
     description: "Semantic HTML5 output — useful when responses will be rendered in a browser"

  7. label: "GenUI"
     description: "Generates a complete styled HTML file and opens it in the browser after every response"

  8. label: "TTS Summary"
     description: "Normal response + audio announcement via ElevenLabs TTS at the end of every reply"

---

After the user selects a style, confirm it with one short line, then apply the full style rules below for **all subsequent responses in this conversation**.

Amend CLAUDE.md and settings.json to reflect this change in output style.

---

## Style Rules

### Ultra Concise
Use absolute minimum words. No explanations unless critical. Direct actions only.
- No greetings, pleasantries, or filler
- Code/commands first, brief status after
- Skip obvious steps
- Use fragments over sentences
- Single-line summaries only
- Assume high technical expertise
- Only explain if prevents errors
- Tool outputs without commentary
- Immediate next action if relevant
- We are not in a conversation
- We DO NOT like WASTING TIME
- IMPORTANT: We're here to FOCUS, BUILD, and SHIP

---

### Bullet Points
Structure all responses using bullet points with clear hierarchy:
- Use dashes (-) for unordered information at all nesting levels
- Use numbers (1., 2., 3.) for ordered sequences or steps
- Never mix ordered and unordered markers at the same level
- Each bullet point concise (1-2 lines max)
- Mark action items with "ACTION:" or "TODO:" prefixes
- Group related information under logical main bullets
- Parent bullet = broader concept; child bullets = specific aspects or examples

---

### Markdown Focused
Structure responses using comprehensive markdown for optimal readability:
- Use **headers** (##, ###, ####) to create clear hierarchy
- `inline code` for commands, file names, function names, variables
- **Bold** for important concepts, warnings, key points
- *Italics* for technical terms, names, emphasis
- > Blockquotes for important notes, tips, warnings
- Tables for comparisons, options, configurations
- Numbered lists for sequential steps; bulleted lists for related items
- Horizontal rules `---` for major topic transitions

---

### Table Based
Structure responses using markdown tables wherever appropriate:
- Use tables for: comparisons, step-by-step processes, configuration options, analysis results
- Clear descriptive headers; keep cell content concise
- Use formatting within cells (bold, inline code) when helpful
- Lead with a brief summary paragraph, then structured tables
- Actions section: step table with priorities and context

---

### YAML Structured
Structure all responses in valid YAML format:
- 2-space indentation throughout
- Standard sections: `task`, `status`, `details`, `files`, `commands`, `notes`, `next_steps`
- Use `#` comments for context and explanations
- Absolute file paths; appropriate YAML data types
- Maintain parseable syntax at all times

---

### HTML Structured
Format all responses as clean semantic HTML5:
- Wrap response in `<article>` tags; use `<header>`, `<main>`, `<section>`, `<aside>`
- `<h2>` for main sections, `<h3>` for subsections
- Code blocks: `<pre><code class="language-{lang}">` with `data-file` and `data-line` attributes
- Tables with `<thead>`, `<tbody>`, `scope` attributes on headers
- Add `data-type="info|warning|error|success"` for status sections
- Minimal inline styles for readability

---

### GenUI
After every request generate a complete self-contained HTML document and open it in the browser:
1. Complete the user's request normally
2. Generate a full HTML5 document with embedded CSS (no external dependencies)
3. Save to `/tmp/cc_genui_<concise_description>_YYYYMMDD_HHMMSS.html`
4. Open with the `open` command
5. Confirm with the file path

Visual theme: primary blue #3498db, dark blue #2c3e50, max-width 900px, white card with shadow, 8px border-radius. Include info/success/warning/error section styles with coloured left borders.

---

### TTS Summary
Respond normally to all requests. At the very END of EVERY response:
1. Write separator `---`
2. Add heading `## Audio Summary for Dan`
3. Write one conversational sentence (under 20 words) addressed directly to Dan about what was accomplished
4. Execute: `uv run .claude/hooks/utils/tts/elevenlabs_tts.py "YOUR_MESSAGE"`

Focus on outcomes and user benefit. Always execute the command — don't just show it.
