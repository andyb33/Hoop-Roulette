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

All **149 award entries and 12 prehistoric entries** were checked against
official NBA regular-season career statistics, historical team-season rosters,
All-NBA/All-Defense lists and championship history. There are no unresolved
fields in the two selected pools. The 17 missing statistical entries and all
historical jersey/accolade fields are now filled. Raw selected source rows and
URLs are preserved in `official_verification.json`; findings are preserved in
`verification_report.json` and [the audit report](GOAT_VERIFICATION.md).

The NBA roster is the evidence for the team-season jersey number. Multiple
different numbers would block verification rather than selecting one arbitrarily.
Real NBA player IDs are resolved using name and career dates, avoiding same-name
collisions. Pre-1973 defensive API zeros become null/not_recorded; unavailable
awards and actual non-selections retain separate availability reasons.
The datasets are ready for GOAT-spin implementation; the feature is still disabled
in the existing alpha. The 38 earlier archived award records are winner metadata
only and were not included in this 161-entry full-field audit.

## Reproduce

1. `python scripts/collect_award_winners.py` refreshes official NBA winners.
2. `python scripts/verify_goat_datasets.py` refreshes official evidence for both
   selected pools. Downloads are cached locally; selected source rows are committed.
3. `python scripts/build_goat_datasets.py` applies the official evidence and
   exports both pools without needing live downloads.
4. `python -m unittest discover -q` checks coverage, co-winners, aliases,
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

12 curated entries, one season per player, remain separate and are verified.
See GDD v1.5 for selections and nullable scoring.
