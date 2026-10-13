import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import collect_historical_stats as collector


class HistoricalStatsTests(unittest.TestCase):
    def test_decimal_ties_round_up(self):
        self.assertEqual(collector.rounded_rate(153, 60), 2.6)
        self.assertEqual(collector.rounded_rate(855, 60), 14.3)

    def test_recorded_zero_minutes_counts_gp_and_dnp_does_not(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(collector, "ROOT", Path(directory)):
            raw = Path(directory) / "data/raw/2022-23/player_boxscores_2023.csv"
            raw.parent.mkdir(parents=True)
            fields = ["game_id", "minutes", "person_id", "team_id", "team_tricode", "first_name", "family_name", "points", "rebounds_total", "assists", "steals", "blocks"]
            with raw.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for i in range(32):
                    writer.writerow(dict(zip(fields, [f"00222{i:05}", "20:00" if i < 30 else "0:00" if i == 30 else "", 1, 10, "ABC", "Example", "Player", 0, 0, 0, 0, 0])))
            collector.collect("2022-23")
            row = json.loads((Path(directory) / "data/staging/stats_2022_23.json").read_text())[0]
            self.assertEqual(row["gp"], 31)
            self.assertEqual(row["mpg"], 19.4)

    def test_next_year_requires_passing_current_report_for_same_data(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(collector, "ROOT", Path(directory)):
            with self.assertRaisesRegex(ValueError, "Verify"):
                collector.require_previous_verified("2021-22")
            staged = Path(directory) / "data/staging"
            staged.mkdir(parents=True)
            data = staged / "stats_2022_23.json"
            data.write_text("[]")
            report = staged / "stats_2022_23_verification.json"
            report.write_text(json.dumps({"passed": True, "staged_sha256": hashlib.sha256(data.read_bytes()).hexdigest()}))
            collector.require_previous_verified("2021-22")
            data.write_text("[{}]")
            with self.assertRaisesRegex(ValueError, "stale"):
                collector.require_previous_verified("2021-22")

    def test_workbook_mojibake_names_match_without_changing_identity(self):
        from scripts.verify_historical_stats import name_key
        self.assertEqual(name_key('Nikola JokiÄ‡'),name_key('Nikola Jokić'))
        self.assertEqual(name_key('Jonas ValanÄ\x8diÅ«nas'),name_key('Jonas Valančiūnas'))
        self.assertEqual(name_key('Dennis SchrÃ¶der'),name_key('Dennis Schröder'))
        self.assertEqual(name_key('Bogdan Bogdanović'),name_key('Bogdan BogdanoviÄ‡'))
        self.assertNotEqual(name_key('Bogdan Bogdanović'),name_key('Bojan Bogdanović'))

        self.assertEqual(name_key('Ömer Aşık'),name_key('Omer Asik'))
        self.assertEqual(name_key('Nene Hilario'),name_key('Nenê'))

    def test_taylor_reference_alias_preserves_identity(self):
        from scripts.verify_historical_stats import name_key
        self.assertEqual(name_key('Jeffery Taylor'),name_key('Jeff Taylor'))
        self.assertNotEqual(name_key('Jeffery Taylor'),name_key('Jeff Adrien'))

    def test_yi_reference_name_order_preserves_identity(self):
        from scripts.verify_historical_stats import name_key
        self.assertEqual(name_key('Jianlian Yi'),name_key('Yi Jianlian'))
        self.assertNotEqual(name_key('Jianlian Yi'),name_key('Yao Ming'))
