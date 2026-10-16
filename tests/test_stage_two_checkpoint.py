"""Preserved verification evidence for the final Stage 2 batch."""
import hashlib
import json
import copy
import sys
import unittest
from unittest.mock import patch
from nba_roulette.data import ROOT


class StageTwoCheckpointTests(unittest.TestCase):
    def test_completed_batch_seasons_preserve_stats_and_complete_evidence(self):
        for season, champion, final, defense_count in [
            ('1982-83', 'PHI', '0048200043', 11),
            ('1981-82', 'LAL', '0048100045', 10),
        ]:
            with self.subTest(season=season):
                slug = season.replace('-', '_')
                staged = ROOT / f'data/staging/stats_{slug}.json'
                game = ROOT / f'data/game/players_{slug}.json'
                stats = json.loads(staged.read_text())
                rows = json.loads(game.read_text())
                verification = json.loads((ROOT / f'data/staging/stats_{slug}_verification.json').read_text())
                audit = json.loads((ROOT / f'data/processed/completion_{slug}.json').read_text())
                self.assertTrue(verification['passed'])
                self.assertTrue(audit['passed'])
                self.assertEqual(verification['errors'], [])
                self.assertEqual(verification['stat_comparisons'], len(rows) * 7)
                self.assertEqual(verification['regular_season_games'], 943)
                self.assertTrue(verification['schedule_evidence']['matches'])
                self.assertEqual(set(verification['schedule_evidence']['team_games'].values()), {82})
                self.assertEqual(audit['unresolved'], [])
                self.assertEqual(audit['staged_sha256'], hashlib.sha256(staged.read_bytes()).hexdigest())
                self.assertEqual(audit['game_sha256'], hashlib.sha256(game.read_bytes()).hexdigest())
                self.assertEqual(len(stats), len(rows))
                for original, row in zip(stats, rows):
                    self.assertEqual({key: row[key] for key in original}, original)
                    self.assertGreaterEqual(row['gp'], 30)
                self.assertEqual(audit['champion_team'], champion)
                self.assertEqual(audit['title_game_verification']['game_id'], final)
                members = {int(player['personId']) for player in audit['champion_roster']}
                for row in rows:
                    self.assertEqual(row['champion'], row['team'] == champion and row['player_id'] in members)
                self.assertEqual(len(audit['official_all_nba']), 10)
                self.assertEqual(len(audit['official_all_defense']), defense_count)
                self.assertEqual(sum(row['dpoy'] for row in rows), int(season == '1982-83'))
                self.assertEqual(audit['jerseys_verified'], len(rows))
                self.assertEqual(len(audit['jersey_evidence']), len(rows))

    def test_placeholder_final_appearances_preserve_original_rows(self):
        proofs = json.loads((ROOT / 'data/staging/final_appearance_1982_83_resolutions.json').read_text())
        indexed = {(proof['player_id'], proof['team']): proof for proof in proofs}
        for key, final in [((77136, 'IND'), '0028200584'), ((78195, 'GSW'), '0028200633')]:
            proof = indexed[key]
            self.assertEqual(proof['game_id'], final)
            self.assertGreater(len(proof['official_stint_game_log_rows']), proof['official_row']['GP'])
            self.assertTrue(proof['excluded_zero_minute_rows'])
            self.assertTrue(all(row['MIN'] == 0 for row in proof['excluded_zero_minute_rows']))
            self.assertGreater(proof['source_observed_game_date'], proof['game_date'])

    def test_collins_partial_counting_disagreements_remain_explicit(self):
        with patch.object(sys, 'path', [str(ROOT / 'scripts'), *sys.path]):
            from complete_historical_seasons import final_log_rows
        proofs = json.loads((ROOT / 'data/staging/final_appearance_1980_81_resolutions.json').read_text())
        proof = next(item for item in proofs if item['player_id'] == 76418)
        rows = final_log_rows(proof)
        self.assertEqual((len(rows), sum(row['MIN'] for row in rows), sum(row['PTS'] for row in rows)), (47, 1184, 597))
        self.assertEqual(proof['game_id'], '0028000533')
        self.assertEqual(proof['counting_total_disagreements'], {'REB': {'observed': 186, 'official': 187}, 'AST': {'observed': 114, 'official': 115}})
        broken = copy.deepcopy(proof)
        broken['player_id'] = 1
        with self.assertRaises(AssertionError):
            final_log_rows(broken)
        broken = copy.deepcopy(proof)
        broken['counting_total_disagreements']['REB']['observed'] = 187
        with self.assertRaises(AssertionError):
            final_log_rows(broken)
