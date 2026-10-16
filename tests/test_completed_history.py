"""Check historical promotion against preserved stats and official jersey evidence."""
import hashlib
import json
import unittest
from pathlib import Path
from nba_roulette.data import ROOT, load_records


class CompletedHistoryTests(unittest.TestCase):
    def test_promoted_stats_are_unchanged_and_all_jerseys_have_final_game_evidence(self):
        for season, count in [('2022-23',305),('2021-22',317),('2020-21',307),('2019-20',298),('2018-19',307),('2017-18',303),('2016-17',310),('2015-16',293),('2014-15',314),('2013-14',291),('2012-13',289),('2011-12',276),('2010-11',287),('2009-10',273),('2008-09',274),('2007-08',271),('2006-07',286),('2005-06',275),('2004-05',283),('2003-04',260),('2002-03',265),('2001-02',268),('2000-01',267),('1999-00',266),('1998-99',234),('1997-98',269),('1996-97',254),('1995-96',258),('1994-95',250),('1993-94',246),('1992-93',247),('1991-92',239),('1990-91',235),('1989-90',231),('1988-89',225),('1987-88',202),('1986-87',208),('1985-86',211),('1984-85',204),('1983-84',199)]:
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
                identity=evidence[(row['team'],row['player_id'])].get('identity_resolution')
                self.assertEqual(int(official['personId']),identity['legacy_player_id'] if identity else row['player_id'])
                if identity:self.assertEqual(identity['canonical_player_id'],row['player_id'])
                resolution=evidence[(row['team'],row['player_id'])].get('jersey_resolution')
                if resolution:
                    self.assertEqual(official['jerseyNum'], resolution['original_nba_jersey'])
                    self.assertEqual(row['jersey'], resolution['resolved_jersey'])
                    self.assertEqual((season,row['team'],row['player_id']), (resolution['season'],resolution['team'],resolution['player_id']))
                else:
                    self.assertEqual(int(official['jerseyNum']),row['jersey'])
                    self.assertEqual(str(official['jerseyNum']),row['jersey_display'])
                self.assertEqual(official['played'],'1')
            self.assertEqual(len({r['player_id'] for r in rows if r['all_nba'] is not None}),10 if int(season[:4])<1988 else 15)
            self.assertEqual(len({r['player_id'] for r in rows if r['all_defense'] is not None}),11 if season in ('2012-13','2005-06','2004-05','1998-99','1987-88') else 10)
            for award in ('mvp','dpoy','roy'):
                self.assertEqual(sum(r[award] for r in rows),2 if award == 'roy' and season in ('1999-00','1994-95') else 1)

    def test_championship_credit_requires_title_roster_and_team_stint(self):
        for season in ('2022-23','2021-22','2020-21','2019-20','2018-19','2017-18','2016-17','2015-16','2014-15','2013-14','2012-13','2011-12','2010-11','2009-10','2008-09','2007-08','2006-07','2005-06','2004-05','2003-04','2002-03','2001-02','2000-01','1999-00','1998-99','1997-98','1996-97','1995-96','1994-95','1993-94','1992-93','1991-92','1990-91','1989-90','1988-89','1987-88','1986-87','1985-86','1984-85','1983-84'):
            slug=season.replace('-','_')
            audit=json.loads((ROOT/f'data/processed/completion_{slug}.json').read_text(encoding='utf-8'))
            members={int(p['personId']) for p in audit['champion_roster']}
            for r in load_records([season]):
                self.assertEqual(r.champion,r.team==audit['champion_team'] and r.player_id in members)
        bones=next(r for r in load_records(['2022-23']) if r.player_id==1630538 and r.team=='DEN')
        self.assertFalse(bones.champion)

    def test_loading_all_forty_six_seasons_has_no_duplicate_entries(self):
        rows=load_records()
        self.assertEqual(len(rows),12169)
        self.assertEqual(len({(r.season,r.team,r.player_id) for r in rows}),12169)
        self.assertEqual(len({(r.season,r.team) for r in rows}),1292)

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
        for season, count in [('2017-18',303),('2016-17',310),('2015-16',293),('2014-15',314),('2013-14',291),('2012-13',289),('2011-12',276),('2010-11',287),('2009-10',273),('2008-09',274),('2007-08',271),('2006-07',286),('2005-06',275),('2004-05',283),('2003-04',260),('2002-03',265),('2001-02',268),('2000-01',267),('1999-00',266),('1998-99',234),('1997-98',269),('1996-97',254),('1995-96',258),('1994-95',250),('1993-94',246),('1992-93',247),('1991-92',239),('1990-91',235),('1989-90',231)]:
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
            self.assertEqual(report['regular_season_games'],{'2012-13':1229,'2011-12':990,'2003-04':1189,'2002-03':1189,'2001-02':1189,'2000-01':1189,'1999-00':1189,'1998-99':725,'1997-98':1189,'1996-97':1189,'1995-96':1189,'1994-95':1107,'1993-94':1107,'1992-93':1107,'1991-92':1107,'1990-91':1107,'1989-90':1107}.get(season,1230))
            counts=report['schedule_evidence']['team_games']
            self.assertEqual(counts,{team:50 if season=='1998-99' else 66 if season=='2011-12' else 81 if season=='2012-13' and team in ('BOS','IND') else 82 for team in counts})

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
        rows=load_records(f'{year}-{str(year+1)[-2:]}' for year in range(2010,2026))
        self.assertEqual({r.season for r in rows},{f'{year}-{str(year+1)[-2:]}' for year in range(2010,2026)})
        for season in ('2010-11','2011-12'):
            teams={r.team for r in load_records([season])}
            self.assertIn('NJN',teams)
            self.assertIn('NOH',teams)
            self.assertNotIn('BKN',teams)
            self.assertNotIn('NOP',teams)
        yi=next(r for r in load_records(['2010-11']) if r.player_id==201146)
        self.assertEqual((yi.team,yi.gp),('WAS',63))

    def test_recovered_sonics_and_thunder_are_scoped_to_their_actual_seasons(self):
        from nba_roulette.models import Lock
        from nba_roulette.roulette import RouletteEngine
        rows=load_records()
        seattle=next(r for r in rows if r.season=='2007-08' and r.team=='SEA')
        self.assertNotIn('OKC', {r.team for r in load_records(['2007-08'])})
        self.assertNotIn('SEA', {r.team for r in load_records(['2008-09','2009-10'])})
        outcomes=RouletteEngine(rows).valid_outcomes(seattle, (Lock.TEAM,))
        self.assertTrue(outcomes)
        self.assertEqual({r.season for r in outcomes}, {f'{year}-{str(year+1)[-2:]}' for year in range(1980,2007)})
        self.assertEqual({r.team for r in outcomes}, {'SEA'})

    def test_recovered_traded_champions_receive_credit_only_for_title_team(self):
        rows=load_records(['2007-08'])
        cassell={r.team:r for r in rows if r.player_id==208}
        self.assertEqual(set(cassell), {'LAC'})
        self.assertFalse(cassell['LAC'].champion)
        yao=next(r for r in load_records(['2008-09']) if r.player_id==2397)
        self.assertEqual(yao.player, 'Yao Ming')

    def test_recovered_all_defense_ties_preserve_both_players(self):
        for season, tier, ids in [('2005-06',1,{977,467}),('2004-05',2,{467,2548})]:
            rows=load_records([season])
            defense=[r for r in rows if r.all_defense is not None]
            self.assertEqual(len({r.player_id for r in defense}),11)
            self.assertEqual(sum(r.all_defense==tier for r in defense),6)
            self.assertEqual({r.player_id for r in defense if r.player_id in ids},ids)
            self.assertTrue(all(r.all_defense==tier for r in defense if r.player_id in ids))

    def test_recovered_davis_photo_resolves_exact_last_game_and_preserves_nba_blank(self):
        audit=json.loads((ROOT/'data/processed/completion_2005_06.json').read_text(encoding="utf-8"))
        evidence=next(r for r in audit['jersey_evidence'] if r['player_id']==213 and r['team']=='NYK')
        proof=evidence['jersey_resolution']
        self.assertEqual((evidence['game_id'],evidence['last_game_date']),('0020500658','2006-01-31'))
        self.assertEqual(evidence['official_box_score_player']['jerseyNum'],'')
        self.assertEqual(evidence['jersey'],32)
        self.assertEqual(proof['status'],'VERIFIED_FINAL_GAME_PHOTO')
        self.assertEqual(proof['credit'],'AP Photo / Frank Franklin II')
        self.assertEqual(len(proof['photo_sha256']),64)
        self.assertIn('image541809150',proof['photo_page'])

    def test_recovered_jacobsen_minutes_match_official_stint_totals(self):
        proof=json.loads((ROOT/'data/staging/stats_2004_05_jacobsen_official_resolution.json').read_text(encoding="utf-8"))
        official=proof['official_row']
        self.assertEqual((official['PLAYER_ID'],official['SEASON_ID'],official['TEAM_ABBREVIATION'],official['GP'],official['MIN']),(2418,'2004-05','NOH',44,1037))
        row=next(r for r in load_records(['2004-05']) if r.player_id==2418 and r.team=='NOH')
        self.assertEqual(row.mpg,23.6)
        report=json.loads((ROOT/'data/staging/stats_2004_05_verification.json').read_text(encoding="utf-8"))
        resolution=next(r for r in report['resolved_differences'] if r['player_id']==2418 and r['field']=='mpg')
        self.assertEqual(resolution['official_total_evidence'],official)
        self.assertEqual(resolution['reference'],23.4)

    def test_recovered_new_orleans_codes_and_smith_identity(self):
        for season in ('2005-06','2006-07'):
            teams={r.team for r in load_records([season])}
            self.assertIn('NOK',teams)
            self.assertNotIn('NOH',teams)
        rows=load_records(['2004-05'])
        self.assertIn('NOH',{r.team for r in rows})
        smith=next(r for r in rows if r.player_id==120)
        self.assertEqual(smith.player,'Steve Smith')

    def test_recovered_pre_bobcats_schedules_and_franchises(self):
        for season in ('2003-04','2002-03','2001-02','2000-01','1999-00','1998-99','1997-98','1996-97','1995-96','1994-95','1993-94','1992-93','1991-92','1990-91','1989-90','1988-89','1987-88','1986-87','1985-86','1984-85','1983-84'):
            slug=season.replace('-','_')
            report=json.loads((ROOT/f'data/staging/stats_{slug}_verification.json').read_text(encoding="utf-8"))
            self.assertTrue(report['passed'] and report['schedule_evidence']['matches'])
            self.assertEqual(report['regular_season_games'],725 if season == '1998-99' else 943 if int(season[:4])<1988 else 1025 if int(season[:4])==1988 else 1107 if int(season[:4])<1995 else 1189)
            self.assertEqual(len(report['schedule_evidence']['team_games']),23 if int(season[:4])<1988 else 25 if int(season[:4])==1988 else 27 if int(season[:4])<1995 else 29)
            self.assertEqual(set(report['schedule_evidence']['team_games'].values()),{50 if season == '1998-99' else 82})
            self.assertNotIn('CHA',{r.team for r in load_records([season])})
        self.assertIn('CHH',{r.team for r in load_records(['2001-02'])})
        self.assertIn('NOH',{r.team for r in load_records(['2002-03'])})

    def test_recovered_ratliff_defense_credit_is_preserved_for_both_stints(self):
        rows=[r for r in load_records(['2003-04']) if r.player=='Theo Ratliff']
        self.assertEqual({r.team for r in rows},{'ATL','POR'})
        self.assertTrue(all(r.all_defense==2 for r in rows))
        defense=[r for r in load_records(['2003-04']) if r.all_defense is not None]
        self.assertEqual(len(defense),11)
        self.assertEqual(len({r.player_id for r in defense}),10)

    def test_recovered_crotty_jersey_uses_2001_02_register_entry(self):
        row=next(r for r in load_records(['2001-02']) if r.player_id==180 and r.team=='UTA')
        self.assertEqual(row.jersey,25)
        audit=json.loads((ROOT/'data/processed/completion_2001_02.json').read_text(encoding="utf-8"))
        evidence=next(r for r in audit['jersey_evidence'] if r['player_id']==180 and r['team']=='UTA')
        self.assertEqual(evidence['official_box_score_player']['jerseyNum'],'')
        self.assertEqual((evidence['game_id'],evidence['last_game_date']),('0020101135','2002-04-11'))
        self.assertIn('2001-02',evidence['jersey_resolution']['uniform_register_entry'])
        self.assertEqual(evidence['jersey_resolution']['pdf_page'],361)

    def test_recovered_lenard_rate_and_whole_minute_source_provenance(self):
        row=next(r for r in load_records(['2001-02']) if r.player_id==702 and r.team=='DEN')
        self.assertEqual((row.gp,row.mpg),(71,23.3))
        proof=json.loads((ROOT/'data/staging/stats_2001_02_702_official_resolution.json').read_text(encoding="utf-8"))
        self.assertEqual((proof['official_row']['GP'],proof['official_row']['MIN']),(71,1656))
        manifest=json.loads((ROOT/'data/staging/stats_2003_04_manifest.json').read_text(encoding="utf-8"))
        self.assertEqual(len(manifest['whole_minute_source_rows']),23)
        self.assertEqual({r['game_id'] for r in manifest['whole_minute_source_rows']},{'0020300778'})
        from scripts.collect_historical_stats import source_seconds
        self.assertEqual(source_seconds('26'),1560)
        self.assertEqual(source_seconds('26:36'),1596)

    def test_1998_lockout_keeps_fixed_cutoff_and_defense_tie(self):
        rows=load_records(['1998-99'])
        self.assertEqual(len(rows),234)
        self.assertTrue(all(30 <= r.gp <= 50 for r in rows))
        report=json.loads((ROOT/'data/staging/stats_1998_99_verification.json').read_text(encoding="utf-8"))
        self.assertEqual(report['regular_season_games'],725)
        self.assertEqual(len(report['schedule_evidence']['team_games']),29)
        self.assertEqual(set(report['schedule_evidence']['team_games'].values()),{50})
        defense=[r for r in rows if r.all_defense is not None]
        self.assertEqual(len({r.player_id for r in defense}),11)
        self.assertEqual(sum(r.all_defense==1 for r in defense),6)
        self.assertTrue(all(r.all_defense==1 for r in defense if r.player in ('Karl Malone','Scottie Pippen')))
        self.assertEqual({r.player for r in defense if r.player in ('Karl Malone','Scottie Pippen')},{'Karl Malone','Scottie Pippen'})

    def test_1999_co_rookies_are_both_preserved(self):
        rows=load_records(['1999-00'])
        self.assertEqual({r.player for r in rows if r.roy},{'Elton Brand','Steve Francis'})
        self.assertEqual(sum(r.mvp for r in rows),1)
        self.assertEqual(sum(r.dpoy for r in rows),1)

    def test_fortson_missing_appearance_is_exact_and_totals_match(self):
        manifest=json.loads((ROOT/'data/staging/stats_1999_00_manifest.json').read_text(encoding="utf-8"))
        proof=manifest['source_corrections']['missing_appearances'][0]
        self.assertEqual((proof['player_id'],proof['team'],proof['official_row']['GAME_ID']),(1504,'BOS','0029900712'))
        self.assertEqual(proof['official_row']['GAME_DATE'],'Feb 15, 2000')
        self.assertEqual(proof['original_response_row']['Game_ID'],proof['official_row']['GAME_ID'])
        row=next(r for r in load_records(['1999-00']) if r.player_id==1504 and r.team=='BOS')
        self.assertEqual((row.gp,row.ppg),(55,7.6))
        self.assertEqual(row.gp,proof['official_season_row']['GP'])

    def test_rate_overrides_keep_source_eligibility_and_primary_totals(self):
        for season,pid,team,expected,gp,minutes in [('1999-00',682,'CLE',30.4,73,2216),('1998-99',432,'VAN',15.2,46,697)]:
            slug=season.replace('-','_')
            manifest=json.loads((ROOT/f'data/staging/stats_{slug}_manifest.json').read_text(encoding="utf-8"))
            proof=next(r for r in manifest['display_rate_overrides'] if r['player_id']==pid and r['team']==team)
            self.assertGreaterEqual(proof['source_unrounded_mpg'],15)
            self.assertEqual(proof['source_gp'],gp)
            self.assertEqual(proof['official_evidence']['official_row']['MIN'],minutes)
            self.assertEqual(proof['official_display_mpg'],expected)
            row=next(r for r in load_records([season]) if r.player_id==pid and r.team==team)
            self.assertEqual((row.gp,row.mpg),(gp,expected))

    def test_cutoff_proofs_exclude_only_the_verified_team_stints(self):
        for season,count in [('2000-01',3),('1999-00',1)]:
            slug=season.replace('-','_')
            proofs=json.loads((ROOT/f'data/staging/stats_{slug}_cutoff_resolutions.json').read_text(encoding="utf-8"))
            self.assertEqual(len(proofs),count)
            actual={(r.player_id,r.team) for r in load_records([season])}
            for p in proofs:
                self.assertEqual(p['official_row']['GP'],p['gp'])
                self.assertLess(p['source_seconds'],900*p['gp'])
                self.assertLess(p['official_row']['MIN'],15*p['gp'])
                self.assertNotIn((p['player_id'],p['team']),actual)

    def test_legacy_title_ids_and_lakers_jersey_photos_are_audited(self):
        for season,gid in [('2000-01','0040000087'),('1999-00','0049900088'),('1998-99','0049800087')]:
            slug=season.replace('-','_')
            audit=json.loads((ROOT/f'data/processed/completion_{slug}.json').read_text(encoding="utf-8"))
            proof=audit['title_game_verification']
            self.assertEqual(proof['game_id'],gid)
            self.assertEqual(proof['champion_team'],audit['champion_team'])
            self.assertEqual(len(proof['official_final_game_rows']),2)
        audit=json.loads((ROOT/'data/processed/completion_2000_01.json').read_text(encoding="utf-8"))
        rows={r.player_id:r for r in load_records(['2000-01']) if r.team=='LAL'}
        for pid,jersey in [(375,7),(2130,12)]:
            e=next(e for e in audit['jersey_evidence'] if e['player_id']==pid and e['team']=='LAL')
            self.assertEqual(e['official_box_score_player']['jerseyNum'],'')
            self.assertEqual(e['jersey_resolution']['status'],'VERIFIED_OFFICIAL_SEASON_PHOTO')
            self.assertEqual(rows[pid].jersey,jersey)
            self.assertFalse(rows[pid].champion)

    def test_bullets_identity_and_composite_jersey_resolution(self):
        rows=load_records(['1996-97','1995-96'])
        self.assertIn('WSB',{r.team for r in rows})
        self.assertNotIn('WAS',{r.team for r in rows})
        self.assertIn('WAS',{r.team for r in load_records(['1997-98'])})
        audit=json.loads((ROOT/'data/processed/completion_1996_97.json').read_text(encoding="utf-8"))
        e=next(e for e in audit['jersey_evidence'] if e['player_id']==694 and e['team']=='HOU')
        self.assertEqual(e['official_box_score_player']['jerseyNum'],'2-5')
        self.assertEqual(e['jersey'],5)
        self.assertEqual(e['jersey_resolution']['pdf_page'],174)

    def test_1995_legacy_ids_preserve_missing_rebounds_and_primary_evidence(self):
        manifest=json.loads((ROOT/'data/staging/stats_1995_96_manifest.json').read_text(encoding="utf-8"))
        self.assertEqual(manifest['primary_player_appearances'],23744)
        proofs=json.loads((ROOT/'data/staging/player_identity_1995_96_resolutions.json').read_text(encoding="utf-8"))
        self.assertEqual({(p['legacy_player_id'],p['canonical_player_id']) for p in proofs},{(78412,919),(77741,709)})
        for p in proofs:
            self.assertTrue({'GP','MIN','PTS','AST','STL','BLK'} <= set(p['matched_fields']))
            for field in p['matched_fields']:self.assertEqual(p['legacy_aggregate'][field],p['canonical_official_row'][field])
        ed=next(p for p in proofs if p['canonical_player_id']==709)
        self.assertIsNone(ed['legacy_aggregate']['REB'])
        self.assertNotIn('REB',ed['matched_fields'])
        corrections=manifest['source_corrections']
        self.assertEqual(len(corrections['missing_appearances']),144)
        ed_games=[p for p in corrections['missing_appearances'] if p['player_id']==709]
        self.assertEqual(len(ed_games),64)
        self.assertTrue(all(p['official_row']['REB'] is None and p['official_row']['DREB'] is None for p in ed_games))
        self.assertEqual(corrections['stat_total_overrides'][0]['official_row']['REB'],168)
        rows={r.player_id:r for r in load_records(['1995-96'])}
        self.assertEqual((rows[709].gp,rows[709].rpg,rows[709].jersey),(64,2.6,31))
        self.assertEqual((rows[919].gp,rows[919].jersey),(80,35))
        audit=json.loads((ROOT/'data/processed/completion_1995_96.json').read_text(encoding="utf-8"))
        for pid,legacy in [(919,78412),(709,77741)]:
            e=next(e for e in audit['jersey_evidence'] if e['player_id']==pid)
            self.assertEqual(e['official_box_score_player']['personId'],legacy)
            self.assertEqual(e['identity_resolution']['canonical_player_id'],pid)

    def test_1996_regular_season_cutoffs_and_new_title_sources(self):
        proofs=json.loads((ROOT/'data/staging/stats_1996_97_cutoff_resolutions.json').read_text(encoding="utf-8"))
        rows={(r.player_id,r.team) for r in load_records(['1996-97'])}
        self.assertEqual({p['player_id']:p['gp'] for p in proofs},{692:71,713:55})
        for p in proofs:
            self.assertLess(p['source_seconds'],900*p['gp'])
            self.assertLess(p['official_row']['MIN'],15*p['gp'])
            self.assertNotIn((p['player_id'],p['team']),rows)
        for season,gid in [('1997-98','0049700088'),('1996-97','0049600088'),('1995-96','0049500068')]:
            audit=json.loads((ROOT/f'data/processed/completion_{season.replace("-","_")}.json').read_text(encoding="utf-8"))
            proof=audit['title_game_verification']
            self.assertEqual((proof['game_id'],proof['champion_team']),(gid,'CHI'))
            self.assertEqual(len(proof['official_final_game_rows']),2)

    def test_1994_conflicting_game_logs_preserve_season_totals_and_observed_gp(self):
        manifest=json.loads((ROOT/'data/staging/stats_1994_95_manifest.json').read_text(encoding="utf-8"))
        audit=json.loads((ROOT/'data/processed/completion_1994_95.json').read_text(encoding="utf-8"))
        rows={(r.player_id,r.team):r for r in load_records(['1994-95'])}
        for pid,team,observed,official in [(324,'LAL',74,73),(76726,'NJN',47,48)]:
            p=next(p for p in manifest['season_total_overrides'] if p['player_id']==pid)
            e=next(e for e in audit['jersey_evidence'] if e['player_id']==pid and e['team']==team)
            self.assertEqual(p['source_aggregate']['gp'],observed)
            self.assertEqual(p['official_row']['GP'],official)
            self.assertEqual(rows[(pid,team)].gp,official)
            self.assertEqual(e['observed_appearance_count'],observed)
            self.assertEqual(e['season_total_resolution'],p)
            self.assertGreaterEqual(p['source_aggregate']['seconds'],900*observed)
            self.assertGreaterEqual(p['official_row']['MIN'],15*official)

    def test_1992_counting_stat_resolutions_retain_original_totals(self):
        from decimal import Decimal, ROUND_HALF_UP
        manifest=json.loads((ROOT/'data/staging/stats_1992_93_manifest.json').read_text(encoding="utf-8"))
        proofs=manifest['season_total_overrides']
        self.assertEqual(len(proofs),8)
        rows={(r.player_id,r.team):r for r in load_records(['1992-93'])}
        fields=[('points','PTS','ppg'),('rebounds_total','REB','rpg'),('assists','AST','apg'),('steals','STL','spg'),('blocks','BLK','bpg')]
        for p in proofs:
            official=p['official_row'];source=p['source_aggregate'];r=rows[(p['player_id'],p['team'])]
            self.assertEqual(source['gp'],official['GP'])
            self.assertTrue(any(source[f] != official[c] for f,c,_ in fields))
            for _,column,field in fields:
                expected=float((Decimal(official[column])/Decimal(official['GP'])).quantize(Decimal('.1'),rounding=ROUND_HALF_UP))
                self.assertEqual(getattr(r,field),expected)

    def test_1994_traded_all_nba_stints_and_co_rookies_are_preserved(self):
        rows=load_records(['1994-95']);clyde={r.team:r for r in rows if r.player_id==17}
        self.assertEqual(set(clyde),{'POR','HOU'})
        self.assertTrue(all(r.all_nba==3 for r in clyde.values()))
        self.assertFalse(clyde['POR'].champion)
        self.assertTrue(clyde['HOU'].champion)
        self.assertEqual({r.player for r in rows if r.roy},{'Grant Hill','Jason Kidd'})
        self.assertEqual(sum(r.all_nba is not None for r in rows),16)
        self.assertEqual(len({r.player_id for r in rows if r.all_nba is not None}),15)

    def test_historical_registers_are_not_labelled_as_official_box_numbers(self):
        for season,expected in [('1994-95',8),('1993-94',6),('1992-93',5)]:
            audit=json.loads((ROOT/f'data/processed/completion_{season.replace("-","_")}.json').read_text(encoding="utf-8"))
            resolved=[e for e in audit['jersey_evidence'] if e['jersey_resolution']]
            self.assertEqual(len(resolved),expected)
            for e in resolved:
                p=e['jersey_resolution']
                self.assertEqual(e['official_box_score_player']['jerseyNum'],p['original_nba_jersey'])
                self.assertEqual(e['jersey'],p['resolved_jersey'])
                if p['status']=='VERIFIED_HISTORICAL_SEASON_REGISTER':
                    self.assertEqual(p['source'],'https://apbr.org/nmbr9000.html')
                    self.assertEqual(p['source_format'],'original_html')
                    self.assertIn(str(p['resolved_jersey'])+' '+p['player'],p['uniform_register_entry'])

    def test_1991_and_1989_stat_discrepancies_preserve_both_totals(self):
        cases=[('1991-92',76017,'POR','blocks',12,'BLK',13,'bpg',0.2),
               ('1989-90',165,'HOU','assists',232,'AST',234,'apg',2.9),
               ('1989-90',137,'HOU','seconds',51900,'MIN',869,'mpg',29.0)]
        for season,pid,team,source_field,original,official_field,total,rate,expected in cases:
            manifest=json.loads((ROOT/f'data/staging/stats_{season.replace("-","_")}_manifest.json').read_text(encoding="utf-8"))
            proof=next(p for p in manifest['season_total_overrides'] if p['player_id']==pid)
            self.assertEqual(proof['source_aggregate'][source_field],original)
            self.assertEqual(proof['official_row'][official_field],total)
            row=next(r for r in load_records([season]) if r.player_id==pid and r.team==team)
            self.assertEqual(getattr(row,rate),expected)

    def test_1991_and_1990_vaught_recovery_matches_canonical_totals(self):
        for season,gp in [('1991-92',79),('1990-91',73)]:
            proofs=json.loads((ROOT/f'data/staging/player_identity_{season.replace("-","_")}_resolutions.json').read_text(encoding="utf-8"))
            p=next(p for p in proofs if p['canonical_player_id']==919)
            self.assertEqual(p['legacy_player_id'],78412)
            self.assertEqual(set(p['matched_fields']),{'GP','MIN','PTS','REB','AST','STL','BLK'})
            for field in p['matched_fields']:self.assertEqual(p['legacy_aggregate'][field],p['canonical_official_row'][field])
            row=next(r for r in load_records([season]) if r.player_id==919)
            self.assertEqual((row.team,row.gp,row.jersey),('LAC',gp,35))

    def test_composite_jerseys_use_specific_evidence_and_preserve_originals(self):
        for season,pid,team,jersey,original in [('1991-92',428,'BOS',20,'4-20'),('1991-92',77167,'SAS',25,'15-25'),('1991-92',78615,'DET',0,'0-6'),('1994-95',182,'MIA',32,'30-32'),('1994-95',943,'GSW',9,'9-33')]:
            audit=json.loads((ROOT/f'data/processed/completion_{season.replace("-","_")}.json').read_text(encoding="utf-8"))
            e=next(e for e in audit['jersey_evidence'] if e['player_id']==pid and e['team']==team)
            self.assertEqual(e['jersey'],jersey)
            self.assertEqual(e['official_box_score_player']['jerseyNum'],original)
            self.assertNotEqual(e['jersey_resolution']['status'],'VERIFIED_HISTORICAL_SEASON_REGISTER')
        row=next(r for r in load_records(['1990-91']) if r.player_id==698 and r.team=='SEA')
        self.assertEqual(row.jersey,22)
        proof=json.loads((ROOT/'data/staging/jersey_1994_95_182_MIA_resolution.json').read_text(encoding="utf-8"))
        self.assertIn('1994-95',proof['uniform_register_entry'])
        self.assertEqual(proof['superseded_resolution']['resolved_jersey'],30)

    def test_1989_through_1991_title_games_match_official_schedules(self):
        for season,gid,team in [('1991-92','0049100073','CHI'),('1990-91','0049000068','CHI'),('1989-90','0048900072','DET')]:
            audit=json.loads((ROOT/f'data/processed/completion_{season.replace("-","_")}.json').read_text(encoding="utf-8"))
            self.assertEqual(audit['title_game_verification']['game_id'],gid)
            self.assertEqual(audit['champion_team'],team)
            self.assertEqual(len(audit['title_game_verification']['official_final_game_rows']),2)

    def test_1980s_reference_archive_preserves_totals_and_same_name_players(self):
        hashes=set()
        for season,count,games,teams in [('1988-89',225,1025,25),('1987-88',202,943,23),('1986-87',208,943,23)]:
            report=json.loads((ROOT/f'data/staging/stats_{season.replace("-","_")}_verification.json').read_text(encoding="utf-8"))
            self.assertTrue(report['passed'] and report['eligibility_sets_match'])
            self.assertEqual(report['stat_comparisons'],7*count)
            self.assertEqual(report['regular_season_games'],games)
            self.assertEqual(len(report['schedule_evidence']['team_games']),teams)
            self.assertEqual(set(report['schedule_evidence']['team_games'].values()),{82})
            self.assertIn('99fb55e641c7009ae729e502ebdade8c6ecb2b7f',report['reference']['url'])
            hashes.add(report['reference_archive_sha256'])
            self.assertTrue(all(len(e['original_reference_totals'])==6 for e in report['reference_evidence']))
        self.assertEqual(len(hashes),1)
        self.assertEqual(len(next(iter(hashes))),64)
        report=json.loads((ROOT/'data/staging/stats_1988_89_verification.json').read_text(encoding="utf-8"))
        evidence={p['player_id']:p for p in report['reference_identity_evidence']}
        self.assertEqual((evidence[279]['official_row']['GP'],evidence[77178]['official_row']['GP']),(53,43))
        rows={r.player_id:r for r in load_records(['1988-89']) if r.team=='WSB'}
        self.assertIn(279,rows)
        self.assertNotIn(77178,rows)
        self.assertEqual(report['reference_identity_resolutions'][0]['original_age'],'27')

    def test_1980s_official_total_overrides_retain_nullable_and_conflicting_logs(self):
        from decimal import Decimal, ROUND_HALF_UP
        for season,count in [('1988-89',4),('1987-88',5),('1986-87',25)]:
            manifest=json.loads((ROOT/f'data/staging/stats_{season.replace("-","_")}_manifest.json').read_text(encoding="utf-8"))
            self.assertEqual(len(manifest['season_total_overrides']),count)
            rows={(r.player_id,r.team):r for r in load_records([season])}
            for p in manifest['season_total_overrides']:
                official=p['official_row'];r=rows[(p['player_id'],p['team'])]
                self.assertGreaterEqual(p['source_aggregate']['seconds'],900*p['source_aggregate']['gp'])
                self.assertGreaterEqual(official['MIN'],15*official['GP'])
                self.assertEqual(r.gp,official['GP'])
                for field,col in [('mpg','MIN'),('ppg','PTS'),('rpg','REB'),('apg','AST'),('spg','STL'),('bpg','BLK')]:
                    expected=float((Decimal(official[col])/Decimal(official['GP'])).quantize(Decimal('.1'),rounding=ROUND_HALF_UP))
                    self.assertEqual(getattr(r,field),expected)
        manifest=json.loads((ROOT/'data/staging/stats_1986_87_manifest.json').read_text(encoding="utf-8"))
        for pid in (9,76993):
            p=next(p for p in manifest['season_total_overrides'] if p['player_id']==pid)
            self.assertIsNone(p['source_aggregate']['rebounds_total'])
            self.assertIsNone(p['source_aggregate']['assists'])
            self.assertEqual(p['source_aggregate']['gp'],p['official_row']['GP']+1)
        report=json.loads((ROOT/'data/staging/stats_1987_88_verification.json').read_text(encoding="utf-8"))
        p=next(p for p in report['resolved_differences'] if p['player_id']==77626)
        self.assertEqual((p['official_total_evidence']['BLK'],p['independent_total'],p['staged'],p['reference']),(12,14,0.2,0.3))

    def test_1987_defense_tie_and_two_team_all_nba_preserve_actual_honors(self):
        for season in ['1987-88','1986-87']:
            rows=load_records([season]);nba=[r for r in rows if r.all_nba is not None]
            self.assertEqual(len({r.player_id for r in nba}),10)
            self.assertEqual({r.all_nba for r in nba},{1,2})
        rows=load_records(['1987-88']);defense=[r for r in rows if r.all_defense is not None]
        self.assertEqual(len({r.player_id for r in defense}),11)
        self.assertEqual(sum(r.all_defense==2 for r in defense),6)
        self.assertTrue(all(r.all_defense==2 for r in defense if r.player in ('Mark Eaton','Patrick Ewing')))
        lever=next(r for r in rows if r.player_id==77376)
        self.assertEqual(lever.all_defense,2)
        report=json.loads((ROOT/'data/staging/stats_1987_88_verification.json').read_text(encoding="utf-8"))
        cutoff=next(p for p in report['cutoff_boundary_resolutions'] if p['player']=='Dallas Comegys')
        self.assertEqual((cutoff['gp'],cutoff['seconds']),(75,67320))
        self.assertNotIn('Dallas Comegys',{r.player for r in rows})

    def test_1986_henderson_final_appearance_uses_individual_log_proof(self):
        audit=json.loads((ROOT/'data/processed/completion_1986_87.json').read_text(encoding="utf-8"))
        e=next(e for e in audit['jersey_evidence'] if e['player_id']==76993 and e['team']=='NYK')
        proof=e['final_appearance_resolution']
        self.assertEqual((e['last_game_date'],e['game_id']),('1987-04-17','0028600925'))
        self.assertEqual((proof['game_date'],proof['game_id']),(e['last_game_date'],e['game_id']))
        self.assertEqual((e['observed_appearance_count'],proof['official_row']['GP']),(69,68))
        self.assertEqual(len(proof['official_stint_game_log_rows']),69)
        self.assertIn('playergamelog?',proof['source'])

    def test_1980s_expansion_and_title_game_proofs_are_scoped(self):
        for season,gid,team in [('1988-89','0048800062','DET'),('1987-88','0048700080','LAL'),('1986-87','0048600071','LAL')]:
            audit=json.loads((ROOT/f'data/processed/completion_{season.replace("-","_")}.json').read_text(encoding="utf-8"))
            self.assertEqual(audit['title_game_verification']['game_id'],gid)
            self.assertEqual(audit['champion_team'],team)
            teams={r.team for r in load_records([season])}
            self.assertEqual({'MIA','CHH'}.intersection(teams),{'MIA','CHH'} if season=='1988-89' else set())
            self.assertFalse({'MIN','ORL','VAN','TOR'}.intersection(teams))
            self.assertIn('WSB',teams)
            self.assertNotIn('WAS',teams)
        row=next(r for r in load_records(['1987-88']) if r.player_id==901 and r.team=='SAC')
        self.assertEqual(row.jersey,33)

    def test_1983_through_1985_schedule_honors_and_title_proofs(self):
        for season,count,gid,champion in [('1985-86',211,'0048500406','BOS'),('1984-85',204,'0048400406','LAL'),('1983-84',199,'0048300079','BOS')]:
            slug=season.replace('-','_');report=json.loads((ROOT/f'data/staging/stats_{slug}_verification.json').read_text(encoding="utf-8"));audit=json.loads((ROOT/f'data/processed/completion_{slug}.json').read_text(encoding="utf-8"))
            self.assertTrue(report['passed'] and report['eligibility_sets_match'])
            self.assertEqual(report['stat_comparisons'],7*count)
            self.assertEqual(report['regular_season_games'],943)
            self.assertEqual(len(report['schedule_evidence']['team_games']),23)
            self.assertEqual(set(report['schedule_evidence']['team_games'].values()),{82})
            self.assertEqual((audit['title_game_verification']['game_id'],audit['champion_team']),(gid,champion))
            rows=load_records([season])
            self.assertEqual(len({r.player_id for r in rows if r.all_nba}),10)
            self.assertEqual({r.all_nba for r in rows if r.all_nba},{1,2})
            self.assertEqual(len({r.player_id for r in rows if r.all_defense}),10)
        audit=json.loads((ROOT/'data/processed/completion_1984_85.json').read_text(encoding="utf-8"))
        self.assertEqual(audit['honors_key_aliases']['benard-king'],'bernard-king')
        king=next(r for r in load_records(['1984-85']) if r.player_id==77264)
        self.assertEqual(king.all_nba,1)

    def test_kansas_city_and_san_diego_boundaries_and_keeps(self):
        from scripts.collect_historical_stats import historical_team
        from nba_roulette.roulette import RouletteEngine
        from nba_roulette.models import Lock
        self.assertEqual(historical_team('1984-85','SAC'),'KCK')
        self.assertEqual(historical_team('1985-86','SAC'),'SAC')
        self.assertEqual(historical_team('1983-84','LAC'),'SDC')
        self.assertEqual(historical_team('1984-85','LAC'),'LAC')
        for season in ['1983-84','1984-85','1985-86']:
            teams={r.team for r in load_records([season])}
            self.assertEqual('KCK' in teams,season!='1985-86')
            self.assertEqual('SDC' in teams,season=='1983-84')
        rows=load_records();anchor=next(r for r in rows if r.season=='1984-85' and r.team=='KCK')
        outcomes=RouletteEngine(rows).valid_outcomes(anchor,(Lock.TEAM,))
        self.assertEqual({r.season for r in outcomes},{'1980-81','1981-82','1982-83','1983-84'})
        self.assertEqual({r.team for r in outcomes},{'KCK'})

    def test_1984_incomplete_minute_coverage_uses_two_sources_for_eligibility(self):
        manifest=json.loads((ROOT/'data/staging/stats_1984_85_manifest.json').read_text(encoding="utf-8"));report=json.loads((ROOT/'data/staging/stats_1984_85_verification.json').read_text(encoding="utf-8"));rows={(r.player_id,r.team):r for r in load_records(['1984-85'])}
        proofs=manifest['eligibility_source_overrides'];self.assertEqual(len(proofs),3)
        for p in proofs:
            official=p['official_row'];ref=p['independent_reference_row'];key=(p['player_id'],p['team'])
            self.assertEqual((official['GP'],official['MIN']),(int(ref['G']),int(ref['MP'])))
            self.assertEqual(p['independent_archive_sha256'],report['reference_archive_sha256'])
            self.assertEqual(key in rows,p['decision']=='include')
            if key in rows:
                self.assertLess(p['source_aggregate']['seconds'],900*p['source_aggregate']['gp'])
                self.assertGreaterEqual(official['MIN'],15*official['GP'])
                self.assertEqual(rows[key].gp,official['GP'])
            else:
                self.assertGreaterEqual(p['source_aggregate']['seconds'],900*p['source_aggregate']['gp'])
                self.assertLess(official['MIN'],15*official['GP'])
        self.assertEqual(rows[(698,'KCK')].mpg,36.9)
        self.assertEqual(rows[(77178,'PHX')].mpg,20.1)
        self.assertNotIn((77191,'SAS'),rows)
        p=next(p for p in report['resolved_differences'] if p['player_id']==76876 and p['field']=='bpg')
        self.assertEqual((p['official_total_evidence']['BLK'],p['independent_total']),(11,14))

    def test_new_official_totals_preserve_original_nulls_and_rate_precision(self):
        from decimal import Decimal, ROUND_HALF_UP
        for season,count in [('1985-86',39),('1984-85',81),('1983-84',30)]:
            manifest=json.loads((ROOT/f'data/staging/stats_{season.replace("-","_")}_manifest.json').read_text(encoding="utf-8"));rows={(r.player_id,r.team):r for r in load_records([season])}
            self.assertEqual(len(manifest['season_total_overrides']),count)
            self.assertTrue(any(p['source_aggregate']['rebounds_total'] is None or p['source_aggregate']['steals'] is None for p in manifest['season_total_overrides']))
            for p in manifest['season_total_overrides']:
                official=p['official_row'];r=rows[(p['player_id'],p['team'])]
                self.assertEqual(r.gp,official['GP'])
                for field,column in [('mpg','MIN'),('ppg','PTS'),('rpg','REB'),('apg','AST'),('spg','STL'),('bpg','BLK')]:
                    expected=float((Decimal(official[column])/Decimal(official['GP'])).quantize(Decimal('.1'),rounding=ROUND_HALF_UP))
                    self.assertEqual(getattr(r,field),expected)

    def test_steve_johnson_final_kck_game_excludes_post_trade_source_errors(self):
        import copy
        import sys
        from unittest.mock import patch
        with patch.object(sys,"path",[str(ROOT/"scripts"),*sys.path]):
            from complete_historical_seasons import final_log_rows
        audit=json.loads((ROOT/'data/processed/completion_1983_84.json').read_text(encoding="utf-8"));e=next(e for e in audit['jersey_evidence'] if e['player_id']==77134 and e['team']=='KCK');p=e['final_appearance_resolution'];bounded=final_log_rows(p)
        self.assertEqual((e['last_game_date'],e['game_id']),('1984-02-14','0028300586'))
        self.assertEqual(p['source_observed_game_date'],'1984-03-31')
        self.assertEqual(p['roster_end_date_exclusive'],'1984-02-15')
        self.assertEqual((len(p['official_stint_game_log_rows']),len(bounded),len(p['excluded_post_transaction_rows'])),(53,50,3))
        self.assertEqual(p['transaction_evidence']['pdf_page'],379)
        self.assertEqual(e['observed_appearance_count'],53)
        for field in ['MIN','PTS','REB','AST','STL','BLK']:self.assertEqual(sum(r[field] for r in bounded),p['official_row'][field])
        bad=copy.deepcopy(p);bad['roster_end_date_exclusive']='1984-04-01';bad['transaction_evidence']['trade_date']='1984-04-01';bad['excluded_post_transaction_rows']=[]
        with self.assertRaises(AssertionError):final_log_rows(bad)

    def test_new_jersey_resolutions_retain_exact_team_and_original_blank(self):
        for season,count in [('1985-86',4),('1984-85',4),('1983-84',5)]:
            audit=json.loads((ROOT/f'data/processed/completion_{season.replace("-","_")}.json').read_text(encoding="utf-8"));resolved=[e for e in audit['jersey_evidence'] if e['jersey_resolution']]
            self.assertEqual(len(resolved),count)
            for e in resolved:
                proof=e['jersey_resolution']
                self.assertEqual(e['official_box_score_player']['jerseyNum'],'')
                self.assertEqual(proof['status'],'VERIFIED_HISTORICAL_SEASON_REGISTER')
                self.assertEqual(proof['source'],'https://apbr.org/nmbr8090.html')
                self.assertEqual(proof['team'],e['team'])
        sam=next(r for r in load_records(['1983-84']) if r.player_id==78569)
        self.assertEqual((sam.team,sam.jersey),('PHI',33))
