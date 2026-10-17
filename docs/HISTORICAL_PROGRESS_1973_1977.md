# Final four NBA seasons: 1973–74 through 1976–77

All four seasons passed independent stats and schedule checks on 2026-10-17 under the fixed 30 team GP / 15 unrounded team MPG rule. Their 660 entries passed 4,620 comparisons. Honors and award winners also match the eligible records. ABA seasons are outside this NBA dataset scope.

| Season | Entries | Comparisons | Teams / games | Completion |
| --- | ---: | ---: | --- | --- |
| 1976–77 | 212 | 1,484 | 22 / 902 | Three final jerseys pending |
| 1975–76 | 152 | 1,064 | 18 / 738 | Three final jerseys pending |
| 1974–75 | 158 | 1,106 | 18 / 738 | Complete |
| 1973–74 | 138 | 966 | 17 / 697 | Complete |

Across all seven Stage 3 seasons (1973–74 through 1979–80), 1,273 entries passed 8,911 stat comparisons and honors verification. 1973–74, 1974–75 and 1978–79 are complete. The consolidated machine-readable evidence is `data/processed/stage3_readiness_1973_1980.json`.

The default game remains v0.11.1 with 46 active seasons, 12,169 entries and 1,292 team-season combinations. All seven Stage 3 seasons remain outside that default pool until the following eight reviews close. No desktop package or release version was created.

## Final-jersey evidence still needed

| Player | Season/team | Alternatives |
| --- | --- | --- |
| Joe Hassett | 1979–80 IND | 10 / 11; the Pacers media guide also lists 30 |
| Slick Watts | 1977–78 NOJ | 00 / 14 |
| Ralph Simpson | 1976–77 DET | 10 / 32 |
| Fred Carter | 1976–77 MIL | 3 / 5 |
| Swen Nater | 1976–77 MIL | 31 / 35 |
| Cliff Pondexter | 1975–76 CHI | 41 / 42 |
| Steve Patterson | 1975–76 CHI | 32 / 42 |
| Ricky Sobers | 1975–76 PHX | 4 / 40 |

Each has a tracked `data/staging/review_...json` file preserving the final-game identity, original composite number, alternatives and source. None supplies a resolved jersey. The [APBR exact-season register](https://apbr.org/nmbr7080.html) confirms the alternatives but does not establish their chronology. Dated late-season photographs, programs or a documented switch timeline are needed. Next-season numbers and listing order alone were not accepted as proof.

## Documented corrections

- **Joe Meriweather, 1976–77 ATL:** the NBA API reports 73 GP, while the team-authored [Hawks media guide](https://atlantahawkspr.wordpress.com/wp-content/uploads/2021/10/2122_hwk_pr_mediaguide.pdf), PDF page 68 / printed page 122, and independent totals give 74. The remaining totals agree. A scoped correction uses 74 and recalculates rates while preserving the original NBA row and incomplete appearance aggregate.
- **Sidney Wicks, 1973–74 POR:** the team-authored [Trail Blazers media guide](https://www.ripcityresource.com/pdf/mediaguide/2022-23_TrailBlazers_MediaGuide.pdf), page 171, and independent archive give 63 blocks; NBA season totals and appearance logs give 64. The scoped correction uses the team guide's 63, producing 0.8 BPG, while preserving both conflicting NBA sources. Both guide proofs include the full source hash, page, headings and extracted row.
- **Zaid Abdul-Aziz, March 26, 1974:** the NBA game page omits his minutes despite recording nine points on three field goals and three free throws. The individual game log confirms that line; all 79 games and 865 points match the season totals and independent archive. The completion audit preserves the original missing minutes and derived played=0 flag, alongside an explicit verified appearance. No minutes were invented.
- **Dan Issel and Jim Price, 1976–77 DEN:** [March 20 photo metadata](https://www.gettyimages.fi/detail/uutiskuva/denver-nuggets-center-dan-issel-reaches-for-a-rebound-during-uutiskuva/1326501963) identifies 44 and 15 respectively, corroborated by an [April 22 playoff photo](https://www.gettyimages.fi/detail/uutiskuva/players-vie-for-a-rebound-during-an-nba-playoff-game-between-uutiskuva/1352680008). Original composite numbers are retained.
- Historical identities include the 1976–77 New York Nets, Kansas City–Omaha through 1974–75, and the 1973–74 Capital Bullets. The 1973–74 All-Defensive teams correctly contain six first-team and six second-team players. DPOY remains absent before its introduction.

## Validation and next step

142 Python tests and frontend animation/score-history checks pass. Twenty complete programmatic games using the staged 1973–74 and 1974–75 pools passed 544 spin/preview checks and unique-player drafting checks. An older 1972–73 jackpot appeared through the unchanged jackpot pool; it is not a new normal-pool season. Results are in `analysis/historical_1973_1975_staged_smoke.json`. These are programmatic checks, not a visual playtest.

No further seasons remain to collect within the agreed scope. Close the eight jersey reviews, rerun completion for the four pending seasons, activate all seven together, update pool totals and tests, run full-pool simulations, and then create the desktop checkpoint.
