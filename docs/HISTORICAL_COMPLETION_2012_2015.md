# Historical completion: 2012–13 through 2014–15

Prepared v0.9.3 adds 894 normal entries. The complete local playable pool contains 4,277 records across 14 seasons, 2012–13 through 2025–26. GitHub main publication remains pending; desktop packaging is deferred until the full 2010–11 onward pool is ready for v0.10. Automatic build triggers are disabled; manual dispatch remains available.

| Season | Entries | Independent stat comparisons | Verified jerseys | Championship entries |
|---|---:|---:|---:|---:|
| 2014–15 | 314 | 2,198 | 314 | 9 (GSW) |
| 2013–14 | 291 | 2,037 | 291 | 9 (SAS) |
| 2012–13 | 289 | 2,023 | 289 | 9 (MIA) |

Every season has all 15 All-NBA selections and exactly one MVP, DPOY and ROTY. All-Defensive selections total 10 for 2014–15 and 2013–14, and 11 for 2012–13: Tyson Chandler and Joakim Noah tied for First Team, giving six First Team and five Second Team selections. Both tied centers remain tier 1. [NBA official announcement](https://pr.nba.com/2012-13-nba-all-defensive-teams/).

## Sources and verification

Collection uses SportsDataverse NBA game box-score mirrors, aggregated by NBA player ID and team stint. Independent per-game comparisons use the Basketball Reference workbook in favourumeh/NBA-DATA-PIPELINE, pinned to a19c7d43b65028d80c782ce64d308ed392c57bbf. The producer script documents the scrape and preserves traded-player stints. Workbook, extracted CSV and staged JSON checksums are retained in the verification reports. Every required stat and independent eligibility set passes; minor minute precision differences are documented individually.

Jeffery Taylor (NBA ID 203106) explicitly matches archive name Jeff Taylor. Name normalization preserves raw reference names and does not merge other Taylors. New Orleans Hornets records retain historical team code NOH; the browser maps it to the existing New Orleans franchise uniform palette.

2014–15 and 2013–14 each contain 1,230 games and 82 per team. 2012–13 contains 1,229: BOS and IND each played 81; every other team played 82. Exact game IDs and team appearances match official NBA LeagueGameFinder. The canceled Celtics home game is documented by the [Celtics](https://www.nba.com/celtics/news/sidebar/after-16-days-cs-will-finally-be-back-home).

Final played regular-season appearances determine each team-stint jersey. Official NBA game-specific roster metadata supplies the number, joined by player ID. All 894 jerseys have preserved source, game date, player evidence and checksums. Title credit requires both the title-team stint and membership in the clinching-game roster, including inactive players and excluding traded-away players.

No required stats, jerseys, accolades or championship fields remain unresolved. Normal eligibility remains 30 team GP / 15 unrounded team MPG. Upper bonus remains 120 → +35; GOAT pools remain unchanged.

## Validation

84 automated tests passed. 100 complete production-data games finished with 14 unique drafted players each; 2,317 kept rerolls preserved all locked fields, and Team+Player Keeps changed season whenever an eligible alternative existed. All 14 normal seasons occurred. Browser HTTP startup, state and spin checks passed with 4,277 records and both GOAT pools. Evidence: `analysis/fourteen_season_engine_smoke.json`.

Prior balance reports describe earlier pools and have not been rerun. Playtest logging uses Batch 12 (v0.9.3). Remaining Stage 1 seasons: 2011–12, then 2010–11.

## Reproduction

For each season in descending order, run:

```sh
python scripts/collect_historical_stats.py --season 2014-15
python scripts/verify_historical_stats.py --season 2014-15
python scripts/complete_historical_seasons.py --season 2014-15
```

Repeat with 2013-14 and 2012-13. The collector requires the preceding independent verification to pass with a current checksum. Official response caches and raw source downloads stay local; committed manifests identify source provenance and audit hashes.
