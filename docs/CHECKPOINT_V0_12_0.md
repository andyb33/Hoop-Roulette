# v0.12.0 — complete NBA history checkpoint

All 53 NBA normal-pool seasons, 1973–74 through 2025–26, are active: **13,442 eligible entries / 1,433 team-season combinations**. Stage 3 adds 1,273 entries across seven seasons, backed by 8,911 independent stat comparisons. Every season retains the fixed 30 team GP / 15 unrounded team MPG rule. ABA seasons are outside scope.

Eight jersey ambiguities use the user-approved higher-number fallback and are labelled as policy resolutions rather than historically verified final numbers. Original conflicting sources, scoped stat corrections and missing-date/appearance evidence remain preserved. The readiness report records zero pending reviews and activation in the default pool.

Validation: 142 Python tests; frontend animation and score-history checks; live HTTP startup, state and spin checks; 100 complete games with 14 unique drafted players each and 2,790 contextual spin-preview checks. All 53 normal seasons appeared. Both jackpot pools remain enabled. Results are in `analysis/full_history_1973_2026_smoke.json` and `analysis/full_history_http_smoke.json`; the gameplay verification can be rerun with `python scripts/verify_full_history_gameplay.py`. This is programmatic validation, not a visual playtest or a balance study.

New games use Batch 26. Windows, Apple Silicon and Intel Mac workflows target v0.12.0. Each packaged launcher must serve all 53 seasons and 13,442 entries over HTTP before upload. All three builds passed; downloads are below.

## Desktop downloads

All three builds passed 142 Python tests, frontend checks and packaged HTTP startup checks asserting all 53 seasons / 13,442 entries. Built from commit `7c7510654bd19b6048a43b369f0fc2a754792e19`; later documentation-only commits do not change the packaged code or data.

- [Windows](https://github.com/andyb33/Hoopreel/actions/runs/39098888467/artifacts/12126080991)
- [Apple Silicon Mac](https://github.com/andyb33/Hoopreel/actions/runs/39098888465/artifacts/12125636832)
- [Intel Mac](https://github.com/andyb33/Hoopreel/actions/runs/39098888465/artifacts/12125716607)

Extract the complete artifact archive before running. Mac artifacts contain an inner ZIP with the app and instructions. Build jobs, artifact sizes and SHA-256 digests are preserved in `analysis/desktop_v0_12_0_builds.json`.
