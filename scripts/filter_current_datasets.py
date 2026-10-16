"""Rebuild current normal pools from the preserved, verified 15 GP / 10 MPG snapshot."""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent.parent
LEGACY = ROOT / "data/legacy/15gp_10mpg"


def eligible(row, season, proofs):
    if row['gp'] < 30 or row['mpg'] < 15.0:
        return False
    if row['mpg'] > 15.0:
        return True
    proof = proofs[(season, row['team'], row['player_id'])]
    official = proof['official_row']
    assert official['SEASON_ID'] == season and official['TEAM_ABBREVIATION'] == row['team']
    assert official['PLAYER_ID'] == row['player_id'] and official['GP'] == row['gp']
    precise = proof.get('precise_totals_evidence', {}).get('official_row', official)
    assert precise.get('PLAYER_ID') == row['player_id'] and precise['GP'] == row['gp']
    decision = precise['MIN'] >= 15 * precise['GP']
    assert decision == proof['eligible']
    return decision


def rebuild():
    report = {}
    review = json.loads((ROOT / 'data/processed/modern_unrounded_eligibility_review.json').read_text())
    proofs = {(r['season'], r['team'], r['player_id']): r for r in review['cases']}
    for source in sorted((LEGACY / "game").glob("players_*.json")):
        original = json.loads(source.read_text(encoding="utf-8"))
        slug = source.stem.removeprefix("players_")
        season = slug.replace('_', '-')
        rows = [r for r in original if eligible(r, season, proofs)]
        keys = {(r["team"], str(r["player_id"])) for r in rows}
        assert len(keys) == len(rows)
        assert len({r["team"] for r in rows}) == 30
        (ROOT / "data/game" / source.name).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        target = ROOT / "data/processed"
        with (target / f"nba_roulette_{slug}.csv").open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        audit_source = LEGACY / "processed" / f"jersey_verification_{slug}.csv"
        with audit_source.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            audits = [a for a in reader if (a["team"], a["player_id"]) in keys]
        with (target / audit_source.name).open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(audits)
        summary_name = f"nba_roulette_{slug}_summary.json"
        summary = json.loads((LEGACY / "processed" / summary_name).read_text())
        summary.update(eligibility={"minimum_team_gp": 30, "minimum_team_mpg": 15.0},
                       eligible_player_team_records=len(rows),
                       eligible_records_by_team={t: sum(r["team"] == t for r in rows) for t in sorted({r["team"] for r in rows})},
                       missing_jersey_records=sum(r["jersey"] is None for r in rows),
                       all_nba_records=sum(r["all_nba"] is not None for r in rows),
                       all_defense_records=sum(r["all_defense"] is not None for r in rows),
                       champion_records=sum(r["champion"] for r in rows),
                       major_award_records=sum(r["mvp"] or r["dpoy"] or r["roy"] for r in rows),
                       filtered_from="data/legacy/15gp_10mpg", eligibility_precision="Published MPG with official total-minute verification for every displayed 15.0 boundary entry",
                       eligibility_review="data/processed/modern_unrounded_eligibility_review.json")
        for field in ("historical_jersey_records_verified", "jersey_records_verified"):
            if field in summary:
                summary[field] = len(audits)
        if "team_table_records_verified" in summary:
            summary["team_table_records_verified"] = len(rows)
        (target / summary_name).write_text(json.dumps(summary, indent=2), encoding="utf-8")
        report[summary["season"]] = {"before": len(original), "after": len(rows),
                                   "removed": len(original)-len(rows), "roster_min": min(summary["eligible_records_by_team"].values()),
                                   "roster_max": max(summary["eligible_records_by_team"].values())}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    rebuild()
