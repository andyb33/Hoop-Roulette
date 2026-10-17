"""Complete verified staging seasons using official final-appearance box scores."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import hashlib
import json
import re
import tempfile
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from verify_goat_datasets import parse_honors, parse_champions, HISTORY_URLS, TEAM_NAMES, table
from build_goat_datasets import player_key
from collect_historical_stats import historical_team

# NBA's box-score mirror uses Jimmy Butler III; the official honors list uses Jimmy Butler.
HONORS_NAME_ALIASES = {202710: 'Jimmy Butler', 77376: 'Fat Lever', 76753: 'World B. Free', 78510: 'Jo Jo White'}

def honors_key(row):
    return player_key(HONORS_NAME_ALIASES.get(row['player_id'], row['player']))

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / '.cache/historical_completion'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.nba.com/'}

def fetch(url):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.sha256(url.encode()).hexdigest() + '.json')
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            pass  # A previously interrupted cache write must be fetched again.
    error = None
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers=HEADERS), timeout=30) as response:
                data = json.load(response)
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=CACHE, delete=False) as temporary:
                temporary.write(json.dumps(data, ensure_ascii=False))
                temporary_path = Path(temporary.name)
            temporary_path.replace(path)
            return data
        except Exception as exc:
            error = exc
    raise RuntimeError(f'{url}: {error}')

def final_log_rows(resolution):
    rows=resolution['official_stint_game_log_rows']
    if resolution.get('method') == 'SCOPED_1979_LANDSBERGER_MISATTRIBUTED_GAME':
        assert (resolution['season'],resolution['player_id'],resolution['team']) == ('1979-80',77334,'CHI')
        excluded=[r for r in rows if r['Game_ID']=='0027900619']
        before=[r for r in rows if r not in excluded]
        assert len(excluded)==1 and excluded[0]['PTS']==14 and excluded==resolution['excluded_misattributed_rows']
        official=resolution['official_row'];ref=resolution['independent_reference_row']
        assert len(before)==official['GP']==int(ref['G'])==54
        assert sum(r['PTS'] for r in before)==official['PTS']==int(ref['PTS'])==453
        assert official['MIN']==int(ref['MP'])==1136
        assert max(r['Game_ID'] for r in before if r['GAME_DATE']=='Feb 06, 1980')=='0027900608'
        assert 'apbr.org/forum/' in resolution['independent_final_appearance_source']
        return before
    if resolution.get('method') in ('OFFICIAL_TOTALS_CORROBORATED_PLACEHOLDER_EXCLUSION','SCOPED_1980_COLLINS_PLACEHOLDER_EXCLUSION'):
        official=resolution['official_row']
        before=[r for r in rows if r['MIN'] is not None and r['MIN']>0]
        after=[r for r in rows if r not in before]
        assert after and all(r['MIN']==0 for r in after)
        assert after==resolution['excluded_zero_minute_rows']
        assert len({r['Game_ID'] for r in before})==len(before)==official['GP']
        fields=set(resolution['bounded_matched_fields'])
        required={'GP','MIN','PTS','REB','AST'}
        if resolution['method']=='SCOPED_1980_COLLINS_PLACEHOLDER_EXCLUSION':
            assert (resolution['season'],resolution['player_id'],resolution['team'])==('1980-81',76418,'ATL')
            assert (official['GP'],official['MIN'],official['PTS'])==(47,1184,597)
            assert int(resolution['independent_reference_row']['PTS'])==597
            required={'GP','MIN','PTS'}
            assert resolution['counting_total_disagreements']=={'REB':{'observed':186,'official':187},'AST':{'observed':114,'official':115}}
            for field,values in resolution['counting_total_disagreements'].items():
                assert sum(r[field] for r in before)==values['observed'] and official[field]==values['official']
        assert required <= fields <= {'GP','MIN','PTS','REB','AST','STL','BLK'}
        for field in fields-{'GP'}:
            assert all(r[field] is not None for r in before) and sum(r[field] for r in before)==official[field]
        ref=resolution['independent_reference_row']
        assert (int(ref['G']),int(ref['MP']))==(official['GP'],official['MIN'])
        return before
    cutoff=resolution.get('roster_end_date_exclusive')
    if not cutoff:return rows
    transaction=resolution['transaction_evidence'];official=resolution['official_row']
    assert (transaction['trade_date'],transaction['player_id'],transaction['from_team'])==(cutoff,resolution['player_id'],resolution['team'])
    before=[r for r in rows if datetime.strptime(r['GAME_DATE'],'%b %d, %Y').strftime('%Y-%m-%d')<cutoff]
    after=[r for r in rows if r not in before]
    assert after==resolution['excluded_post_transaction_rows']
    assert len({r['Game_ID'] for r in before})==len(before)
    assert len(before)==official['GP'] and set(resolution['bounded_matched_fields'])=={'GP','MIN','PTS','REB','AST','STL','BLK'}
    for field in ('MIN','PTS','REB','AST','STL','BLK'):
        assert all(r[field] is not None for r in before) and sum(r[field] for r in before)==official[field]
    return before


def fetch_box(gid, season):
    live_url = f'https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{gid}.json'
    live_cache = CACHE / (hashlib.sha256(live_url.encode()).hexdigest() + '.json')
    if int(season[:4]) >= 2020 or live_cache.exists():
        return fetch(live_url)
    # Older NBA game pages retain game-specific roster numbers even when
    # their legacy box-score rows leave jerseyNum blank.
    url = f'https://www.nba.com/game/{gid}/box-score'
    path = CACHE / (hashlib.sha256(url.encode()).hexdigest() + '.json')
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            pass  # A previously interrupted cache write must be fetched again.
    error = None
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers=HEADERS), timeout=30) as response:
                raw = response.read()
            match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', raw.decode('utf-8'), re.DOTALL)
            if not match:
                raise ValueError('NBA game page has no embedded game data')
            game = json.loads(match[1])['props']['pageProps']['game']
            assert game['gameId'] == gid
            game['gameTimeLocal'] = game['gameEt']
            for side in ('homeTeam', 'awayTeam'):
                numbers = {int(p['personId']): str(p['jerseyNum']) for p in game[side + 'Players']}
                team = game[side]
                for player in team['players']:
                    old = str(player.get('jerseyNum', ''))
                    number = numbers.get(int(player['personId']), old)
                    if old and number != old:
                        raise ValueError('Conflicting NBA box-score and game-roster jerseys')
                    player['jerseyNum'] = number
                    player['played'] = '1' if player['statistics']['minutes'] != '' else '0'
                # Inactive title-roster players also belong to the championship squad.
                for player in team.get('inactives', []):
                    if int(player['personId']) not in {int(p['personId']) for p in team['players']}:
                        team['players'].append({**player, 'played': '0', 'statistics': {'minutes': ''}})
            result = {'game': game, '_source_url': url, '_source_sha256': hashlib.sha256(raw).hexdigest(),
                      '_jersey_method': 'Official game-specific active/inactive roster joined by NBA player ID'}
            path.write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
            return result
        except Exception as exc:
            error = exc
    raise RuntimeError(f'{url}: {error}')

def complete(season, workers=6):
    slug = season.replace('-', '_')
    identity_path=ROOT/f'data/staging/player_identity_{slug}_resolutions.json'
    identities=json.loads(identity_path.read_text()) if identity_path.exists() else []
    for proof in identities:
        official=proof['canonical_official_row']
        assert (proof['season'],official['SEASON_ID'],official['PLAYER_ID'],official['TEAM_ABBREVIATION']) == (season,season,proof['canonical_player_id'],proof['team'])
        assert {'GP','MIN','PTS','AST','STL','BLK'} <= set(proof['matched_fields'])
        assert all(proof['legacy_aggregate'][f] == official[f] for f in proof['matched_fields'])
    identity_by_legacy={p['legacy_player_id']:p for p in identities}
    def canonical_id(value):
        value=int(value)
        return identity_by_legacy[value]['canonical_player_id'] if value in identity_by_legacy else value
    staged = ROOT / f'data/staging/stats_{slug}.json'
    report = json.loads((ROOT / f'data/staging/stats_{slug}_verification.json').read_text(encoding='utf-8'))
    assert report['passed'] and report['staged_sha256'] == hashlib.sha256(staged.read_bytes()).hexdigest()
    rows = json.loads(staged.read_text(encoding='utf-8'))
    manifest = json.loads((ROOT / f'data/staging/stats_{slug}_manifest.json').read_text(encoding='utf-8'))
    raw = ROOT / f'data/raw/{season}/player_boxscores_{int(season[:4])+1}.csv'
    if not raw.exists():
        raw.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(Request(manifest['source'], headers=HEADERS), timeout=45) as response:
            raw.write_bytes(response.read())
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == manifest['source_sha256']
    url = 'https://stats.nba.com/stats/leaguegamefinder?' + urlencode({'LeagueID':'00', 'Season':season, 'SeasonType':'Regular Season'})
    if int(season[:4]) < 1983:
        url = 'https://stats.nba.com/stats/leaguegamelog?' + urlencode({'LeagueID':'00','Season':season,'SeasonType':'Regular Season','PlayerOrTeam':'T','Counter':0,'Direction':'ASC','Sorter':'DATE','DateFrom':'','DateTo':''})
    games = table(fetch(url), 'LeagueGameLog' if int(season[:4]) < 1983 else 'LeagueGameFinderResults')
    dates = {r['GAME_ID']: r['GAME_DATE'] for r in games}
    keys = {(r['team'], r['player_id']) for r in rows}
    appearances = {k: [] for k in keys}
    prefix = '002' + season[2:4]
    with raw.open(encoding='utf-8-sig') as handle:
        for r in csv.DictReader(handle):
            gid = r['game_id'].zfill(10)
            key = (historical_team(season,r['team_tricode']), int(r['person_id']))
            if gid.startswith(prefix) and r['minutes'] and key in keys:
                assert gid in dates, f'Missing game date {gid}'
                appearances[key].append((dates[gid], gid))
    for proof in manifest.get('source_corrections', {}).get('missing_appearances', []):
        official = proof['official_row']
        key = (proof['team'], proof['player_id'])
        if key in appearances:
            gid = official['GAME_ID']
            assert all(observed_gid != gid for _, observed_gid in appearances[key])
            assert dates[gid] == datetime.strptime(official['GAME_DATE'], '%b %d, %Y').strftime('%Y-%m-%d')
            appearances[key].append((dates[gid],gid))
    total_overrides={(p['team'],p['player_id']):p for p in manifest.get('season_total_overrides',[])+[p for p in manifest.get('eligibility_source_overrides',[]) if p['decision']=='include']}
    assert all(len(appearances[(r['team'], r['player_id'])]) == total_overrides[(r['team'],r['player_id'])]['source_aggregate']['gp'] if (r['team'],r['player_id']) in total_overrides else len(appearances[(r['team'],r['player_id'])])==r['gp'] for r in rows)
    last = {k: max(v) for k,v in appearances.items()}
    final_path=ROOT/f'data/staging/final_appearance_{slug}_resolutions.json'
    final_proofs=json.loads(final_path.read_text()) if final_path.exists() else []
    final_resolutions={(p['team'],p['player_id']):p for p in final_proofs}
    for key,resolution in final_resolutions.items():
        if not resolution.get('roster_end_date_exclusive') and resolution.get('method') not in ('OFFICIAL_TOTALS_CORROBORATED_PLACEHOLDER_EXCLUSION','SCOPED_1980_COLLINS_PLACEHOLDER_EXCLUSION','SCOPED_1979_LANDSBERGER_MISATTRIBUTED_GAME'):continue
        assert (resolution['season'],resolution['source_observed_game_date'],resolution['source_observed_game_id'])==(season,*last[key])
        bounded=final_log_rows(resolution)
        target=max((datetime.strptime(r['GAME_DATE'],'%b %d, %Y').strftime('%Y-%m-%d'),r['Game_ID']) for r in bounded)
        assert target==(resolution['game_date'],resolution['game_id']) and target[1] in dates
        last[key]=target
    for key in total_overrides:
        proof=total_overrides[key]
        if proof['source_aggregate']['gp'] != proof['official_row']['GP']:
            team_final=max(g['GAME_DATE'] for g in games if historical_team(season,g['TEAM_ABBREVIATION']) == key[0])
            if last[key][0] != team_final:
                assert key in final_resolutions, 'Conflicting GP requires a separate final-appearance proof'
                resolution=final_resolutions[key]
                assert (resolution['season'],resolution['game_date'],resolution['game_id'])==(season,*last[key])
                assert resolution['official_row']==proof['official_row']
                log=final_log_rows(resolution)
                assert log and all(r['Player_ID']==key[1] and historical_team(season,r['MATCHUP'].split()[0])==key[0] and r['Game_ID'] in dates for r in log)
                assert max((datetime.strptime(r['GAME_DATE'],'%b %d, %Y').strftime('%Y-%m-%d'),r['Game_ID']) for r in log)==last[key]

    ids = sorted({gid for date,gid in last.values()})
    boxes = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        jobs = {pool.submit(fetch_box, gid, season):gid for gid in ids}
        for job in as_completed(jobs):
            gid = jobs[job]
            boxes[gid] = job.result()
            print(f'{season}: final box scores {len(boxes)}/{len(ids)}', flush=True)
    for name, source_url in HISTORY_URLS.items():
        path = CACHE / f'{name}.html'
        if not path.exists():
            with urlopen(Request(source_url, headers=HEADERS), timeout=30) as response:
                path.write_bytes(response.read())
    nba = parse_honors((CACHE/'all_nba.html').read_text(encoding='utf-8'))[season]
    defense = parse_honors((CACHE/'all_defense.html').read_text(encoding='utf-8'))[season]
    # Official historical list misspells Beverley in the 2016-17 section.
    if 'patrick-beverly' in defense:
        assert 'patrick-beverley' not in defense
        defense['patrick-beverley'] = defense.pop('patrick-beverly')
    if season == '1984-85' and 'benard-king' in nba:
        assert 'bernard-king' not in nba
        nba['bernard-king']=nba.pop('benard-king')
    if season == '1998-99' and 'gary-payton-seattle-supersonics' in nba:
        assert 'gary-payton' not in nba
        nba['gary-payton'] = nba.pop('gary-payton-seattle-supersonics')
    # Official 1980-81 history spells Micheal Ray Richardson as Michael.
    if season in ('1980-81','1979-80') and 'michael-ray-richardson' in defense:
        assert 'micheal-ray-richardson' not in defense
        defense['micheal-ray-richardson'] = defense.pop('michael-ray-richardson')
    champion = historical_team(season, TEAM_NAMES[parse_champions((CACHE/'champions.html').read_text(encoding='utf-8'))[season]])
    awards = {r['player_key']:r for r in json.loads((ROOT/'data/goat/award_winners_history.json').read_text(encoding='utf-8')) if r['season']==season}
    # Final title-game roster includes active players and DNPs, but excludes players traded away.
    finals_id = {'2022-23': '0042200405', '2021-22': '0042100406', '2020-21': '0042000406', '2019-20': '0041900406', '2018-19': '0041800406', '2017-18': '0041700404', '2016-17': '0041600405', '2015-16': '0041500407', '2014-15': '0041400406', '2013-14': '0041300405', '2012-13': '0041200407', '2011-12': '0041100405', '2010-11': '0041000406', '2009-10': '0040900407', '2008-09': '0040800405', '2007-08': '0040700406', '2006-07': '0040600404', '2005-06': '0040500406', '2004-05': '0040400407', '2003-04': '0040300405', '2002-03': '0040200406', '2001-02': '0040100404', '2000-01': '0040000087', '1999-00': '0049900088', '1998-99': '0049800087', '1997-98':'0049700088', '1996-97':'0049600088', '1995-96':'0049500068','1994-95':'0049400073','1993-94':'0049300077','1992-93':'0049200076','1991-92':'0049100073','1990-91':'0049000068','1989-90':'0048900072','1988-89':'0048800062','1987-88':'0048700080','1986-87':'0048600071','1985-86':'0048500406','1984-85':'0048400406','1983-84':'0048300079','1982-83':'0048200043','1981-82':'0048100045','1980-81':'0048000053','1979-80':'0047900048','1978-79':'0047800053','1977-78':'0047700051','1976-77':'0047600100','1975-76':'0047500406','1974-75':'0047409404','1973-74':'0047300407'}[season]
    finals_url = f'https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{finals_id}.json'
    title_proof = None
    if season in ('1976-77','1975-76','1974-75','1973-74'):
        title_proof=json.loads((ROOT/'data/processed/title_game_verification_1973_1977.json').read_text())[season]
        assert title_proof['champion_team'] == champion and title_proof['game_id'] == finals_id
    elif season in ('1979-80','1978-79','1977-78'):
        title_proof=json.loads((ROOT/'data/processed/title_game_verification_1977_1980.json').read_text())[season]
        assert title_proof['champion_team'] == champion and title_proof['game_id'] == finals_id
    elif season in ('1982-83','1981-82','1980-81'):
        title_proof=json.loads((ROOT/'data/processed/title_game_verification_1980_1983.json').read_text())[season]
        assert title_proof['champion_team'] == champion and title_proof['game_id'] == finals_id
    if season in ('1985-86','1984-85','1983-84'):
        title_proof=json.loads((ROOT/'data/processed/title_game_verification_1983_1986.json').read_text())[season]
        assert title_proof['champion_team'] == champion and title_proof['game_id'] == finals_id
    if season in ('1988-89','1987-88','1986-87'):
        title_proof=json.loads((ROOT/'data/processed/title_game_verification_1986_1989.json').read_text())[season]
        assert title_proof['champion_team'] == champion and title_proof['game_id'] == finals_id
    if season in ('1991-92','1990-91','1989-90'):
        title_proof=json.loads((ROOT/'data/processed/title_game_verification_1989_1992.json').read_text())[season]
        assert title_proof['champion_team'] == champion and title_proof['game_id'] == finals_id
    if season in ('1994-95','1993-94','1992-93'):
        title_proof=json.loads((ROOT/'data/processed/title_game_verification_1992_1995.json').read_text())[season]
        assert title_proof['champion_team'] == champion and title_proof['game_id'] == finals_id
    if season in ('1997-98','1996-97','1995-96'):
        title_proof = json.loads((ROOT/'data/processed/title_game_verification_1995_1998.json').read_text())[season]
        assert title_proof['champion_team'] == champion and title_proof['game_id'] == finals_id
    if season in ('2000-01','1999-00','1998-99'):
        title_proof = json.loads((ROOT/'data/processed/title_game_verification_1998_2001.json').read_text(encoding='utf-8'))[season]
        assert title_proof['champion_team'] == champion
        finals_id = title_proof['game_id']
        finals_url = f'https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{finals_id}.json'
    finals_box = fetch_box(finals_id, season)
    finals_url = finals_box.get('_source_url', finals_url)
    finals = finals_box['game']
    if title_proof:
        assert finals['gameId'] == title_proof['game_id'] and finals['gameTimeLocal'][:10] == title_proof['game_date']
    champion_sides = [finals[s] for s in ('homeTeam', 'awayTeam') if historical_team(season,finals[s]['teamTricode']) == champion]
    assert len(champion_sides) == 1
    champion_players = {canonical_id(p['personId']) for p in champion_sides[0]['players']}
    unresolved = []
    for r in rows:
        date,gid = last[(r['team'],r['player_id'])]
        game = boxes[gid]['game']
        players = [p for side in ('homeTeam','awayTeam') if historical_team(season,game[side]['teamTricode']) == r['team'] for p in game[side]['players'] if canonical_id(p['personId']) == r['player_id']]
        assert len(players) == 1
        jersey = str(players[0]['jerseyNum'])
        path = ROOT / f"data/staging/jersey_{slug}_{r['player_id']}_{r['team']}_resolution.json"
        if not jersey.isdigit() and not path.exists():
            unresolved.append({'season':season,'player_id':r['player_id'],'player':r['player'],'team':r['team'],'game_id':gid,'game_date':date,'original_nba_jersey':jersey})
    if unresolved:
        path = CACHE / f'unresolved_jerseys_{slug}.json'
        path.write_text(json.dumps(unresolved,indent=2)+'\n',encoding='utf-8')
        raise ValueError(f'{len(unresolved)} jersey resolutions required; see {path}')
    evidence = []
    for r in rows:
        date,gid = last[(r['team'],r['player_id'])]
        box = boxes[gid]['game']
        assert box['gameId'] == gid and box['gameStatus'] in (3, 'finalbox')
        date_resolution = None
        if season == '1975-76' and box['gameTimeLocal'] == '0001-01-01T00:00:00Z':
            schedule_rows = [g for g in games if g['GAME_ID'] == gid]
            assert len(schedule_rows) == 2 and all(g['GAME_DATE'] == date for g in schedule_rows)
            date_resolution = {'method': 'BOTH_TEAM_OFFICIAL_SCHEDULE_ROWS',
                               'original_game_time_local': box['gameTimeLocal'],
                               'resolved_date': date, 'source': url, 'schedule_rows': schedule_rows}
        else:
            assert box['gameTimeLocal'][:10] == date, (season,gid,date,box['gameTimeLocal'])
        sides = [box[s] for s in ('homeTeam','awayTeam') if historical_team(season,box[s]['teamTricode'])==r['team']]
        assert len(sides)==1
        players = [p for p in sides[0]['players'] if canonical_id(p['personId'])==r['player_id']]
        assert len(players)==1
        p = players[0]
        jersey = str(p['jerseyNum'])
        resolution = None
        if not jersey.isdigit():
            path = ROOT / f"data/staging/jersey_{slug}_{r['player_id']}_{r['team']}_resolution.json"
            resolution = json.loads(path.read_text(encoding='utf-8'))
            assert (resolution['season'], resolution['player_id'], resolution['team'], resolution['game_id'], resolution['game_date'], resolution['original_nba_jersey']) == (season, r['player_id'], r['team'], gid, date, jersey)
            jersey = str(resolution['resolved_jersey'])
        assert jersey.isdigit() and 0 <= int(jersey) <= 99
        appearance_resolution=None
        if p['played']!='1':
            assert (season,r['player_id'],r['team'],gid)==('1973-74',76002,'HOU','0027300689')
            appearance_resolution=json.loads((ROOT/'data/staging/played_1973_74_76002_HOU_resolution.json').read_text(encoding='utf-8'))
            proof=appearance_resolution;log=proof['official_stint_game_log_rows'];ref=proof['independent_reference_row']
            assert proof['original_box_score_player']==p and p['statistics']['minutes']=='' and p['statistics']['points']==9
            assert len(log)==len({a['Game_ID'] for a in log})==r['gp']==int(ref['G'])==79
            assert sum(a['PTS'] for a in log)==int(ref['PTS'])==865
            last_log=max(log,key=lambda a:datetime.strptime(a['GAME_DATE'],'%b %d, %Y'))
            assert last_log['Game_ID']==gid and last_log['PTS']==9 and last_log['FGM']==last_log['FTM']==3
            assert proof['game_date']==date and proof['player_id']==r['player_id'] and proof['team']==r['team'] and proof['season']==season

        key = honors_key(r)
        award = awards.get(key,{})
        r.update(jersey=int(jersey), jersey_display=jersey, all_nba=nba.get(key), all_defense=defense.get(key), champion=r['team']==champion and r['player_id'] in champion_players,
                 **{a:bool(award.get(a,False)) for a in ('mvp','dpoy','roy')})
        evidence.append({'player_id':r['player_id'],'player':r['player'],'team':r['team'],'last_game_date':date,'game_id':gid,
                         'jersey':int(jersey),'jersey_display':jersey,'official_box_score_player':{k:p[k] for k in ('personId','firstName','familyName','jerseyNum','played')},
                         'box_score_sha256':hashlib.sha256(json.dumps(boxes[gid],ensure_ascii=False).encode()).hexdigest(),
                         'jersey_method':resolution['method'] if resolution else boxes[gid].get('_jersey_method', 'Official final-appearance live box score'),
                         'jersey_resolution':resolution,
                         'game_date_resolution':date_resolution,
                         'identity_resolution':identity_by_legacy.get(int(p['personId'])),
                         'season_total_resolution':total_overrides.get((r['team'],r['player_id'])),
                         'team_guide_total_resolution':next((p for p in manifest.get('team_guide_total_overrides',[]) if (p['team'],p['player_id'])==(r['team'],r['player_id'])),None),
                         'final_appearance_resolution':final_resolutions.get((r['team'],r['player_id'])),
                         'appearance_resolution':appearance_resolution,
                         'verified_played':True,
                         'observed_appearance_count':len(appearances[(r['team'],r['player_id'])]),
                         'source_sha256':boxes[gid].get('_source_sha256'),
                         'source':boxes[gid].get('_source_url', f'https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{gid}.json')})
    assert len(nba)==(10 if int(season[:4])<1988 else 15) and len(defense)==(12 if season == "1973-74" else 11 if season in ("2012-13", "2005-06", "2004-05", "1998-99", "1987-88", "1982-83", "1980-81", "1979-80", "1977-78") else 10)
    if season == "1973-74":
        assert sum(tier == 1 for tier in defense.values()) == 6
        assert sum(tier == 2 for tier in defense.values()) == 6
    if season == "2012-13":
        assert defense["tyson-chandler"] == defense["joakim-noah"] == 1
        assert sum(tier == 1 for tier in defense.values()) == 6
    for tied_season, tier, names in [("1979-80", 1, ("dennis-johnson", "don-buse")), ("1977-78", 2, ("artis-gilmore", "kareem-abdul-jabbar")), ("1987-88", 2, ("mark-eaton", "patrick-ewing")), ("1998-99", 1, ("karl-malone", "scottie-pippen")), ("2005-06", 1, ("kobe-bryant", "jason-kidd")), ("2004-05", 2, ("jason-kidd", "dwyane-wade"))]:
        if season == tied_season:
            assert all(defense[name] == tier for name in names)
            assert sum(value == tier for value in defense.values()) == 6
    expected_awards = {a: 0 if a == 'dpoy' and int(season[:4]) < 1982 else 2 if a == 'roy' and season in ('1999-00','1994-95') else 1 for a in ('mvp','dpoy','roy')}
    assert all(sum(bool(r.get(a)) for r in awards.values()) == expected_awards[a] for a in expected_awards)
    for honors,field in [(nba,'all_nba'),(defense,'all_defense')]:
        matched={honors_key(r) for r in rows if r[field] is not None}
        assert matched==set(honors), (field,set(honors)-matched)
    for a in ('mvp','dpoy','roy'):
        assert sum(r[a] for r in rows)==expected_awards[a]
    # Champion is attached to the specific team stint; another team's stint cannot inherit it.
    assert all(r['champion']==(r['team']==champion and r['player_id'] in champion_players) for r in rows)
    output=ROOT/f'data/game/players_{slug}.json'
    output.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    processed=ROOT/'data/processed'
    with (processed/f'nba_roulette_{slug}.csv').open('w',newline='',encoding='utf-8-sig') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    policy_resolutions = sum(e['jersey_resolution'] is not None and
                             e['jersey_resolution'].get('historically_verified_final_jersey') is False
                             for e in evidence)
    audit={'season':season,'completed_at':datetime.now(timezone.utc).isoformat(),'passed':True,
           'entries':len(rows),'jerseys_verified':len(evidence)-policy_resolutions,
           'jerseys_resolved':len(evidence),'jerseys_resolved_by_user_policy':policy_resolutions,'unresolved':[],
           'staged_sha256':hashlib.sha256(staged.read_bytes()).hexdigest(),'game_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
           'sources':{'game_dates':url,**HISTORY_URLS},
           'history_sha256':{name:hashlib.sha256((CACHE/f'{name}.html').read_bytes()).hexdigest() for name in HISTORY_URLS},'award_sources':{k:v.get('award_sources',{}) for k,v in awards.items()},
           'honors_name_aliases':HONORS_NAME_ALIASES, 'honors_key_aliases':{'patrick-beverly':'patrick-beverley', **({'michael-ray-richardson':'micheal-ray-richardson'} if season in ('1980-81','1979-80') else {}), **({'benard-king':'bernard-king'} if season == '1984-85' else {}), **({'gary-payton-seattle-supersonics':'gary-payton'} if season == '1998-99' else {})}, 'official_all_nba':nba, 'official_all_defense':defense, 'official_award_winners':awards,
           'all_nba_records':sum(r['all_nba'] is not None for r in rows),'all_defense_records':sum(r['all_defense'] is not None for r in rows),
           'title_game_verification':title_proof,
           'champion_roster_source':finals_url, 'champion_roster':[{k:p[k] for k in ('personId','firstName','familyName','jerseyNum','played')} for p in champion_sides[0]['players']], 'champion_team':champion,'champion_records':sum(r['champion'] for r in rows),'jersey_evidence':evidence}
    (processed/f'completion_{slug}.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary = {key: value for key, value in audit.items() if key not in ('jersey_evidence', 'champion_roster', 'official_all_nba', 'official_all_defense', 'official_award_winners')}
    summary['eligibility'] = manifest['eligibility']
    summary['eligible_records_by_team'] = manifest['records_by_team']
    (processed/f'nba_roulette_{slug}_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (processed/f'jersey_verification_{slug}.csv').open('w',newline='',encoding='utf-8-sig') as handle:
        fields = ['team','player_id','player','last_game_date','game_id','verified_final_jersey','status','source']
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader()
        for entry in evidence:
            writer.writerow({**{key:entry[key] for key in ('team','player_id','player','last_game_date','game_id','source')}, 'verified_final_jersey':entry['jersey'],'status':entry['jersey_resolution']['status'] if entry['jersey_resolution'] else 'VERIFIED'})
    manifest.update(status='complete_promoted',enabled_in_game=True,pending=['Distribution analysis'])
    (ROOT/f'data/staging/stats_{slug}_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(f'{season} complete: {len(rows)} records, no unresolved fields',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--season',required=True,choices=['2022-23','2021-22','2020-21','2019-20','2018-19','2017-18','2016-17','2015-16','2014-15','2013-14','2012-13','2011-12','2010-11','2009-10','2008-09','2007-08','2006-07','2005-06','2004-05','2003-04','2002-03','2001-02','2000-01','1999-00','1998-99','1997-98','1996-97','1995-96','1994-95','1993-94','1992-93','1991-92','1990-91','1989-90','1988-89','1987-88','1986-87','1985-86','1984-85','1983-84','1982-83','1981-82','1980-81','1979-80','1978-79','1977-78','1976-77','1975-76','1974-75','1973-74']);p.add_argument('--workers',type=int,default=6)
    a=p.parse_args();complete(a.season,a.workers)
