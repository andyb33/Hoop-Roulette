> Update 2026-10-17: All seven Stage 3 datasets are complete. The user approved the higher of each unresolved jersey pair: eight policy choices, zero pending reviews. These choices are not historically verified final numbers. See [the consolidated report](HISTORICAL_PROGRESS_1973_1977.md). The default pool is still unchanged pending activation. The earlier review status below is retained as research history.

# Stage 3: 1977–78 through 1979–80

All three stats gates passed on 2026-10-17 using the fixed 30 team GP / 15 unrounded team MPG rule. The playable release remains v0.11.1: 46 seasons, 12,169 entries. This batch is not enabled, and no desktop package was built.

| Season | Eligible entries | Stat comparisons | Schedule | Completion |
| --- | ---: | ---: | --- | --- |
| 1979–80 | 197 | 1,379 | 902 games, 22 teams × 82 | Joe Hassett final jersey pending |
| 1978–79 | 209 | 1,463 | 902 games, 22 teams × 82 | Complete, awaiting batch activation |
| 1977–78 | 207 | 1,449 | 902 games, 22 teams × 82 | Slick Watts final jersey pending |

The 613 staged entries passed 4,291 independent stat comparisons. Verification reports retain the pinned archive hash, original reference totals, eligibility set comparison, original nullable NBA aggregates and explicit official season-total overrides. The official title-game proofs preserve original NBA rows and historical team codes. The collector still requires the preceding season's passing verification and matching data hash.

## Validation

138 Python tests and the frontend animation/score-history checks pass. Ten complete programmatic games using the staged 1978–79 pool passed 269 spin/preview checks and unique-player drafting checks; this is not a visual playtest. `analysis/historical_1978_1979_staged_smoke.json` records the results.

## Two evidence requests

| Player | Season/team | Alternatives | Evidence needed |
| --- | --- | --- | --- |
| Joe Hassett | 1979–80 IND | 10 / 11; Pacers media guide also lists 30 | A dated late-season photo, program or chronological uniform record establishing the final number |
| Slick Watts | 1977–78 NOJ | 00 / 14 | A dated late-season photo, program or chronological uniform record establishing the final number |

Neither review file supplies a resolved jersey. NBA composite strings and the conflicting independent listings remain preserved in `data/staging/review_1979_80_76966_IND.json` and `data/staging/review_1977_78_78473_NOJ.json`. Listing order is not treated as chronology.

Sources: [APBR uniform register](https://apbr.org/nmbr7080.html), [Pacers media guide](https://ak-static-int.nba.com/wp-content/uploads/sites/3/2016/10/2016-17-Media-Guide-Pacers.pdf), [1977–78 Jazz roster](https://www.landofbasketball.com/nba_rosters/1977_1978_jazz_grs.htm).

## Recorded resolutions

- Mark Landsberger's February 8, 1980 Bulls scoring line was misattributed from Scott May. The [independent box-score audit](https://apbr.org/forum/viewtopic.php?p=25417) identifies February 6 as Landsberger's final Bulls appearance. Excluding exactly February 8 restores 54 GP and 453 points against both season-total sources. Incomplete minute and other counting fields remain preserved. The exception is limited to that player, stint and game and cannot silently affect another player.
- Rick Barry wore 2 at home and 4 away, per his [interview explanation](https://www.basketballnetwork.net/old-school/rick-barry-explains-why-he-wore-two-different-jersey-numbers-with-the-rockets). His final 1978–79 appearance was away at Washington (4); his final 1979–80 appearance was home against Detroit (2). Both original composite strings remain preserved.
- Mike Bantom's 1979–80 Indiana number is 42, corroborated by the [exact-season uniform register](https://www.basketball-reference.com/leagues/NBA_1980_numbers.html). The APBR season list omits him; that omission is recorded.
- Historical boundaries preserve Buffalo in 1977–78, San Diego from 1978–79, New Orleans through 1978–79, Utah from 1979–80, Seattle before Oklahoma City, and Washington Bullets before the Wizards rename.
- Honor parsing supports the 1979–80 six-player All-Defensive first team and the 1977–78 six-player second team. World B. Free and Micheal Ray Richardson have explicit name aliases. DPOY is absent before its introduction.
- Interrupted or concurrent API cache writes now use atomic replacement; invalid disposable JSON caches are fetched again.

The final four seasons (1976–77 through 1973–74) have now passed their stats and honors checks too. See [the final-four report](HISTORICAL_PROGRESS_1973_1977.md) for the consolidated eight-case jersey review. After all eight close, rerun completion and activate all seven Stage 3 seasons together, update default-pool assertions, run the full tests and simulations, and publish the checkpoint. No seasons remain to collect within the agreed NBA scope.
