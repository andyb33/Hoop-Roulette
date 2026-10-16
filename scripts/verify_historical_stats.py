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

try:
    from .collect_historical_stats import historical_team, rounded_rate
except ImportError:
    from collect_historical_stats import historical_team, rounded_rate

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
} for season in ("2017-18", "2016-17", "2015-16", "2014-15", "2013-14", "2012-13", "2011-12", "2010-11", "2009-10", "2008-09", "2007-08", "2006-07", "2005-06", "2004-05", "2003-04", "2002-03", "2001-02", "2000-01", "1999-00", "1998-99", "1997-98", "1996-97", "1995-96", "1994-95", "1993-94", "1992-93", "1991-92", "1990-91", "1989-90")})
REFERENCES.update({season: {
    "url": "https://raw.githubusercontent.com/illumitata/NBA/99fb55e641c7009ae729e502ebdade8c6ecb2b7f/data/Seasons_Stats.csv",
    "format": "historical_totals_csv", "season": season,
    "provenance": "https://www.kaggle.com/datasets/drgilermo/nba-players-stats",
    "primary": f"https://www.basketball-reference.com/leagues/NBA_{int(season[:4])+1}_per_game.html",
    "note": "Archived Basketball Reference totals from NBA Players stats since 1950; exact ending Year and individual traded-player stints retained. Rates derive from original totals with decimal half-up rounding; original archive and selected totals preserved."
} for season in ("1988-89", "1987-88", "1986-87", "1985-86", "1984-85", "1983-84", "1982-83", "1981-82", "1980-81")})
SCHEDULES.update({"1988-89": (1025,82), "1987-88": (943,82), "1986-87": (943,82), "1985-86": (943,82), "1984-85": (943,82), "1983-84": (943,82), "1982-83": (943,82), "1981-82": (943,82), "1980-81": (943,82)})


def extract_reference_csv(path, season, output):
    from decimal import Decimal
    selected=[]
    with path.open(encoding="utf-8-sig",newline="") as handle:
        for r in csv.DictReader(handle):
            if r["Year"] != str(int(season[:4])+1):continue
            gp=Decimal(r["G"])
            if gp != gp.to_integral_value() or gp<=0:raise ValueError("Invalid independent games count")
            row={"Player":r["Player"],"Tm":r["Tm"],"G":str(int(gp)),"reference_key_name":r["Player"],"original_age":r["Age"],"original_archive_index":r[""]}
            # Two different Charles Joneses shared WSB. Preserve both original names;
            # the younger player's GP/minutes match NBA ID 77178, not eligible ID 279.
            if (season,r["Tm"],r["Player"],r["Age"])==("1988-89","WSB","Charles Jones","27"):
                row["reference_key_name"]="Charles Jones [77178]"
            for key in ("MP","PTS","TRB","AST","STL","BLK"):
                total=Decimal(r[key])
                row[key]=rounded_rate(total,int(gp))
                row["original_total_"+key]=r[key]
            selected.append(row)
    if not selected:raise ValueError("Independent archive has no rows for season")
    with output.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=selected[0]);writer.writeheader();writer.writerows(selected)


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
SCHEDULES.update({s: (1230, 82) for s in ("2009-10", "2008-09", "2007-08", "2006-07", "2005-06", "2004-05", "2003-04", "2002-03", "2001-02", "2000-01", "1999-00", "1998-99", "1997-98", "1996-97", "1995-96", "1994-95", "1993-94", "1992-93", "1991-92", "1990-91", "1989-90")})
SCHEDULES.update({s: (1189, 82) for s in ("2003-04", "2002-03", "2001-02", "2000-01", "1999-00", "1998-99", "1997-98", "1996-97", "1995-96", "1994-95", "1993-94", "1992-93", "1991-92", "1990-91", "1989-90")})
SCHEDULES["1998-99"] = (725, 50)
SCHEDULES.update({s:(1107,82) for s in ("1994-95","1993-94","1992-93","1991-92","1990-91","1989-90")})
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
            "tomassatoransk": "tomassatoransky", "flipmurray": "ronaldmurray", "mingyao": "yaoming", "michaelsweetney": "mikesweetney", "clarweatherspoon": "clarenceweatherspoon", "slavamedvedenko": "stanislavmedvedenko", "ikeaustin": "isaacaustin", "lafayettelever":"fatlever", "davidgreenwood":"davegreenwood", "garfieldheard":"garheard", "charleswhitney":"hawkeyewhitney", "janvanbredakolff":"janvan", "peterverhoeven":"peteverhoeven", "billyraybates":"billyray", "mitchellanderson":"jjanderson", "edmundsherod":"edsherod", "natearchibald":"tinyarchibald", "samuelwilliams":"samwilliams", "eddielee":"eddieleewilkins", "melvinturpin":"melturpin", "worldb":"worldfree", "worldbfree":"worldfree", "charlesdavis":"charliedavis", "michealray":"michealrayrichardson", "charlespittman":"charliepittman", "clifftrobinson":"cliffrobinson", "hotrod":"hotrodwilliams", "joebarry":"joebarrycarroll", "vinnydel":"vinnydelnegro", "michaelholton":"mikeholton", "dwaynewashington":"pearlwashington", "danschayes": "dannyschayes", "gheorghemureetman": "gheorghemuresan"}.get(text, text)


