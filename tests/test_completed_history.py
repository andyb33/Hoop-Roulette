"""Check historical promotion against preserved stats and official jersey evidence."""
import hashlib
import json
import unittest
from pathlib import Path
from nba_roulette.data import ROOT, load_records


class CompletedHistoryTests(unittest.TestCase):
    def test_promoted_stats_are_unchanged_and_all_jerseys_have_final_game_evidence(self):
        for season, count in [('2022-23',305),('2021-22',317)]:
            slug=season.replace('-','_')
            staged=ROOT/f'data/staging/stats_{slug}.json'
            output=ROOT/f'data/game/players_{slug}.json'
            audit=json.loads((ROOT/f'data/processed/completion_{slug}.json').read_text())
            rows=json.loads(output.read_text())
            originals=json.loads(staged.read_text())
            self.assertTrue(audit['passed'])
            self.assertEqual(audit['unresolved'],[])
            self.assertEqual(audit['entries'],count)
            self.assertEqual(audit['staged_sha256'],hashlib.sha256(staged.read_bytes()).hexdigest())
            self.assertEqual(audit['game_sha256'],hashlib.sha256(output.read_bytes()).hexdigest())
            evidence={(r['team'],r['player_id']):r for r in audit['jersey_evidence']}
            self.assertEqual(len(evidence),count)
            for row,original in zip(rows,originals):
                self.assertEqual({k:row[k] for k in original},original)
                official=evidence[(row['team'],row['player_id'])]['official_box_score_player']
                self.assertEqual(int(official['personId']),row['player_id'])
                self.assertEqual(int(official['jerseyNum']),row['jersey'])
                self.assertEqual(str(official['jerseyNum']),row['jersey_display'])
                self.assertEqual(official['played'],'1')
            self.assertEqual(sum(r['all_nba'] is not None for r in rows),15)
            self.assertEqual(sum(r['all_defense'] is not None for r in rows),10)
            for award in ('mvp','dpoy','roy'):
                self.assertEqual(sum(r[award] for r in rows),1)

    def test_championship_credit_requires_title_roster_and_team_stint(self):
        for season in ('2022-23','2021-22'):
            slug=season.replace('-','_')
            audit=json.loads((ROOT/f'data/processed/completion_{slug}.json').read_text())
            members={int(p['personId']) for p in audit['champion_roster']}
            for r in load_records([season]):
                self.assertEqual(r.champion,r.team==audit['champion_team'] and r.player_id in members)
        bones=next(r for r in load_records(['2022-23']) if r.player_id==1630538 and r.team=='DEN')
        self.assertFalse(bones.champion)

    def test_loading_all_five_seasons_has_no_duplicate_entries(self):
        rows=load_records()
        self.assertEqual(len(rows),1565)
        self.assertEqual(len({(r.season,r.team,r.player_id) for r in rows}),1565)
        self.assertEqual(len({(r.season,r.team) for r in rows}),150)
