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
REFERENCES.update({
    season: {
        "url": f"https://raw.githubusercontent.com/dataprofessor/data/087cb5383af3b09e68f6eeb00dea8819c1340de0/{filename}",
        "provenance": "https://github.com/dataprofessor/data/tree/087cb5383af3b09e68f6eeb00dea8819c1340de0",
        "primary": f"https://www.basketball-reference.com/leagues/NBA_{int(season[:4])+1}_per_game.html",
        "note": "Archived Basketball Reference per-game table; retains separate traded-player team stints.",
    }
    for season, filename in [("2020-21", "NBA_2021.csv"), ("2019-20", "NBA_2020.csv"), ("2018-19", "nba-player-stats-2019.csv")]
})
SCHEDULES = {"2020-21": (1080, 72), "2019-20": (1059, None), "2018-19": (1230, 82)}

REFERENCES.update({season: {
    "url": "https://raw.githubusercontent.com/favourumeh/NBA-DATA-PIPELINE/a19c7d43b65028d80c782ce64d308ed392c57bbf/1990_2021_NBA_ppg_stats.xlsx",
    "format": "xlsx", "year": int(season[:4])+1,
    "provenance": "https://github.com/favourumeh/NBA-DATA-PIPELINE/blob/a19c7d43b65028d80c782ce64d308ed392c57bbf/NBA_webscraping_OOP.py",
    "primary": f"https://www.basketball-reference.com/leagues/NBA_{int(season[:4])+1}_per_game.html",
    "note": "Independently scraped Basketball Reference workbook. Producer removes TOT rows but retains individual team stints; season selected by ending Year."
} for season in ("2017-18", "2016-17", "2015-16", "2014-15", "2013-14", "2012-13", "2011-12", "2010-11", "2009-10", "2008-09", "2007-08")})
SCHEDULES.update({s:(1230,82) for s in ("2017-18", "2016-17", "2015-16", "2014-15", "2013-14", "2012-13", "2011-12", "2010-11")})


def extract_reference_workbook(path, year, output):
    import zipfile
    import xml.etree.ElementTree as ET
    ns={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        strings=["".join(node.itertext()) for node in ET.fromstring(archive.read("xl/sharedStrings.xml")).findall("m:si",ns)]
        rows=ET.fromstring(archive.read("xl/worksheets/sheet1.xml")).findall("m:sheetData/m:row",ns)
        values=[]
        for row in rows:
            cells={}
            for cell in row:
                col=re.match(r"[A-Z]+",cell.attrib["r"])[0]
                index=0
                for letter in col:index=index*26+ord(letter)-64
                value=cell.find("m:v",ns)
                text=value.text if value is not None else ""
                if cell.get("t")=="s":text=strings[int(text)]
                cells[index-1]=text
            values.append(cells)
        headings=[values[0].get(i,"") for i in range(max(values[0])+1)]
        selected=[]
        for cells in values[1:]:
            record={heading:cells.get(i,"") for i,heading in enumerate(headings)}
            if record.get("Year")==str(year):selected.append(record)
    if not selected:raise ValueError("Reference workbook has no rows for season")
    with output.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=headings);writer.writeheader();writer.writerows(selected)

SCHEDULES["2011-12"] = (990, 66)
SCHEDULES.update({s: (1230, 82) for s in ("2009-10", "2008-09", "2007-08")})
SCHEDULES["2012-13"] = (1229, None)  # NBA schedule: BOS/IND 81 games, all other teams 82.

FIELDS = {"gp": "G", "mpg": "MP", "ppg": "PTS", "rpg": "TRB", "apg": "AST", "spg": "STL", "bpg": "BLK"}
TEAM_ALIASES = {"BRK": "BKN", "CHO": "CHA", "PHO": "PHX"}


def name_key(name):
    # This older workbook decoded UTF-8 names as Windows-1252/Latin-1.
    # Reverse only valid byte sequences; retain the raw name in audit evidence.
    if any(marker in name for marker in ("Ã", "Ä", "Å", "Â")):
        try:
            parts=[]
            for char in name:
                try:parts.append(char.encode("cp1252"))
                except UnicodeEncodeError:parts.append(bytes([ord(char)]))
            name=b"".join(parts).decode("utf-8")
        except (UnicodeError,ValueError):
            pass
    text = unicodedata.normalize("NFKD", name.replace("ı", "i")).encode("ascii", "ignore").decode().lower().rstrip("*").strip()
    text = re.sub(r"\b(jr|sr|ii|iii|iv)\.?$", "", text).strip()
    text = re.sub("[^a-z0-9]", "", text)
    return {"jianlianyi": "yijianlian", "jefferytaylor": "jefftaylor", "nenehilario": "nene", "juanhernangomez": "juanchohernangomez", "enesfreedom": "eneskanter", "wesiwundu": "wesleyiwundu", "kjmartin": "kenyonmartin", "bogdanbogdanovi": "bogdanbogdanovic",
            "bojanbogdanovi": "bojanbogdanovic", "lukadoni": "lukadoncic",
            "nikolajoki": "nikolajokic", "jusufnurki": "jusufnurkic",
            "kristapsporziis": "kristapsporzingis", "alperenengun": "alperensengun",
            "jonasvalaninas": "jonasvalanciunas", "nikolavuevi": "nikolavucevic",
            "tomassatoransk": "tomassatoransky", "flipmurray": "ronaldmurray", "mingyao": "yaoming"}.get(text, text)


