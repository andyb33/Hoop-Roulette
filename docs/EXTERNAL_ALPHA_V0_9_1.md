# Hoopreel v0.9.1 — Eight-season pool

Normal spins now cover 2018–19 through 2025–26: 2,477 player-team-season entries.
The 2020–21, 2019–20 and 2018–19 additions include independently checked stats, official
final-team-appearance jerseys, All-NBA, All-Defense, major awards, and title-roster
championship membership.

Eligibility stays 30 GP / 15 MPG. The 120 → +35 upper bonus, unique draft picks,
and both GOAT pools are unchanged. New games log to Playtest Batch 10.

## Run from source

```bash
git pull
python scripts/run_web.py
```

Open http://127.0.0.1:8000. Restart the server after pulling.

## Desktop download

Extract the entire downloaded archive. Run the Windows executable or Mac app;
the browser opens automatically. Keep the launcher running while playing.
Mac Gatekeeper may require opening via the contextual Open command.

Development-only jackpot previews: `python scripts/run_web.py --dev-jackpots`.
Preview games are excluded from playtest logs.

The earlier distribution reports have not been rerun for the eight-season pool.
2010–11 through 2017–18 remain outside this build.
