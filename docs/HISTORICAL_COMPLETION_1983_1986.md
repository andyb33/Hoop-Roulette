# Historical expansion: 1983–84 through 1985–86

| Season | Eligible entries | Independent comparisons | Verified jerseys | Champion entries |
|---|---:|---:|---:|---|
| 1985–86 | 211 | 1,477 | 211 | BOS: 8 |
| 1984–85 | 204 | 1,428 | 204 | LAL: 8 |
| 1983–84 | 199 | 1,393 | 199 | BOS: 8 |

Added 614 entries. v0.10.9 contains 11,540 normal entries across 43 seasons, 1983–84 through 2025–26, and 1,223 team-season combinations. Stage 2 is 27/30 complete. The final Stage 2 batch is 1982–83, 1981–82 and 1980–81; desktop packaging follows that major checkpoint. Stage 3 then covers 1979–80 through 1973–74. No package is built with this batch.

## Verification and historical identities

All three exact schedules match 943 official NBA games, 23 teams and 82 games per team. Source game IDs and team appearances match the official schedule. KCK preserves Kansas City before the 1985–86 move; SDC preserves San Diego before the 1984–85 move. Team Keeps and animation choices use those season-specific identities, with colors available for both historical codes.

The original NBA LeagueGameLog payloads, nullable fields and whole-minute adapter hashes remain preserved. Independent verification uses the Basketball Reference totals archive pinned to illumitata/NBA commit 99fb55e641c7009ae729e502ebdade8c6ecb2b7f, retaining traded-player stints and original totals. Seven comparisons per entry cover GP, MPG, PPG, RPG, APG, SPG and BPG. Display rates use decimal half-up rounding. Explicit aliases preserve the raw reference names, including World Free/World B., Mel/Melvin Turpin, Charlie/Charles Davis and Pittman, Micheal Ray Richardson, Eddielee Wilkins, Nate/Tiny Archibald and Samuel/Sam Williams.

There are 39 scoped official season-total resolutions in 1985–86, 81 in 1984–85 and 30 in 1983–84. Every proof retains original appearance counts, minutes, nullable/counting aggregates, the complete official season row and source hashes. Nullable eligible stints account for one, 31 and 20 of those proofs respectively. Examples include Gus Williams WSB in 1985–86 (80 observed versus 77 official GP), and missing counting fields in the older logs. No source appearance is fabricated or deleted.

Sidney Green CHI 1984–85 remains an explicit source disagreement: NBA logs and official season totals report 11 blocks / 48 GP = 0.2 BPG; the independent archive reports 14 = 0.3. The NBA value is retained alongside the archive's conflicting total. This is separately recorded from discrepancies corrected using official totals that agree with the archive.

## Eligibility when game-log minutes are incomplete

The fixed cutoff remains 30 team-stint GP / 15 unrounded MPG. Some older logs cannot establish full-stint eligibility: they contain zero-minute placeholders or only partial coverage. Three explicit 1984–85 proofs use official season GP/MIN that exactly match the independent archive, applying the unchanged cutoff before display rounding:

| Player / team | Original log GP / MIN | Corroborated full-stint GP / MIN | Decision |
|---|---:|---:|---|
| Eddie Johnson KCK | 82 / 85 | 82 / 3,029 | Include |
| Charles Jones PHX | 78 / 20 | 78 / 1,565 | Include |
| Ozell Jones SAS | 31 / 503 | 67 / 888 | Exclude |

The source aggregates and independent original rows/hashes remain in eligibility_source_overrides. This neither treats placeholders as genuine season minutes nor lowers either cutoff. Tests enforce both the exact 30-GP/15-MPG boundary and exclusion below it; contradictory corroborating totals are rejected. Published historical minutes retain their original whole-minute precision.

## Final appearances and the Steve Johnson trade correction

Four 1984–85 non-season-ending stints retain separate official individual game-log proofs: Sly Williams ATL (March 11), Caldwell Jones CHI (April 5), Eddielee Wilkins NYK (April 12) and Lester Conner GSW (April 13). The individual logs do not resolve the season GP discrepancies; both observed and official GP remain explicit. Independent full-season log reviews also corroborate Williams's and Caldwell Jones's final regular-season dates, excluding playoff games.

The 1983–84 Steve Johnson KCK logs incorrectly include February 16, March 18 and March 31 appearances after his move to Chicago. The official Bulls guide confirms the February 15 trade (PDF page 379, printed page 387). Bounding the original individual log before that date gives exactly 50 games; GP, MIN, PTS, REB, AST, STL and BLK all match his official KCK season row. His verified final KCK appearance is February 14, game 0028300586, rather than the erroneous March 31 source maximum. The three post-trade records and original source maximum remain preserved in the proof. The final-box jersey check uses the corrected stint boundary; displayed season stats already use the verified official totals.

## Jerseys, honors and title credit

All 614 entries preserve exact checked final-game identities and original NBA roster metadata. Thirteen blanks use the independently authored APBR exact season/team uniform register, explicitly labelled VERIFIED_HISTORICAL_SEASON_REGISTER with original HTML hashes: Bobby Jones PHI 24, Charles Jones PHX 34, Jim Paxson POR 4 and Eddie Johnson SAC 8 in 1985–86; the same first three numbers and Eddie Johnson KCK 8 in 1984–85; George Johnson IND 24, Eddie Johnson KCK 8, Bobby Jones PHI 24, Samuel Williams PHI 33 and Jim Paxson POR 4 in 1983–84. The remaining 601 jerseys use unambiguous official checked-game metadata. The independent register is not labelled as an official club source or an exact game photograph.

Each season retains ten distinct All-NBA selections across two teams, ten All-Defense winners and one MVP, DPOY and ROY. The official 1984–85 All-NBA history's “Benard King” typo has a scoped correction to Bernard King; the original source hash and explicit alias are retained. Official playoff schedules confirm title games 0048500406 (1985–86 BOS), 0048400406 (1984–85 LAL) and 0048300079 (1983–84 BOS). Championship credit requires the eligible champion-team stint and title-game roster.

## Game validation

Playtest Batch 22 / v0.10.9 passes 128 automated tests and 100 complete games with fourteen unique drafted players each. All 43 normal seasons appear across 2,790 checked spins; animation choices remain valid under Keeps. Live HTTP page/state/spin checks, both GOAT pools (149 award / 15 prehistoric), JavaScript syntax and whitespace checks pass. Normal-season coverage is separated from jackpot-only years in analysis/historical_1983_1986_smoke.json. CSV CRLF endings are preserved and checked with Git's cr-at-eol setting. Earlier balance reports have not been rerun.
