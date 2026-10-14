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
    if not 2001 <= year < 2022:
        raise ValueError("This staging batch covers 2001–02 through 2022–23")
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
    rows = []
    for record in groups.values():
        gp = record["gp"]
        mpg = record["seconds"] / 60 / gp
        if gp < 30 or mpg < 15:
            continue
        rows.append({**{k: record[k] for k in ("season", "player_id", "player", "team", "gp")},
                     "mpg": rounded_rate(record["seconds"], 60 * gp), **{stat: rounded_rate(record[field], gp) for stat, field in
                     (("ppg", "points"), ("rpg", "rebounds_total"), ("apg", "assists"), ("spg", "steals"), ("bpg", "blocks"))}})
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
