# Hoopreel v0.11.0 — Stage 2 complete

46 playable seasons, 1980–81 through 2025–26. The normal pool contains 12,169 eligible player-team-season entries across 1,292 team-seasons. Every season uses 30 team-stint GP / 15 unrounded MPG.

## Desktop

Download the archive for Windows, Apple Silicon Mac or Intel Mac from the matching v0.11.0 GitHub Actions run. Extract the full archive. Run the Windows executable or the Mac app and keep it running while playing in the browser. No separate Python installation is required. These are unsigned alpha builds; operating-system security prompts may appear.

If macOS blocks the app, use Finder’s Open command or System Settings → Privacy & Security → Open Anyway only for the build downloaded from this repository.

Logs are saved under Documents/Hoopreel/playtest_logs (or an existing legacy NBA Roulette folder). New games use Playtest Batch 24.

## Source

Run `python scripts/run_web.py` and open http://127.0.0.1:8000. Restart the launcher after pulling updates. Development jackpot previews use `--dev-jackpots` and are excluded from playtest logs.

Stage 1 and Stage 2 are complete. Stage 3, 1973–74 through 1979–80, remains pending. Seven 1980–81 jersey numbers are accepted user-reviewed decisions with explicit chronology limitations and conflicting evidence retained. Earlier historical inference notes remain preserved.

## Desktop downloads — builds verified

- [Windows](https://github.com/andyb33/Hoopreel/actions/runs/38905403057/artifacts/12048346253)
- [Apple Silicon Mac](https://github.com/andyb33/Hoopreel/actions/runs/38905042518/artifacts/12048385601)
- [Intel Mac](https://github.com/andyb33/Hoopreel/actions/runs/38905042518/artifacts/12048595129)

All three uploaded archives passed their platform tests and packaged HTTP launch checks. GitHub sign-in may be required for Actions artifact downloads. Extract the downloaded archive fully; Mac artifacts contain a second ZIP holding the app and README.

The common game/data source is `84a8f04`; Windows includes `fa8f10d`, which fixes UTF-8 audit-fixture reads and enables UTF-8 mode in its workflow. Game and data files are identical. Build provenance is saved in `analysis/desktop_v0_11_0_builds.json`.
