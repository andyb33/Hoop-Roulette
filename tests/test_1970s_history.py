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

    def test_user_policy_resolves_eight_conflicts_without_claiming_historical_verification(self):
        expected = {76966: 11, 78473: 14, 78157: 32, 76356: 5,
                    77689: 35, 77869: 42, 77812: 42, 78215: 40}
        status = read('data/processed/stage3_readiness_1973_1980.json')
        observed = {}
        for season in status['seasons']:
            slug = season['season'].replace('-', '_')
            audit = read(f'data/processed/completion_{slug}.json')
            rows = read(f'data/game/players_{slug}.json')
            policies = season['policy_jersey_resolutions']
            self.assertEqual(audit.get('jerseys_resolved_by_user_policy', 0), len(policies))
            for review in policies:
                proof = read(review['resolution_file'])
                chosen = max(map(int, review['alternatives']))
                self.assertEqual(proof['resolved_jersey'], chosen)
                self.assertFalse(proof['historically_verified_final_jersey'])
                self.assertEqual(proof['status'], 'RESOLVED_BY_USER_POLICY')
                row = next(r for r in rows if r['player_id'] == proof['player_id'] and r['team'] == proof['team'])
                self.assertEqual(row['jersey'], chosen)
                observed[proof['player_id']] = chosen
            for entry in audit['jersey_evidence']:
                date_proof = entry.get('game_date_resolution')
                if date_proof:
                    self.assertEqual(date_proof['original_game_time_local'], '0001-01-01T00:00:00Z')
                    self.assertEqual(len(date_proof['schedule_rows']), 2)
                    self.assertTrue(all(r['GAME_ID'] == entry['game_id'] and r['GAME_DATE'] == entry['last_game_date']
                                        for r in date_proof['schedule_rows']))
        self.assertEqual(observed, expected)

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

    def test_final_four_stats_and_historical_team_counts(self):
        for season, count, teams, games in [('1976-77', 212, 22, 902), ('1975-76', 152, 18, 738),
                                            ('1974-75', 158, 18, 738), ('1973-74', 138, 17, 697)]:
            slug = season.replace('-', '_')
            rows = read(f'data/staging/stats_{slug}.json')
            report = read(f'data/staging/stats_{slug}_verification.json')
            self.assertTrue(report['passed'] and report['eligibility_sets_match'])
            self.assertEqual((len(rows), report['stat_comparisons']), (count, count * 7))
            self.assertEqual(report['regular_season_games'], games)
            self.assertEqual(len(report['schedule_evidence']['team_games']), teams)
            self.assertEqual(set(report['schedule_evidence']['team_games'].values()), {82})
            self.assertEqual(report['staged_sha256'], hashlib.sha256(
                (ROOT / f'data/staging/stats_{slug}.json').read_bytes()).hexdigest())
            codes = {r['team'] for r in rows}
            self.assertEqual('CAP' in codes, season == '1973-74')
            self.assertEqual('KCO' in codes, season in ('1973-74', '1974-75'))
            self.assertEqual('NYN' in codes, season == '1976-77')
            self.assertTrue(all(r['gp'] >= 30 for r in rows))

    def test_team_guides_resolve_only_the_documented_conflicts(self):
        for season, player, team, field, original, corrected in [
                ('1976-77', 77582, 'ATL', 'GP', 73, 74), ('1973-74', 78520, 'POR', 'BLK', 64, 63)]:
            slug = season.replace('-', '_')
            manifest = read(f'data/staging/stats_{slug}_manifest.json')
            proofs = manifest['team_guide_total_overrides']
            self.assertEqual(len(proofs), 1)
            proof = proofs[0]
            self.assertEqual((proof['player_id'], proof['team']), (player, team))
            self.assertEqual(proof['original_nba_official_row'][field], original)
            self.assertEqual(proof['team_guide_totals'][field], corrected)
            self.assertEqual(len(proof['source_sha256']), 64)
            row = next(r for r in read(f'data/staging/stats_{slug}.json') if r['player_id'] == player)
            self.assertEqual(row['gp'], proof['team_guide_totals']['GP'])
            self.assertEqual(row['bpg'], 0.8 if field == 'BLK' else 1.1)
            self.assertEqual(read(f'data/staging/stats_{slug}_verification.json')['team_guide_total_resolutions'], proofs)

    def test_completed_1973_and_1974_preserve_every_stat_and_original_appearance(self):
        for season, count, champion in [('1973-74', 138, 'BOS'), ('1974-75', 158, 'GSW')]:
            slug = season.replace('-', '_')
            rows = read(f'data/game/players_{slug}.json')
            staged = read(f'data/staging/stats_{slug}.json')
            audit = read(f'data/processed/completion_{slug}.json')
            self.assertTrue(audit['passed'])
            self.assertEqual(audit['unresolved'], [])
            self.assertEqual((len(rows), audit['champion_team']), (count, champion))
            self.assertEqual(len(audit['jersey_evidence']), count)
            for row, original in zip(rows, staged):
                self.assertEqual({k: row[k] for k in original}, original)
            self.assertEqual(sum(bool(r['all_nba']) for r in rows), 10)
            self.assertEqual(sum(bool(r['all_defense']) for r in rows), 12 if season == '1973-74' else 10)
            self.assertEqual(sum(r['dpoy'] for r in rows), 0)
            if season == '1973-74':
                self.assertEqual(sum(r['all_defense'] == 1 for r in rows), 6)
                self.assertEqual(sum(r['all_defense'] == 2 for r in rows), 6)
                entry = next(p for p in audit['jersey_evidence'] if p['player_id'] == 76002)
                self.assertEqual(entry['official_box_score_player']['played'], '0')
                self.assertTrue(entry['verified_played'])
                self.assertEqual(entry['appearance_resolution']['original_box_score_player']['statistics']['minutes'], '')
                self.assertEqual(entry['appearance_resolution']['original_box_score_player']['statistics']['points'], 9)

    def test_stage3_readiness_lists_every_pending_uniform_without_enabling_the_batch(self):
        status = read('data/processed/stage3_readiness_1973_1980.json')
        self.assertEqual((status['entries'], status['stat_comparisons']), (1273, 8911))
        self.assertEqual(status['complete_seasons'], [f'{y}-{(y+1)%100:02}' for y in range(1973, 1980)])
        self.assertEqual(status['pending_jerseys'], 0)
        self.assertEqual(status['policy_jersey_resolutions'], 8)
        self.assertFalse(status['enabled_in_default_pool'])
        self.assertEqual(len(status['seasons']), 7)
        for season in status['seasons']:
            self.assertTrue(season['stats_verified'] and season['honors_verified'])
            for review in season['pending_jerseys']:
                self.assertNotIn('resolved_jersey', review)
                self.assertGreaterEqual(len(review['alternatives']), 2)
        self.assertEqual(len({r.season for r in load_records()}), 46)
