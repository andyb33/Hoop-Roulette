from __future__ import annotations

import unittest
from collections import Counter

from nba_roulette.data import load_records


class DataLoaderTests(unittest.TestCase):
    def test_loads_validated_five_season_pool(self) -> None:
        records = load_records()
        self.assertEqual(len(records), 1565)
        self.assertEqual(Counter(row.season for row in records), {
            "2021-22": 317, "2022-23": 305, "2023-24": 300, "2024-25": 317, "2025-26": 326,
        })
        self.assertEqual(len({(row.season, row.team) for row in records}), 150)
        self.assertTrue(all(row.gp >= 30 and row.mpg >= 15.0 for row in records))
        self.assertTrue(all(0 <= row.jersey <= 99 for row in records))

    def test_legacy_snapshot_preserves_old_pool_and_current_is_exact_subset(self):
        from pathlib import Path
        from nba_roulette.data import ROOT
        current_seasons = ("2023-24", "2024-25", "2025-26")
        legacy = load_records(current_seasons, data_dir=ROOT / "data/legacy/15gp_10mpg/game")
        self.assertEqual(len(legacy), 1346)
        self.assertEqual(set(load_records(current_seasons)), {r for r in legacy if r.gp >= 30 and r.mpg >= 15.0})


if __name__ == "__main__":
    unittest.main()
