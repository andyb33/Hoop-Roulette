#!/usr/bin/env python3
"""Export distinct GOAT pools; never modify or enable the live normal pool."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def identity(row, pool):
    row = dict(row)
    row['pool'] = pool
    row['game_player_id'] = f"{pool}:{row['player_id']}"
    row['entry_id'] = f"{row['game_player_id']}:{row['season']}:{row['team']}"
    return row


def build():
    awards = []
    seasons = []
    for path in sorted((ROOT / 'data/game').glob('players_20*.json')):
        rows = json.loads(path.read_text())
        seasons.append(rows[0]['season'])
        for row in rows:
            if any(row[k] for k in ('mvp', 'dpoy', 'roy')):
                entry = identity(row, 'award')
                entry['canonical_record'] = f"{row['player_id']}:{row['season']}:{row['team']}"
                entry['source'] = str(path.relative_to(ROOT))
                awards.append(entry)
    prehistoric = [identity(r, 'prehistoric') for r in
                   json.loads((ROOT / 'data/goat/prehistoric_candidates.json').read_text())]
    assert len({r['player_id'] for r in prehistoric}) == len(prehistoric)
    assert all(int(r['season'][:4]) < 1973 for r in prehistoric)
    assert all(r['spg'] is None and r['bpg'] is None for r in prehistoric)
    for pool, rows in [('award', awards), ('prehistoric', prehistoric)]:
        assert len({r['entry_id'] for r in rows}) == len(rows)
        (ROOT / f'data/goat/{pool}_jackpot.json').write_text(
            json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    manifest = {'schema_version': 1, 'enabled_in_game': False,
                'jackpot_probability': {'numerator': 1, 'denominator': 1296},
                'pool_weights': {'award': 1, 'prehistoric': 1},
                'award': {'count': len(awards), 'covered_seasons': seasons,
                          'target_start': '1973-74', 'historical_coverage_complete': False},
                'prehistoric': {'count': len(prehistoric),
                               'status': 'draft: historical jerseys and accolades require audit'}}
    (ROOT / 'data/goat/manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    (ROOT / 'data/goat').mkdir(parents=True, exist_ok=True)
    build()
