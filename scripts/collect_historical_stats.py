"""Collect stats-only historical staging data; does not enable seasons in-game."""
import argparse
import csv
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent


def source_seconds(minutes):
    if ':' in minutes:
        whole, seconds = minutes.split(':')
        return int(whole) * 60 + int(seconds)
    value = Decimal(minutes) * 60
    if value != value.to_integral_value():
        raise ValueError('Source minute value cannot be represented as seconds')
    return int(value)


def rounded_rate(total, games):
    return float((Decimal(total) / Decimal(games)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def require_previous_verified(season):
    year = int(season[:4])
    if year == 2022:
        return
    if not 1998 <= year < 2022:
        raise ValueError("This staging batch covers 1998–99 through 2022–23")
    previous_slug = f"{year + 1}_{str(year + 2)[-2:]}"
    report_path = ROOT / f"data/staging/stats_{previous_slug}_verification.json"
    data_path = ROOT / f"data/staging/stats_{previous_slug}.json"
    if not report_path.exists() or not data_path.exists():
        raise ValueError("Verify the preceding season before collecting this one")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not report.get("passed") or report.get("staged_sha256") != hashlib.sha256(data_path.read_bytes()).hexdigest():
        raise ValueError("Preceding season verification failed or is stale; resolve it first")


def collect(season):
    year = int(season[:4])
    if season != f"{year}-{str(year + 1)[-2:]}":
        raise ValueError("Use season format YYYY-YY")
    require_previous_verified(season)
    url = f"https://github.com/sportsdataverse/sportsdataverse-data/releases/download/nba_stats_player_boxscores/player_boxscores_{year + 1}.csv"
    raw = ROOT / f"data/raw/{season}/player_boxscores_{year + 1}.csv"
    corrections_path = ROOT / f"data/staging/stats_{season.replace('-', '_')}_source_corrections.json"
    corrections = json.loads(corrections_path.read_text(encoding='utf-8')) if corrections_path.exists() else {}
    if corrections:
        assert corrections['season'] == season
    raw.parent.mkdir(parents=True, exist_ok=True)
    if not raw.exists():
        with urlopen(Request(url, headers={"User-Agent": "Hoopreel"}), timeout=45) as response:
            raw.write_bytes(response.read())
    groups, games, seen, whole_minute_rows = {}, set(), set(), []
    with raw.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            game_id = row["game_id"].zfill(10)
            if not game_id.startswith(f"002{str(year)[-2:]}"):
                continue
            games.add(game_id)
            if not row["minutes"]:
                continue
            played_seconds = source_seconds(row['minutes'])
            if ':' not in row['minutes']:
                whole_minute_rows.append({k: row[k] for k in ('game_id','team_tricode','person_id','minutes')})
            # A recorded 0:00 appearance still counts toward GP. DNP rows have no minutes.
            player_id, team_id = int(row["person_id"]), int(row["team_id"])
            appearance = (game_id, team_id, player_id)
            if appearance in seen:
                raise ValueError(f"Duplicate box-score appearance: {appearance}")
            seen.add(appearance)
            key = (team_id, player_id)
            if key not in groups:
                groups[key] = {"season": season, "player_id": player_id,
                               "player": "Yao Ming" if player_id == 2397 else "Steve Smith" if player_id == 120 else "Clarence Weatherspoon" if player_id == 221 else f"{row['first_name']} {row['family_name']}",
                               "team": row["team_tricode"], "gp": 0, "seconds": 0,
                               "points": 0, "rebounds_total": 0, "assists": 0, "steals": 0, "blocks": 0}
            record = groups[key]
            record["gp"] += 1
            record["seconds"] += played_seconds
            for field in ("points", "rebounds_total", "assists", "steals", "blocks"):
                record[field] += int(float(row[field]))
    for proof in corrections.get('missing_appearances', []):
        r = proof['official_row']
        assert r['SEASON_ID'] == f'2{year}' and r['PLAYER_ID'] == proof['player_id'] and r['MATCHUP'].split()[0] == proof['team']
        appearance = (r['GAME_ID'], proof['team_id'], proof['player_id'])
        assert r['GAME_ID'] in games and appearance not in seen
        seen.add(appearance)
        g = groups[(proof['team_id'], proof['player_id'])]
        assert g['team'] == proof['team']
        g['gp'] += 1
        g['seconds'] += source_seconds(str(r['MIN']))
        for field, official_field in [('points','PTS'),('rebounds_total','REB'),('assists','AST'),('steals','STL'),('blocks','BLK')]:
            g[field] += r[official_field]
            assert g[field] == proof['official_season_row'][official_field]
        assert g['gp'] == proof['official_season_row']['GP']
    rows, rate_evidence = [], []
    for record in groups.values():
        gp = record["gp"]
        mpg = record["seconds"] / 60 / gp
        if gp < 30 or mpg < 15:
            continue
        rows.append({**{k: record[k] for k in ("season", "player_id", "player", "team", "gp")},
                     "mpg": rounded_rate(record["seconds"], 60 * gp), **{stat: rounded_rate(record[field], gp) for stat, field in
                     (("ppg", "points"), ("rpg", "rebounds_total"), ("apg", "assists"), ("spg", "steals"), ("bpg", "blocks"))}})
        for proof in corrections.get('rate_overrides', []):
            if (proof['player_id'],proof['team']) == (record['player_id'],record['team']):
                official = proof['official_row']
                assert (official['PLAYER_ID'],official['SEASON_ID'],official['TEAM_ABBREVIATION'],official['GP']) == (record['player_id'],season,record['team'],gp)
                assert official['MIN'] >= 15 * gp
                rate_evidence.append({'player_id':record['player_id'],'team':record['team'],'source_gp':gp,'source_seconds':record['seconds'],'source_unrounded_mpg':mpg,'source_display_mpg':rows[-1]['mpg'],'official_display_mpg':rounded_rate(official['MIN'],gp),'official_evidence':proof})
                rows[-1]['mpg'] = rounded_rate(official['MIN'], gp)
    assert len(rate_evidence) == len(corrections.get('rate_overrides', []))
    rows.sort(key=lambda r: (r["team"], r["player"]))
    if not rows:
        raise ValueError("No eligible staging records")
    output = ROOT / "data/staging"
    output.mkdir(parents=True, exist_ok=True)
    slug = season.replace("-", "_")
    (output / f"stats_{slug}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = {"season": season, "status": "stats_only_unverified", "enabled_in_game": False,
                "source": url, "source_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
                "regular_season_games_observed": len(games), "eligible_records": len(rows),
                "whole_minute_source_rows": whole_minute_rows,
                "source_corrections": corrections,
                "display_rate_overrides": rate_evidence,
                "eligibility": {"minimum_team_gp": 30, "minimum_team_mpg": 15},
                "eligibility_precision": "Unrounded box-score minutes per team stint",
                "records_by_team": {t: sum(r["team"] == t for r in rows) for t in sorted({r["team"] for r in rows})},
                "pending": ["Final team-stint jersey numbers", "Accolades and champions", "Independent source verification", "Distribution analysis", "Game activation"]}
    (output / f"stats_{slug}_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", default="2022-23")
    collect(parser.parse_args().season)
