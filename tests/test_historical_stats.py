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

    def test_incomplete_logs_use_corroborated_totals_without_relaxing_cutoffs(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(collector,'ROOT',Path(directory)), patch('builtins.print'):
            root=Path(directory);raw=root/'data/raw/2022-23/player_boxscores_2023.csv';raw.parent.mkdir(parents=True)
            fields=['game_id','minutes','person_id','team_id','team_tricode','first_name','family_name','points','rebounds_total','assists','steals','blocks']
            with raw.open('w',newline='') as handle:
                writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader()
                for pid in (1,2,3):
                    for i in range(30):writer.writerow(dict(zip(fields,[f'00222{i:05}','20:00' if pid==2 else '0:00',pid,10,'ABC','Example',str(pid),0,0,0,0,0])))
            proofs=[]
            for pid,gp,minutes,decision in [(1,30,450,'include'),(2,40,599,'exclude'),(3,29,600,'exclude')]:
                official=dict(PLAYER_ID=pid,SEASON_ID='2022-23',TEAM_ID=10,TEAM_ABBREVIATION='ABC',GP=gp,MIN=minutes,PTS=0,REB=0,AST=0,STL=0,BLK=0)
                proofs.append(dict(season='2022-23',player_id=pid,team='ABC',source_aggregate=dict(gp=30,seconds=36000 if pid==2 else 0,points=0,rebounds_total=0,assists=0,steals=0,blocks=0),official_row=official,independent_reference_row={'G':str(gp),'MP':str(minutes)},decision=decision))
            staging=root/'data/staging';staging.mkdir(parents=True);path=staging/'stats_2022_23_source_corrections.json';payload=dict(season='2022-23',eligibility_source_overrides=proofs);path.write_text(json.dumps(payload))
            collector.collect('2022-23')
            rows=json.loads((staging/'stats_2022_23.json').read_text())
            self.assertEqual([(r['player_id'],r['gp'],r['mpg']) for r in rows],[(1,30,15.0)])
            manifest=json.loads((staging/'stats_2022_23_manifest.json').read_text())
            self.assertEqual(len(manifest['eligibility_source_overrides']),3)
            proofs[0]['independent_reference_row']['MP']='449';path.write_text(json.dumps(payload))
            with self.assertRaises(AssertionError):collector.collect('2022-23')
