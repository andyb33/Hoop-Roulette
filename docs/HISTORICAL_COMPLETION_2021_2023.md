# 2022–23 and 2021–22 completion — v0.9

Both independently verified staging seasons are now playable.

| Season | Entries | Final-appearance jerseys | All-NBA | All-Defense | Championship members |
|---|---:|---:|---:|---:|---:|
| 2022–23 | 305 | 305 | 15 | 10 | 9 (DEN) |
| 2021–22 | 317 | 317 | 15 | 10 | 12 (GSW) |

The full normal pool contains 1,565 entries across 2021–22 through 2025–26.
Eligibility remains 30 team GP / 15 team MPG. The 120 → +35 upper bonus and
GOAT pools are unchanged. New game logs use Playtest Batch 9.

## Evidence and method

- Preserve the exact stats snapshots that passed 2,135 and 2,219 independent
  comparisons respectively; game exports contain the same stats without changes.
- Verify the source checksum against each collection manifest.
- Use official NBA LeagueGameFinder dates rather than sorting game IDs, so
  rescheduled games are ordered correctly.
- Select the last recorded regular-season appearance for each player-team stint.
  Blank-minute DNPs are excluded; recorded 0:00 appearances remain eligible.
- Retrieve the final game's official NBA live box score. Match player ID and
  team, require played status, and record jersey evidence and source hashes for
  all 622 entries. Preserve jersey display strings, including 00.
- Parse the official NBA historical All-NBA and All-Defense articles. Store
  actual tiers, leaving cumulative eligibility to the scoring engine.
- Join the existing verified official MVP, DPOY and ROTY history. Each season
  has one winner for each award, and all are present in the new normal pools.
- Championship credit requires the championship team stint AND membership in
  the official title-clinching game roster, including its DNP players.

The 2022–23 title roster is game 0042200405; 2021–22 is 0042100406.
Bones Hyland's Denver entry does not receive championship credit: he was traded
away before Denver's title run. Jimmy Butler III is explicitly matched by NBA
player ID 202710 to the honors-list name Jimmy Butler.

Detailed evidence: `data/processed/completion_2022_23.json` and
`data/processed/completion_2021_22.json`. Flat jersey audits and processed CSVs
are alongside those files. No unresolved required fields remain.

## Validation

74 automated tests pass. Promotion checks preserve every staged stat, verify
checksums, compare jerseys with official final-game evidence, and check
championship roster membership. 100 complete games finish with 14 unique
scored players each, and both newly added seasons appear in the results.

## Reproduce

```bash
python scripts/complete_historical_seasons.py --season 2022-23
python scripts/complete_historical_seasons.py --season 2021-22
python -m unittest discover -v
```

The source collector downloads the original box-score mirror if needed; its
checksum must still match. Official endpoint responses are cached locally.
The earlier source precision differences remain documented in staging.
Distribution analysis has not been rerun; earlier reports describe their
original pools. 2010–11 through 2020–21 remain pending.
