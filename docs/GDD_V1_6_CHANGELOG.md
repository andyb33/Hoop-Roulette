# GDD v1.6 — Unique Draft Picks

Implemented in Hoopreel v0.7.

- Scoring a player removes that real NBA player from all remaining draws in this game, across seasons, teams, Award Jackpot and Prehistoric Jackpot identities.
- A zero-point sacrifice also uses the player.
- Players merely rolled or passed remain eligible. Existing reroll change rules still apply.
- New Game resets all drafted-player exclusions.
- Season → Team → Player weighting remains equal among the valid undrafted options at each stage. Empty team/season options disappear.
- Jackpot trigger odds and type weighting remain unchanged. If the selected jackpot pool has no undrafted entries, fall back to a normal draw; development forcing reports the exhausted pool instead.
- Existing scoring, eligibility and bonus rules remain unchanged.

Historical distribution reports and simulation results describe their original rule versions. New simulations use the unique-draft rule; policy heuristics have not been rebalanced for it.

Playtest Batch 7 separates these results from earlier repeat-player games.
