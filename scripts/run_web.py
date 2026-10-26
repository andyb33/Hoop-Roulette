#!/usr/bin/env python3
"""Run the local Hoopreel browser prototype without external packages."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import threading
import traceback
import webbrowser
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

FROZEN = bool(getattr(sys, "frozen", False))
ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(ROOT))

for stream_name in ("stdout", "stderr"):
    stream = getattr(sys, stream_name, None)
    if stream and hasattr(stream, "reconfigure"):
        stream.reconfigure(errors="replace")

from nba_roulette.data import load_records, load_goat_pools
from nba_roulette.playtest import PlaytestBatchLogger
from nba_roulette.web import BrowserGame


STATIC = ROOT / "web" / "static"
RECORDS = load_records(data_dir=ROOT / "data" / "game")
GOAT_POOLS = load_goat_pools(data_dir=ROOT / "data" / "goat")
DEV_JACKPOTS = False


def default_log_directory() -> Path:
    """Keep packaged playtest evidence outside PyInstaller's temporary folder."""
    override = os.environ.get("HOOPREEL_LOG_DIR") or os.environ.get("NBA_ROULETTE_LOG_DIR")
    if override:
        return Path(override).expanduser()
    if FROZEN:
        documents = Path.home() / "Documents"
        legacy = documents / "NBA Roulette" / "playtest_logs"
        current = documents / "Hoopreel" / "playtest_logs"
        # Keep an existing batch in one location without moving anyone's files.
        return legacy if legacy.exists() and not current.exists() else current
    return ROOT / "playtest_logs"


PLAYTEST_LOGGER = PlaytestBatchLogger(
    default_log_directory(),
    "playtest_batch_28_v0_13_0_desktop",
    "Playtest Batch 28 - v0.13.0 Standalone Desktop",
    target=100,
)
SESSIONS: dict[str, BrowserGame] = {}
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/brand-mark.svg": ("brand-mark.svg", "image/svg+xml"),
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/state":
            game, cookie = self._session()
            self._json(game.state(), cookie=cookie)
            return
        if path in ASSETS:
            filename, content_type = ASSETS[path]
            body = (STATIC / filename).read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        game, cookie = self._session(new=path == "/api/new")
        try:
            payload = self._body()
            if path == "/api/new":
                result = game.state()
            elif path == "/api/spin":
                result = game.spin(payload.get("keeps", []), payload.get("force_pool"))
            elif path == "/api/score":
                result = game.score(str(payload.get("category", "")))
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self._json(result, cookie=cookie)
        except (ValueError, RuntimeError) as error:
            self._json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST, cookie=cookie)

    def _session(self, new: bool = False) -> tuple[BrowserGame, str | None]:
        cookie = SimpleCookie(self.headers.get("Cookie"))
        session_id = cookie.get("nba_session")
        key = session_id.value if session_id else ""
        created = new or key not in SESSIONS
        if created:
            key = secrets.token_urlsafe(18)
            SESSIONS[key] = BrowserGame(RECORDS, logger=None if DEV_JACKPOTS else PLAYTEST_LOGGER,
                                       goat_pools=GOAT_POOLS, dev_jackpots=DEV_JACKPOTS)
        return SESSIONS[key], f"nba_session={key}; Path=/; SameSite=Lax" if created else None

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _json(
        self,
        payload: dict,
        status: HTTPStatus = HTTPStatus.OK,
        cookie: str | None = None,
    ) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[web] {self.address_string()} - {format % args}")


def main() -> None:
    global DEV_JACKPOTS
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0 if FROZEN else 8000)
    parser.add_argument("--dev-jackpots", action="store_true", help="Local-only jackpot previews; disables playtest logging")
    parser.add_argument(
        "--open-browser",
        action=argparse.BooleanOptionalAction,
        default=FROZEN,
        help="Open Hoopreel in the default browser after startup",
    )
    args = parser.parse_args()
    if args.dev_jackpots and (FROZEN or args.host not in ("127.0.0.1", "localhost", "::1")):
        parser.error("Jackpot previews require an unfrozen local loopback server")
    DEV_JACKPOTS = args.dev_jackpots
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    port = server.server_address[1]
    url = f"http://{args.host}:{port}"
    print(f"Hoopreel running at {url}")
    print(
        f"Playtest batch: {PLAYTEST_LOGGER.batch_name} "
        f"({PLAYTEST_LOGGER.completed_count()}/{PLAYTEST_LOGGER.target})"
    )
    print(f"Logs: {PLAYTEST_LOGGER.directory}")
    print("Keep this window open while playing. Close it to stop Hoopreel.")
    if args.open_browser:
        threading.Timer(0.6, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    try:
        main()
    except Exception:  # pragma: no cover - last-resort packaged-app diagnostics
        details = traceback.format_exc()
        error_directory = default_log_directory().parent
        error_directory.mkdir(parents=True, exist_ok=True)
        error_path = error_directory / "launcher_error.txt"
        error_path.write_text(details, encoding="utf-8")
        print("Hoopreel could not start.", file=sys.stderr)
        print(f"Error details were saved to: {error_path}", file=sys.stderr)
        print(details, file=sys.stderr)
        if FROZEN and sys.stdin and sys.stdin.isatty():
            input("Press Enter to close...")
        raise
