"""Check historical promotion against preserved stats and official jersey evidence."""
import hashlib
import json
import unittest
from pathlib import Path
from nba_roulette.data import ROOT, load_records


class CompletedHistoryTests(unittest.TestCase):
    def test_promoted_stats_are_unchanged_and_all_jerseys_have_final_game_evidence(self):
        for season, count in [('2022-23',305),('2021-22',317),('2020-21',307),('2019-20',298),('2018-19',307),('2017-18',303),('2016-17',310),('2015-16',293),('2014-15',314),('2013-14',291),('2012-13',289),('2011-12',276),('2010-11',287)]:
            slug=season.replace('-','_')
            staged=ROOT/f'data/staging/stats_{slug}.json'
            output=ROOT/f'data/game/players_{slug}.json'
            audit=json.loads((ROOT/f'data/processed/completion_{slug}.json').read_text(encoding='utf-8'))
            rows=json.loads(output.read_text(encoding='utf-8'))
            originals=json.loads(staged.read_text(encoding='utf-8'))
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
            self.assertEqual(sum(r['all_defense'] is not None for r in rows),11 if season=='2012-13' else 10)
            for award in ('mvp','dpoy','roy'):
                self.assertEqual(sum(r[award] for r in rows),1)

    def test_championship_credit_requires_title_roster_and_team_stint(self):
        for season in ('2022-23','2021-22','2020-21','2019-20','2018-19','2017-18','2016-17','2015-16','2014-15','2013-14','2012-13','2011-12','2010-11'):
            slug=season.replace('-','_')
            audit=json.loads((ROOT/f'data/processed/completion_{slug}.json').read_text(encoding='utf-8'))
            members={int(p['personId']) for p in audit['champion_roster']}
            for r in load_records([season]):
                self.assertEqual(r.champion,r.team==audit['champion_team'] and r.player_id in members)
        bones=next(r for r in load_records(['2022-23']) if r.player_id==1630538 and r.team=='DEN')
        self.assertFalse(bones.champion)

    def test_loading_all_sixteen_seasons_has_no_duplicate_entries(self):
        rows=load_records()
        self.assertEqual(len(rows),4840)
        self.assertEqual(len({(r.season,r.team,r.player_id) for r in rows}),4840)
        self.assertEqual(len({(r.season,r.team) for r in rows}),480)

    def test_shortened_seasons_match_official_schedule(self):
        for season, games, uniform in [('2020-21',1080,72),('2019-20',1059,None),('2018-19',1230,82)]:
            slug=season.replace('-','_')
            report=json.loads((ROOT/f'data/staging/stats_{slug}_verification.json').read_text(encoding='utf-8'))
            staged=ROOT/f'data/staging/stats_{slug}.json'
            self.assertTrue(report['passed'])
            self.assertEqual(report['errors'],[])
            self.assertEqual(report['staged_sha256'],hashlib.sha256(staged.read_bytes()).hexdigest())
            self.assertEqual(report['regular_season_games'],games)
            self.assertTrue(report['eligibility_sets_match'])
            self.assertTrue(report['schedule_evidence']['matches'])
            counts=report['schedule_evidence']['team_games']
            self.assertEqual(len(counts),30)
            self.assertEqual(sum(counts.values()),2*games)
            if uniform:
                self.assertEqual(set(counts.values()),{uniform})
            else:
                self.assertGreater(len(set(counts.values())),1)

    def test_double_award_winner_uses_one_normal_entry(self):
        rows=[r for r in load_records(['2019-20']) if r.player_id==203507]
        self.assertEqual(len(rows),1)
        self.assertTrue(rows[0].mvp and rows[0].dpoy)
        from nba_roulette.scoring import category_score, Category
        self.assertEqual(category_score(rows[0], Category.MAJOR_AWARD),50)

    def test_inactive_champion_and_traded_raptors(self):
        tor={r.player_id:r for r in load_records(['2018-19']) if r.team=='TOR'}
        self.assertTrue(tor[1628384].champion)  # OG Anunoby: inactive for the Finals.
        self.assertFalse(tor[1626153].champion)  # Delon Wright: traded to Memphis.
        self.assertFalse(tor[202685].champion)   # Jonas Valanciunas: traded to Memphis.

    def test_workbook_reference_seasons_are_complete_and_pinned(self):
        for season, count in [('2017-18',303),('2016-17',310),('2015-16',293),('2014-15',314),('2013-14',291),('2012-13',289),('2011-12',276),('2010-11',287)]:
            slug=season.replace('-','_')
            report=json.loads((ROOT/f'data/staging/stats_{slug}_verification.json').read_text(encoding='utf-8'))
            self.assertTrue(report['passed'])
            self.assertEqual(report['errors'],[])
            self.assertEqual(report['stat_comparisons'],7*count)
            self.assertEqual(report['records_checked'],count)
            self.assertEqual(report['reference']['year'],int(season[:4])+1)
            self.assertEqual(len(report['reference_workbook_sha256']),64)
            self.assertIn('a19c7d43b65028d80c782ce64d308ed392c57bbf',report['reference']['url'])
            self.assertTrue(report['schedule_evidence']['matches'])
            self.assertEqual(report['regular_season_games'],{'2012-13':1229,'2011-12':990}.get(season,1230))
            counts=report['schedule_evidence']['team_games']
            self.assertEqual(counts,{team:66 if season=='2011-12' else 81 if season=='2012-13' and team in ('BOS','IND') else 82 for team in counts})

    def test_prince_assists_resolution_matches_official_totals(self):
        report=json.loads((ROOT/'data/staging/stats_2015_16_verification.json').read_text(encoding='utf-8'))
        matches=[r for r in report['resolved_differences'] if r['player_id']==2419 and r['field']=='apg']
        self.assertEqual(len(matches),1)
        item=matches[0]
        self.assertEqual(item['official_total_evidence']['AST'],74)
        self.assertEqual(item['official_total_evidence']['GP'],77)
        self.assertEqual(item['staged'],1.0)
        self.assertEqual(item['reference'],0.9)
        row=next(r for r in load_records(['2015-16']) if r.player_id==2419)
        self.assertEqual(row.apg,1.0)

    def test_2013_schedule_and_taylor_identity(self):
        report=json.loads((ROOT/'data/staging/stats_2012_13_verification.json').read_text(encoding='utf-8'))
        self.assertTrue(report['passed'] and report['schedule_evidence']['matches'])
        self.assertEqual(report['stat_comparisons'],2023)
        self.assertEqual(report['regular_season_games'],1229)
        self.assertEqual(report['schedule_evidence']['team_games']['BOS'],81)
        self.assertEqual(report['schedule_evidence']['team_games']['IND'],81)
        rows=load_records(['2012-13'])
        taylor=next(r for r in rows if r.player_id==203106)
        self.assertEqual((taylor.player,taylor.team,taylor.gp),('Jeffery Taylor','CHA',77))
        self.assertEqual({r.team for r in rows if r.team.startswith('NO')},{'NOH'})

    def test_historical_team_codes_have_uniform_colors(self):
        from nba_roulette.web import TEAM_COLORS
        self.assertTrue({r.team for r in load_records()}.issubset(TEAM_COLORS))

    def test_2013_defense_tie_keeps_both_first_team_centers(self):
        rows=load_records(['2012-13'])
        defense=[r for r in rows if r.all_defense is not None]
        self.assertEqual(len(defense),11)
        self.assertEqual(sum(r.all_defense==1 for r in defense),6)
        self.assertEqual({r.player_id for r in defense if r.player_id in (2199,201149)},{2199,201149})
        self.assertTrue(all(r.all_defense==1 for r in defense if r.player_id in (2199,201149)))

    def test_stage_one_has_every_season_and_historical_franchises(self):
        rows=load_records()
        self.assertEqual({r.season for r in rows},{f'{year}-{str(year+1)[-2:]}' for year in range(2010,2026)})
        for season in ('2010-11','2011-12'):
            teams={r.team for r in load_records([season])}
            self.assertIn('NJN',teams)
            self.assertIn('NOH',teams)
            self.assertNotIn('BKN',teams)
            self.assertNotIn('NOP',teams)
        yi=next(r for r in load_records(['2010-11']) if r.player_id==201146)
        self.assertEqual((yi.team,yi.gp),('WAS',63))
