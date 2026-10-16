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

    def test_older_totals_adapter_keeps_traded_rows_names_and_unrounded_totals(self):
        from scripts.verify_historical_stats import extract_reference_csv, name_key
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'source.csv';output=Path(directory)/'reference.csv'
            fields=['','Year','Player','Age','Tm','G','MP','PTS','TRB','AST','STL','BLK']
            cases=[['1','1989','Charles Jones','31','WSB','53','1154','136','257','42','39','76'],['2','1989','Charles Jones','27','WSB','43','516','110','140','18','18','16'],['3','1989','Traded Player','25','TOT','60','1800','600','100','100','30','10'],['4','1989','Traded Player','25','BOS','30','449','300','50','50','15','5'],['5','1989','Traded Player','25','SAC','30','1351','300','50','50','15','5']]
            with path.open('w',newline='') as handle:
                writer=csv.writer(handle);writer.writerow(fields);writer.writerows(cases)
            extract_reference_csv(path,'1988-89',output)
            with output.open() as handle:rows=list(csv.DictReader(handle))
            self.assertEqual(len(rows),5)
            self.assertEqual([r['Player'] for r in rows[:2]],['Charles Jones','Charles Jones'])
            self.assertNotEqual(rows[0]['reference_key_name'],rows[1]['reference_key_name'])
            self.assertEqual({r['Tm'] for r in rows[2:]},{'TOT','BOS','SAC'})
            self.assertEqual((float(rows[3]['MP']),rows[3]['original_total_MP']),(15.0,'449'))
            self.assertEqual(name_key('Cliff T. Robinson'),name_key('Cliff Robinson'))
            self.assertNotEqual(name_key('Cliff T. Robinson'),name_key('Clifford Robinson'))
