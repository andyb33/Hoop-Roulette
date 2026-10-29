# Hoop Roulette web alpha v0.16.0

The first hosted browser version preserves the desktop visual system and adds phone-width Draw / Scorecard tabs, touch-sized controls, responsive dialogs and a return to Draw after scoring. All 53 normal seasons (13,442 entries) and both GOAT pools (164 entries) are included. Gameplay runs per-browser, with no shared server-side game state.

Python remains the scoring/data truth. `python -m scripts.build_browser browser/dist` generates display payloads, scores and availability for every record. Browser `engine.js` implements hierarchical selection, the original no-Keep rejection distribution, unlocked-slot changes/fallbacks, GOAT eligibility, unique draft identities and bonus rules. `node browser/test-engine.cjs` checks 217 exact Python valid-outcome candidate sets, 100 complete seeded games, restored saves, GOAT and player exclusions. The original desktop code is unchanged.

Scores, sound/Instant spins preferences, active game and the last 100 completed browser playtest logs stay in local browser storage. Refresh restores the unfinished game. Scores → Export playtest logs downloads JSONL manually. Clear history confirms scorecard/personal-best reset, keeps preferences/logs, and avoids restoring a cleared completed score on refresh. There is no cross-device or desktop score sync. Clearing browser storage/private browsing can discard these records.

UI validation: a full 14-turn desktop browser game, Team + Player preview/reroll, refresh restoration, results dismissal, history confirmation/reset, and 390px phone-frame tabs/preview/scoring were exercised. This is Chromium QA, not actual iPhone Safari or Android-device testing. First-load asset download requires internet; offline installation/PWA is not implemented in this alpha. Sound quality still needs device feedback.

Hosting starts owner-private for review; changing tester/public access is a separate explicit action. No cloud leaderboard, accounts within the game, automatic telemetry, monetization or wagering is added. Existing desktop releases stay available. A private host may require the owner's ChatGPT sign-in.

## Source and build

- Browser source: `browser/`
- Rebuild: `python -m scripts.build_browser browser/dist`
- Rule parity: `node browser/test-engine.cjs`
- Static output: `browser/dist/` (generated, ignored)

Private hosted game: https://hoop-roulette-web.bouncykiwi13.chatgpt.site

Site project: appgprj_6ae2dac33bfc81918ebe58b11acc33eb. Source commit: ccdda96f0681a07f9ad44b874b2e0cf08c1da97a. Deployment appgdep_6ae2dc813de081918b4fd0ad8f072425 succeeded. The deployed browser correctly shows the private ChatGPT sign-in gate; gameplay was verified on the local Sites preview. Actual-device testing remains next.
