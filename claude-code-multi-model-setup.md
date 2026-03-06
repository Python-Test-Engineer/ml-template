# Using Claude Code with Multiple AI Models
#### A simple setup guide

---

## What this gives you

One command to start, then simple commands to chat with any AI model (ChatGPT, Gemini, Claude) directly in your terminal — all from your existing project.

---

## Before you start

Make sure you have:
- ✅ UV installed
- ✅ An existing UV project folder
- ✅ API keys for whichever providers you want (OpenAI, Google, Anthropic)

---

## One-time setup (do this once, ever)

### Step 1 — Add LiteLLM to your project
In your project folder, run:
```bash
uv add "litellm[proxy]"
```

---

### Step 2 — Add your API keys
Open (or create) the `.env` file in your project folder and paste in your keys:
```
ANTHROPIC_API_KEY="sk-ant-..."
OPENAI_API_KEY="sk-..."
GEMINI_API_KEY="AIza..."
```
> 💡 Only add the keys for services you actually have. The others can be deleted.

---

### Step 3 — Create the model config file
Create a file called `litellm-config.yaml` in your project folder with this content:
```yaml
model_list:
  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY

  - model_name: gemini-pro
    litellm_params:
      model: gemini/gemini-2.5-pro
      api_key: os.environ/GEMINI_API_KEY

litellm_settings:
  drop_params: true
```
> 💡 Remove any models you don't have API keys for.

---

### Step 4 — Add shortcuts to `pyproject.toml`
Open your `pyproject.toml` file and add this section at the bottom:
```toml
[tool.uv.scripts]
proxy = "litellm --config litellm-config.yaml --port 8082"
claude-gpt     = "bash -c 'ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_MODEL=gpt-4o claude'"
claude-gemini  = "bash -c 'ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_MODEL=gemini-pro claude'"
claude-sonnet  = "bash -c 'ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_MODEL=claude-sonnet claude'"
```

---

## Every day usage

### Terminal 1 — Start the proxy (do this first, every time)
```bash
uv run proxy
```
> Leave this terminal running in the background.

### Terminal 2 — Chat with your chosen model
```bash
uv run claude-gpt       # use ChatGPT (GPT-4o)
uv run claude-gemini    # use Google Gemini
uv run claude-sonnet    # use Anthropic Claude
```

---

## Adding a new model later

1. Add 4 lines to `litellm-config.yaml` (copy an existing block, change the names)
2. Add 1 line to `pyproject.toml` (copy an existing shortcut, change the model name)
3. Restart the proxy (`uv run proxy`)

---

## Using models in Python / Jupyter notebooks

```python
from litellm import completion

def ask(prompt, model="claude-sonnet"):
    """Options: claude-sonnet, gpt-4o, gemini-pro"""
    response = completion(
        model=model,
        api_base="http://localhost:8082",
        api_key="anything",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Example usage
print(ask("Summarise this dataframe", model="gpt-4o"))
print(ask("Write a data cleaning script", model="gemini-pro"))
print(ask("Explain this chart", model="claude-sonnet"))
```
> 💡 The proxy must be running (`uv run proxy`) for this to work.

---

## Quick reference

| What you want to do | Command |
|---|---|
| Start the proxy | `uv run proxy` |
| Chat with GPT-4o | `uv run claude-gpt` |
| Chat with Gemini | `uv run claude-gemini` |
| Chat with Claude | `uv run claude-sonnet` |
| See available models | Open `http://localhost:8082/models` in browser |
| Proxy dashboard | Open `http://localhost:8082/ui` in browser |
