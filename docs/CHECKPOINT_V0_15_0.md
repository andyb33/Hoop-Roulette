# Hoop Roulette v0.15.0 — desktop polish

Adds visible personal best and a new-record highlight; normal-pool coverage in the footer (53 seasons, 1973–74 to 2025–26), with Prehistoric Jackpots distinguished; optional synthesized sound cues with a remembered toggle; scoring/record effects that respect reduced motion; and a paginated Team + Player reroll preview showing legal seasons and unused-category scores. Previewing neither consumes randomness nor spends a spin. The current year is excluded when an alternative exists; a single-season fallback is explicitly identified.

Scores → Clear history has a separate confirmation and resets saved scorecards and personal best only. Active game, preferences and playtest logs remain. The clear is persisted before the UI reports success; a just-completed cleared game cannot be reinserted by rerendering. Errors keep the previous visible history. Preferences and history keep existing save identifiers.

## Batch 30 review

The tester reported no frustrating behavior or new gameplay bugs, requested audiovisual polish and clearer information, and confirmed the v0.14.3 Windows installer works. The supplied 19-game logs have mean 377.05, median 389, range 260–466, bonus in 13/19 games, 517 distinct players across 710 spins and all 53 normal seasons. 136/444 rerolls used Keeps; 28 kept Team + Player. No jackpots occurred. Completed score totals reconcile and each scorecard has fourteen distinct player identities. This is a single-player sample, not evidence that all balance/bugs are resolved. No scoring or data changes are made. New games use Batch 31, keeping the baseline separate.

## Verification

148 Python tests and frontend behavior checks pass locally. Native builds additionally exercise two full games at initial/minimum window sizes, preview geometry, score-history reset persistence, preservation of sound/Instant spins and shutdown. Windows retains the scanned per-user installer and Korean-path/marked-download regression; Mac targets Apple Silicon only. Sound uses original Web Audio tones, no external audio files. Sound defaults off. Actual audible quality still needs tester feedback.

Both packages passed all native checks, including persistent history reset and preference preservation. The Mac screenshot was visually inspected and the new header, preview button and coverage footer fit the no-scroll canvas. Windows Defender reported no threats in payload and installer (engine 1.1.26090.9, signature 1.461.140.0 dated 2026-10-21). The marked-download installer/Korean-path regression passed. These checks do not guarantee Chrome acceptance or audible sound quality.

## Downloads

- [Windows installer](https://github.com/andyb33/Hoop-Roulette/actions/runs/40382116002/artifacts/12678918246)
- [Apple Silicon Mac](https://github.com/andyb33/Hoop-Roulette/actions/runs/40382102386/artifacts/12679301242)

Source: 934aea1679c59602c891c0fa650b559479171481. Native reports are preserved in analysis/desktop_v0_15_0_*. Existing saves upgrade without a reset; use Clear history only if you want to remove saved scorecards and personal best.
