import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_goat_datasets import player_key, apply_verification
from collect_award_winners import parse_award_html
from verify_goat_datasets import parse_honors, resolve_player_id


class GoatDataTests(unittest.TestCase):
    def test_co_winners_are_separate(self):
        rows = parse_award_html('<p>1994-95 — Jason Kidd, Grant Hill, Dallas Mavericks, Detroit Pistons</p>')
        self.assertEqual(rows, [('1994-95', 'Jason Kidd', 'Dallas Mavericks'),
                                ('1994-95', 'Grant Hill', 'Detroit Pistons')])

    def test_aliases_and_accents(self):
        self.assertEqual(player_key('Lew Alcindor'), player_key('Kareem Abdul-Jabbar'))
        self.assertEqual(player_key('Luka Dončić'), player_key('Luka Doncic'))
        self.assertEqual(player_key('Shaquille O’Neal'), player_key("Shaquille O'Neal"))

    def test_same_name_players_are_disambiguated_by_career_years(self):
        players = [dict(DISPLAY_FIRST_LAST='Patrick Ewing', FROM_YEAR='1985', TO_YEAR='2001', PERSON_ID=121),
                   dict(DISPLAY_FIRST_LAST='Patrick Ewing', FROM_YEAR='2010', TO_YEAR='2010', PERSON_ID=201607)]
        self.assertEqual(resolve_player_id(players, 'Patrick Ewing', '1985-86'), 121)
        self.assertEqual(resolve_player_id(players, 'Patrick Ewing', '2010-11'), 201607)
        with self.assertRaises(ValueError):
            resolve_player_id(players, 'Patrick Ewing', '2005-06')

    def test_complete_winner_coverage_and_deduplication(self):
        rows = json.loads((ROOT / 'data/goat/award_jackpot.json').read_text())
        self.assertEqual(len(rows), 149)
        self.assertEqual(len({(r['season'], r['player_key']) for r in rows}), 149)
        self.assertEqual(sum(r['mvp'] is True for r in rows), 53)
        self.assertEqual(sum(r['roy'] is True for r in rows), 55)
        self.assertEqual(sum(r['dpoy'] is True for r in rows), 44)
        for season, name in [('1987-88', 'Michael Jordan'), ('1993-94', 'Hakeem Olajuwon'),
                             ('2019-20', 'Giannis Antetokounmpo')]:
            matching = [r for r in rows if r['season'] == season and r['player_key'] == player_key(name)]
            self.assertEqual(len(matching), 1)
            self.assertTrue(matching[0]['mvp'] and matching[0]['dpoy'])

    def test_verified_manifest_matches_evidence(self):
        manifest = json.loads((ROOT / 'data/goat/manifest.json').read_text())
        self.assertTrue(manifest['award']['winner_coverage_complete'])
        self.assertTrue(manifest['enabled_in_game'])
        rows = json.loads((ROOT / 'data/goat/award_jackpot.json').read_text())
        self.assertEqual(manifest['award']['historical_coverage_complete'],
                         all(r['verification_status'] == 'official_verified' for r in rows))

    def test_every_selected_record_has_complete_official_evidence(self):
        awards = json.loads((ROOT / 'data/goat/award_jackpot.json').read_text())
        prehistoric = json.loads((ROOT / 'data/goat/prehistoric_jackpot.json').read_text())
        report = json.loads((ROOT / 'data/goat/verification_report.json').read_text())
        self.assertEqual(report['requested'], 161)
        self.assertEqual(report['verified'], 161)
        self.assertEqual(report['failures'], [])
        for r in awards + prehistoric:
            self.assertEqual(r['verification_status'], 'official_verified')
            self.assertIsInstance(r['player_id'], int)
            for field in ('gp', 'mpg', 'ppg', 'rpg', 'apg', 'jersey'):
                self.assertIsNotNone(r[field], (r['entry_id'], field))
            self.assertIsInstance(r['champion'], bool)
            self.assertFalse(any(v == 'pending_verification' for v in r['availability'].values()))
            self.assertTrue(r['sources']['stats'].startswith('https://stats.nba.com/'))
        for r in awards:
            self.assertIsNotNone(r['spg'])
            self.assertIsNotNone(r['bpg'])
        for r in prehistoric:
            self.assertIsNone(r['spg'])
            self.assertIsNone(r['bpg'])
            self.assertEqual(r['availability']['spg'], 'not_recorded')

    def test_trade_and_pool_identity_cases(self):
        awards = json.loads((ROOT / 'data/goat/award_jackpot.json').read_text())
        prehistoric = json.loads((ROOT / 'data/goat/prehistoric_jackpot.json').read_text())
        mutombo = next(r for r in awards if r['player_key'] == 'dikembe-mutombo' and r['season'] == '2000-01')
        self.assertEqual((mutombo['team'], mutombo['gp'], mutombo['jersey']), ('PHI', 26, 55))
        early = next(r for r in prehistoric if r['player_key'] == 'kareem-abdul-jabbar')
        later = next(r for r in awards if r['player_key'] == early['player_key'])
        self.assertEqual(early['player_id'], later['player_id'])
        self.assertNotEqual(early['game_player_id'], later['game_player_id'])
        ewing = next(r for r in awards if r['player_key'] == 'patrick-ewing')
        johnson = next(r for r in awards if r['player_key'] == 'larry-johnson')
        self.assertEqual(ewing['player_id'], 121)
        self.assertEqual(johnson['player_id'], 913)

    def test_honors_parser_keeps_actual_tiers(self):
        fixture = '<article>' + ''.join(
            f'<p>&gt; {year}-{(year+1)%100:02}</p><p>FIRST TEAM<br>• G: Jerry West, Los Angeles Lakers</p>'
            '<p>SECOND TEAM<br>• John Havlicek, Boston Celtics</p>'
            for year in range(1950, 2001)) + '</article>'
        parsed = parse_honors(fixture)
        self.assertEqual(parsed['1970-71']['jerry-west'], 1)
        self.assertEqual(parsed['1970-71']['john-havlicek'], 2)

    def test_preofficial_zero_is_not_a_recorded_stat(self):
        original = dict(player='Wilt Chamberlain', season='1961-62', spg=0, bpg=0)
        evidence = {('prehistoric', '1961-62', 'wilt-chamberlain'):
                    dict(spg=0, bpg=0, all_nba=1, all_defense=None, jersey=13)}
        row = apply_verification(original, 'prehistoric', evidence)
        self.assertIsNone(row['spg'])
        self.assertIsNone(row['bpg'])
        self.assertEqual(row['availability']['spg'], 'not_recorded')
        self.assertEqual(row['availability']['all_defense'], 'award_not_introduced')
        self.assertIsNone(row['dpoy'])
