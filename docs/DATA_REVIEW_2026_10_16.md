# Data and publication review — v0.10.10

The playable pool remains 43 seasons, 1983–84 through 2025–26, now with **11,536 entries** and **1,223 team-season combinations**. The review fixes four rounded-MPG eligibility mistakes and publishes the recovery work to main without activating the unfinished final Stage 2 batch.

## What the review checked

All 40 historical completion reports in the playable pool have passing stat verification, no recorded unresolved fields, and game-file checksums matching the current outputs. All 11,536 active entries have required stats and jersey values, with no duplicate player/team/season keys. The original three modern datasets retain their separate legacy-source and jersey audits.

Passing these checks demonstrates consistency with preserved evidence; it does not make every historical source infallible. Some jerseys use independent registers or historical inference, rather than an exact dated game photograph. One previously accepted composite needs further review below.

## Corrected modern eligibility

The original 2023–26 migration used published one-decimal MPG. Every eligible entry displayed as exactly 15.0 MPG was checked against official team-stint totals. Four fail the fixed unrounded cutoff:

| Season | Player | Team | Official GP | Official total minutes | Action |
|---|---|---|---:|---:|---|
| 2023–24 | Danuel House Jr. | PHI | 34 | 509 | Excluded |
| 2024–25 | Gary Payton II | GSW | 62 | 927 | Excluded |
| 2024–25 | Antonio Reeves | NOP | 44 | 659.5583333333333 | Excluded |
| 2025–26 | Micah Peavy | NOP | 61 | 913 | Excluded |

Reeves's whole-minute career total rounds to 660, which would incorrectly appear to satisfy 15 × 44. The precise official LeagueDashPlayerStats total resolves the boundary. Other reviewed career-minute totals are safely away from the threshold despite whole-minute presentation. Original responses, canonical rows, checksums and decisions are preserved in `data/processed/modern_unrounded_eligibility_review.json`. The rebuild script requires a boundary proof instead of silently using rounded 15.0 MPG.

Modern counts are now 299, 315 and 325 respectively; 939 modern entries replace 943. The legacy 1,346-entry snapshot is preserved. The other 40 season datasets are unchanged.

## Historical issues encountered and retained evidence

The expansion encountered incomplete or nullable NBA appearance logs, alternate legacy player IDs, rounded eligibility boundaries, conflicting counting totals, misspelled names, renamed franchises, tied awards, traded-player championship membership and blank/composite jerseys. Scoped proofs preserve the original data and selected resolution. No universal 82-GP requirement is applied.

Examples include recovering Loy Vaught's legacy-ID appearances; preserving Sidney Moncrief's 1987–88 NBA 12 blocks versus archive 14 and Sidney Green's 1984–85 NBA 11 versus archive 14; correcting Steve Johnson's erroneous post-trade KCK appearances; and earlier jersey corrections for Billy Owens MIA (32), Harold Miner MIA (4) and Ryan Lorthridge GSW (initially 33, subsequently corrected to 9 after user evidence review). Detailed batch reports and machine-readable audit files preserve these decisions.

## Items requiring stronger jersey evidence

**User evidence follow-up:** all six uploaded images were visually reviewed. They show the 1994–95 roster alternatives (Seikaly 4/9; Lorthridge 9/33), Seikaly as 4 in 1995–96, Webber as 4 in 1993–94, the trade/signing timeline, a 1995 SkyBox card listing Seikaly 9 after the trade, and Wikipedia's 1994–95 roster listing Seikaly 4 / Lorthridge 9.

The user accepts **Seikaly 4** and explicitly corrects **Lorthridge from 33 to 9**. These are retained as documented chronology inferences, not exact final-game visual verification. Lorthridge joined in January after Webber's November departure; neither screenshot ordering nor the card dates the actual number changes. The former assumption that Fanspo display order established Lorthridge's final 33 is superseded. Both proofs preserve their prior decisions and all six image hashes/Library references.

The Seikaly open question is closed under the accepted inference standard. Three values carry an inference qualification: **Seikaly GSW 1994–95 = 4**, **Lorthridge GSW 1994–95 = 9**, and **Vinnie Johnson SAS 1991–92 = 25**. Stronger dated confirmation remains welcome. Sherman Douglas BOS 1991–92 = 20 additionally has an explicit first-4 then-20 account.

The unactivated 1980–81 season still has seven unresolved final numbers:

| Player | Team | Alternatives |
|---|---|---|
| Don Collins | ATL | 7 / 42 |
| Ricky Sobers | CHI | 14 / 40 |
| Jim Spanarkel | DAL | 33 / 34 |
| Paul Mokeski | DET | 44 / 53 |
| Don Buse | IND | 10 / 11 |
| Johnny Moore | SAS | 00 / 10 |
| Henry Bibby | SDC | 10 / 15 |

No manual stat entry is required from the user. These are source-research items, not requests to invent missing values. See `data/staging/jersey_1980_81_unresolved.json` and the final-batch checkpoint report.

## Publication and documentation

Notion's detailed verification tracker was current, but the project dashboard, data overview, roadmap, playtesting and decision indexes retained obsolete v0.6–v0.8 snapshots. Current summaries are synchronized in this review; historical design documents, balance reports and playtest results retain their original scope rather than being relabelled as fresh analyses.

1982–83 (217 entries) and 1981–82 (208) are complete in the repository but remain outside the default loader. 1980–81 has 208 independently verified stats entries but incomplete jersey/honors completion. The final three seasons will be activated together after remaining validation. Stage 2 verification is 29/30 complete, while 27/30 Stage 2 seasons are playable. Desktop packaging remains deferred to the completed 1980–81 checkpoint.

Validation: **133 tests pass; 100 complete games, 2,790 checked spins, all 43 normal seasons observed; live HTTP startup/state/spin checks; both GOAT pools; JavaScript syntax and whitespace checks pass.** New games use Playtest Batch 23. Earlier balance studies have not been rerun.
