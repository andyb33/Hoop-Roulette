"""Collect stats-only historical staging data; does not enable seasons in-game."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent


def collect(season):
    year = int(season[:4])
    if season != f"{year}-{str(year + 1)[-2:]}":
        raise ValueError("Use season format YYYY-YY")
    url = f"https://github.com/sportsdataverse/sportsdataverse-data/releases/download/nba_stats_player_boxscores/player_boxscores_{year + 1}.csv"
    raw = ROOT / f"data/raw/{season}/player_boxscores_{year + 1}.csv"
    raw.parent.mkdir(parents=True, exist_ok=True)
    if not raw.exists():
        with urlopen(Request(url, headers={"User-Agent": "Hoopreel"}), timeout=45) as response:
            raw.write_bytes(response.read())
    groups, games, seen = {}, set(), set()
    with raw.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            game_id = row["game_id"].zfill(10)
            if not game_id.startswith(f"002{str(year)[-2:]}"):
                continue
            games.add(game_id)
            if not row["minutes"]:
                continue
            minutes, seconds = row["minutes"].split(":")
            played_seconds = int(minutes) * 60 + int(seconds)
            if played_seconds <= 0:
                continue
            player_id, team_id = int(row["person_id"]), int(row["team_id"])
            appearance = (game_id, team_id, player_id)
            if appearance in seen:
                raise ValueError(f"Duplicate box-score appearance: {appearance}")
            seen.add(appearance)
            key = (team_id, player_id)
            if key not in groups:
                groups[key] = {"season": season, "player_id": player_id,
                               "player": f"{row['first_name']} {row['family_name']}",
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
                     "mpg": round(mpg, 1), **{stat: round(record[field] / gp, 1) for stat, field in
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
