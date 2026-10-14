# Historical stats staging

| Season | Eligible entries | Independent stat checks | Status |
|---|---:|---:|---|
| 2022–23 | 305 | 2,135 | Passed with documented source precision/revision differences |
| 2021–22 | 317 | 2,219 | Passed with documented minute precision and cutoff differences |
| 2020–21 | 307 | 2,149 | Passed; official 72-game schedule verified |
| 2019–20 | 298 | 2,086 | Passed; official unequal pandemic schedule verified |
| 2018–19 | 307 | 2,149 | Passed; official 82-game schedule verified |
| 2017–18 | 303 | 2,121 | Passed; official 82-game schedule verified |
| 2016–17 | 310 | 2,170 | Passed; official 82-game schedule verified |
| 2015–16 | 293 | 2,051 | Passed; Prince APG resolved using official NBA totals |

All eight historical staging seasons have now been completed and promoted. The latest three enter the prepared v0.9.2 playable pool. The stats-only snapshots and independent verification reports remain here as preserved evidence. Final-appearance jerseys, accolades, and title-roster championship membership are audited under `data/processed/completion_*.json`. The prepared playable pool covers 2015–16 through 2025–26; distribution analysis is still pending.

## Mandatory order

Collect → independently verify → resolve discrepancies → proceed to next year.
The collector refuses to move backward until the preceding verification report passes and its SHA-256 matches that dataset. Changing a checked dataset invalidates its gate. Unconfigured reference seasons require a vetted independent reference before verification.

## Collection and comparison

Collection uses the SportsDataverse mirror of NBA game-level box scores. Verification uses separately archived Basketball Reference season tables, recording their URLs, SHA-256 hashes and matched per-player evidence. Direct Basketball Reference downloads returned HTTP 403, so the independently scraped CSV snapshots are used with provenance notes.

Checks include all eligible player-team stints, seven stat fields, eligibility completeness, duplicate keys and source appearances, checksum consistency, postseason exclusion, 1,230 regular-season games, two teams per game, and all 30 teams playing 82 games for these two seasons. Shortened seasons must use their own schedule expectations.

## Corrections and resolutions

- Decimal half-up rounding replaces Python banker's rounding for the new historical collector.
- A recorded 0:00 appearance counts toward GP; a blank-minute DNP does not. Corrected Willy Hernangomez's 2021–22 GP from 49 to 50 and rebuilt his rates.
- Normalize suffixes and explicit historical name/encoding aliases; preserve source names in the audit evidence.
- 2022–23: 20 MPG comparisons differ by 0.1; retain NBA second-precision aggregation and record each difference. The archived reference has Blake Wesley APG 2.7, but his current Basketball Reference page reports 98 assists / 37 games = 2.6, matching our result.
- 2021–22: ten 0.1 MPG differences are recorded. D.J. Augustin's Houston stint displays 15.0 MPG in the reference but has 30,588 seconds over 34 games = 14.9941 MPG; excluded by the unrounded cutoff. All other eligibility matches.

Current filter is 30 team GP / 15 team MPG applied to unrounded source minutes. Displayed rates are one decimal. Older live datasets were filtered using their existing published one-decimal MPG; this distinction is documented.

## Reproduce

python scripts/collect_historical_stats.py --season 2022-23
python scripts/verify_historical_stats.py --season 2022-23
python scripts/collect_historical_stats.py --season 2021-22
python scripts/verify_historical_stats.py --season 2021-22

Raw source downloads live under ignored data/raw; committed manifests and verification evidence identify the exact inputs. Both verification JSON files provide the per-record independent comparisons and every resolved discrepancy.

## Next season

The earlier 2020–21 download block was resolved. 2020–21, 2019–20 and 2018–19 are complete and enabled in v0.9.1. The next three (2017–18 through 2015–16) are now also complete locally in v0.9.2. Next is 2014–15; seasons from 2010–11 through 2014–15 remain pending. Obtain a vetted independent reference before collecting and verifying the next season.

## Complete the verified seasons

python scripts/complete_historical_seasons.py --season 2022-23
python scripts/complete_historical_seasons.py --season 2021-22

This requires the preceding independent stats check to pass and match the staged checksum. It reads official NBA game dates, selects the final played game for each player-team stint, checks the official final box-score jersey, and joins official honors. Championship credit requires membership in the title-clinching game roster as well as the championship team stint.

