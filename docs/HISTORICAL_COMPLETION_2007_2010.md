# Historical recovery: 2007–08 through 2009–10

This batch rebuilds the first three Stage 2 seasons after workspace maintenance removed unpublished local work. The published Stage 1 and animation fix were restored from GitHub main at 0df9681. Earlier local expansion logs are historical evidence, not recoverable datasets. Future batches contain three seasons; each completed season is checkpointed remotely before advancing.

| Season | Entries | Independent comparisons | Jersey evidence | Champion entries |
|---|---:|---:|---:|---|
| 2009–10 | 273 | 1,911 | 273 | LAL: 8 |
| 2008–09 | 274 | 1,918 | 274 | LAL: 9 |
| 2007–08 | 271 | 1,897 | 271 | BOS: 8 |

All 818 entries have verified required fields. The prepared recovery pool contains 5,658 entries, 19 seasons, and 570 team-season combinations. Each recovered schedule exactly matches 1,230 official games and 82 games per team. Eligibility remains at least 30 regular-season games for the team stint and 15 unrounded minutes per game. No lockout or shortened-season proration applies.

Raw NBA box-score mirror CSVs are aggregated with second-precision minutes and decimal half-up display rounding. Independent seven-field checks use the Basketball Reference workbook pinned to a19c7d43b65028d80c782ce64d308ed392c57bbf. Source URLs, hashes, names, comparisons, and exact NBA schedules remain in staging reports. Flip Murray/Ronald Murray and Ming Yao/Yao Ming are explicitly joined; canonical NBA ID 2397 displays Yao Ming. Original reference names are retained.

Final team-stint appearance dates identify the exact NBA game-specific roster supplying each jersey. Championship credit requires the title-clinching roster and correct team stint. Each season retains 15 All-NBA and 10 All-Defensive winners, plus MVP, DPOY, and ROY. No jersey resolutions or unresolved required fields remain.

Seattle remains SEA in 2007–08, with green/yellow colors; OKC begins in 2008–09. New Jersey and New Orleans remain NJN and NOH. The existing dataset-driven animation includes all valid seasons and players under Keeps.

Validation passed: 90 unit tests; 100 complete browser games with 14 unique drafted players each; 2,790 spins with valid animation choices, including kept rerolls; all 19 normal seasons observed; live HTTP page/state/spin checks; both GOAT pools (149 award, 15 prehistoric); JavaScript syntax and whitespace checks. Smoke evidence is in analysis/recovery_2007_2010_smoke.json. Jackpot season appearances in that report are separate from the normal pool.

Prepared source uses Playtest Batch 14 / recovery v0.10.1. GitHub main is unchanged. Desktop packages remain deferred until the normal pool reaches 1973–74. Older balance reports have not been rerun.

Recoverable Stage 2 progress is now 3/30. Next recovery batch: 2006–07, 2005–06, 2004–05. Previously completed unpublished seasons from 1999–2000 through 2006–07 and the unfinished 1994–99 batch still need rebuilding; their earlier status logs are preserved in Notion.
