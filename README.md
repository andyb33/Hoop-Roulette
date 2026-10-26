# Hoop Roulette

**Spin. Keep. Score.**

[GitHub repository](https://github.com/andyb33/Hoop-Roulette)

<img src="web/static/brand-mark.svg" alt="Hoop Roulette symbol" width="96">

Hoop Roulette is a Yahtzee-inspired NBA strategy game built around historical
player-team-season statistics, accolades, games played, and jersey numbers.

## Current status

**v0.15.0 desktop polish:** visible personal best, season coverage, optional sound/effects, Team + Player season previews and confirmed Clear history. Existing saves stay compatible; new games use Batch 31. [Downloads and verification](docs/CHECKPOINT_V0_15_0.md).

**Windows v0.14.3 installer:** [download and verification](docs/CHECKPOINT_V0_14_3_WINDOWS.md). Replaces the portable build that encountered downloaded-DLL restrictions. Extract the ZIP, run Setup, then open Hoop Roulette from Start. Defender and installed native GUI tests passed, including a marked-installer/Korean-path check. Tester confirmation remains pending. Mac remains v0.14.1.

**v0.14.1 Hoop Roulette rebrand:** the approved side-by-side Classic/Accolades scorecard is now the working UI. The complete game canvas fits without scrolling; history uses game-by-game navigation. Windows and Apple Silicon Mac only. [Checkpoint and downloads](docs/CHECKPOINT_V0_14_1.md).

**v0.13.0 standalone desktop:** double-click the Windows `.exe` or Apple Silicon Mac `.app` to play in a dedicated window with all data bundled. No CMD window or browser tab. Desktop testing comes first; public web hosting is deferred. [Release and downloads](docs/CHECKPOINT_V0_13_0.md) · [Tester instructions](docs/EXTERNAL_ALPHA_V0_13_0.md).

**Previous v0.12.1 browser-launching desktop checkpoint:** Skip animation, remembered Instant spins, unfinished-game restart confirmation, bonus points remaining and Clear Keeps. New builds target Windows and Apple Silicon Mac only; Intel builds are discontinued. [Release and downloads](docs/CHECKPOINT_V0_12_1.md) · [Tester instructions](docs/EXTERNAL_ALPHA_V0_12_1.md).

**v0.12.0 includes the normal pool from 1973–74 through 2025–26.**
Stage 3 stats and honors verification now reaches 1973–74: all seven seasons from 1973–74 through 1979–80 have passed. Three seasons are complete; eight final-jersey chronology cases remain across the other four. The seven-season batch stays outside the default pool. See [final four seasons and review list](docs/HISTORICAL_PROGRESS_1973_1977.md).

All three historical stages are complete and active. The final checkpoint adds all seven seasons from 1973–74 through 1979–80.
Normal eligibility remains 30 team GP / 15 team MPG. The Upper
Bonus remains 120 → +35; GOAT pool eligibility is unchanged.

**Unique draft picks:** scoring a player (even for zero) removes every
season, team, and jackpot version of that real player for the rest of the game.
Passed players remain eligible; starting a new game resets the draft.

**Includes GOAT spins:** a gold Award Jackpot (149 verified historical entries)
and purple/blue Prehistoric Jackpot (15 curated entries, including three new
assist-oriented seasons). Eligible spins have a
combined 1/1,296 chance. See [GOAT implementation](docs/GOAT_SPINS_V0_6.md).

Run locally with `python scripts/run_web.py` and open http://127.0.0.1:8000.
For local jackpot preview buttons, use `python scripts/run_web.py --dev-jackpots`.
Development games are not logged. v0.12.0 completes the 53-season normal pool, retaining faster contextual spins, a dismissible results popup, and browser-local score history. [Tester instructions](docs/EXTERNAL_ALPHA_V0_12_0.md). Desktop builds run from the updated packaging workflows.

The forty-six playable datasets from 1973–74 through 2025–26 contain:

- 13,442 eligible player-team records across fifty-three seasons and 1,433 team-season combinations;
- eligibility of at least 30 games and 15.0 minutes per game for that team;
- team-specific statistics for traded players;
- final jersey number for each team stint;
- All-NBA, All-Defensive, champion, MVP, DPOY, and ROTY fields;
- verified jersey evidence retained for all surviving records;
- previous 15 GP / 10 MPG outputs preserved in `data/legacy/15gp_10mpg/`.

The new historical seasons retain their independent stats audits and official
final-appearance jersey audits. See [recovery completion report](docs/HISTORICAL_COMPLETION_1983_1986.md).
The [October 16 data review](docs/DATA_REVIEW_2026_10_16.md) fixes four rounded-MPG eligibility errors, records the accepted Seikaly 4 / Lorthridge 9 chronology inference and the existing Vinnie Johnson inference. All seven 1980–81 jersey decisions are user-reviewed, with conflicting evidence and chronology limitations retained. The final batch is active. Existing balance reports describe the earlier pool and have not been rerun.

Stage 1 and Stage 2 are complete in v0.11.0. Desktop packaging resumes at this checkpoint. Stage 3 continues through 1973–74.
Stage 2 covers 1980–81 through 2009–10; Stage 3 covers 1973–74 through 1979–80.

## Repository structure

```text
data/
├── game/          # Lightweight JSON consumed by the game
└── processed/     # Auditable CSV and validation summaries
nba_roulette/      # Core roulette, scoring, and game-state engine
docs/              # Data architecture and methodology
scripts/           # Reproducible collection and verification scripts
tests/              # Deterministic engine and probability tests
```

See [`docs/DATA_README.md`](docs/DATA_README.md) for the schema, source notes,
eligibility rules, jersey-number policy, and rebuild instructions.

See [`docs/DISTRIBUTION_REPORT.md`](docs/DISTRIBUTION_REPORT.md) for the
roulette-weighted three-season scoring, Joker, and accolade distributions.

See [`docs/ENGINE.md`](docs/ENGINE.md) for roulette resolution, lock semantics,
scoring defaults, and engine verification.

See [`docs/BASELINE_SIMULATION.md`](docs/BASELINE_SIMULATION.md) for the
Random and Greedy full-game simulation baselines.

See [`docs/STRATEGIC_SIMULATION.md`](docs/STRATEGIC_SIMULATION.md) for the
lock-aware heuristic comparison.

See [`docs/THREE_SEASON_SIMULATION_RERUN.md`](docs/THREE_SEASON_SIMULATION_RERUN.md)
for the consolidated two-season versus three-season simulation results and
the resulting decision to retain the 120 → +35 Upper Bonus.

See [`docs/GDD_V1_1_CHANGELOG.md`](docs/GDD_V1_1_CHANGELOG.md) for the evidence-
based change from the original 140-point bonus threshold to the 120-point
prototype rule.

See [`docs/GDD_V1_2_CHANGELOG.md`](docs/GDD_V1_2_CHANGELOG.md) and
[`docs/HUMAN_PLAYTEST_01.md`](docs/HUMAN_PLAYTEST_01.md) for the cumulative
accolade rule and terminology changes made after the first human playtest.

See [`docs/GDD_V1_3_CHANGELOG.md`](docs/GDD_V1_3_CHANGELOG.md) for the
playtest-driven reroll difference rule, repeat-rate audit, and rationale for
not yet adding a game-wide player ban.

See [`docs/GDD_V1_4_CHANGELOG.md`](docs/GDD_V1_4_CHANGELOG.md) for the stronger
unlocked-slot reroll rule, clarified used-category state, and clean transition
from the interrupted v0.3 batch to v0.4 validation.

## Rebuild a dataset

```bash
python scripts/build_dataset.py --season 2023-24
python scripts/build_dataset.py --season 2024-25
python scripts/build_boxscore_dataset.py --season 2025-26 \
  --boxscores data/raw/2025-26/player_boxscores_2026.csv
```

## Rebuild the distribution report

```bash
python scripts/analyze_distributions.py
```

## Verify the game engine

```bash
python -m unittest discover -v
python scripts/verify_engine.py
```

## Run the baseline simulations

```bash
python scripts/simulate_baselines.py
python scripts/simulate_strategic.py
python scripts/simulate_bonus_sensitivity.py
python scripts/summarize_simulation_rerun.py
```

## Play one terminal game

```bash
python scripts/play_game.py
```

## Run the browser prototype

```bash
python scripts/run_web.py
```

Then open `http://127.0.0.1:8000`. The prototype uses only the Python standard
library and the existing game engine; no additional packages are required.
See [`docs/WEB_PROTOTYPE.md`](docs/WEB_PROTOTYPE.md) for the included features,
architecture, v0.2 playtest-driven interface changes, and deliberate limitations.
Prototype v0.4 guarantees that every unlocked slot changes whenever a valid
combined outcome permits it, and gives used scorecard categories an unmistakable
filled and checked state.

## Build the Windows or Mac alpha

The GitHub Actions workflows build a standalone Windows `.exe` and an Apple Silicon Mac `.app`, with bundled game data and a dedicated native window. Intel builds are discontinued. Testers do not need Python or a command prompt. Run **Build Hoop Roulette Windows alpha v0.14.1** or **Build Hoop Roulette Mac alpha v0.14.1** from the Actions tab. See [tester instructions](docs/EXTERNAL_ALPHA_V0_14_1.md) and [current downloads](docs/CHECKPOINT_V0_14_1.md). Older packages retain their original names and remain historical releases.

Completed local games are captured in `playtest_logs/` during development, or Documents/Hoopreel/playtest_logs in packaged apps, with legacy NBA Roulette folders retained when already present. This folder is intentionally excluded from Git.

## Game design snapshot

Each turn produces a valid `Season → Team → Player` combination. Before a
reroll, players explicitly choose which slots to **keep**; all other slots are
rerolled. The final player-team-season is assigned to an unused scorecard
category. The initial game design uses 14 categories and up to three spins per
turn.

## Brand and rights

The current product name is **Hoop Roulette**, with the tagline **Spin. Keep. Score.** Trademark clearance and registration are pending; no registered status is claimed. See [brand and rights notes](docs/BRAND_AND_RIGHTS.md).

Hoop Roulette is an independent basketball fan project and is not affiliated with or endorsed by the NBA, its teams, or players. This statement does not replace any necessary permissions.

Legacy `Hoopreel` save-directory and storage identifiers remain intentionally compatible so existing scores and preferences survive the rename. Historical release records retain their original names.
