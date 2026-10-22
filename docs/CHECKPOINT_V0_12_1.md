# v0.12.1 — UI QOL desktop checkpoint

This release packages Skip animation, Instant spins, unfinished-game restart confirmation, upper-bonus points remaining and Clear Keeps. See [UI behavior notes](UI_QOL_2026_10_22.md).

New desktop builds target Windows and Apple Silicon Mac only. The Intel job is removed from the Mac workflow. Apple Silicon builds explicitly target arm64 and verify the runner architecture before packaging. Existing Intel artifacts remain historical downloads.

The normal pool remains 53 seasons / 13,442 entries / 1,433 team-seasons. Scoring and eligibility are unchanged. New games use Batch 27 / v0.12.1. Packaged launch checks verify the complete pool and that the served HTML/JavaScript includes the new QOL controls.

Both builds passed 142 Python tests, frontend checks and packaged launch checks. Built from commit `9a25fe2c2f9bc0ca71a30e6a005510acbc3a0f6d`. The Mac job verified its arm64 runner and explicitly targeted arm64; no Intel job ran. Evidence and artifact SHA-256 digests are recorded in `analysis/desktop_v0_12_1_builds.json`. Visual browser/mobile QA remains separate from automated checks.

## Downloads

- [Windows](https://github.com/andyb33/Hoopreel/actions/runs/39745738081/artifacts/12411237688)
- [Mac — Apple Silicon, M1 or later](https://github.com/andyb33/Hoopreel/actions/runs/39745738294/artifacts/12410139914)

Fully extract the archive before running. The Mac artifact contains an inner ZIP with the app and instructions. GitHub sign-in may be required. New builds no longer include an Intel Mac executable.
