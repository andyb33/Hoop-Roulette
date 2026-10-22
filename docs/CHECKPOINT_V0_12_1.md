# v0.12.1 — UI QOL desktop checkpoint

This release packages Skip animation, Instant spins, unfinished-game restart confirmation, upper-bonus points remaining and Clear Keeps. See [UI behavior notes](UI_QOL_2026_10_22.md).

New desktop builds target Windows and Apple Silicon Mac only. The Intel job is removed from the Mac workflow. Apple Silicon builds explicitly target arm64 and verify the runner architecture before packaging. Existing Intel artifacts remain historical downloads.

The normal pool remains 53 seasons / 13,442 entries / 1,433 team-seasons. Scoring and eligibility are unchanged. New games use Batch 27 / v0.12.1. Packaged launch checks verify the complete pool and that the served HTML/JavaScript includes the new QOL controls.

Build results and downloads will be appended after both workflows finish. Visual browser/mobile QA remains separate from automated checks.
