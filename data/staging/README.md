# Historical stats staging

| Season | Eligible entries | Independent stat checks | Status |
|---|---:|---:|---|
| 2022–23 | 305 | 2,135 | Passed with documented source precision/revision differences |
| 2021–22 | 317 | 2,219 | Passed with documented minute precision and cutoff differences |

These are stats-only staging datasets. Jerseys, accolades, championship joins and game activation remain pending. The playable pool stays 2023–24 through 2025–26.

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

2020–21 collection attempted but the environment blocked the release-assets.githubusercontent.com source download. No data for it was enabled or approved. Resume once an accessible complete source is obtained, then verify its shortened schedule before advancing to 2019–20. Other 2010–11 through 2020–21 seasons remain pending.