def verify(season):
    source = REFERENCES[season]
    raw = ROOT / f"data/raw/{season}"
    ref_path = raw / "reference/reference.csv"
    workbook_sha256 = None
    if source.get("format") == "xlsx":
        workbook_path = raw / "reference/reference.xlsx"
        workbook_path.parent.mkdir(parents=True, exist_ok=True)
        if not workbook_path.exists():
            with urlopen(Request(source["url"], headers={"User-Agent":"Hoopreel"}), timeout=45) as response:
                workbook_path.write_bytes(response.read())
        workbook_sha256 = hashlib.sha256(workbook_path.read_bytes()).hexdigest()
        extract_reference_workbook(workbook_path, source["year"], ref_path)
    if not ref_path.exists():
        ref_path.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(Request(source["url"], headers={"User-Agent": "Hoopreel"}), timeout=30) as response:
            ref_path.write_bytes(response.read())
    try:
        reference_text = ref_path.read_bytes().decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        reference_text = ref_path.read_bytes().decode("cp1252", errors="strict")
    dialect = csv.excel if source.get("format") == "xlsx" else csv.Sniffer().sniff("\n".join(reference_text.splitlines()[:10]), delimiters=",;")
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
    records = json.loads(data_path.read_text(encoding="utf-8"))
    manifest_path = ROOT / f"data/staging/stats_{slug}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
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
            elif season == "2015-16" and row["player_id"] == 2419 and row["team"] == "MIN" and field == "apg" and row[field] == 1.0 and float(ref[column]) == 0.9:
                proof=json.loads((ROOT/"data/staging/stats_2015_16_official_resolution.json").read_text(encoding="utf-8"))
                official=proof["official_row"]
                from decimal import Decimal, ROUND_HALF_UP
                official_apg=float((Decimal(official["AST"])/Decimal(official["GP"])).quantize(Decimal("0.1"),rounding=ROUND_HALF_UP))
                if official["PLAYER_ID"] != row["player_id"] or official["SEASON_ID"] != season or official["TEAM_ABBREVIATION"] != row["team"] or official["GP"] != row["gp"] or official_apg != row[field]:
                    errors.append("Official Prince resolution does not match staged record")
                else:
                    item["resolution"]=proof["resolution"]
                    item["resolution_source"]=proof["source"]
                    item["official_total_evidence"]=official
                    item["official_source_sha256"]=proof["source_sha256"]
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
    schedule_evidence = None
    expected_games, expected_team_games = SCHEDULES.get(season, (1230, 82))
    if season in SCHEDULES:
        from urllib.parse import urlencode
        schedule_url = "https://stats.nba.com/stats/leaguegamefinder?" + urlencode({"LeagueID": "00", "Season": season, "SeasonType": "Regular Season"})
        schedule_path = raw / "reference/official_schedule.json"
        if not schedule_path.exists():
            with urlopen(Request(schedule_url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.nba.com/"}), timeout=45) as response:
                schedule_path.write_bytes(response.read())
        payload = json.loads(schedule_path.read_text(encoding="utf-8"))
        result = next(r for r in payload["resultSets"] if r["name"] == "LeagueGameFinderResults")
        official_games, official_team_games = defaultdict(set), defaultdict(set)
        for values in result["rowSet"]:
            item = dict(zip(result["headers"], values))
            if not item["GAME_ID"].startswith(f"002{season[2:4]}"):
                continue
            official_games[item["GAME_ID"]].add(item["TEAM_ABBREVIATION"])
            official_team_games[item["TEAM_ABBREVIATION"]].add(item["GAME_ID"])
        if dict(official_games) != dict(games) or dict(official_team_games) != dict(team_games):
            errors.append("Source game IDs and team appearances differ from official NBA schedule")
        schedule_evidence = {"source": schedule_url, "sha256": hashlib.sha256(schedule_path.read_bytes()).hexdigest(),
                             "matches": dict(official_games) == dict(games),
                             "team_games": {t: len(v) for t, v in sorted(official_team_games.items())}}
    if len(games) != expected_games or len(team_games) != 30 or any(len(t) != 2 for t in games.values()):
        errors.append(f"Expected {expected_games} games, two teams per game, and all 30 teams")
    if expected_team_games is not None and any(len(g) != expected_team_games for g in team_games.values()):
        errors.append(f"Expected {expected_team_games} games for every team")
    if season == "2012-13" and {t: len(g) for t, g in team_games.items()} != {t: (81 if t in ("BOS", "IND") else 82) for t in team_games}:
        errors.append("Expected BOS/IND 81 games and the remaining 28 teams 82")
    report = {"season": season, "passed": not errors, "scope": "Stats-only; jerseys and accolades not yet verified",
              "records_checked": len(records), "fields_per_record": 7, "stat_comparisons": len(evidence)*7,
              "reference_workbook_sha256": workbook_sha256, "reference": source, "reference_sha256": hashlib.sha256(ref_path.read_bytes()).hexdigest(),
              "staged_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
              "eligibility_sets_match": expected == actual, "all_30_teams_have_82_games": all(len(g)==82 for g in team_games.values()) and len(team_games)==30,
              "schedule_evidence": schedule_evidence, "regular_season_games": len(games), "cutoff_boundary_resolutions": borderline, "resolved_differences": resolutions, "errors": errors,
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
