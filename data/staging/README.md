# Historical stats staging

2022–23: 305 eligible team-specific player records, 30 teams, 1,230 observed regular-season games.
Filter: 30 team GP / 15 team MPG, using unrounded box-score minutes.
Stats-only, not independently verified and not enabled in the game. No jersey or accolade values are fabricated.

Source: SportsDataverse mirror of NBA player box scores; original download is cached in data/raw/2022-23 (ignored by Git). The committed manifest records the URL and SHA-256.

Reproduce: python scripts/collect_historical_stats.py --season 2022-23

Next: final stint jerseys, season accolades/champion joins, independent verification, and distribution analysis. 2021–22 is also collected: 317 eligible records, 30 teams, 1,230 observed regular-season games. Other 2010–11 through 2020–21 seasons are not yet collected.
