"""
Movie Launcher — starts Scene 1 (HTML poster) and Scene 2 (Shiny app),
then opens the browser.

Usage:
    uv run python src/movie_launcher.py
"""
from __future__ import annotations

import http.server
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

SCENE1_PORT = 8001
SCENE2_PORT = 8000
CREDITS_PORT = 8002
SRC_DIR = Path(__file__).parent


# ---------------------------------------------------------------------------
# Static file server factory — one instance per HTML file
# ---------------------------------------------------------------------------

def _make_handler(html_file: Path):
    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                content = html_file.read_bytes()
            except FileNotFoundError:
                self.send_error(404, f"{html_file.name} not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, fmt, *args):
            pass

    return _Handler


def _run_static_server(port: int, html_file: Path) -> None:
    try:
        server = http.server.HTTPServer(("127.0.0.1", port), _make_handler(html_file))
        server.serve_forever()
    except Exception as exc:
        print(f"  Static server on port {port} error: {exc}")


# ---------------------------------------------------------------------------
# Scene 2 — launch lesson01_app.py via uvicorn (Shiny)
# ---------------------------------------------------------------------------

def _run_scene2_server() -> subprocess.Popen:
    script = Path(__file__).parent / "lesson01_app.py"
    # Use uv run so the subprocess gets the correct virtual environment
    return subprocess.Popen(
        ["uv", "run", "python", str(script)],
        cwd=Path(__file__).parent.parent,  # project root
    )


def _wait_for_scene2(timeout: float = 15.0) -> bool:
    """Poll until the Shiny app responds or timeout expires."""
    import urllib.request
    import urllib.error

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{SCENE2_PORT}/", timeout=1)
            return True
        except Exception:
            time.sleep(0.4)
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"  Starting Shiny app on port {SCENE2_PORT} ...")
    scene2_proc = _run_scene2_server()

    print(f"  Starting Scene 1 (poster) on port {SCENE1_PORT} ...")
    threading.Thread(
        target=_run_static_server,
        args=(SCENE1_PORT, SRC_DIR / "movie_scene1.html"),
        daemon=True,
    ).start()

    print(f"  Starting Credits on port {CREDITS_PORT} ...")
    threading.Thread(
        target=_run_static_server,
        args=(CREDITS_PORT, SRC_DIR / "movie_scene2.html"),
        daemon=True,
    ).start()

    print("  Waiting for Shiny to be ready ...")
    ready = _wait_for_scene2()
    if not ready:
        print("  WARNING: Shiny did not respond in time — opening anyway.")

    url = f"http://127.0.0.1:{SCENE1_PORT}/"
    print(f"\n  Opening browser -> {url}")
    print("  Press Ctrl-C to stop.\n")
    webbrowser.open(url)

    try:
        scene2_proc.wait()
    except KeyboardInterrupt:
        print("\n  Shutting down...")
        scene2_proc.terminate()


if __name__ == "__main__":
    main()
