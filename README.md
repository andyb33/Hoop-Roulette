# Hoopreel

**Spin. Keep. Score.**

[GitHub repository](https://github.com/andyb33/Hoopreel)

<img src="web/static/brand-mark.svg" alt="Hoopreel symbol" width="96">

Hoopreel is a Yahtzee-inspired NBA strategy game built around historical
player-team-season statistics, accolades, games played, and jersey numbers.

## Current status

**v0.10.7 includes the normal pool from 1989–90 through 2025–26.**
The first twenty-one Stage 2 seasons have been rebuilt and independently verified.
The verified 37-season pool is published on `main`. Recovery checkpoints remain on `recovery/three-season-batches-20261014`.
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
Development games are not logged. Windows and Mac v0.10 packaging workflows are prepared for manual dispatch.
Packages have not been built; [tester instructions](docs/EXTERNAL_ALPHA_V0_10.md).

The thirty-seven datasets from 1989–90 through 2025–26 are complete:

- 10,291 eligible player-team records across thirty-seven seasons and 1,083 team-season combinations;
- eligibility of at least 30 games and 15.0 minutes per game for that team;
- team-specific statistics for traded players;
- final jersey number for each team stint;
- All-NBA, All-Defensive, champion, MVP, DPOY, and ROTY fields;
- verified jersey evidence retained for all surviving records;
- previous 15 GP / 10 MPG outputs preserved in `data/legacy/15gp_10mpg/`.

The new historical seasons retain their independent stats audits and official
final-appearance jersey evidence. See [recovery completion report](docs/HISTORICAL_COMPLETION_1989_1992.md).
Existing balance reports describe the earlier pool and have not been rerun.

Stage 1 data is complete in the v0.10 source. The next desktop package will be built after Stage 2 reaches 1980–81. Stage 3 then continues through 1973–74.
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

The GitHub Actions workflows build a Windows `.exe` and separate Apple Silicon
and Intel Mac `.app` artifacts with the v0.5 screen and three-reel animation. They bundle the three
game datasets and browser assets, select an available local port, and open the
game automatically. Testers do not need Python or a command prompt.

Run **Build Hoopreel Windows alpha v0.5** or **Build Hoopreel Mac alpha v0.5** from the Actions
tab and send the resulting ZIP to testers. See
[`docs/EXTERNAL_ALPHA_V0_5.md`](docs/EXTERNAL_ALPHA_V0_5.md) for the exact
tester instructions. The previous v0.4 Windows workflow artifacts remain
available in GitHub Actions history as legacy builds.

Completed local games are automatically captured for **Playtest Batch 4 — v0.4
External Alpha** in `playtest_logs/` as detailed JSONL plus a CSV summary. The
folder is intentionally excluded from Git. Packaged Windows builds use the
tester-facing Documents location described in the alpha instructions.

## Game design snapshot

Each turn produces a valid `Season → Team → Player` combination. Before a
reroll, players explicitly choose which slots to **keep**; all other slots are
rerolled. The final player-team-season is assigned to an unused scorecard
category. The initial game design uses 14 categories and up to three spins per
turn.
