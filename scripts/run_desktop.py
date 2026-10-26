#!/usr/bin/env python3
"""Hoopreel desktop window: bundled game, no external browser or console."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(ROOT))

from nba_roulette.desktop import DesktopStore, app_directory


def show_error(message: str) -> None:
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, message, "Hoopreel could not start", 0x10)
    elif sys.platform == "darwin":
        import subprocess
        subprocess.run(["osascript", "-e", 'on run argv\ndisplay alert "Hoopreel could not start" message (item 1 of argv)\nend run', message], check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", type=Path, help="Run packaged native-window QA and write a JSON report")
    args = parser.parse_args()
    temporary = tempfile.TemporaryDirectory(prefix="hoopreel-smoke-") if args.smoke_test else None
    directory = Path(temporary.name) if temporary else app_directory()
    directory.mkdir(parents=True, exist_ok=True)
    # Windowed Windows executables have no stdout/stderr. Keep diagnostics in-app.
    log = (directory / "desktop.log").open("a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stderr = log
    server = None
    thread = None
    result = {"success": False}
    try:
        import webview
        from scripts import run_web
        from http.server import ThreadingHTTPServer
        from urllib.parse import urlparse

        store = DesktopStore(directory)
        if args.smoke_test:
            run_web.PLAYTEST_LOGGER = None
            store.save("hoopreel.instantSpins.v1", "true")
            store.save("hoopreel.scores.v1", json.dumps({"recent": [], "best": 321}))

        class DesktopHandler(run_web.Handler):
            def do_GET(self):
                if urlparse(self.path).path == "/api/desktop-storage":
                    try:
                        self._json(store.read())
                    except (OSError, ValueError) as error:
                        self._json({"error": str(error)}, status=500)
                    return
                super().do_GET()

            def do_POST(self):
                if urlparse(self.path).path == "/api/desktop-storage":
                    # Restrict desktop writes to the locally loaded game origin.
                    if self.headers.get("Origin") != self.server.desktop_origin:
                        self._json({"error": "Invalid desktop origin"}, status=403)
                        return
                    try:
                        payload = self._body()
                        store.save(payload.get("key"), payload.get("value"))
                        self._json({"saved": True})
                    except (OSError, ValueError, TypeError) as error:
                        self._json({"error": str(error)}, status=400)
                    return
                super().do_POST()

        server = ThreadingHTTPServer(("127.0.0.1", 0), DesktopHandler)
        server.daemon_threads = True
        origin = f"http://127.0.0.1:{server.server_address[1]}"
        server.desktop_origin = origin
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        window = webview.create_window("Hoopreel", origin + "/?desktop=1", width=1280, height=900,
                                       min_size=(900, 650), background_color="#07111f", text_select=True)
        loaded = threading.Event()
        window.events.loaded += loaded.set

        def flush_on_close():
            try:
                window.evaluate_js("desktopPending.then(() => true)")
            except Exception:
                pass
        window.events.closing += flush_on_close

        def smoke():
            try:
                if not loaded.wait(40):
                    raise RuntimeError("Native window did not load")
                deadline = time.monotonic() + 40
                while not window.evaluate_js("Boolean(state.game)"):
                    if time.monotonic() > deadline:
                        raise RuntimeError("Game did not initialize in native window")
                    time.sleep(0.1)
                window.evaluate_js("""window.__desktopQA = null; (async () => {
                  if (!instantSpins || scores.best !== 321) throw Error('Native save not loaded');
                  const pool = state.game.normal_pool;
                  if (pool.seasons !== 53 || pool.records !== 13442) throw Error('Incomplete pool');
                  for (const id of ['skip-animation','instant-spins','clear-keeps','bonus-remaining','restart-confirm'])
                    if (!document.getElementById(id)) throw Error('Missing control: '+id);
                  await spin();
                  if (!state.game.player || state.game.spins_used !== 1) throw Error('Spin failed');
                  state.keeps.add('season'); render(state.game); clearKeeps();
                  if (state.keeps.size) throw Error('Keeps did not clear');
                  requestNewGame();
                  if (!document.getElementById('restart-confirm').open) throw Error('Restart warning missing');
                  document.getElementById('restart-confirm').close();
                  const category = state.game.categories.find(c => !c.used && c.preview !== null);
                  await score(category.id);
                  setInstantSpins(false); await desktopPending;
                  return {seasons:pool.seasons, records:pool.records, spin:true, scoring:true, controls:true, native_storage:true};
                })().then(result => {window.__desktopQA = result;})
                  .catch(error => {window.__desktopQA = {error:String(error)};});""")
                report = None
                deadline = time.monotonic() + 40
                while report is None:
                    report = window.evaluate_js("window.__desktopQA")
                    if time.monotonic() > deadline:
                        raise RuntimeError("Native gameplay check timed out")
                    time.sleep(0.1)
                assert report and report["records"] == 13442, report
                assert DesktopStore(directory).read()["hoopreel.instantSpins.v1"] == "false"
                result.update(report, success=True)
            except Exception:
                result["error"] = traceback.format_exc()
            finally:
                window.destroy()

        webview.start(smoke if args.smoke_test else None,
                      gui="edgechromium" if sys.platform == "win32" else "cocoa" if sys.platform == "darwin" else None,
                      private_mode=False, storage_path=str(directory / "webview"), debug=False)
        return 0 if not args.smoke_test or result["success"] else 1
    except Exception:
        details = traceback.format_exc()
        (directory / "launcher_error.txt").write_text(details, encoding="utf-8")
        result["error"] = details
        if not args.smoke_test:
            show_error(f"Please check {directory / 'launcher_error.txt'}.\nOn Windows, Microsoft Edge WebView2 Runtime is required.")
        return 1
    finally:
        if server:
            server.shutdown()
            server.server_close()
        if thread:
            thread.join(timeout=5)
        if args.smoke_test:
            result["server_stopped"] = thread is None or not thread.is_alive()
            args.smoke_test.resolve().write_text(json.dumps(result, indent=2), encoding="utf-8")
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        log.close()
        if temporary:
            temporary.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
