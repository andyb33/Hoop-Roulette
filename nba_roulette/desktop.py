"""Durable, port-independent desktop preferences and completed score history."""
from __future__ import annotations

import json
import os
import sys
import threading
from pathlib import Path

KEYS = {"hoopreel.scores.v1", "hoopreel.instantSpins.v1"}


def app_directory() -> Path:
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "Hoopreel"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Hoopreel"
    return Path.home() / ".local" / "share" / "Hoopreel"


class DesktopStore:
    def __init__(self, directory: Path):
        directory.mkdir(parents=True, exist_ok=True)
        self.path = directory / "preferences.json"
        self.lock = threading.RLock()

    def read(self) -> dict[str, str]:
        with self.lock:
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
            except FileNotFoundError:
                return {}
            if not isinstance(data, dict):
                raise ValueError("Desktop preferences must contain an object")
            return {k: v for k, v in data.items() if k in KEYS and isinstance(v, str)}

    def save(self, key: str, value: str) -> None:
        if key not in KEYS or not isinstance(value, str) or len(value) > 2_000_000:
            raise ValueError("Invalid desktop preference")
        with self.lock:
            data = self.read()
            data[key] = value
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            temporary.replace(self.path)
