# Hoopreel v0.12.0

Complete NBA normal pool from 1973–74 through 2025–26: 53 seasons, 13,442 eligible player-team-season entries and 1,433 team-season combinations. Eligibility is 30 team GP / 15 unrounded team MPG. Eight ambiguous 1970s jerseys use the user-approved higher-number fallback; source conflicts remain documented.

Normal spins take 1.1 seconds; rerolls at most 0.73 seconds. All previews use eligible candidates. The finished popup offers View scorecard and Play Again; Escape dismisses it. Scores opens browser-local history and personal best.

New games use Batch 26. Extract the complete artifact archive and run the launcher. Mac archives include an inner ZIP containing the app and instructions. These are unsigned alpha packages. Source users can run `python scripts/run_web.py`.

History belongs to the browser and launcher address on this device. Clearing site data or changing the port/browser can affect availability. Development games are excluded.

All three desktop builds passed; downloads are below.

## Desktop downloads

All three builds passed 142 Python tests, frontend checks and packaged HTTP startup checks asserting all 53 seasons / 13,442 entries. Built from commit `7c7510654bd19b6048a43b369f0fc2a754792e19`; later documentation-only commits do not change the packaged code or data.

- [Windows](https://github.com/andyb33/Hoopreel/actions/runs/39098888467/artifacts/12126080991)
- [Apple Silicon Mac](https://github.com/andyb33/Hoopreel/actions/runs/39098888465/artifacts/12125636832)
- [Intel Mac](https://github.com/andyb33/Hoopreel/actions/runs/39098888465/artifacts/12125716607)

Extract the complete artifact archive before running. Mac artifacts contain an inner ZIP with the app and instructions. Build jobs, artifact sizes and SHA-256 digests are preserved in `analysis/desktop_v0_12_0_builds.json`.
