"""Local HTTP server for Slime Chronicles.

Run with ``python server.py`` and open http://127.0.0.1:8787.
Only the display layer uses JavaScript; every game rule and save mutation is
processed by the Python engine.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import secrets
import webbrowser
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from game import GameEngine, GameError
from game.storage import ChronicleStore


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
STORE = ChronicleStore(ROOT / "data" / "chronicles.db")
ENGINE = GameEngine()
SESSION_COOKIE = "chronicle_session"


class ChronicleHandler(BaseHTTPRequestHandler):
    server_version = "ChroniclePython/0.1"

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/state":
            session_id, is_new = self._session()
            state = STORE.load(session_id)
            if state:
                payload = ENGINE.refresh(state)
                STORE.save(session_id, state)
            else:
                payload = ENGINE.landing_state()
            self._json(payload, cookie=session_id if is_new else None)
            return
        self._static(path)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        session_id, is_new = self._session()
        try:
            body = self._read_json()
            state = STORE.load(session_id)
            if path == "/api/new-game":
                state = ENGINE.new_game("rimuru")
                result = ENGINE.public_state(state)
            elif path == "/api/reset":
                STORE.delete(session_id)
                self._json(ENGINE.landing_state(), cookie=session_id if is_new else None)
                return
            else:
                if not state:
                    raise GameError("Begin a chronicle first.")
                ENGINE.refresh(state)
                if path == "/api/action":
                    result = ENGINE.start_activity(state, str(body.get("action", "")))
                elif path == "/api/action/cancel":
                    result = ENGINE.cancel_activity(state)
                elif path == "/api/combat/start":
                    result = ENGINE.start_dungeon(state, str(body.get("zone", "")))
                elif path == "/api/combat/turn":
                    # Accept optional 'target' parameter (0-based index or name)
                    result = ENGINE.combat_turn(state, str(body.get("skill", "")), body.get("target"))
                elif path == "/api/story/start":
                    result = ENGINE.start_story(state, str(body.get("node", "")))
                elif path == "/api/combat/flee":
                    result = ENGINE.abandon_dungeon(state)
                elif path == "/api/party/toggle":
                    result = ENGINE.toggle_party_member(state, str(body.get("ally", "")))
                elif path == "/api/rest":
                    result = ENGINE.rest(state)
                elif path == "/api/choice":
                    result = ENGINE.make_story_choice(state, str(body.get("choice", "")))
                else:
                    self._json({"error": "Unknown action."}, HTTPStatus.NOT_FOUND)
                    return
            STORE.save(session_id, state)
            self._json(result, cookie=session_id if is_new else None)
        except (GameError, ValueError, TypeError) as error:
            self._json({"error": str(error)}, HTTPStatus.BAD_REQUEST, cookie=session_id if is_new else None)
        except json.JSONDecodeError:
            self._json({"error": "Invalid request data."}, HTTPStatus.BAD_REQUEST)

    def _session(self) -> tuple[str, bool]:
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        if SESSION_COOKIE in cookie and len(cookie[SESSION_COOKIE].value) == 32:
            return cookie[SESSION_COOKIE].value, False
        return secrets.token_hex(16), True

    def _read_json(self) -> dict:
        length = min(int(self.headers.get("Content-Length", "0")), 16_384)
        if not length:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _json(
        self,
        payload: dict,
        status: HTTPStatus = HTTPStatus.OK,
        cookie: str | None = None,
    ) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        if cookie:
            self.send_header(
                "Set-Cookie",
                f"{SESSION_COOKIE}={cookie}; Path=/; HttpOnly; SameSite=Strict; Max-Age=31536000",
            )
        self.end_headers()
        self.wfile.write(data)

    def _static(self, requested_path: str) -> None:
        relative = "index.html" if requested_path == "/" else requested_path.lstrip("/")
        file_path = (WEB_ROOT / relative).resolve()
        if not file_path.is_relative_to(WEB_ROOT.resolve()) or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        data = file_path.read_bytes()
        content_type, _ = mimetypes.guess_type(file_path.name)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type or 'application/octet-stream'}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[chronicle] {self.address_string()} — {format % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Python-first Slime Chronicles game.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--open", action="store_true", help="Open the game in your default browser.")
    args = parser.parse_args()
    address = (args.host, args.port)
    server = ThreadingHTTPServer(address, ChronicleHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"Slime Chronicles is running at {url}")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nChronicle paused. Your save is safe.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
