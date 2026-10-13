# Stage 1 complete — prepared Hoopreel v0.10

All 16 normal seasons from 2010–11 through 2025–26 are complete locally: 4,840 eligible player-team-season entries and 480 team-season combinations. The final batch adds 563 entries. Desktop builds are deferred until the normal pool is complete through 1973–74. Windows, Apple Silicon and Intel Mac workflows now target v0.10, with manual dispatch only.

| Season | Entries | Independent stat comparisons | Verified jerseys | Championship entries |
|---|---:|---:|---:|---:|
| 2011–12 | 276 | 1,932 | 276 | 9 (MIA) |
| 2010–11 | 287 | 2,009 | 287 | 8 (DAL) |

Each final season has all 15 All-NBA selections, 10 All-Defensive selections and exactly one MVP, DPOY and ROTY. No required fields remain unresolved. Eligibility remains 30 team GP / 15 unrounded team MPG. Upper bonus remains 120 → +35; unique draft picks and both GOAT pools remain unchanged.

## Verification and provenance

Stats aggregate SportsDataverse NBA game box-score mirrors by NBA player ID and team stint. Independent per-game comparisons use the Basketball Reference workbook in favourumeh/NBA-DATA-PIPELINE pinned to a19c7d43b65028d80c782ce64d308ed392c57bbf, with producer provenance and workbook/extracted/staging hashes. Each season passed independent verification before collection proceeded backward. Minute-precision differences are individually documented.

2011–12 matches all 990 official NBA games, with 66 per team. 2010–11 matches all 1,230 games, with 82 per team. Game IDs and team appearances exactly match LeagueGameFinder. Historical NJN and NOH codes remain intact rather than being relabeled BKN/NOP; both have browser uniform palette mappings.

The box-score source stores Yi Jianlian as Jianlian Yi. This explicit name-order alias joins NBA ID 201146 to the independent archive; all seven fields and eligibility agree. The NBA identity is documented at https://www.nba.com/player/201146/yi-jianlian. Raw reference names remain preserved.

Every jersey uses the final played regular-season game for that player/team stint. Official game-specific roster metadata is joined by NBA player ID, with source URLs, dates, source hashes and exact player evidence retained in `data/processed/completion_*.json`. Title-clinching game IDs are 0041100405 (Miami 2012) and 0041000406 (Dallas 2011). Championship credit requires both the championship team stint and membership in the clinching-game roster, including inactive players and excluding traded-away players.

## Validation

86 automated tests passed, covering the expanded pool, checksums, all jersey evidence, accolades, championship eligibility, shortened schedules and historical franchise codes. 100 complete production-data games finished with 14 unique drafted players each. 2,322 kept rerolls preserved locked fields; Team+Player Keeps changed season whenever an alternative existed. All 16 normal seasons appeared. Browser HTTP startup, state and spin checks passed with all 4,840 records and both GOAT pools. Evidence: `analysis/sixteen_season_engine_smoke.json`.

New games use Playtest Batch 13 (v0.10). Prior balance reports describe smaller pools and have not been rerun. Stage 2 covers 1980–81 through 2009–10; Stage 3 covers 1973–74 through 1979–80. Earlier seasons remain in the separate Prehistoric Jackpot pool.

## Reproduction

```sh
python scripts/collect_historical_stats.py --season 2011-12
python scripts/verify_historical_stats.py --season 2011-12
python scripts/complete_historical_seasons.py --season 2011-12
python scripts/collect_historical_stats.py --season 2010-11
python scripts/verify_historical_stats.py --season 2010-11
python scripts/complete_historical_seasons.py --season 2010-11
python -m unittest discover -v
```

Raw downloads and official response caches stay local. Committed manifests, verification and completion reports retain provenance and checksums. Desktop tester instructions are in `EXTERNAL_ALPHA_V0_10.md`; packages have not been built.
