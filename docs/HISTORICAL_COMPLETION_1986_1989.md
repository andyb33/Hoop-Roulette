# Historical expansion: 1986–87 through 1988–89

| Season | Eligible entries | Independent comparisons | Verified jerseys | Champion entries |
|---|---:|---:|---:|---|
| 1988–89 | 225 | 1,575 | 225 | DET: 9 |
| 1987–88 | 202 | 1,414 | 202 | LAL: 7 |
| 1986–87 | 208 | 1,456 | 208 | LAL: 8 |

Added 635 entries. v0.10.8 contains 10,926 normal entries across 40 seasons, 1986–87 through 2025–26, and 1,154 team-season combinations. Eligibility remains 30 team-stint GP / 15 unrounded MPG. Stage 2 is 24/30 complete; next are 1985–86, 1984–85 and 1983–84, then 1982–83 through 1980–81. Desktop packaging follows that 1980–81 major checkpoint; Stage 3 then continues through 1973–74. No desktop package is built with this batch.

## Sources, exact schedules and identities

The primary source remains the official NBA LeagueGameLog player endpoint, retaining original payload hashes, nullable fields and deterministic whole-minute adapter hashes. Independent checks use the Basketball Reference totals archive Seasons_Stats.csv, pinned to illumitata/NBA commit 99fb55e641c7009ae729e502ebdade8c6ecb2b7f, with the NBA Players stats since 1950 dataset as provenance. Original archive hashes and selected totals are preserved; decimal half-up rates are calculated explicitly from the independent totals. Combined TOT rows are excluded from verification, while individual traded-player team stints remain intact. The seven comparisons per entry are GP, MPG, PPG, RPG, APG, SPG and BPG.

The 1988–89 exact schedule matches 1,025 games, 25 teams and 82 games per team. Both earlier schedules match 943 games, 23 teams and 82 games per team. Source game IDs and team appearances match the official NBA schedule. MIA and CHH appear from their 1988–89 expansion; MIN and ORL do not appear in these earlier seasons. WSB retains the Bullets identity.

Two different players named Charles Jones shared Washington in 1988–89. Canonical NBA ID 279 has 53 GP / 1,154 MIN, meeting eligibility. ID 77178 has 43 GP / 516 MIN and is excluded. Independent archive age/index fields distinguish the two original identical names, with separate official season rows validating GP, minutes and all counting totals. The qualified comparison key does not overwrite the original reference name. Explicit name aliases cover truncated Hot Rod Williams, Joe Barry Carroll and Vinny Del Negro entries, Michael/Mike Holton, Dwayne/Pearl Washington and Cliff T./Cliff Robinson. Cliff T. Robinson remains distinct from Clifford Robinson.

Dallas Comegys NJN in 1987–88 remains excluded: 1,122 minutes / 75 GP = 14.96 MPG, although the rounded archive display is 15.0. No cutoff is relaxed.

## Scoped official-total resolutions

Four 1988–89 stints retain original NBA aggregates alongside official career-endpoint season totals: Danny Ainge BOS (1,339 logged minutes versus 1,349 official), Charles Smith LAC (101 versus 103 assists), Norm Nixon LAC (334 versus 339 assists) and Darrell Walker WSB (150 versus 155 steals).

Five 1987–88 stints have primary-source proofs: Fat Lever DEN (631 logged assists versus 639 official), Mike Gminski NJN (32 versus 33 blocks), Bernard King WSB (70 observed appearances versus 69 official GP), Frank Johnson WSB (74 versus 75 GP), and Sidney Moncrief MIL. Moncrief is a source disagreement: NBA game logs and official NBA season totals both report 12 blocks / 56 GP = 0.2 BPG, while the independent archive reports 14 = 0.3. The NBA value is retained and both totals remain explicitly recorded; the archive is not silently changed.

Twenty-five 1986–87 stints retain scoped official season-total proofs for differences or missing fields. Sedale Threatt CHI and Gerald Henderson NYK each have one original row with nullable rebounds, assists, steals and blocks. Their original aggregates preserve those nulls; official season totals supply complete rates. Threatt has 41 observed appearances versus 40 official GP, and Henderson 69 versus 68. Other proofs preserve counting/minute discrepancies, including Hot Rod Williams CLE's 79 observed versus 80 official GP. Original and official GP/minutes satisfy the fixed cutoff for every promoted override. No source game is fabricated or deleted.

Henderson's final observed NYK appearance is April 17, 1987, game 0028600925, one day before the club's season ended. A separate official individual player-game-log payload confirms that exact final stint date and game. Its own 69 rows still disagree with the 68-GP season total; the audit preserves that disagreement rather than claiming the individual log fixes GP. Other conflicting-GP cases have final observed appearances on their clubs' final regular-season dates. Final-box participation is checked independently of the displayed official season GP.

## Jerseys, honors and title credit

All 635 entries preserve exact final-appearance IDs, dates and original NBA roster metadata. Eight blank/composite fields require extra evidence; the other 627 use unambiguous official final-appearance metadata. Official club registers resolve Jim Paxson BOS 4 in 1988–89 (Celtics PDF page 174) and Otis Thorpe SAC 33 in 1987–88 (Kings franchise uniform list explicitly covers 1984–85 through 1987–88). Thorpe's original 24-33 composite remains in the audit.

Six exceptions use the independent APBR exact season/team uniform register, labelled VERIFIED_HISTORICAL_SEASON_REGISTER: Reggie Williams LAC 34 in 1988–89 and 1987–88; Eddie Johnson PHX 8 in both those seasons; Jim Paxson POR 4 and Eddie Johnson SAC 8 in 1986–87. The original HTML hash and specific team register are retained. These independent resolutions are distinguished from official NBA metadata and club sources; no exact final-game photograph is claimed.

Official playoff schedules confirm title-clinching games 0048800062 (1988–89 DET), 0048700080 (1987–88 LAL) and 0048600071 (1986–87 LAL). Championship flags require the eligible champion-team stint and title-game roster.

All-NBA has fifteen selections in 1988–89 and ten in each earlier season, with no invented third team. All-Defense has ten selections in 1988–89 and 1986–87; 1987–88 retains eleven, including both Mark Eaton and Patrick Ewing in the six-player second team. Fat Lever's NBA honors name is explicitly joined to the original Lafayette Lever player identity. Each season retains one MVP, DPOY and ROY; Michael Jordan's combined MVP/DPOY in 1987–88 remains on one normal entry.

## Validation

Playtest Batch 21 / v0.10.8 passes 121 automated tests and 100 complete games with fourteen unique drafted players each. All 40 normal seasons appear across 2,790 checked spins; animation choices remain valid under Keeps. Live HTTP page/state/spin checks, both GOAT pools (149 award / 15 prehistoric), JavaScript syntax and whitespace checks pass. CSV CRLF line endings remain preserved and are checked using Git's cr-at-eol setting. Evidence: analysis/historical_1986_1989_smoke.json. Normal-season coverage is reported separately from jackpot-only years. Earlier balance reports have not been rerun.
