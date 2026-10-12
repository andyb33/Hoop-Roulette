#!/usr/bin/env python3
"""Audit selected GOAT records against official NBA careers, rosters and honors."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from build_goat_datasets import ROOT, player_key

CACHE = ROOT / '.cache/goat_nba'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.nba.com/'}
TEAMS = {'ATL': 1610612737, 'BOS': 1610612738, 'CLE': 1610612739,
         'NOP': 1610612740, 'CHI': 1610612741, 'DAL': 1610612742,
         'DEN': 1610612743, 'GSW': 1610612744, 'HOU': 1610612745,
         'LAC': 1610612746, 'LAL': 1610612747, 'MIA': 1610612748,
         'MIL': 1610612749, 'MIN': 1610612750, 'BKN': 1610612751,
         'NYK': 1610612752, 'ORL': 1610612753, 'IND': 1610612754,
         'PHI': 1610612755, 'PHX': 1610612756, 'POR': 1610612757,
         'SAC': 1610612758, 'SAS': 1610612759, 'TOR': 1610612761,
         'UTA': 1610612762, 'MEM': 1610612763, 'WAS': 1610612764,
         'DET': 1610612765, 'CHA': 1610612766, 'OKC': 1610612760}
TEAM_NAMES = {
    'Atlanta Hawks': 'ATL', 'Boston Celtics': 'BOS', 'Cleveland Cavaliers': 'CLE',
    'Chicago Bulls': 'CHI', 'Dallas Mavericks': 'DAL', 'Denver Nuggets': 'DEN',
    'Golden State Warriors': 'GSW', 'Houston Rockets': 'HOU', 'LA Clippers': 'LAC',
    'Indiana Pacers': 'IND',
    'Los Angeles Clippers': 'LAC', 'Los Angeles Lakers': 'LAL', 'Miami Heat': 'MIA',
    'Milwaukee Bucks': 'MIL', 'Minnesota Timberwolves': 'MIN', 'New York Knicks': 'NYK',
    'Orlando Magic': 'ORL', 'Philadelphia 76ers': 'PHI', 'Phoenix Suns': 'PHX',
    'Portland Trail Blazers': 'POR', 'San Antonio Spurs': 'SAS', 'Utah Jazz': 'UTA',
    'Toronto Raptors': 'TOR', 'Memphis Grizzlies': 'MEM', 'Detroit Pistons': 'DET',
    'Oklahoma City Thunder': 'OKC', 'Seattle SuperSonics': 'OKC',
    'Seattle Supersonics': 'OKC', 'Buffalo Braves': 'LAC', 'San Diego Clippers': 'LAC',
    'New Jersey Nets': 'BKN', 'Charlotte Hornets': 'CHA', 'Charlotte Bobcats': 'CHA',
    'New Orleans/Oklahoma City Hornets': 'NOP', 'New Orleans Hornets': 'NOP',
    'Sacramento Kings': 'SAC', 'Kansas City Kings': 'SAC',
    'Baltimore Bullets': 'WAS', 'Washington Bullets': 'WAS', 'Washington Wizards': 'WAS',
    'Philadelphia Warriors': 'GSW', 'San Francisco Warriors': 'GSW',
    'St. Louis Hawks': 'ATL', 'Cincinnati Royals': 'SAC',
}
HISTORY_URLS = {
    'all_nba': 'https://www.nba.com/news/history-all-nba-teams',
    'all_defense': 'https://www.nba.com/news/history-all-defensive-team',
    'champions': 'https://www.nba.com/news/history-nba-champions',
}


def download(url):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.sha256(url.encode()).hexdigest() + '.txt')
    if path.exists():
        return path.read_text()
    error = None
    for _ in range(3):
        try:
            with urlopen(Request(url, headers=HEADERS), timeout=25) as response:
                content = response.read().decode()
            path.write_text(content)
            return content
        except Exception as exc:
            error = exc
    raise RuntimeError(f'Could not fetch {url}: {error}')


def api(endpoint, **params):
    url = 'https://stats.nba.com/stats/' + endpoint + '?' + urlencode(params)
    return url, json.loads(download(url))


def table(data, name):
    result = next(r for r in data['resultSets'] if r['name'] == name)
    return [dict(zip(result['headers'], row)) for row in result['rowSet']]


def article_text(content):
    article = re.search(r'<article\b.*?</article>', content, re.DOTALL)
    if not article:
        raise ValueError('Official history article not found')
    content = re.sub(r'<(?:br|hr)\b[^>]*>|</(?:p|h[1-6]|li|div)>', '\n', article[0])
    return html.unescape(re.sub('<[^>]+>', '', content))


def parse_honors(content):
    text = article_text(content)
    sections = re.split(r'>\s*((?:19|20)\d{2}[-–]\d{2})', text)
    honors = {}
    for i in range(1, len(sections), 2):
        season = sections[i].replace('–', '-')
        honors[season] = {}
        tier = None
        for line in sections[i + 1].splitlines():
            line = line.strip()
            m = re.match(r'(FIRST|SECOND|THIRD) TEAM', line)
            if m:
                tier = {'FIRST': 1, 'SECOND': 2, 'THIRD': 3}[m[1]]
            if line.startswith('•') and tier:
                name = re.sub(r'^•\s*(?:[FCG](?:/[FCG])?:\s*)?', '', line).split(',')[0].strip()
                honors[season][player_key(name)] = tier
    if len(honors) < 50:
        raise ValueError('Incomplete honors parsing')
    return honors


def parse_champions(content):
    text = article_text(content)
    champions = {}
    for season, name in re.findall(r'((?:19|20)\d{2}[-–]\d{2})\s*[—–]\s*(.*?)\s+def\.', text, re.DOTALL):
        champions[season.replace('–', '-')] = ' '.join(name.split())
    if len(champions) < 70:
        raise ValueError('Incomplete champion parsing')
    return champions


def resolve_player_id(players, name, season):
    year = int(season[:4])
    matches = [r for r in players if player_key(r['DISPLAY_FIRST_LAST']) == player_key(name)
               and int(r['FROM_YEAR']) <= year <= int(r['TO_YEAR'])]
    if len(matches) != 1:
        raise ValueError(f'Ambiguous player identity {season} {name}: {[r["PERSON_ID"] for r in matches]}')
    return matches[0]['PERSON_ID']


def run(workers=4):
    awards = json.loads((ROOT / 'data/goat/award_jackpot.json').read_text())
    prehistoric = json.loads((ROOT / 'data/goat/prehistoric_candidates.json').read_text())
    selected = [('award', r) for r in awards] + [('prehistoric', r) for r in prehistoric]
    award_history = {(r['season'], r['player_key']): r for r in
                     json.loads((ROOT / 'data/goat/award_winners_history.json').read_text())}
    _, players = api('commonallplayers', IsOnlyCurrentSeason=0, LeagueID='00', Season='2025-26')
    allplayers = table(players, 'CommonAllPlayers')
    ids = {(r['season'], player_key(r['player'])): resolve_player_id(allplayers, r['player'], r['season'])
           for _, r in selected}
    history = {k: download(url) for k, url in HISTORY_URLS.items()}
    nba = parse_honors(history['all_nba'])
    defense = parse_honors(history['all_defense'])
    champions = parse_champions(history['champions'])
    jobs = sorted(set(ids.values()))
    careers = {}
    failures = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        tasks = {executor.submit(api, 'playercareerstats', PlayerID=pid, PerMode='PerGame', LeagueID='00'): pid for pid in jobs}
        for task in as_completed(tasks):
            pid = tasks[task]
            try:
                url, data = task.result()
                careers[pid] = (url, table(data, 'SeasonTotalsRegularSeason'))
            except Exception as exc:
                failures.append(str(exc))
            print(f'Career evidence {len(careers)}/{len(jobs)}', flush=True)
    resolved = []
    for pool, old in selected:
        key = player_key(old['player'])
        pid = ids[(old['season'], key)]
        if pid not in careers:
            continue
        url, rows = careers[pid]
        season_rows = [r for r in rows if r['SEASON_ID'] == old['season'] and r['TEAM_ID'] != 0]
        if pool == 'award':
            tid = TEAMS[TEAM_NAMES[old['award_team']]]
            season_rows = [r for r in season_rows if r['TEAM_ID'] == tid]
        if len(season_rows) != 1:
            failures.append(f'Ambiguous team stats {pool} {old["season"]} {old["player"]}')
            continue
        stat = season_rows[0]
        resolved.append((pool, old, key, pid, url, stat))
    roster_jobs = sorted({(r[5]['TEAM_ID'], r[1]['season']) for r in resolved})
    rosters = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        tasks = {executor.submit(api, 'commonteamroster', TeamID=tid, Season=season, LeagueID='00'): (tid, season)
                 for tid, season in roster_jobs}
        for task in as_completed(tasks):
            key = tasks[task]
            try:
                url, data = task.result()
                rosters[key] = (url, table(data, 'CommonTeamRoster'))
            except Exception as exc:
                failures.append(str(exc))
            print(f'Roster evidence {len(rosters)}/{len(roster_jobs)}', flush=True)
    evidence = []
    differences = []
    for pool, old, key, pid, url, stat in resolved:
        season = old['season']
        year = int(season[:4])
        roster_url, roster = rosters.get((stat['TEAM_ID'], season), ('', []))
        matches = [r for r in roster if r['PLAYER_ID'] == pid]
        numbers = {r['NUM'] for r in matches if r['NUM'] is not None and str(r['NUM']).isdigit()}
        jersey = int(next(iter(numbers))) if len(numbers) == 1 else None
        if jersey is None:
            failures.append(f'Unresolved jersey {pool} {season} {old["player"]}: {numbers}')
        if season not in nba or (year >= 1968 and season not in defense) or season not in champions:
            failures.append(f'Missing accolade evidence {season}')
            continue
        champ_name = champions[season]
        champ_tid = TEAMS.get(TEAM_NAMES.get(champ_name, ''))
        if champ_tid is None:
            failures.append('Unmapped championship team ' + champ_name)
            continue
        fields = {'player_id': pid, 'player_key': key, 'season': season,
                  'team': stat['TEAM_ABBREVIATION'], 'team_id': stat['TEAM_ID'],
                  'gp': stat['GP'], 'mpg': stat['MIN'], 'ppg': stat['PTS'],
                  'rpg': stat['REB'], 'apg': stat['AST'],
                  'spg': stat['STL'] if year >= 1973 else None,
                  'bpg': stat['BLK'] if year >= 1973 else None,
                  'jersey': jersey, 'all_nba': nba[season].get(key),
                  'all_defense': defense.get(season, {}).get(key),
                  'champion': stat['TEAM_ID'] == champ_tid}
        award_row = award_history.get((season, key), {})
        fields.update({k: award_row.get(k, None if k == 'dpoy' and year < 1982 else False)
                       for k in ('mvp', 'dpoy', 'roy')})
        fields['jersey_display'] = next(iter(numbers)) if len(numbers) == 1 else None
        recorded_fields = ('gp', 'mpg', 'ppg', 'rpg', 'apg') + (('spg', 'bpg') if year >= 1973 else ())
        missing_stats = [field for field in recorded_fields if fields[field] is None]
        if missing_stats:
            failures.append(f'Unresolved recorded stats {pool} {season} {old["player"]}: {missing_stats}')
        for field, value in fields.items():
            if field in old and old[field] is not None and old[field] != value:
                differences.append({'pool': pool, 'season': season, 'player': old['player'],
                                    'field': field, 'before': old[field], 'after': value})
        evidence.append({'pool': pool, **fields, 'verification_status': 'official_verified' if jersey is not None and not missing_stats else 'verification_pending',
                         'sources': {'stats': url, 'jersey': roster_url,
                                     'all_nba': HISTORY_URLS['all_nba'],
                                     'all_defense': HISTORY_URLS['all_defense'],
                                     'champion': HISTORY_URLS['champions']},
                         'award_sources': award_row.get('award_sources', {}),
                         'official_stat_row': stat,
                         'official_roster_rows': matches})
    output = ROOT / 'data/goat/official_verification.json'
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'requested': len(selected),
              'verified': sum(r['verification_status'] == 'official_verified' for r in evidence),
              'failures': failures, 'differences': differences,
              'notes': ['Jersey evidence is the NBA team-season roster snapshot; ambiguous values remain unresolved.',
                        'Pre-1973 defensive API zeros are deliberately replaced by null/not_recorded.',
                        'All-NBA and defense entries are exact actual tiers, not cumulative scoring previews.']}
    (ROOT / 'data/goat/verification_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'differences'}, indent=2), flush=True)
    print(f'Differences: {len(differences)}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=4)
    run(parser.parse_args().workers)
