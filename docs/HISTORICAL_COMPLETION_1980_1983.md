# v0.11.0 — Stage 2 complete

All 46 normal seasons from 1980–81 through 2025–26 are active: **12,169 entries, 1,292 team-seasons**. Stage 1 and all 30 Stage 2 seasons are complete. Stage 3 remains 1979–80 through 1973–74. Eligibility is fixed at 30 team-stint GP and 15 unrounded MPG, including shortened seasons.

| Final batch | Entries | Independent stat comparisons | All-NBA winners | All-Defense winners | Eligible champion entries |
|---|---:|---:|---:|---:|---:|
| 1982–83 | 217 | 1,519 | 10 | 11 | 8 PHI |
| 1981–82 | 208 | 1,456 | 10 | 10 | 8 LAL |
| 1980–81 | 208 | 1,456 | 10 | 11 | 9 BOS |

Each schedule matches all 943 games, 23 teams and 82 games per team. Independent stats checks passed before completion. Final-game identities, source responses/checksums, canonical totals and original missing/conflicting fields remain preserved. Championship membership uses the title-clinching roster. DPOY is absent before 1982–83. The official 1980–81 All-Defense history's Michael/Micheal Ray Richardson spelling discrepancy is explicitly normalized without changing the original source.

The seven 1980–81 composite/blank jersey cases are user-reviewed decisions: Collins ATL 7; Sobers CHI 40; Spanarkel DAL 34; Mokeski DET 44; Buse IND 11; Moore SAS 00; Bibby SDC 10. Individual resolution files retain uploaded image hashes/identifiers, observations, sources and conflicting evidence. These are accepted inferences with chronology limitations, not exact final-game photo confirmations. Moore's leading zero is retained for display. Prior Seikaly, Lorthridge and Vinnie Johnson inference qualifications remain unchanged.

The earlier checkpoint preserves the original incomplete-log corrections, including Collins's 186 versus 187 rebounds and 114 versus 115 assists. Those disagreements remain explicit; the canonical independently verified stats are retained. No missing user-entered stats are required.

Validation: **133 tests passed; 100 complete games; 2,790 checked spins; all 46 seasons observed; fourteen unique drafted players per game; animation options checked against valid outcomes under Keeps; live HTTP startup/state/spin passed; both GOAT pools loaded (149 Award, 15 Prehistoric); JavaScript syntax and whitespace passed.** Results are in `analysis/historical_1980_1983_smoke.json` and `analysis/stage_two_http_smoke.json`. These checks are not a fresh balance study.

New games use Playtest Batch 24 / v0.11.0. Windows, Apple Silicon Mac and Intel Mac workflows package the same source and run tests plus packaged HTTP smoke checks. Packaging is authorized at this checkpoint. Build success and downloadable artifacts must be checked in the corresponding Actions runs; workflow configuration alone is not a completed build.

## Desktop downloads — builds verified

- [Windows](https://github.com/andyb33/Hoopreel/actions/runs/38905403057/artifacts/12048346253)
- [Apple Silicon Mac](https://github.com/andyb33/Hoopreel/actions/runs/38905042518/artifacts/12048385601)
- [Intel Mac](https://github.com/andyb33/Hoopreel/actions/runs/38905042518/artifacts/12048595129)

All three uploaded archives passed their platform tests and packaged HTTP launch checks. GitHub sign-in may be required for Actions artifact downloads. Extract the downloaded archive fully; Mac artifacts contain a second ZIP holding the app and README.

The common game/data source is `84a8f04`; Windows includes `fa8f10d`, which fixes UTF-8 audit-fixture reads and enables UTF-8 mode in its workflow. Game and data files are identical. Build provenance is saved in `analysis/desktop_v0_11_0_builds.json`.
