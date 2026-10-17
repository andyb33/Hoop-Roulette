"""Keep the first 1970s batch gated by evidence, including unresolved uniforms."""
import copy
import hashlib
import json
import unittest

from nba_roulette.data import ROOT, load_records
from scripts.collect_historical_stats import historical_team


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class SeventiesHistoryTests(unittest.TestCase):
    def test_three_independent_stats_gates_and_22_team_schedules(self):
        for season, count in [('1979-80', 197), ('1978-79', 209), ('1977-78', 207)]:
            slug = season.replace('-', '_')
            path = ROOT / f'data/staging/stats_{slug}.json'
            report = read(f'data/staging/stats_{slug}_verification.json')
            self.assertTrue(report['passed'] and report['eligibility_sets_match'])
            self.assertEqual(report['errors'], [])
            self.assertEqual(report['staged_sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(report['stat_comparisons'], count * 7)
            self.assertEqual(report['regular_season_games'], 902)
            schedule = report['schedule_evidence']['team_games']
            self.assertEqual(len(schedule), 22)
            self.assertEqual(set(schedule.values()), {82})
            self.assertEqual(len(json.loads(path.read_text(encoding='utf-8'))), count)

    def test_historical_franchise_boundaries(self):
        for season, source, expected in [('1977-78', 'LAC', 'BUF'), ('1978-79', 'LAC', 'SDC'),
                                          ('1978-79', 'UTH', 'NOJ'), ('1979-80', 'UTH', 'UTA'),
                                          ('1978-79', 'OKC', 'SEA'), ('2008-09', 'OKC', 'OKC'),
                                          ('1977-78', 'WAS', 'WSB')]:
            self.assertEqual(historical_team(season, source), expected)

    def test_landsberger_exception_is_exactly_scoped(self):
        import sys
        from unittest.mock import patch
        with patch.object(sys, "path", [str(ROOT / "scripts"), *sys.path]):
            from complete_historical_seasons import final_log_rows
        proof = next(p for p in read('data/staging/final_appearance_1979_80_resolutions.json')
                     if p['player_id'] == 77334)
        bounded = final_log_rows(proof)
        self.assertEqual(len(bounded), 54)
        self.assertNotIn('0027900619', {r['Game_ID'] for r in bounded})
        self.assertEqual(sum(r['PTS'] for r in bounded), 453)
        changed = copy.deepcopy(proof)
        changed['player_id'] = 1
        with self.assertRaises(AssertionError):
            final_log_rows(changed)

    def test_hassett_stays_pending_and_batch_stays_out_of_default_pool(self):
        review = read('data/staging/review_1979_80_76966_IND.json')
        self.assertEqual(review['status'], 'NEEDS_DATED_FINAL_UNIFORM_EVIDENCE')
        self.assertNotIn('resolved_jersey', review)
        self.assertFalse((ROOT / 'data/staging/jersey_1979_80_76966_IND_resolution.json').exists())
        self.assertFalse({'1979-80', '1978-79', '1977-78'} & {r.season for r in load_records()})

    def test_completed_1978_season_has_verified_title_and_every_uniform(self):
        audit = read('data/processed/completion_1978_79.json')
        rows = read('data/game/players_1978_79.json')
        self.assertTrue(audit['passed'])
        self.assertEqual(audit['unresolved'], [])
        self.assertEqual(len(audit['jersey_evidence']), len(rows))
        self.assertEqual(audit['champion_team'], 'SEA')
        self.assertEqual(audit['title_game_verification']['game_id'], '0047800053')
        self.assertEqual(sum(bool(r['all_nba']) for r in rows), 10)
        self.assertEqual(sum(bool(r['all_defense']) for r in rows), 10)
        self.assertEqual(sum(r['dpoy'] for r in rows), 0)
