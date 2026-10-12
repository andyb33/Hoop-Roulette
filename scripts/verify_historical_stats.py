"""Gate staged seasons against an independently scraped Basketball Reference table."""
import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
REFERENCES = {
    "2022-23": {
        "url": "https://raw.githubusercontent.com/rfhickey/nba_players_data/main/nba_2022_2023.csv",
        "provenance": "https://github.com/rfhickey/nba_players_data/blob/main/NBA_Players_Data_2022_2023.ipynb",
        "primary": "https://www.basketball-reference.com/leagues/NBA_2023_per_game.html",
    },
    "2021-22": {
        "url": "https://raw.githubusercontent.com/Raychun1/NBA_2022/main/2021-2022%20NBA%20Player%20Stats%20-%20Regular.csv",
        "provenance": "https://github.com/drjpeibol/NBA-Data-Project",
        "primary": "https://www.basketball-reference.com/leagues/NBA_2022_per_game.html",
    },
}
FIELDS = {"gp": "G", "mpg": "MP", "ppg": "PTS", "rpg": "TRB", "apg": "AST", "spg": "STL", "bpg": "BLK"}
TEAM_ALIASES = {"BRK": "BKN", "CHO": "CHA", "PHO": "PHX"}


def name_key(name):
    text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower().rstrip("*").strip()
    text = re.sub(r"\b(jr|sr|ii|iii|iv)\.?$", "", text).strip()
    text = re.sub("[^a-z0-9]", "", text)
    return {"kjmartin": "kenyonmartin", "bogdanbogdanovi": "bogdanbogdanovic",
            "bojanbogdanovi": "bojanbogdanovic", "lukadoni": "lukadoncic",
            "nikolajoki": "nikolajokic", "jusufnurki": "jusufnurkic",
            "kristapsporziis": "kristapsporzingis", "alperenengun": "alperensengun",
            "jonasvalaninas": "jonasvalanciunas", "nikolavuevi": "nikolavucevic",
            "tomassatoransk": "tomassatoransky"}.get(text, text)


