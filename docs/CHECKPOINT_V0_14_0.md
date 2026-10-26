# v0.14.0 — compact desktop layout

The user-approved prototype is now the working game UI. The scorecard has two equal columns with seven categories each: Classic stats plus Jokers, and Accolades. Reels, player information and spins sit on the right. Totals are in the header; the scoring action has a permanent place below the scorecard. The main game never scrolls. On smaller native windows, the complete canvas scales to fit instead of hiding controls. The app remains Windows / Apple Silicon Mac only.

History retains the last 50 saved scorecards and personal best, with one full scorecard per page and Newer/Older navigation. Existing native saves and all five QOL controls remain compatible. Scoring, spins, eligibility and the 53-season data pool are unchanged. Playtest Batch 29 identifies this layout checkpoint.

Validation includes 146 Python tests and frontend behavior checks, plus native-window geometry checks at default and minimum window sizes. The native checks cover long names, multiple awards, jackpot banners, historical notes, all fourteen score selections, completed scorecards, history, settings persistence and shutdown. Packaged GUI checks complete two games per platform. Local Chromium could not be installed, so rendered geometry and a Mac screenshot are collected from the native builds instead.

Both packages passed. Each completed two full games, all 14 score selections and default/minimum-window geometry checks. The Mac screenshot was visually inspected: the complete two-column scorecard, player card and controls fit without scrolling. Native content viewports checked were Windows 1028×749 and 884×611, and Mac 1024×646 and 900×622 (runner displays constrain the initial window). Native QA reports and build metadata are preserved in `analysis/desktop_v0_14_0_*`.

## Downloads

- [Windows standalone app](https://github.com/andyb33/Hoopreel/actions/runs/40315524709/artifacts/12647200735)
- [Apple Silicon Mac standalone app](https://github.com/andyb33/Hoopreel/actions/runs/40315524737/artifacts/12645604121)

Built from commit `7106d8698c5ded265e852e29ccfaf48ba67290dc`. Fully extract before running; the Mac artifact contains an inner ZIP. Existing native score history and preferences remain compatible. The native QA artifact on the Mac run includes the captured screenshot. Human playtesting remains the next step.
