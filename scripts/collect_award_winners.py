#!/usr/bin/env python3
"""Collect official NBA award history, retaining ties and merging player-seasons."""
import argparse
import html
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

from build_goat_datasets import ROOT, player_key

SOURCES = {
    'mvp': 'https://www.nba.com/news/history-mvp-award-winners',
    'roy': 'https://www.nba.com/news/history-rookie-of-the-year-winners',
    'dpoy': 'https://www.nba.com/news/history-defensive-player-of-the-year-winners',
}


def parse_award_html(content):
    result = []
    for paragraph in re.findall(r'<p(?:\s[^>]*)?>.*?</p>', content, re.DOTALL):
        line = html.unescape(re.sub('<[^>]*>', '', paragraph)).strip()
        match = re.match(r'(\d{4}[-–]\d{2})\s*(?:—|–|--)\s*(.*)', line)
        if not match:
            continue
        season = match[1].replace('–', '-')
        parts = re.sub(r'\s*\(Voting\).*', '', match[2]).split(', ')
        if len(parts) == 2:
            pairs = [parts]
        elif len(parts) == 4:
            pairs = [(parts[0], parts[2]), (parts[1], parts[3])]
        else:
            raise ValueError(f'Unrecognized award row: {line}')
        result.extend((season, name, team) for name, team in pairs)
    if not result:
        raise ValueError('No award rows found; source format may have changed')
    return result


def collect(cache_dir=None):
    winners = {}
    for award, url in SOURCES.items():
        if cache_dir:
            content = (Path(cache_dir) / f'{award}.html').read_text()
        else:
            with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30) as response:
                content = response.read().decode()
        for season, name, team in parse_award_html(content):
            key = (season, player_key(name))
            row = winners.setdefault(key, {
                'season': season, 'player_key': key[1],
                'player': 'Kareem Abdul-Jabbar' if name == 'Lew Alcindor' else name,
                'award_team': team, 'mvp': False, 'roy': False,
                'dpoy': None if int(season[:4]) < 1982 else False,
                'award_sources': {}, 'source_names': [],
            })
            row[award] = True
            row['award_sources'][award] = url
            if name not in row['source_names']:
                row['source_names'].append(name)
    rows = sorted(winners.values(), key=lambda row: (row['season'], row['player_key']))
    (ROOT / 'data/goat/award_winners_history.json').write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    print(f'Collected {len(rows)} unique award-winning player-seasons')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache-dir', help='Read saved mvp/roy/dpoy HTML instead of downloading')
    collect(parser.parse_args().cache_dir)