def verify(season):
    source = REFERENCES[season]
    raw = ROOT / f"data/raw/{season}"
    ref_path = raw / "reference/reference.csv"
    if not ref_path.exists():
        ref_path.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(Request(source["url"], headers={"User-Agent": "Hoopreel"}), timeout=30) as response:
            ref_path.write_bytes(response.read())
    try:
        reference_text = ref_path.read_bytes().decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        reference_text = ref_path.read_bytes().decode("cp1252", errors="strict")
    dialect = csv.Sniffer().sniff(reference_text[:2000], delimiters=",;")
    reference = {}
    errors, differences, resolutions = [], [], []
    for row in csv.DictReader(reference_text.splitlines(), dialect=dialect):
        if not row["G"].isdigit() or row["Tm"] in ("TOT", "2TM", "3TM", "4TM"):
            continue
        key = (TEAM_ALIASES.get(row["Tm"], row["Tm"]), name_key(row["Player"]))
        if key in reference:
            errors.append(f"Duplicate independent reference key: {key}")
        reference[key] = row
    slug = season.replace("-", "_")
    data_path = ROOT / f"data/staging/stats_{slug}.json"
    records = json.loads(data_path.read_text())
    manifest_path = ROOT / f"data/staging/stats_{slug}_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    box_path = raw / f"player_boxscores_{int(season[:4])+1}.csv"
    if hashlib.sha256(box_path.read_bytes()).hexdigest() != manifest["source_sha256"]:
        errors.append("Raw box-score checksum changed")
    if len({(r["team"], r["player_id"]) for r in records}) != len(records):
        errors.append("Duplicate staged player-team key")
    actual = {(r["team"], name_key(r["player"])) for r in records}
    expected = {key for key, row in reference.items() if int(row["G"]) >= 30 and float(row["MP"]) >= 15}
    borderline = []
    # A table rounded to 15.0 MPG can include a stint strictly below the cutoff.
    for key in sorted(expected - actual):
        candidates = []
        for raw_row in csv.DictReader(box_path.open(encoding="utf-8", newline="")):
            if raw_row["game_id"].zfill(10).startswith(f"002{season[2:4]}") and raw_row["minutes"]:
                if (raw_row["team_tricode"], name_key(f"{raw_row['first_name']} {raw_row['family_name']}")) == key:
                    m, s = map(int, raw_row["minutes"].split(":"))
                    candidates.append(m * 60 + s)
        if candidates and len(candidates) == int(reference[key]["G"]) and float(reference[key]["MP"]) == 15 and 14.95 <= sum(candidates)/60/len(candidates) < 15:
            borderline.append({"team": key[0], "player": reference[key]["Player"], "gp": len(candidates), "seconds": sum(candidates), "unrounded_mpg": sum(candidates)/60/len(candidates), "decision": "Excluded: actual MPG below 15 despite reference display rounding to 15.0"})
            expected.remove(key)
    if expected != actual:
        errors.append({"eligibility_missing": sorted(expected-actual), "eligibility_unexpected": sorted(actual-expected)})
    evidence = []
    for row in records:
        ref = reference.get((row["team"], name_key(row["player"])))
        if ref is None:
            errors.append(f"Missing independent row: {row['team']} {row['player']}")
            continue
        evidence.append({"player_id": row["player_id"], "player": row["player"], "team": row["team"],
                         "reference_name": ref["Player"], "reference_stats": {f: float(ref[c]) for f, c in FIELDS.items()}})
        for field, column in FIELDS.items():
            difference = abs(row[field] - float(ref[column]))
            if difference < 0.000001:
                continue
            item = {"player": row["player"], "player_id": row["player_id"], "team": row["team"],
                    "field": field, "staged": row[field], "reference": float(ref[column])}
            differences.append(item)
            if field == "mpg" and difference <= 0.100001:
                item["resolution"] = "Retain second-precision NBA aggregate; reference minute rounding differs by 0.1. Eligibility sets agree."
            elif season == "2022-23" and row["player_id"] == 1631104 and field == "apg" and row[field] == 2.6 and float(ref[column]) == 2.7:
                item["resolution"] = "Archived reference is stale; current Basketball Reference page reports 98 assists / 37 GP = 2.6."
                item["resolution_source"] = "https://www.basketball-reference.com/players/w/weslebl01.html"
            else:
                errors.append(item)
            if "resolution" in item:
                resolutions.append(item)
    games, team_games, appearances = defaultdict(set), defaultdict(set), set()
    for row in csv.DictReader(box_path.open(encoding="utf-8", newline="")):
        game = row["game_id"].zfill(10)
        if not game.startswith(f"002{season[2:4]}"):
            continue
        games[game].add(row["team_tricode"])
        team_games[row["team_tricode"]].add(game)
        if row["minutes"]:
            appearance = (game, row["team_id"], row["person_id"])
            if appearance in appearances:
                errors.append(f"Duplicate source appearance: {appearance}")
            appearances.add(appearance)
    if len(games) != 1230 or len(team_games) != 30 or any(len(g) != 82 for g in team_games.values()) or any(len(t) != 2 for t in games.values()):
        errors.append("Expected 1,230 games, two teams per game, and 82 games per each of 30 teams")
    report = {"season": season, "passed": not errors, "scope": "Stats-only; jerseys and accolades not yet verified",
              "records_checked": len(records), "fields_per_record": 7, "stat_comparisons": len(evidence)*7,
              "reference": source, "reference_sha256": hashlib.sha256(ref_path.read_bytes()).hexdigest(),
              "staged_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
              "eligibility_sets_match": expected == actual, "all_30_teams_have_82_games": all(len(g)==82 for g in team_games.values()) and len(team_games)==30,
              "regular_season_games": len(games), "cutoff_boundary_resolutions": borderline, "resolved_differences": resolutions, "errors": errors,
              "reference_evidence": evidence}
    (ROOT / f"data/staging/stats_{slug}_verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest["status"] = "stats_independently_checked" if report["passed"] else "stats_verification_failed"
    manifest["verification_report"] = f"data/staging/stats_{slug}_verification.json"
    if report["passed"]:
        manifest["pending"] = [p for p in manifest["pending"] if p != "Independent source verification"]
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("season", "passed", "records_checked", "stat_comparisons", "errors")}, indent=2))
    if errors:
        raise SystemExit("Verification failed: resolve errors before collecting the next season")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", choices=REFERENCES, default="2022-23")
    verify(parser.parse_args().season)
