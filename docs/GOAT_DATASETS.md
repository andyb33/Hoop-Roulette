# GOAT dataset coverage

Updated 2026-10-12. These datasets are not enabled in the alpha yet.

## Award Jackpot

`data/goat/award_jackpot.json` contains every NBA MVP, ROTY, and DPOY winner
from 1973–74 through 2025–26: **149 unique player-seasons**.

- 53 MVP awards, 55 ROTY awards including co-winners, 44 DPOY awards.
- 152 award assignments become 149 entries after merging Jordan 1987–88,
  Olajuwon 1993–94, and Antetokounmpo 2019–20 double winners.
- Different seasons for the same player remain distinct entries.
- Co-winners are different people and retain separate entries.
- Deduplicate by normalized real player identity and season, not award or team.
- A traded winner uses the award-history team and that team's stint stats.
- Pool-specific IDs distinguish award versions from normal versions.

`award_winners_history.json` preserves **187 unique player-seasons** across the
entire official award histories (MVP from 1955–56, ROTY from 1952–53, DPOY from
1982–83). The 38 pre-1973 records are archived, not added to the current Award
Jackpot or the curated Prehistoric Jackpot.

## Verification status

Winner coverage is complete; playable data enrichment is not. 132 entries have
all seven requested statistical fields populated, using historical totals or
the existing three canonical season datasets. Historical source imports are
not equivalent to a completed independent data audit. Only the 9 canonical
recent entries currently have the previous complete game-data verification.

The remaining 17 statistical entries, historical jerseys, All-NBA/All-Defense,
and championship status require collection/verification. Unknown fields use
null and `pending_verification`; they must not be displayed as historical N/A
or silently scored as zero. Historically unavailable awards use separate
availability rules. `manifest.json` explicitly separates winner coverage,
stat coverage and game readiness.

## Reproduce

1. `python scripts/collect_award_winners.py` refreshes official NBA winners.
2. `python scripts/build_goat_datasets.py` joins the committed historical
   stat extracts and current canonical records, then exports both pools.
3. `python -m unittest discover -q` checks coverage, co-winners, aliases,
   merged awards and existing engine regressions.

Saved HTML can be supplied to the collector with `--cache-dir`; it expects
`mvp.html`, `roy.html`, and `dpoy.html`. Historical extracts are committed so
rebuilding does not depend on live downloads. The historical totals source is
https://github.com/peasant98/TheNBACSV/blob/master/nbaNew.csv.

## Official winner sources

- https://www.nba.com/news/history-mvp-award-winners
- https://www.nba.com/news/history-rookie-of-the-year-winners
- https://www.nba.com/news/history-defensive-player-of-the-year-winners

## Prehistoric Jackpot

12 curated entries, one season per player, remain separate. Their jersey and
accolade audit is pending. See GDD v1.5 for selections and nullable scoring.
