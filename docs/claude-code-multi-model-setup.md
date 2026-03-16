# Using Claude Code with OpenRouter

OpenRouter gives you 300+ models (Claude, GPT-4o, Gemini, Llama, and more) through a single API key. Claude Code can be pointed directly at OpenRouter — no extra tools needed.

---

## Before you start

- Claude Code installed
- An [OpenRouter](https://openrouter.ai) API key

---

## Setup

Add your key to the `.env` file in your project folder:

```env
OPENROUTER_API_KEY="sk-or-..."
```

---

## Usage

Set two environment variables when launching Claude Code:

```bash
ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1 \
ANTHROPIC_API_KEY=$OPENROUTER_API_KEY \
ANTHROPIC_MODEL=anthropic/claude-sonnet-4-5 \
claude
```

To make this easier, add shortcuts to `pyproject.toml`:

```toml
[tool.uv.scripts]
claude-sonnet = "bash -c 'ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1 ANTHROPIC_API_KEY=$OPENROUTER_API_KEY ANTHROPIC_MODEL=anthropic/claude-sonnet-4-5 claude'"
claude-gpt    = "bash -c 'ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1 ANTHROPIC_API_KEY=$OPENROUTER_API_KEY ANTHROPIC_MODEL=openai/gpt-4o claude'"
claude-gemini = "bash -c 'ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1 ANTHROPIC_API_KEY=$OPENROUTER_API_KEY ANTHROPIC_MODEL=google/gemini-2.5-pro claude'"
```

Then run:

```bash
uv run claude-sonnet
uv run claude-gpt
uv run claude-gemini
```

---

## Adding a new model

Find the model ID at `openrouter.ai/models`, then add one line to `pyproject.toml`:

```toml
claude-llama = "bash -c 'ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1 ANTHROPIC_API_KEY=$OPENROUTER_API_KEY ANTHROPIC_MODEL=meta-llama/llama-3.3-70b-instruct claude'"
```

---

## Quick reference

| Task | Command |
|---|---|
| Chat with Claude Sonnet | `uv run claude-sonnet` |
| Chat with GPT-4o | `uv run claude-gpt` |
| Chat with Gemini | `uv run claude-gemini` |
| Browse available models | `openrouter.ai/models` |
