from __future__ import annotations

import unittest
from collections import Counter

from nba_roulette.data import load_records


class DataLoaderTests(unittest.TestCase):
    def test_loads_validated_forty_season_pool(self) -> None:
        records = load_records()
        self.assertEqual(len(records), 10926)
        self.assertEqual(Counter(row.season for row in records), {
            "1986-87": 208, "1987-88": 202, "1988-89": 225, "1989-90": 231, "1990-91": 235, "1991-92": 239, "1992-93": 247, "1993-94": 246, "1994-95": 250, "1995-96": 258, "1996-97": 254, "1997-98": 269, "1998-99": 234, "1999-00": 266, "2000-01": 267, "2001-02": 268, "2002-03": 265, "2003-04": 260, "2004-05": 283, "2005-06": 275, "2006-07": 286, "2007-08": 271, "2008-09": 274, "2009-10": 273, "2010-11": 287, "2011-12": 276, "2012-13": 289, "2013-14": 291, "2014-15": 314, "2015-16": 293, "2016-17": 310, "2017-18": 303, "2018-19": 307, "2019-20": 298, "2020-21": 307, "2021-22": 317, "2022-23": 305, "2023-24": 300, "2024-25": 317, "2025-26": 326,
        })
        self.assertEqual(len({(row.season, row.team) for row in records}), 1154)
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
