#!/usr/bin/env python3
"""Export distinct GOAT pools; never modify or enable the live normal pool."""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def player_key(name):
    name = name.replace('Lew Alcindor', 'Kareem Abdul-Jabbar').replace('Ron Artest', 'Metta World Peace')
    name = name.replace('’', '').replace("'", '').replace('.', '')
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def identity(row, pool):
    row = dict(row)
    row['pool'] = pool
    row['game_player_id'] = f"{pool}:{row['player_id']}"
    row['entry_id'] = f"{row['game_player_id']}:{row['season']}"
    if pool != 'award':
        row['entry_id'] += f":{row['team']}"
    return row


def apply_verification(row, pool, evidence):
    key = (pool, row['season'], player_key(row['player']))
    verified = evidence.get(key)
    if not verified:
        return row
    row = dict(row)
    row.update({k: v for k, v in verified.items()
                if k not in ('pool', 'official_stat_row', 'official_roster_rows')})
    year = int(row['season'][:4])
    row['availability'] = {}
    for field in ('spg', 'bpg'):
        if year < 1973:
            row[field] = None
            row['availability'][field] = 'not_recorded'
    for field in ('all_nba', 'all_defense'):
        if row[field] is None:
            row['availability'][field] = ('award_not_introduced' if field == 'all_defense' and year < 1968
                                          else 'not_selected')
    if year < 1982:
        row['dpoy'] = None
        row['availability']['dpoy'] = 'award_not_introduced'
    if year < 1988:
        row['availability']['all_nba_third'] = 'award_not_introduced'
    if row['jersey'] is None:
        row['availability']['jersey'] = 'pending_verification'
    return row


def build():
    verification_path = ROOT / 'data/goat/official_verification.json'
    verified_rows = json.loads(verification_path.read_text()) if verification_path.exists() else []
    evidence = {(r['pool'], r['season'], r['player_key']): r for r in verified_rows}
    canonical = {}
    for path in sorted((ROOT / 'data/game').glob('players_20*.json')):
        rows = json.loads(path.read_text())
        for row in rows:
            if any(row[k] for k in ('mvp', 'dpoy', 'roy')):
                key = (row['season'], player_key(row['player']))
                if key in canonical:
                    raise ValueError(f'Award winner has multiple team stints; select the award team explicitly: {key}')
                canonical[key] = dict(row, source=str(path.relative_to(ROOT)))
    history = json.loads((ROOT / 'data/goat/award_winners_history.json').read_text())
    stats = {(r['season'], r['player_key']): r for r in
             json.loads((ROOT / 'data/goat/award_historical_stats.json').read_text())}
    awards = []
    for winner in history:
        if int(winner['season'][:4]) < 1973:
            continue
        key = (winner['season'], winner['player_key'])
        row = {'player_id': 'historical:' + winner['player_key'], 'team': None,
               **{k: None for k in ('gp', 'mpg', 'ppg', 'rpg', 'apg', 'spg', 'bpg',
                                    'jersey', 'all_nba', 'all_defense', 'champion')}}
        row.update(stats.get(key, {}))
        row.update(canonical.get(key, {}))
        row.update(winner)
        row['availability'] = {k: 'pending_verification' for k in
                               ('gp', 'mpg', 'ppg', 'rpg', 'apg', 'spg', 'bpg', 'jersey',
                                'all_nba', 'all_defense', 'champion') if row[k] is None}
        row['verification_status'] = 'canonical_verified' if key in canonical else 'winner_verified_enrichment_pending'
        if key in canonical:
            for field in ('all_nba', 'all_defense'):
                if row[field] is None:
                    row['availability'][field] = 'not_selected'
        if row['dpoy'] is None:
            row['availability']['dpoy'] = 'award_not_introduced'
        if int(row['season'][:4]) < 1988:
            row['availability']['all_nba_third'] = 'award_not_introduced'
        awards.append(identity(apply_verification(row, 'award', evidence), 'award'))
    seasons = sorted({r['season'] for r in awards})
    prehistoric = [identity(apply_verification(r, 'prehistoric', evidence), 'prehistoric') for r in
                   json.loads((ROOT / 'data/goat/prehistoric_candidates.json').read_text())]
    assert len({r['player_id'] for r in prehistoric}) == len(prehistoric)
    assert all(int(r['season'][:4]) < 1973 for r in prehistoric)
    assert all(r['spg'] is None and r['bpg'] is None for r in prehistoric)
    for pool, rows in [('award', awards), ('prehistoric', prehistoric)]:
        assert len({r['entry_id'] for r in rows}) == len(rows)
        (ROOT / f'data/goat/{pool}_jackpot.json').write_text(
            json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    manifest = {'schema_version': 1, 'enabled_in_game': all(r['verification_status'] == 'official_verified' for r in awards + prehistoric),
                'jackpot_probability': {'numerator': 1, 'denominator': 1296},
                'pool_weights': {'award': 1, 'prehistoric': 1},
                'award': {'count': len(awards), 'covered_seasons': seasons,
                          'target_start': '1973-74', 'winner_coverage_complete': True,
                          'historical_coverage_complete': all(r['verification_status'] == 'official_verified' for r in awards),
                          'archive_entries': len(history),
                          'stat_records_complete': sum(all(r[k] is not None for k in
                              ('gp', 'mpg', 'ppg', 'rpg', 'apg', 'spg', 'bpg')) for r in awards),
                          'game_ready_records': sum(r['verification_status'] in ('canonical_verified', 'official_verified') for r in awards)},
                'prehistoric': {'count': len(prehistoric),
                               'verified_records': sum(r['verification_status'] == 'official_verified' for r in prehistoric),
                               'status': 'official_verified' if all(r['verification_status'] == 'official_verified' for r in prehistoric)
                                         else 'draft: historical jerseys and accolades require audit'}}
    (ROOT / 'data/goat/manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    (ROOT / 'data/goat').mkdir(parents=True, exist_ok=True)
    build()
