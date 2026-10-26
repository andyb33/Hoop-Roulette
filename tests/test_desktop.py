import json
import tempfile
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from nba_roulette.desktop import DesktopStore


class DesktopStoreTests(unittest.TestCase):
    def test_scores_and_settings_survive_relaunch(self):
        with tempfile.TemporaryDirectory() as directory:
            store = DesktopStore(Path(directory))
            self.assertEqual(store.read(), {})
            store.save("hoopreel.scores.v1", json.dumps({"best": 321, "recent": []}))
            store.save("hoopreel.instantSpins.v1", "true")
            restored = DesktopStore(Path(directory)).read()
            self.assertEqual(json.loads(restored["hoopreel.scores.v1"])["best"], 321)
            self.assertEqual(restored["hoopreel.instantSpins.v1"], "true")

    def test_concurrent_writes_keep_both_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            store = DesktopStore(Path(directory))
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = [pool.submit(store.save, key, value) for key, value in
                           [("hoopreel.scores.v1", '{"best": 222}'), ("hoopreel.instantSpins.v1", "false")]]
                for result in results:
                    result.result()
            self.assertEqual(len(store.read()), 2)

    def test_rejects_invalid_and_oversized_preferences(self):
        with tempfile.TemporaryDirectory() as directory:
            store = DesktopStore(Path(directory))
            for key, value in [("../other", "x"), ("hoopreel.scores.v1", "x" * 2_000_001)]:
                with self.assertRaises(ValueError):
                    store.save(key, value)
            self.assertEqual(store.read(), {})

    def test_corrupt_save_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            store = DesktopStore(Path(directory))
            store.path.write_text("broken", encoding="utf-8")
            with self.assertRaises(ValueError):
                store.save("hoopreel.instantSpins.v1", "true")
            self.assertEqual(store.path.read_text(), "broken")
