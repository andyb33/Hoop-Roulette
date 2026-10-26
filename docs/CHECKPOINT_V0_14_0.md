# v0.14.0 — compact desktop layout

The user-approved prototype is now the working game UI. The scorecard has two equal columns with seven categories each: Classic stats plus Jokers, and Accolades. Reels, player information and spins sit on the right. Totals are in the header; the scoring action has a permanent place below the scorecard. The main game never scrolls. On smaller native windows, the complete canvas scales to fit instead of hiding controls. The app remains Windows / Apple Silicon Mac only.

History retains the last 50 saved scorecards and personal best, with one full scorecard per page and Newer/Older navigation. Existing native saves and all five QOL controls remain compatible. Scoring, spins, eligibility and the 53-season data pool are unchanged. Playtest Batch 29 identifies this layout checkpoint.

Validation includes 146 Python tests and frontend behavior checks, plus native-window geometry checks at default and minimum window sizes. The native checks cover long names, multiple awards, jackpot banners, historical notes, all fourteen score selections, completed scorecards, history, settings persistence and shutdown. Packaged GUI checks complete two games per platform. Local Chromium could not be installed, so rendered geometry and a Mac screenshot are collected from the native builds instead.

Build results and download links will be recorded when the native packages pass.
