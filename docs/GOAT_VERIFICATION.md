# GOAT Dataset Verification — 2026-10-12

## Result

All 161 selected records verified: 149 Award Jackpot entries and 12 Prehistoric
Jackpot entries. No unresolved statistics, jerseys, team matches, or accolades.
The existing alpha still has GOAT spins disabled; engine and UI work comes next.

## Findings and corrections

- Filled the 17 missing award statistical records and 140 missing award jerseys.
- Filled actual All-NBA, All-Defense and championship fields from official history.
- Corrected Allen Iverson 1996–97 MPG from imported 40.1 to the NBA's 40.0.
- Resolved Patrick Ewing to NBA ID 121 and Larry Johnson to 913. The official
  player list contains same-name records; name-only dictionary matching was unsafe.
  The collector now filters by career dates and rejects ambiguous matches.
- Replaced draft historical string IDs with stable real NBA IDs. Pool-prefixed
  game IDs still keep normal, award and prehistoric versions separate.
- Confirmed Mutombo 2000–01 uses Philadelphia's 26 games and jersey 55,
  rather than his combined Atlanta/Philadelphia statistics.
- Preserved N/A for pre-1973 steals/blocks, even if the API supplies zero.
- Preserved actual accolade tiers; cumulative eligibility remains a scoring rule.
- Winner totals remain 53 MVP + 55 ROTY + 44 DPOY = 152 assignments, merged
  into 149 player-seasons. The 187-entry all-time winner archive remains intact.

## Prehistoric selections

| Player | Season | Team | GP | MPG | PPG | RPG | APG | Jersey | All-NBA | All-Defense |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| Wilt Chamberlain | 1961-62 | PHW | 80 | 48.5 | 50.4 | 25.7 | 2.4 | 13 | 1 | N/A |
| Bill Russell | 1964-65 | BOS | 78 | 44.4 | 14.1 | 24.1 | 5.3 | 6 | 1 | N/A |
| Oscar Robertson | 1961-62 | CIN | 79 | 44.3 | 30.8 | 12.5 | 11.4 | 14 | 1 | N/A |
| Jerry West | 1969-70 | LAL | 74 | 42.0 | 31.2 | 4.6 | 7.5 | 44 | 1 | 1 |
| Kareem Abdul-Jabbar | 1971-72 | MIL | 81 | 44.2 | 34.8 | 16.6 | 4.6 | 33 | 1 | None |
| Elgin Baylor | 1961-62 | LAL | 48 | 44.4 | 38.3 | 18.6 | 4.6 | 22 | 1 | N/A |
| Bob Pettit | 1958-59 | STL | 72 | 39.9 | 29.2 | 16.4 | 3.1 | 9 | 1 | N/A |
| Rick Barry | 1966-67 | SFW | 78 | 40.7 | 35.6 | 9.2 | 3.6 | 24 | 1 | N/A |
| John Havlicek | 1970-71 | BOS | 81 | 45.4 | 28.9 | 9.0 | 7.5 | 17 | 1 | 2 |
| Walt Frazier | 1969-70 | NYK | 77 | 39.5 | 20.9 | 6.0 | 8.2 | 10 | 1 | 1 |
| Nate Thurmond | 1967-68 | SFW | 51 | 43.6 | 20.5 | 22.0 | 4.2 | 42 | None | N/A |
| Bob Cousy | 1956-57 | BOS | 64 | 36.9 | 20.6 | 4.8 | 7.5 | 14 | 1 | N/A |

All 12 have N/A steals, blocks and DPOY. All-NBA Third did not exist for these
seasons, but actual First/Second selections still qualify for cumulative Third scoring.

## Evidence and limits

Official `playercareerstats` regular-season rows verify team-specific stats;
`commonteamroster` snapshots verify team-season jerseys. Exact selected rows and
source URLs are preserved in `data/goat/official_verification.json`. The NBA's
All-NBA, All-Defense, championship and major-award histories provide accolades.

Roster snapshots are the jersey evidence; ambiguous different numbers cause a
verification failure. This is a source-based audit, not an independent reconstruction
of every historical jersey-change date. The 38 pre-1973 archived award entries
are metadata-only and outside this selected-pool audit.

## Validation

56 automated tests pass, including winner coverage, shared ROTY winners,
multi-award deduplication, same-name identity resolution, historical N/A handling,
trade-specific stats, pool identity separation and the existing engine regressions.
Rebuilding uses committed evidence, so it does not depend on live API availability.
