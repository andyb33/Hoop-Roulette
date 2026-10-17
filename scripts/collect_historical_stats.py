"""Collect stats-only historical staging data; does not enable seasons in-game."""
import argparse
import csv
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode

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


def historical_team(season, team):
    team = {"GOS":"GSW", "PHL":"PHI", "SAN":"SAS", "UTH":"UTA"}.get(team, team)
    if team == "OKC" and int(season[:4]) < 2008:
        return "SEA"
    if team == "UTA" and int(season[:4]) < 1979:
        return "NOJ"
    if team == "LAC" and int(season[:4]) < 1978:
        return "BUF"
    if team == "LAC" and int(season[:4]) < 1984:
        return "SDC"
    if team == "SAC" and int(season[:4]) < 1985:
        return "KCK"
    return "WSB" if team == "WAS" and int(season[:4]) < 1997 else team


def primary_game_log(season, raw):
    """Deterministic adapter; retain the original payload and nullable statistics."""
    from complete_historical_seasons import fetch, table
    url = 'https://stats.nba.com/stats/leaguegamelog?' + urlencode(dict(LeagueID='00',Season=season,SeasonType='Regular Season',PlayerOrTeam='P',Counter=0,Direction='ASC',Sorter='DATE',DateFrom='',DateTo=''))
    payload=fetch(url)
    original=raw.parent/'official_player_game_log.json'
    original.write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
    rows=table(payload,'LeagueGameLog')
    fields=['game_id','team_id','team_tricode','person_id','first_name','family_name','minutes','points','rebounds_total','assists','steals','blocks']
    nullable=[]
    with raw.open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader()
        for r in sorted(rows,key=lambda r:(r['GAME_ID'],r['TEAM_ID'],r['PLAYER_ID'])):
            first,_,family=r['PLAYER_NAME'].partition(' ')
            out=dict(game_id=r['GAME_ID'],team_id=r['TEAM_ID'],team_tricode=r['TEAM_ABBREVIATION'],person_id=r['PLAYER_ID'],first_name=first,family_name=family,minutes=r['MIN'])
            for field,src in [('points','PTS'),('rebounds_total','REB'),('assists','AST'),('steals','STL'),('blocks','BLK')]:out[field]=r[src]
            missing=[f for f in fields if out[f] is None]
            if missing:nullable.append(dict(game_id=r['GAME_ID'],player_id=r['PLAYER_ID'],missing_fields=missing))
            writer.writerow(out)
    return url,dict(source_format='official_player_game_log',primary_payload_path=str(original.relative_to(ROOT)),primary_payload_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),primary_player_appearances=len(rows),nullable_source_rows=nullable)