The latest three seasons use Basketball Reference snapshots pinned to dataprofessor/data commit 087cb5383af3b09e68f6eeb00dea8819c1340de0. All source games and team appearances match official NBA LeagueGameFinder records. 2019–20 has 1,059 games with differing team totals; 2020–21 has 1,080 games and 72 games per team. The 2018–19 name aliases preserve NBA IDs while matching historical names (Juan/ Juancho Hernangomez, Enes Kanter/Freedom, Wes/Wesley Iwundu).

## Latest reference source

2017–18 through 2015–16 use the independently scraped Basketball Reference workbook from favourumeh/NBA-DATA-PIPELINE, pinned to a19c7d43b65028d80c782ce64d308ed392c57bbf. The producer code identifies the per-game pages and preserves separate team stints. Source workbook and extracted CSV hashes are retained; extraction selects the ending Year. Mojibake names are repaired only through valid UTF-8 byte decoding; audit rows retain the raw reference names. Nenê/Hilario and Turkish dotless-i aliases are explicit.

The archived Prince APG differs: official NBA totals and box-score aggregation both show 74 assists over 77 GP, so APG stays 1.0. The resolution record is committed alongside the stats audit. Official historical All-Defense lists misspell Patrick Beverley in 2016–17; the completion audit records that alias.

## Latest prepared expansion: v0.9.3

2014–15 (314 entries / 2,198 comparisons), 2013–14 (291 / 2,037), and 2012–13 (289 / 2,023) passed independent stats verification. The same pinned workbook and official final-appearance method apply. 2012–13 has 1,229 games: BOS and IND played 81 each, the remaining teams 82, with exact game IDs matched to NBA LeagueGameFinder. Jeffery Taylor is explicitly matched to archive name Jeff Taylor; his NBA ID remains 203106. Historical New Orleans records preserve NOH.

The current expansion report is `docs/HISTORICAL_COMPLETION_2012_2015.md`. The previous progress sections above describe earlier batches. Next: 2011–12, then 2010–11. Desktop packages wait until the complete v0.10 pool; automatic build triggers are disabled. GitHub main publication remains pending.

## Current Stage 1 completion — prepared v0.10

2011–12 has 276 eligible entries and 1,932 independent stat comparisons; 2010–11 has 287 entries and 2,009 comparisons. The preceding verification/checksum gate remains enforced. The 2011–12 schedule matches all 990 official games and 66 per team; 2010–11 matches all 1,230 games and 82 per team. Archive name Yi Jianlian is explicitly joined to source name Jianlian Yi (NBA ID 201146), with raw reference names retained. Historical NJN and NOH team codes are preserved.

Stage 1 now covers every season from 2010–11 through 2025–26: 4,840 normal entries across 16 seasons. Current completion evidence is in `docs/HISTORICAL_COMPLETION_2010_2012.md`. Earlier progress sections describe completed prior batches. Version v0.10 contains the completed Stage 1 source. Desktop packages are deferred until the normal pool is complete through 1973–74. Manual package workflows target v0.10. Stage 2: 1980–81 through 2009–10; Stage 3: 1973–74 through 1979–80. Distribution analysis has not been rerun.


## Recovery checkpoint: 2007–08 through 2009–10

The first three Stage 2 seasons are rebuilt: 271, 274 and 273 entries respectively. The current prepared pool contains 5,658 entries across 19 seasons. All stats, exact schedules, final jerseys and accolades passed verification. See [recovery report](../../docs/HISTORICAL_COMPLETION_2007_2010.md) for retained evidence and remaining recovery work. Completed batches are checkpointed remotely; future batches contain three seasons.


## Second recovery batch: 2004–05 through 2006–07

Recovered 283, 275 and 286 entries respectively. Current prepared pool: 6,502 entries across 22 seasons, 2004–05 through 2025–26. All stats, schedules, jerseys, honors and championship credit passed verification. The original blank NBA jersey for Antonio Davis is resolved to 32 using an exact final-game AP photo. Casey Jacobsen MPG is verified against official totals. See [completion report](../../docs/HISTORICAL_COMPLETION_2004_2007.md). Stage 2 recovery is 6/30; next: 2003–04, 2002–03, 2001–02.
