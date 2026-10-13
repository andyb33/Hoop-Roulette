# Historical completion — prepared v0.9.2

2017–18, 2016–17 and 2015–16 are complete locally, adding 906 entries. The combined normal pool is 3,383 entries across 11 seasons, 2015–16 through 2025–26.

| Season | Entries | Stat comparisons | Jerseys | Championship members |
|---|---:|---:|---:|---:|
| 2017-18 | 303 | 2121 | 303 | 9 (GSW) |
| 2016-17 | 310 | 2170 | 310 | 8 (GSW) |
| 2015-16 | 293 | 2051 | 293 | 10 (CLE) |

## Collection and independent verification

Each season was collected, independently verified and its discrepancies resolved before proceeding backward. The original game-level NBA mirror and separately scraped Basketball Reference season table are different inputs. Every eligible team stint and all seven stats were compared; eligibility sets match. Every source game and team appearance matches the official NBA LeagueGameFinder schedule: 1,230 games and 82 per each of 30 teams.

Reference source: https://github.com/favourumeh/NBA-DATA-PIPELINE/blob/a19c7d43b65028d80c782ce64d308ed392c57bbf/1990_2021_NBA_ppg_stats.xlsx . Producer provenance: the same repository commit’s NBA_webscraping_OOP.py, which scrapes the Basketball Reference per-game pages and removes combined TOT rows while retaining team stints. Source workbook, extracted CSV and staged data SHA-256 values are in each verification report. XLSX extraction selects the season-ending Year and preserves raw values.

The archive has UTF-8 names previously decoded as Windows-1252/Latin-1. Matching reverses only valid byte sequences, handles Turkish dotless-i, and uses an explicit Nenê/Hilario alias. Raw reference names remain in the audit evidence. Tests distinguish Bogdan from Bojan Bogdanović to guard against identity collisions.

Tayshaun Prince’s 2015–16 archive lists 0.9 APG. The NBA’s official career totals and the source game aggregate both report 74 assists over 77 games, which rounds half-up to 1.0. The normal entry retains 1.0. Official evidence, URL and response checksum are in data/staging/stats_2015_16_official_resolution.json and the resolved-difference record. Minor minute-precision differences remain individually documented.

## Jerseys, awards and champions

All 906 jerseys are verified against each player’s final regular-season appearance for the specific team, using official game dates. Legacy NBA game-specific active/inactive roster metadata supplies jersey numbers where box-score rows are blank; sources and page hashes are retained.

Actual All-NBA and All-Defense tiers are stored, with 15 and 10 eligible selections per season. Major awards come from the previously verified NBA winner archive. The official historical All-Defense page spells Patrick Beverley as Patrick Beverly in 2016–17; an explicit alias joins the correct player without changing the raw source.

Championship flags require the championship team stint and membership in the title-clinching active/inactive roster. Required fields have no unresolved records. The detailed completion JSONs and flat jersey audits are in data/processed.

## Validation and versioning

80 automated tests pass, including season-table extraction provenance, all jersey joins, exact stats preservation and the official Prince discrepancy resolution. 100 complete games each finish with 14 unique scored players; all 11 normal seasons appear. The full-game smoke summary is analysis/eleven_season_engine_smoke.json. Browser HTTP startup and spin checks pass with all 3,383 entries.

Eligibility stays 30 GP / 15 MPG. The 120 → +35 bonus, unique-pick rule and both GOAT pools are unchanged. The prepared source uses Playtest Batch 11 and v0.9.2 packaging names. Earlier balance reports have not been rerun.

This is a prepared local release. Main publication remains pending the earlier approval block; new desktop packages have not been built. v0.10 is reserved for the complete 2010–11 onward normal pool.

## Reproduce

```bash
python scripts/verify_historical_stats.py --season 2017-18
python scripts/complete_historical_seasons.py --season 2017-18
python scripts/verify_historical_stats.py --season 2016-17
python scripts/complete_historical_seasons.py --season 2016-17
python scripts/verify_historical_stats.py --season 2015-16
python scripts/complete_historical_seasons.py --season 2015-16
python -m unittest discover -v
```

The collector supplies original raw box scores. Workbook and official responses are cached locally; committed manifests identify them. The next season is 2014–15; 2010–11 through 2014–15 remain pending.
