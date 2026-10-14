# Historical expansion: 1995–96 through 1997–98

This three-season batch completes all required game fields: independent statistics, exact official schedules, final team-stint jerseys, honors and title-roster membership.

| Season | Eligible entries | Independent comparisons | Verified jerseys | Champion entries |
|---|---:|---:|---:|---|
| 1997–98 | 269 | 1,883 | 269 | CHI: 8 |
| 1996–97 | 254 | 1,778 | 254 | CHI: 8 |
| 1995–96 | 258 | 1,806 | 258 | CHI: 8 |

Added 781 entries. v0.10.5 contains 8,843 normal entries across 31 seasons, 1995–96 through 2025–26, and 921 team-season combinations. All three exact schedules match 1,189 official NBA games, 29 teams and 82 games per team. Every season keeps 30 team-stint GP / 15 unrounded MPG. Stage 2 progress is 15/30; its next major checkpoint is 1980–81. The next three-season batch is 1994–95, 1993–94 and 1992–93. Stage 3 then covers 1979–80 through 1973–74. Desktop packages remain deferred until that full range is complete.

Independent seven-field checks retain the Basketball Reference workbook pinned to a19c7d43b65028d80c782ce64d308ed392c57bbf. Original reference names and source hashes remain in each verification report. Dan/Danny Schayes and the archive's Gheorghe Mureetman typo use explicit name aliases. Washington is WSB (Bullets) before 1997–98 and WAS thereafter; source codes are normalized consistently across stats, exact schedules, final game boxes and game presentation.

For 1997–98, official career totals resolve displayed MPG for Bobby Phills CHH 30.4, Dell Curry CHH 18.7, Matt Geiger CHH 23.6 and Grant Hill DET 40.7. For 1996–97, official totals confirm Derek Harper DAL 29.3, Jamal Mashburn DAL 26.6, Detlef Schrempf SEA 36.1 and Vernon Maxwell SAS 28.8. Maxwell's source display was 28.9. All display overrides retain source GP, seconds, unrounded MPG and original rates alongside the exact primary rows; eligibility is unchanged.

Andrew DeClercq GSW (71 GP, 63,338 source seconds, official 1,056 MIN) and Chris Carr MIN (55 regular-season GP, 49,331 seconds, official 822 MIN) remain excluded in 1996–97. Both exact aggregates and official season totals are below 15 MPG, despite archive displays of 15.0 and 15.1. Carr's playoff appearance is excluded from regular-season GP. Scoped cutoff proofs preserve NBA IDs, team stints, schedules and all source evidence.

The mirror's release CSVs stop at 1996–97. The 1995–96 adapter instead reads the official NBA LeagueGameLog player endpoint, preserving the original 23,744-row payload and its SHA-256. Its deterministic CSV retains whole-minute precision and nullable statistics; it does not invent per-game seconds or replace missing fields with zero. Each metadata manifest links the primary payload hash and source URL.

Two players are absent from that named league log. Official individual legacy game logs recover 80 Loy Vaught appearances and 64 Ed O'Bannon appearances. The scoped identity ledger maps legacy 78412 to canonical 919 (Vaught, LAC) and legacy 77741 to canonical 709 (O'Bannon, NJN). Vaught's GP/MIN/PTS/REB/AST/STL/BLK exactly match canonical NBA season totals: 80/2966/1298/808/112/87/40. O'Bannon's GP/MIN/PTS/AST/STL/BLK match: 64/1253/399/63/44/11. His legacy REB and DREB fields are null and stay null in all 64 retained source rows. His 2.6 RPG uses the canonical official season total of 168 rebounds through a scoped total override; rebounds are explicitly excluded from the legacy identity matching fields. The adapter validates original rows, canonical IDs and completed counting-stat totals before promotion. Final-game audits preserve original legacy box IDs and the identity proof alongside canonical game records.

Four original missing/composite jersey fields are resolved from reviewed primary club guides: Dee Brown BOS 7 (Celtics 2016 guide PDF page 174, 1990–98 register); Sam Mack HOU 5 (Rockets 2016 guide PDF page 174, 1996–97 register, original NBA field `2-5`); Loy Vaught LAC 35 (actual 1995–96 Clippers club guide PDF page 15, printed 11, numerical roster); Ed O'Bannon NJN 31 (Nets 2016 guide PDF page 171, exact 1995–96 roster). Original NBA fields, final dates/game IDs, primary URLs/hashes/pages and resolution methods are retained. Other 777 new jerseys use official final-appearance roster metadata.

Official playoff schedules independently identify the title-clinching games: 0049700088 (1997–98), 0049600088 (1996–97) and 0049500068 (1995–96). Winners agree with NBA champion history, and exact final dates match game boxes. Each season retains fifteen All-NBA and ten distinct All-Defense selections, plus MVP, DPOY and ROY winners. Championship credit remains scoped to the eligible team stint and title-game roster.

Validation passed: 107 unit tests; 100 complete browser games with fourteen unique picks each; 2,789 checked spins with valid animation choices under Keeps; all 31 normal seasons observed; live HTTP page/state/spin checks; both GOAT pools (149 award and 15 prehistoric); JavaScript syntax and whitespace checks. Evidence: analysis/historical_1995_1998_smoke.json. Jackpot-only seasons in that report are separate from normal-pool availability. Source uses Playtest Batch 18 / v0.10.5. Earlier balance reports have not been rerun.
