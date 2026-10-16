# Final Stage 2 checkpoint — completed in v0.11.0

All three final seasons are complete and active. The current pool has 46 seasons and 12,169 entries. See [final completion and validation report](HISTORICAL_COMPLETION_1980_1983.md). The earlier checkpoint below is retained as historical source-review context and is superseded by this completion.

# Final Stage 2 batch — verification checkpoint

The published playable pool remains v0.10.9: 43 seasons, 1983–84 through 2025–26. This checkpoint preserves new validation work; it does not activate the final batch or declare the desktop-package checkpoint complete.

| Season | Eligible entries | Independent comparisons | Status |
|---|---:|---:|---|
| 1982–83 | 217 | 1,519 | Stats, jerseys, honors and championship membership complete |
| 1981–82 | 208 | 1,456 | Stats, jerseys, honors and championship membership complete |
| 1980–81 | 208 | 1,456 | Stats passed; seven final-number jersey resolutions pending |

All three exact schedules match 943 games, 23 teams and 82 games per team. Eligibility remains 30 team-stint GP and 15 unrounded MPG. Two 1980–81 entries whose incomplete logs understate eligibility use official GP/MIN exactly corroborated by the independent original totals archive.

The older LeagueGameFinder endpoint has empty results for these seasons. The official NBA team LeagueGameLog endpoint supplies full regular-season schedules and title-game verification instead. The same exact game-ID/team-appearance checks remain mandatory.

Official season totals resolve incomplete or nullable appearance aggregates: 181 scoped proofs in 1982–83, 185 in 1981–82, and 168 in 1980–81, plus two eligibility proofs. Original aggregates, canonical rows, sources and response checksums remain preserved.

## Final-appearance source corrections

Some historical zero-minute rows are placeholders rather than reliable appearances. The general zero-minute GP rule is unchanged. Scoped final-appearance corrections retain every original individual log row and excluded placeholder, and require corroborating official totals and independent archive coverage.

Clemon Johnson's final 1982–83 IND game is February 15 (0028200584); Larry Smith's final GSW game is February 23 (0028200633). Their positive-minute subsets match official GP/MIN/PTS/REB/AST; Smith also matches STL/BLK. Earlier source maxima with placeholder rows remain in the evidence.

Don Collins's 1980–81 ATL positive-minute subset exactly matches 47 GP, 1,184 MIN and 597 PTS, independently corroborated by the archive. It establishes a January 16 final appearance (0028000533). The subset has 186 rebounds versus the official 187 and 114 assists versus the official 115; these disagreements remain explicit. Canonical independently verified season stats are retained. The exceptional resolution is scoped to this exact player, team, season and totals, and does not claim that all counting totals match.

Phil Smith's individual 1981–82 SDC log separately corroborates the March 2 final game while retaining its unresolved aggregate GP disagreement. No claim is made that this corroboration fixes the aggregate source.

## Jerseys and remaining work

Seven 1982–83 blanks and six 1981–82 blanks have unambiguous single-number APBR season/team register entries. Frank Johnson WSB 1981–82 uses the official Wizards all-time uniform register: PDF page 186, printed page 197, visually reviewed under number 15. APBR's omission of him from that season's list is explicitly preserved.

Thirteen 1980–81 jerseys have unambiguous single-number register entries. Seven still require dated evidence distinguishing multiple numbers:

| Player | Team | Original NBA field | Independent register alternatives |
|---|---|---|---|
| Don Collins | ATL | 7-42 | 7 and 42 |
| Ricky Sobers | CHI | 14-40 | 14 and 40 |
| Jim Spanarkel | DAL | 33-34 | 33 and 34 |
| Paul Mokeski | DET | blank | 44 and 53 |
| Don Buse | IND | 10-11 | 10 and 11 |
| Johnny Moore | SAS | 00-10 | 00 and 10 |
| Henry Bibby | SDC | 10-15 | 10 and 15 |

A register's main number, parenthetical alternative, or numeric ordering does not establish the final number. No guessed resolutions have been applied. The machine-readable pending list is `data/staging/jersey_1980_81_unresolved.json`.

1982–83 keeps eleven All-Defense winners, including the First Team tie. 1981–82 keeps ten. DPOY flags must remain absent before its introduction in 1982–83. The 1980–81 eleven-winner defensive list, including the official history's Michael/Micheal Richardson spelling mismatch, still requires completion-stage reconciliation after jerseys are resolved.

133 tests pass for this checkpoint, including completed-season checks, source-name aliases, strict zero-minute appearance behavior, scoped placeholder proofs and preserved Collins counting disagreements. These are source/data validation checks; the proposed 46-season playable pool has not yet been activated or given the 100-game expansion smoke check. The published 43-season default remains unchanged.

Next: resolve the seven final jersey numbers; finish 1980–81 completion; activate all three seasons together; update counts/version/playtest metadata; run full tests, 100 games and live HTTP checks; publish main and update Notion; then build Windows, Apple Silicon Mac and Intel Mac packages at the Stage 2 checkpoint.

## Jersey decisions accepted — 2026-10-16

The user accepted all seven pending 1980–81 choices: Collins ATL **7**, Sobers CHI **40**, Spanarkel DAL **34**, Mokeski DET **44**, Buse IND **11**, Moore SAS **00**, Bibby SDC **10**. This supersedes the pending-jersey statements above. Individual resolution files retain original NBA fields, sources, uploaded-image hashes and conflicting evidence. These are reviewed project decisions with chronology limitations, not claims of exact final-game visual verification.

No jersey research items remain open in this batch. The 1980–81 honors/completion checks and activation of the final three seasons remain pending; the playable pool remains 43 seasons.
