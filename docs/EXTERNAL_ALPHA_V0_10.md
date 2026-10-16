# Hoopreel v0.10.10 — 43-season source build

Normal spins cover 1983–84 through 2025–26: 11,536 eligible player/team/season entries across 43 seasons and 1,223 team-season combinations. Eligibility is 30 team-stint GP / 15 unrounded MPG. The October 16 review corrects four rounded-MPG boundary entries. New games use Playtest Batch 23.

Run `python scripts/run_web.py` and open http://127.0.0.1:8000. Restart the server after pulling updates. Development jackpot previews use `python scripts/run_web.py --dev-jackpots`; preview games are excluded from playtest logs.

The repository also contains completed 1982–83 and 1981–82 datasets and staged 1980–81 stats. These three seasons are not activated. Seven 1980–81 final jersey numbers remain unresolved. Seikaly 4, Lorthridge 9 and Vinnie Johnson 25 use documented historical inference. See [the review](DATA_REVIEW_2026_10_16.md).

Desktop packages are deferred until the final Stage 2 season, 1980–81, is complete. Manual GitHub Actions workflows target Windows, Apple Silicon Mac and Intel Mac. Earlier downloadable packages contain smaller pools and do not represent this source version.

When new packages become available, extract the full archive and run the Windows executable or Mac app. Keep the launcher running while playing. The browser opens automatically.

Stage 1 (2010–11 through 2025–26) is complete. Stage 2 covers 1980–81 through 2009–10 and is 29/30 complete in validation, with 27/30 activated. Stage 3 covers 1973–74 through 1979–80. Historical balance reports have not been rerun for the current pool.