def verify(season):
    source = REFERENCES[season]
    raw = ROOT / f"data/raw/{season}"
    ref_path = raw / "reference/reference.csv"
    workbook_sha256 = None
    archive_sha256 = None
    if source.get("format") == "historical_totals_csv":
        archive_path=raw/"reference/original_totals_archive.csv"
        archive_path.parent.mkdir(parents=True,exist_ok=True)
        if not archive_path.exists():
            with urlopen(Request(source["url"],headers={"User-Agent":"Hoopreel"}),timeout=45) as response:archive_path.write_bytes(response.read())
        archive_sha256=hashlib.sha256(archive_path.read_bytes()).hexdigest()
        extract_reference_csv(archive_path,season,ref_path)
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
        key = (historical_team(season, TEAM_ALIASES.get(row["Tm"], row["Tm"])), name_key(row.get("reference_key_name",row["Player"])))
        if key in reference:
            errors.append(f"Duplicate independent reference key: {key}")
        reference[key] = row
    reference_identity_evidence=[]
    if season=="1988-89":
        reference_identity_evidence=json.loads((ROOT/'data/staging/reference_identity_1988_89_resolutions.json').read_text())
        for p in reference_identity_evidence:
            key_name="Charles Jones [77178]" if p['player_id']==77178 else "Charles Jones"
            ref=reference[("WSB",name_key(key_name))]
            assert int(ref['G'])==p['official_row']['GP']
            for col,official_col in [('MP','MIN'),('PTS','PTS'),('TRB','REB'),('AST','AST'),('STL','STL'),('BLK','BLK')]:
                assert int(ref['original_total_'+col])==p['official_row'][official_col]
    slug = season.replace("-", "_")
    data_path = ROOT / f"data/staging/stats_{slug}.json"
    records = json.loads(data_path.read_text(encoding="utf-8"))
    manifest_path = ROOT / f"data/staging/stats_{slug}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    box_path = raw / f"player_boxscores_{int(season[:4])+1}.csv"
    if hashlib.sha256(box_path.read_bytes()).hexdigest() != manifest["source_sha256"]:
        errors.append("Raw box-score checksum changed")
    if manifest.get('primary_payload_path'):
        if hashlib.sha256((ROOT/manifest['primary_payload_path']).read_bytes()).hexdigest() != manifest['primary_payload_sha256']:
            errors.append('Primary NBA game-log checksum changed')
    if len({(r["team"], r["player_id"]) for r in records}) != len(records):
        errors.append("Duplicate staged player-team key")
    for p in manifest.get('eligibility_source_overrides',[]):
        official=p['official_row'];ref=p['independent_reference_row']
        assert p['independent_archive_sha256']==archive_sha256
        key=(historical_team(season,TEAM_ALIASES.get(ref['Tm'],ref['Tm'])),name_key(ref['Player']))
        independent=reference[key]
        assert int(independent['G'])==int(ref['G'])==official['GP'] and int(independent['original_total_MP'])==int(ref['MP'])==official['MIN']
        assert p['decision']==('include' if official['GP']>=30 and official['MIN']>=15*official['GP'] else 'exclude')
    actual = {(r["team"], name_key(r["player"])) for r in records}
    expected = {key for key, row in reference.items() if int(row["G"]) >= 30 and float(row["MP"]) >= 15}
    borderline = []
    cutoff_path = ROOT / f'data/staging/stats_{slug}_cutoff_resolutions.json'
    cutoff_proofs = json.loads(cutoff_path.read_text(encoding='utf-8')) if cutoff_path.exists() else []
    # A table rounded to 15.0 MPG can include a stint strictly below the cutoff.
    for key in sorted(expected - actual):
        candidates = []
        candidate_ids = set()
        for raw_row in csv.DictReader(box_path.open(encoding="utf-8", newline="")):
            if raw_row["game_id"].zfill(10).startswith(f"002{season[2:4]}") and raw_row["minutes"]:
                if (historical_team(season, raw_row["team_tricode"]), name_key(f"{raw_row['first_name']} {raw_row['family_name']}")) == key:
                    try:
                        from .collect_historical_stats import source_seconds
                    except ImportError:
                        from collect_historical_stats import source_seconds
                    candidates.append(source_seconds(raw_row['minutes']))
                    candidate_ids.add(int(raw_row['person_id']))
        proof = None
        for p in cutoff_proofs:
            if candidate_ids == {p['player_id']} and p['team'] == key[0] and p['gp'] == len(candidates) and p['source_seconds'] == sum(candidates):
                official = p['official_row']
                assert p['season'] == season and official['PLAYER_ID'] == p['player_id'] and official['SEASON_ID'] == season
                assert official['TEAM_ABBREVIATION'] == key[0] and official['GP'] == len(candidates)
                assert official['MIN'] < 15 * official['GP'] and sum(candidates) < 900 * len(candidates)
                assert float(reference[key]['MP']) == p['reference_mpg'] and int(reference[key]['G']) == official['GP']
                proof = p
                break
        if proof:
            borderline.append(proof)
            expected.remove(key)
        elif candidates and len(candidates) == int(reference[key]["G"]) and float(reference[key]["MP"]) == 15 and 14.95 <= sum(candidates)/60/len(candidates) < 15:
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
                         "reference_name": ref["Player"], **({"original_reference_totals": {k: ref["original_total_"+k] for k in ("MP","PTS","TRB","AST","STL","BLK")}} if source.get("format")=="historical_totals_csv" else {}), "reference_stats": {f: float(ref[c]) for f, c in FIELDS.items()}})
        for field, column in FIELDS.items():
            difference = abs(row[field] - float(ref[column]))
            if difference < 0.000001:
                continue
            item = {"player": row["player"], "player_id": row["player_id"], "team": row["team"],
                    "field": field, "staged": row[field], "reference": float(ref[column])}
            differences.append(item)
            if season == '1996-97' and field == 'mpg' and row['player_id'] in (157,469,96,137):
                from decimal import Decimal, ROUND_HALF_UP
                proofs=json.loads((ROOT/'data/staging/stats_1996_97_official_resolutions.json').read_text())
                proof=next(p for p in proofs if (p['player_id'],p['team']) == (row['player_id'],row['team']))
                official=proof['official_row']
                assert (official['PLAYER_ID'],official['SEASON_ID'],official['TEAM_ABBREVIATION'],official['GP']) == (row['player_id'],season,row['team'],row['gp'])
                assert float((Decimal(official['MIN'])/Decimal(official['GP'])).quantize(Decimal('.1'),rounding=ROUND_HALF_UP)) == row[field]
                item.update(resolution=proof['resolution'],resolution_source=proof['source'],official_total_evidence=official,official_source_sha256=proof['source_sha256'])
            elif field == "mpg" and difference <= 0.100001:
                item["resolution"] = "Retain official whole-minute game-log aggregate; archived display rounding differs by 0.1. Eligibility sets agree." if manifest.get('source_format') == 'official_player_game_log' else "Retain second-precision NBA aggregate; reference minute rounding differs by 0.1. Eligibility sets agree."
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
            elif (season,row["player_id"],row["team"],field) in {("2004-05",2418,"NOH","mpg"), ("2001-02",702,"DEN","mpg")}:
                proof_path = "data/staging/stats_2004_05_jacobsen_official_resolution.json" if season == "2004-05" else "data/staging/stats_2001_02_702_official_resolution.json"
                proof=json.loads((ROOT/proof_path).read_text(encoding="utf-8"))
                official=proof["official_row"]
                from decimal import Decimal, ROUND_HALF_UP
                official_mpg=float((Decimal(official["MIN"])/Decimal(official["GP"])).quantize(Decimal("0.1"),rounding=ROUND_HALF_UP))
                if official["PLAYER_ID"] != row["player_id"] or official["SEASON_ID"] != season or official["TEAM_ABBREVIATION"] != row["team"] or official["GP"] != row["gp"] or official_mpg != row[field]:
                    errors.append("Official MPG resolution does not match staged record")
                else:
                    item.update(resolution=proof["resolution"], resolution_source=proof["source"], official_total_evidence=official, official_source_sha256=proof["source_sha256"])
            elif (season,row["player_id"],row["team"],field) in {("1987-88",77626,"MIL","bpg"),("1984-85",76876,"CHI","bpg")}:
                gp,blocks,independent_blocks={("1987-88",77626):(56,12,14),("1984-85",76876):(48,11,14)}[(season,row['player_id'])]
                proof=next(p for p in manifest['season_total_overrides'] if p['player_id']==row['player_id'] and p['team']==row['team'])
                assert proof['official_row']['GP']==row['gp']==gp and proof['official_row']['BLK']==proof['source_aggregate']['blocks']==blocks
                assert int(ref['original_total_BLK'])==independent_blocks and row[field]==rounded_rate(blocks,gp) and float(ref[column])==rounded_rate(independent_blocks,gp)
                item.update(resolution=f"Retain {blocks} blocks / {gp} GP from official NBA season totals and original game logs; independent Basketball Reference archive reports {independent_blocks}. Source disagreement remains explicit.",resolution_source=proof['source'],official_total_evidence=proof['official_row'],official_source_sha256=proof['source_sha256'],independent_total=independent_blocks)
            else:
                errors.append(item)
            if "resolution" in item:
                resolutions.append(item)
    games, team_games, appearances = defaultdict(set), defaultdict(set), set()
    for row in csv.DictReader(box_path.open(encoding="utf-8", newline="")):
        game = row["game_id"].zfill(10)
        if not game.startswith(f"002{season[2:4]}"):
            continue
        games[game].add(historical_team(season, row["team_tricode"]))
        team_games[historical_team(season, row["team_tricode"])].add(game)
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
        if int(season[:4]) < 1983:
            schedule_url = "https://stats.nba.com/stats/leaguegamelog?" + urlencode({"LeagueID":"00", "Season":season, "SeasonType":"Regular Season", "PlayerOrTeam":"T", "Counter":0, "Direction":"ASC", "Sorter":"DATE", "DateFrom":"", "DateTo":""})
        schedule_path = raw / "reference/official_schedule.json"
        if not schedule_path.exists():
            with urlopen(Request(schedule_url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.nba.com/"}), timeout=45) as response:
                schedule_path.write_bytes(response.read())
        payload = json.loads(schedule_path.read_text(encoding="utf-8"))
        result = next(r for r in payload["resultSets"] if r["name"] == ("LeagueGameLog" if int(season[:4]) < 1983 else "LeagueGameFinderResults"))
        official_games, official_team_games = defaultdict(set), defaultdict(set)
        for values in result["rowSet"]:
            item = dict(zip(result["headers"], values))
            if not item["GAME_ID"].startswith(f"002{season[2:4]}"):
                continue
            official_games[item["GAME_ID"]].add(historical_team(season, item["TEAM_ABBREVIATION"]))
            official_team_games[historical_team(season,item["TEAM_ABBREVIATION"])].add(item["GAME_ID"])
        if dict(official_games) != dict(games) or dict(official_team_games) != dict(team_games):
            errors.append("Source game IDs and team appearances differ from official NBA schedule")
        schedule_evidence = {"source": schedule_url, "sha256": hashlib.sha256(schedule_path.read_bytes()).hexdigest(),
                             "matches": dict(official_games) == dict(games),
                             "team_games": {t: len(v) for t, v in sorted(official_team_games.items())}}
    expected_teams = 23 if int(season[:4]) < 1988 else 25 if int(season[:4]) == 1988 else 27 if int(season[:4]) < 1995 else 29 if int(season[:4]) < 2004 else 30
    if len(games) != expected_games or len(team_games) != expected_teams or any(len(t) != 2 for t in games.values()):
        errors.append(f"Expected {expected_games} games, two teams per game, and all {expected_teams} teams")
    if expected_team_games is not None and any(len(g) != expected_team_games for g in team_games.values()):
        errors.append(f"Expected {expected_team_games} games for every team")
    if season == "2012-13" and {t: len(g) for t, g in team_games.items()} != {t: (81 if t in ("BOS", "IND") else 82) for t in team_games}:
        errors.append("Expected BOS/IND 81 games and the remaining 28 teams 82")
    report = {"season": season, "passed": not errors, "scope": "Stats-only; jerseys and accolades not yet verified",
              "records_checked": len(records), "fields_per_record": 7, "stat_comparisons": len(evidence)*7,
              "reference_workbook_sha256": workbook_sha256, "reference_archive_sha256": archive_sha256,
              "reference_identity_evidence": reference_identity_evidence, "reference_identity_resolutions": [{k:r[k] for k in ("Player","Tm","G","reference_key_name","original_age","original_archive_index","original_total_MP")} for r in reference.values() if r.get("reference_key_name",r["Player"])!=r["Player"]], "reference": source, "reference_sha256": hashlib.sha256(ref_path.read_bytes()).hexdigest(),
              "staged_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
              "eligibility_sets_match": expected == actual, "all_30_teams_have_82_games": all(len(g)==82 for g in team_games.values()) and len(team_games)==30,
              "schedule_evidence": schedule_evidence, "regular_season_games": len(games), "eligibility_source_resolutions": manifest.get("eligibility_source_overrides",[]), "cutoff_boundary_resolutions": borderline, "resolved_differences": resolutions, "errors": errors,
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
