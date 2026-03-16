# The Movie — Implementation Plan

## Goal

A single-page web app that plays like a movie: an animated title card (Scene 1) automatically transitions into the existing Shiny investigation dashboard (Scene 2), which auto-starts with a 2-second message delay.

---

## Architecture

Two processes, one browser tab:

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Scene 1 host | Plain HTML + CSS + JS (served by a minimal Python HTTP server) | Animated poster, fade-out, redirect |
| Scene 2 | `src/lesson01_app.py` (Shiny on port 8000) | The investigation dashboard |
| Launcher | `src/movie_launcher.py` | Starts both servers, opens the browser |

**Flow:**

```
Browser opens port 8001 (Scene 1)
  -> CSS animation plays (~4 s)
  -> JS redirects to port 8000 (Scene 2)
  -> Shiny app loads and auto-clicks Start with interval=2
```

---

## Scene 1 — Poster Animation

**File:** `src/movie_scene1.html` (served by the launcher)

### Visual design

```
[blank page, black background]
       |
       | 0.5 s — small card fades in at center (~200x300 px)
       |
       | 1.5 s — card expands to fill viewport (CSS scale + border-radius -> 0)
       |
       | 3.0 s — full-page poster holds for 0.8 s
       |
       | 3.8 s — entire page fades to black
       |
       | 4.2 s — JS: window.location = "http://127.0.0.1:8000"
```

### Poster content (rendered in CSS/HTML, no image file required)

```
+----------------------------------+
|                                  |
|    [magnifying glass SVG icon]   |
|                                  |
|  THE DATA SCIENCE                |
|  DETECTIVE AGENCY                |
|                                  |
|  "Every dataset hides a secret"  |
|                                  |
|  LESSON 01                       |
|  Multi-Agent Collaboration       |
|                                  |
|  [gradient bar: blue -> purple]  |
+----------------------------------+
```

Fonts: system monospace stack. Colors: dark navy background (`#1A1A2E`), gold title (`#F0C040`), white subtitle.

### CSS keyframes (summary)

```css
@keyframes card-expand {
  0%   { transform: scale(0.15); border-radius: 20px; opacity: 0; }
  15%  { opacity: 1; }
  60%  { transform: scale(0.15); border-radius: 20px; }
  100% { transform: scale(1);    border-radius: 0;    }
}

@keyframes page-fade-out {
  from { opacity: 1; }
  to   { opacity: 0; }
}
```

Animation 1 runs 0 -> 3.5 s (`card-expand`, ease-in-out).
Animation 2 runs 3.5 -> 4.2 s (`page-fade-out`, ease-in, `forwards` fill).

---

## Scene 2 — Shiny App Changes

**File:** `src/lesson01_app.py` — two small additions only.

### 2a. Accept `?autostart=1` query parameter

On page load, if `autostart=1` is present in the URL, trigger the Start button automatically and use `interval=2` as the message delay.

Implementation inside `app_server`:

```python
@reactive.effect
def _autostart():
    # Runs once on session init; reads the URL search string via a JS message
    session.send_custom_message("check_autostart", {})
```

Simpler alternative — a dedicated autostart route: the launcher passes `?autostart=1` in the redirect URL and a small `<script>` block already present in `app_ui` reads `URLSearchParams` and clicks the button after a 300 ms delay.

### 2b. Default interval set to 2 when autostart is active

The `input_select` for interval keeps `selected="2"` when `?autostart=1` is present. This is handled by the same JS snippet that auto-clicks the button.

### JS snippet added to `app_ui`

```javascript
(function() {
  var p = new URLSearchParams(window.location.search);
  if (p.get('autostart') === '1') {
    // Wait for Shiny to bind, then click Start
    var iv = setInterval(function() {
      var btn = document.getElementById('start_btn');
      if (btn) { btn.click(); clearInterval(iv); }
    }, 300);
  }
})();
```

No other changes to `lesson01_app.py`.

---

## Launcher

**File:** `src/movie_launcher.py`

Responsibilities:

1. Start `lesson01_app.py` (Shiny) on port 8000 as a subprocess.
2. Serve `movie_scene1.html` on port 8001 using `http.server.HTTPServer` in a thread.
3. Wait ~1 s for Shiny to be ready (poll `GET /` with retry).
4. Open `http://127.0.0.1:8001` in the default browser.
5. Block until the user hits Ctrl-C, then terminate both servers.

```
uv run python src/movie_launcher.py
```

---

## File Summary

| File | Action | Notes |
|------|--------|-------|
| `src/movie_launcher.py` | Create | Orchestrates both servers + opens browser |
| `src/movie_scene1.html` | Create | Poster animation + redirect JS |
| `src/lesson01_app.py` | Edit (minor) | Add autostart JS snippet to `app_ui` |

---

## Scene 1 Timing Table

| Time (s) | Event |
|----------|-------|
| 0.0 | Page loads — black screen |
| 0.3 | Tiny card appears (fade-in opacity 0->1) |
| 0.5 | Card begins expanding |
| 3.0 | Card fills viewport — poster fully visible |
| 3.5 | Page begins fade to black |
| 4.2 | JS redirects to `http://127.0.0.1:8000?autostart=1` |

---

## Dependencies

No new packages required. All are already available:

- `shiny` — Scene 2
- `uvicorn` — Scene 2 server
- `http.server` (stdlib) — Scene 1 server
- `subprocess`, `threading`, `webbrowser` (stdlib) — Launcher

---

## How to Run (final)

```bash
uv run python src/movie_launcher.py
```

The browser opens automatically. Scene 1 plays, transitions to Scene 2, investigation starts at 2 s/message.
