# Hoopreel v0.10 — Complete Stage 1 pool

Normal spins cover every season from 2010–11 through 2025–26: 4,840 player-team-season entries across 16 seasons. Historical additions retain independent stat checks, final-team-appearance jersey evidence, All-NBA, All-Defense, major awards and title-roster championship membership.

Eligibility remains 30 team GP / 15 team MPG. The 120 → +35 upper bonus, unique draft picks and both GOAT pools are unchanged. New games use Playtest Batch 13.

## Run from source

```bash
python scripts/run_web.py
```

Open http://127.0.0.1:8000. Restart the server after updating the source.

## Desktop packages

This is the v0.10 source; Windows and Mac packages are deferred until all normal seasons through 1973–74 are complete. Manual GitHub Actions workflows are configured for Windows, Apple Silicon Mac and Intel Mac. No automatic build triggers are enabled.

When packages become available, extract the entire archive and run the Windows executable or Mac app. The browser opens automatically. Keep the launcher running while playing. Mac Gatekeeper may require opening via the contextual Open command.

Development jackpot previews: `python scripts/run_web.py --dev-jackpots`. Preview games are excluded from playtest logs.

Earlier distribution reports describe smaller pools and have not been rerun. Stage 2 is 1980–81 through 2009–10; Stage 3 is 1973–74 through 1979–80. These older seasons are outside the normal v0.10 pool.