def require_previous_verified(season):
    year = int(season[:4])
    if year == 2022:
        return
    if not 1973 <= year < 2022:
        raise ValueError("This staging batch covers 1973–74 through 2022–23")
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
    primary_metadata={}
    if year <= 1995:
        url,primary_metadata=primary_game_log(season,raw)
    elif not raw.exists():
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
                               "team": historical_team(season, row["team_tricode"]), "gp": 0, "seconds": 0,
                               "points": 0, "rebounds_total": 0, "assists": 0, "steals": 0, "blocks": 0}
            record = groups[key]
            record["gp"] += 1
            record["seconds"] += played_seconds
            for field in ("points", "rebounds_total", "assists", "steals", "blocks"):
                record[field] = None if row[field] == '' or record[field] is None else record[field] + int(float(row[field]))
    for proof in corrections.get('missing_appearances', []):
        r = proof['official_row']
        if proof.get('identity_resolution'):
            identity=proof['identity_resolution'];original={k.upper():v for k,v in proof['original_response_row'].items()}
            assert (identity['season'],identity['canonical_player_id'],original['PLAYER_ID']) == (season,proof['player_id'],identity['legacy_player_id'])
            assert {k:v for k,v in r.items() if k != 'PLAYER_ID'} == {k:v for k,v in original.items() if k != 'PLAYER_ID'}
            assert {'GP','MIN','PTS','AST','STL','BLK'} <= set(identity['matched_fields'])
            assert all(identity['legacy_aggregate'][f] == identity['canonical_official_row'][f] for f in identity['matched_fields'])
        assert r['SEASON_ID'] == f'2{year}' and r['PLAYER_ID'] == proof['player_id'] and r['MATCHUP'].split()[0] == proof['team']
        appearance = (r['GAME_ID'], proof['team_id'], proof['player_id'])
        assert r['GAME_ID'] in games and appearance not in seen
        seen.add(appearance)
        key=(proof['team_id'],proof['player_id'])
        if key not in groups:
            groups[key]=dict(season=season,player_id=proof['player_id'],player=proof['player'],team=proof['team'],gp=0,seconds=0,points=0,rebounds_total=0,assists=0,steals=0,blocks=0)
        g = groups[key]
        assert g['team'] == proof['team']
        g['gp'] += 1
        g['seconds'] += source_seconds(str(r['MIN']))
        for field, official_field in [('points','PTS'),('rebounds_total','REB'),('assists','AST'),('steals','STL'),('blocks','BLK')]:
            g[field] = None if r[official_field] is None or g[field] is None else g[field]+r[official_field]
    for proof in corrections.get('stat_total_overrides', []):
        official=proof['official_row'];g=groups[(official['TEAM_ID'],proof['player_id'])]
        assert (official['PLAYER_ID'],official['SEASON_ID'],official['TEAM_ABBREVIATION'],official['GP']) == (g['player_id'],season,g['team'],g['gp'])
        assert g[proof['field']] is None
        g[proof['field']]=official[proof['official_field']]
    for proof in corrections.get('missing_appearances', []):
        g=groups[(proof['team_id'],proof['player_id'])];official=proof['official_season_row']
        assert g['gp']==official['GP']
        for field,src in [('points','PTS'),('rebounds_total','REB'),('assists','AST'),('steals','STL'),('blocks','BLK')]:assert g[field]==official[src]
    rows, rate_evidence, total_evidence, eligibility_evidence = [], [], [], []
    for record in groups.values():
        gp = record["gp"]
        mpg = record["seconds"] / 60 / gp
        matches=[p for p in corrections.get('eligibility_source_overrides',[]) if (p['player_id'],p['team'])==(record['player_id'],record['team'])]
        assert len(matches)<=1
        if matches:
            proof=matches[0];official=proof['official_row'];independent=proof['independent_reference_row']
            assert (proof['season'],official['PLAYER_ID'],official['SEASON_ID'],historical_team(season,official['TEAM_ABBREVIATION']))==(season,record['player_id'],season,record['team'])
            assert proof['source_aggregate']=={f:record[f] for f in proof['source_aggregate']}
            assert int(independent['G'])==official['GP'] and int(independent['MP'])==official['MIN']
            included=official['GP']>=30 and official['MIN']>=15*official['GP']
            assert proof['decision']==('include' if included else 'exclude')
            assert not any((p['player_id'],p['team'])==(record['player_id'],record['team']) for p in corrections.get('season_total_overrides',[]))
            eligibility_evidence.append(proof)
            if not included:continue
            record=dict(record,gp=official['GP'],seconds=official['MIN']*60,**{f:official[c] for f,c in [('points','PTS'),('rebounds_total','REB'),('assists','AST'),('steals','STL'),('blocks','BLK')]})
            gp=record['gp'];mpg=record['seconds']/60/gp
        if gp < 30 or mpg < 15:
            continue
        for proof in corrections.get('season_total_overrides', []):
            if (proof['player_id'],proof['team']) == (record['player_id'],record['team']):
                official=proof['official_row']
                assert (official['PLAYER_ID'],official['SEASON_ID'],historical_team(season,official['TEAM_ABBREVIATION'])) == (record['player_id'],season,record['team'])
                assert proof['source_aggregate'] == {f:record[f] for f in proof['source_aggregate']}
                assert official['GP'] >= 30 and official['MIN'] >= 15*official['GP']
                total_evidence.append(proof)
                record=dict(record,gp=official['GP'],seconds=official['MIN']*60,**{f:official[c] for f,c in [('points','PTS'),('rebounds_total','REB'),('assists','AST'),('steals','STL'),('blocks','BLK')]})
                gp=record['gp']
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
    assert len(total_evidence) == len(corrections.get('season_total_overrides', []))
    assert len(eligibility_evidence) == len(corrections.get('eligibility_source_overrides', []))
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
                "whole_minute_source_rows": [] if primary_metadata else whole_minute_rows,
                "whole_minute_source_row_count": len(whole_minute_rows),
                **primary_metadata,
                "source_corrections": corrections,
                "display_rate_overrides": rate_evidence,
                "season_total_overrides": total_evidence,
                "eligibility_source_overrides": eligibility_evidence,
                "eligibility": {"minimum_team_gp": 30, "minimum_team_mpg": 15},
                "eligibility_precision": "Unrounded box-score minutes per team stint; explicitly scoped incomplete-log cases use official season totals corroborated by independent totals" if eligibility_evidence else "Unrounded box-score minutes per team stint",
                "records_by_team": {t: sum(r["team"] == t for r in rows) for t in sorted({r["team"] for r in rows})},
                "pending": ["Final team-stint jersey numbers", "Accolades and champions", "Independent source verification", "Distribution analysis", "Game activation"]}
    (output / f"stats_{slug}_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", default="2022-23")
    collect(parser.parse_args().season)
