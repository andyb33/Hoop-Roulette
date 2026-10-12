"""Complete verified staging seasons using official final-appearance box scores."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from verify_goat_datasets import parse_honors, parse_champions, HISTORY_URLS, TEAM_NAMES, table
from build_goat_datasets import player_key

# NBA's box-score mirror uses Jimmy Butler III; the official honors list uses Jimmy Butler.
HONORS_NAME_ALIASES = {202710: 'Jimmy Butler'}

def honors_key(row):
    return player_key(HONORS_NAME_ALIASES.get(row['player_id'], row['player']))

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / '.cache/historical_completion'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.nba.com/'}

def fetch(url):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.sha256(url.encode()).hexdigest() + '.json')
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    error = None
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers=HEADERS), timeout=30) as response:
                data = json.load(response)
            path.write_text(json.dumps(data, ensure_ascii=False),encoding='utf-8')
            return data
        except Exception as exc:
            error = exc
    raise RuntimeError(f'{url}: {error}')

def complete(season, workers=6):
    slug = season.replace('-', '_')
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
    games = table(fetch(url), 'LeagueGameFinderResults')
    dates = {r['GAME_ID']: r['GAME_DATE'] for r in games}
    keys = {(r['team'], r['player_id']) for r in rows}
    appearances = {k: [] for k in keys}
    prefix = '002' + season[2:4]
    with raw.open(encoding='utf-8-sig') as handle:
        for r in csv.DictReader(handle):
            gid = r['game_id'].zfill(10)
            key = (r['team_tricode'], int(r['person_id']))
            if gid.startswith(prefix) and r['minutes'] and key in keys:
                assert gid in dates, f'Missing game date {gid}'
                appearances[key].append((dates[gid], gid))
    assert all(len(appearances[(r['team'], r['player_id'])]) == r['gp'] for r in rows)
    last = {k: max(v) for k,v in appearances.items()}
    ids = sorted({gid for date,gid in last.values()})
    boxes = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        jobs = {pool.submit(fetch, f'https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{gid}.json'):gid for gid in ids}
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
    champion = TEAM_NAMES[parse_champions((CACHE/'champions.html').read_text(encoding='utf-8'))[season]]
    awards = {r['player_key']:r for r in json.loads((ROOT/'data/goat/award_winners_history.json').read_text(encoding='utf-8')) if r['season']==season}
    # Final title-game roster includes active players and DNPs, but excludes players traded away.
    finals_id = {'2022-23': '0042200405', '2021-22': '0042100406'}[season]
    finals_url = f'https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{finals_id}.json'
    finals = fetch(finals_url)['game']
    champion_sides = [finals[s] for s in ('homeTeam', 'awayTeam') if finals[s]['teamTricode'] == champion]
    assert len(champion_sides) == 1
    champion_players = {int(p['personId']) for p in champion_sides[0]['players']}
    evidence = []
    for r in rows:
        date,gid = last[(r['team'],r['player_id'])]
        box = boxes[gid]['game']
        assert box['gameId'] == gid and box['gameStatus'] == 3
        assert box['gameTimeLocal'][:10] == date
        sides = [box[s] for s in ('homeTeam','awayTeam') if box[s]['teamTricode']==r['team']]
        assert len(sides)==1
        players = [p for p in sides[0]['players'] if int(p['personId'])==r['player_id']]
        assert len(players)==1
        p = players[0]
        jersey = str(p['jerseyNum'])
        assert jersey.isdigit() and 0 <= int(jersey) <= 99
        assert p['played']=='1', (r['player'],gid,p['played'])
        key = honors_key(r)
        award = awards.get(key,{})
        r.update(jersey=int(jersey), jersey_display=jersey, all_nba=nba.get(key), all_defense=defense.get(key), champion=r['team']==champion and r['player_id'] in champion_players,
                 **{a:bool(award.get(a,False)) for a in ('mvp','dpoy','roy')})
        evidence.append({'player_id':r['player_id'],'player':r['player'],'team':r['team'],'last_game_date':date,'game_id':gid,
                         'jersey':int(jersey),'jersey_display':jersey,'official_box_score_player':{k:p[k] for k in ('personId','firstName','familyName','jerseyNum','played')},
                         'box_score_sha256':hashlib.sha256(json.dumps(boxes[gid],ensure_ascii=False).encode()).hexdigest(),
                         'source':f'https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{gid}.json'})
    assert len(nba)==15 and len(defense)==10 and len(awards)==3
    for honors,field in [(nba,'all_nba'),(defense,'all_defense')]:
        matched={honors_key(r) for r in rows if r[field] is not None}
        assert matched==set(honors), (field,set(honors)-matched)
    for a in ('mvp','dpoy','roy'):
        assert sum(r[a] for r in rows)==1
    # Champion is attached to the specific team stint; another team's stint cannot inherit it.
    assert all(r['champion']==(r['team']==champion and r['player_id'] in champion_players) for r in rows)
    output=ROOT/f'data/game/players_{slug}.json'
    output.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    processed=ROOT/'data/processed'
    with (processed/f'nba_roulette_{slug}.csv').open('w',newline='',encoding='utf-8-sig') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    audit={'season':season,'completed_at':datetime.now(timezone.utc).isoformat(),'passed':True,
           'entries':len(rows),'jerseys_verified':len(evidence),'unresolved':[],
           'staged_sha256':hashlib.sha256(staged.read_bytes()).hexdigest(),'game_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
           'sources':{'game_dates':url,**HISTORY_URLS},
           'history_sha256':{name:hashlib.sha256((CACHE/f'{name}.html').read_bytes()).hexdigest() for name in HISTORY_URLS},'award_sources':{k:v.get('award_sources',{}) for k,v in awards.items()},
           'honors_name_aliases':HONORS_NAME_ALIASES, 'official_all_nba':nba, 'official_all_defense':defense, 'official_award_winners':awards,
           'all_nba_records':sum(r['all_nba'] is not None for r in rows),'all_defense_records':sum(r['all_defense'] is not None for r in rows),
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
            writer.writerow({**{key:entry[key] for key in ('team','player_id','player','last_game_date','game_id','source')}, 'verified_final_jersey':entry['jersey'],'status':'VERIFIED'})
    manifest.update(status='complete_promoted',enabled_in_game=True,pending=['Distribution analysis'])
    (ROOT/f'data/staging/stats_{slug}_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(f'{season} complete: {len(rows)} records, no unresolved fields',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--season',required=True,choices=['2022-23','2021-22']);p.add_argument('--workers',type=int,default=6)
    a=p.parse_args();complete(a.season,a.workers)
