# GDD v1.5 — Historical Seasons & GOAT Spins

Design accepted 2026-10-12. Specification for the next implementation; the
published v0.5 alpha continues to run v1.4 until this feature is implemented.

## Historical normal pool

Target NBA seasons: 1973–74 through 2025–26. Only teams with eligible records in
the selected season can appear. Never generate a team before its existence.
Historical team identities and franchise lineage must be stored separately;
whether Team Keep crosses a relocation remains unresolved.

Proposed filter: 30 team GP and 20 team MPG for 1973–74 through 1988–89;
15 team GP and 10 team MPG from 1989–90. The early-era filter is provisional,
pending roster-count and balance analysis. All other scoring and the 120/+35
bonus remain unchanged.

## GOAT spins

GOAT spins is the collective name for Award Jackpot and Prehistoric Jackpot.
Each eligible spin has a combined trigger probability of 1/1296. On a trigger,
choose the two types equally: each has probability 1/2592 per eligible spin.
This is the probability of five identical fair dice in one roll, not the
probability of achieving Yahtzee over multiple rolls.

Eligible attempts are the first spin of each turn and any reroll with no kept
slots. Attempts with kept slots have no jackpot check. Each attempt consumes
one of the usual three spins. A jackpot may be scored immediately. All Keep
controls are disabled on a jackpot result. Rerolling releases the entire result
and performs a fresh check; consecutive GOAT spins are possible. Normal-result
rerolls continue to use the v1.4 difference filter. Whether consecutive jackpot
draws may repeat the exact entry is unresolved; do not silently apply normal
reroll filtering to the jackpot pool.

Initial data draw proposal: uniform among distinct entries within each jackpot
pool, rather than normal Season → Team → Player weighting. Validate in simulation.

## Award Jackpot

Include actual NBA MVP, DPOY, or ROTY winning player-seasons from 1973–74 onward.
A player winning multiple qualifying awards in a season has one entry with
multiple flags. Major Award still scores 50, not 50 per award. Historical
coverage must be explicit. The winner catalogue now covers all 53 seasons:
149 unique player-seasons representing 53 MVP, 55 ROTY (including ties), and
44 DPOY awards. Three MVP/DPOY double winners are merged. Full historical
statistics, jerseys and other accolades still need verification before enabling
the feature. A separate archive preserves all 187 winning player-seasons since
each award's inception; its 38 pre-1973 entries are excluded from this pool.

Award Jackpot has exactly one entry per real player per season, independent of
how many qualifying awards or team stints they had. Use the team named in the
official award history and that team's stint statistics, not combined totals.
Other stints remain normal-pool records. If award sources disagree about the
team, flag the entry for review rather than creating duplicates. Normal-pool
GP/MPG thresholds do not exclude an actual winner from this special pool.

## Prehistoric Jackpot

NBA seasons before 1973–74. Exactly one curated season per real player. Initial
selection: Wilt 1961–62, Russell 1964–65, Robertson 1961–62, West 1969–70,
Kareem 1971–72, Baylor 1961–62, Pettit 1958–59, Barry 1966–67,
Havlicek 1970–71, Frazier 1969–70, Thurmond 1967–68, Cousy 1956–57.
Use regular-season team stats, the final team-stint jersey, and actual accolades.
Do not estimate defensive statistics from anecdotes.

## Missing values

Use null plus an explicit availability reason for unrecorded statistics or
awards not introduced. Display N/A; never silently convert null into zero.
Unavailable categories can deliberately be sacrificed for 0 with clear wording.
False means an available award was not won; null means unavailable historically.
All-Defense starts 1968–69, DPOY 1982–83, All-NBA Third 1988–89.
Earlier All-NBA First/Second selections still qualify for the cumulative Third
scoring category, even though an actual Third-Team selection did not exist.

## Identity and provenance

Keep the source's real player ID stable. Add pool-specific game_player_id and a
pool/season/team entry_id. Normal, award, and prehistoric versions are distinct
game identities; e.g. 2025–26 award Wembanyama differs from normal Wembanyama.
Shared statistics come from canonical records instead of manual duplicate entry.
Store pool and entry IDs in playtest logs. Pool origin does not change scoring
or create a ban on using the same real player on later turns.

## Delivery order

Document → build and verify both GOAT datasets → implement and test GOAT spins
→ expand the normal historical pool → simulate balance → hosted browser version.
Browser plan: preserve the Python engine, add isolated per-player sessions and
production hosting/logging. Multiplayer later uses server-authoritative actions.
