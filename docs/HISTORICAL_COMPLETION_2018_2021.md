# Historical completion — v0.9.1

2020–21, 2019–20 and 2018–19 are complete and enabled. Normal play spans eight seasons, 2018–19 through 2025–26, with 2,477 entries.

| Season | Entries | Stat comparisons | Jerseys | Championship members |
|---|---:|---:|---:|---:|
| 2020-21 | 307 | 2149 | 307 | 8 (MIL) |
| 2019-20 | 298 | 2086 | 298 | 9 (LAL) |
| 2018-19 | 307 | 2149 | 307 | 8 (TOR) |

## Verification

Each season was collected, independently compared with an archived Basketball Reference per-game table, and its discrepancies resolved before proceeding backward. Reference snapshots are pinned to dataprofessor/data commit 087cb5383af3b09e68f6eeb00dea8819c1340de0. Raw NBA box-score aggregates retain exact team stints and unrounded eligibility minutes. Source and export checksums are recorded.

All game IDs and team appearances match official NBA LeagueGameFinder records. 2020–21 has 1,080 games (72 per team). 2019–20 has 1,059 games with differing team totals due to the interrupted season and restart. 2018–19 has 1,230 games (82 per team). Postseason and play-in IDs are excluded from regular-season aggregation.

Name aliases resolve Juan/ Juancho Hernangomez, Enes Kanter/Freedom and Wes/Wesley Iwundu without merging unrelated players. Minor minute precision differences remain documented in the per-season stats verification reports.

Every new jersey comes from the final played regular-season game for that player-team stint, selected using official dates rather than game-ID order. Modern NBA live box scores and older NBA game pages provide the evidence. Legacy pages have blank numbers in some box rows but retain game-specific active/inactive roster metadata; these numbers are joined by NBA player ID. The raw-page checksum and source URL are preserved. Legacy live data can mark a completed game as finalbox rather than status 3; both official final statuses are recognized.

Actual All-NBA and All-Defense tiers are stored: 15 and 10 selections respectively per season. Major awards come from the previously verified official winner archive. Giannis’s 2019–20 MVP and DPOY wins occupy one normal entry with both flags.

Championship membership requires the title-team stint and the title-clinching roster, including inactive players. OG Anunoby is included for Toronto in 2018–19; traded-away Delon Wright and Jonas Valanciunas are excluded. Required fields have no unresolved entries.

Detailed official evidence is in data/processed/completion_2020_21.json, completion_2019_20.json and completion_2018_19.json. Stats comparisons remain in data/staging.

## Gameplay and validation

Eligibility stays 30 team GP / 15 MPG. The 120 → +35 bonus and GOAT pools are unchanged. New logs use Playtest Batch 10. The earlier distribution reports have not been rerun for this pool.

77 automated tests pass, including exact stat preservation, checksum validity, all final-appearance jerseys, official shortened schedules, inactive/traded championship cases, and merged major-award flags. 100 full games finish with 14 unique scored players each; 2,326 kept rerolls preserve their locked slots. All eight seasons appear in the sample. Browser HTTP startup and spin checks pass with 2,477 records. The production-data smoke summary is in analysis/eight_season_engine_smoke.json.

## Reproduce

```bash
python scripts/verify_historical_stats.py --season 2020-21
python scripts/complete_historical_seasons.py --season 2020-21
python scripts/verify_historical_stats.py --season 2019-20
python scripts/complete_historical_seasons.py --season 2019-20
python scripts/verify_historical_stats.py --season 2018-19
python scripts/complete_historical_seasons.py --season 2018-19
python -m unittest discover -v
```

The original collector supplies the raw files if needed; completion validates their SHA-256 against the committed manifests. All text uses explicit UTF-8, with Git line-ending rules preserving audit bytes on Windows. 2010–11 through 2017–18 remain pending; the next season is 2017–18.
