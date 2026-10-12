import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_goat_datasets import player_key
from collect_award_winners import parse_award_html


class GoatDataTests(unittest.TestCase):
    def test_co_winners_are_separate(self):
        rows = parse_award_html('<p>1994-95 — Jason Kidd, Grant Hill, Dallas Mavericks, Detroit Pistons</p>')
        self.assertEqual(rows, [('1994-95', 'Jason Kidd', 'Dallas Mavericks'),
                                ('1994-95', 'Grant Hill', 'Detroit Pistons')])

    def test_aliases_and_accents(self):
        self.assertEqual(player_key('Lew Alcindor'), player_key('Kareem Abdul-Jabbar'))
        self.assertEqual(player_key('Luka Dončić'), player_key('Luka Doncic'))
        self.assertEqual(player_key('Shaquille O’Neal'), player_key("Shaquille O'Neal"))

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

    def test_incomplete_enrichment_cannot_claim_game_readiness(self):
        manifest = json.loads((ROOT / 'data/goat/manifest.json').read_text())
        self.assertTrue(manifest['award']['winner_coverage_complete'])
        self.assertFalse(manifest['award']['historical_coverage_complete'])
        self.assertFalse(manifest['enabled_in_game'])
