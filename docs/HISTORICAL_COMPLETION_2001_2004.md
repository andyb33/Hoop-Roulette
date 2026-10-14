# Historical recovery: 2001–02 through 2003–04

This third recovery batch rebuilds previously completed data after the unpublished workspace was removed. Each season retains independent statistics, exact official schedules, final team-stint jerseys, honors and title-roster evidence. Completed data is checkpointed remotely before the next batch.

| Season | Entries | Independent comparisons | Verified jerseys | Champion entries |
|---|---:|---:|---:|---|
| 2003–04 | 260 | 1,820 | 260 | DET: 7 |
| 2002–03 | 265 | 1,855 | 265 | SAS: 9 |
| 2001–02 | 268 | 1,876 | 268 | LAL: 8 |

All 793 new entries have complete required fields. Prepared recovery v0.10.3 contains 7,295 normal entries across 25 seasons, 2001–02 through 2025–26, and 747 team-season combinations. Each recovered season matches 1,189 exact official NBA games, 29 teams and 82 games per team. The fixed eligibility rule remains 30 team-stint GP / 15 unrounded MPG; no lockout or shortened-season proration applies.

The independent Basketball Reference workbook remains pinned to a19c7d43b65028d80c782ce64d308ed392c57bbf, retaining traded-player team stints, original names and evidence hashes. Clar. Weatherspoon is canonicalized only for NBA ID 221; Slava/Stanislav Medvedenko is explicitly matched. Historical Charlotte is CHH in 2001–02, and New Orleans is NOH from 2002–03. CHA is absent from all three recovered seasons.

The 2003–04 mirror records 23 player appearances from game 0020300778 with whole-minute strings. These are parsed as supplied, not treated as absent or credited with invented seconds. The exact original values are retained in the manifest. All eligible rates still pass independent checks. Other source minutes retain second precision; display rates use decimal half-up rounding.

Voshon Lenard's 2001–02 DEN rate is 23.3 MPG, confirmed by official NBA totals of 1,656 MIN / 71 GP. The archive's 23.5 is resolved by a scoped proof matching NBA ID 702, season, team, GP and rate; the official row, URL and response hash are preserved. Staged statistics remain unchanged during completion.

Four blank NBA final-game jerseys in 2001–02 are resolved by reviewed official club uniform registers: Greg Anthony CHI 50, Mookie Blaylock GSW 10, Chris Gatling MIA 15 and John Crotty UTA 25. The Utah guide explicitly distinguishes Crotty's 25 in 2001–02 from 22 in 2000–01. Original blanks, exact game IDs/dates, primary PDF URLs/hashes/pages, registry entries and resolution methods remain in staging and completion evidence. Audit rows are labelled VERIFIED_OFFICIAL_UNIFORM_REGISTER. Other 789 new jerseys use final-appearance NBA roster metadata.

Each season has 15 All-NBA and 10 distinct All-Defense selections, plus one each of MVP, DPOY and ROY. Theo Ratliff has eligible ATL and POR stints in 2003–04, so both retain second-team defense credit: eleven flagged entries represent ten distinct winners. Championship credit requires the correct team stint and membership in the title-clinching roster, including inactives.

Validation passed: 98 unit tests; 100 complete browser games with fourteen unique drafted players each; 2,791 checked spins with valid animation choices and Keeps; all 25 normal seasons observed; live HTTP page/state/spin checks; both GOAT pools (149 award, 15 prehistoric); JavaScript syntax and whitespace checks. Evidence is retained in analysis/recovery_2001_2004_smoke.json. Jackpot season appearances in that report are separate from the normal pool.

Published v0.10.3 source uses Playtest Batch 16 and includes the verified pool through 2001–02 on GitHub main. The existing animation fix is retained; recovery/three-season-batches-20261014 preserves the recovery checkpoints. Desktop packages remain deferred through 1973–74, and earlier balance reports have not been rerun.

Recoverable Stage 2 progress is 9/30. This batch stops at 2001–02 as requested. Next proposed recovery batch: 2000–01, 1999–2000, 1998–99. The earlier unpublished 1999–2001 completion and unfinished 1994–99 work remain historical logs until rebuilt.
