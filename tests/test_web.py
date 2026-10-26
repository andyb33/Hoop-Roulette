import unittest
from dataclasses import replace

from nba_roulette.scoring import Category
from nba_roulette.web import BrowserGame

from .test_roulette import make_record, draft_pool as pool


class BrowserGameTests(unittest.TestCase):
    def test_initial_state_is_ready_to_spin(self) -> None:
        state = BrowserGame(pool(), seed=1).state()
        self.assertIsNone(state["player"])
        self.assertEqual(state["turn"], 1)
        self.assertEqual(len(state["categories"]), 14)
        points = next(item for item in state["categories"] if item["id"] == "points")
        major = next(item for item in state["categories"] if item["id"] == "major_award")
        self.assertEqual(points["formula"], "×2")
        self.assertEqual(points["glow_threshold"], 40)
        self.assertEqual(major["fixed_value"], 50)
        self.assertEqual(major["icon"], "⭐")

    def test_spin_keep_and_score_round_trip(self) -> None:
        browser = BrowserGame(pool(), seed=7)
        first = browser.spin()
        season = first["player"]["season"]
        second = browser.spin(["season"])
        self.assertEqual(second["player"]["season"], season)
        self.assertEqual(second["spins_used"], 2)
        scored = browser.score(Category.POINTS.value)
        points = next(item for item in scored["categories"] if item["id"] == "points")
        self.assertTrue(points["used"])
        self.assertIsNone(scored["player"])
        self.assertEqual(scored["turn"], 2)

    def test_all_three_keeps_are_rejected_by_engine(self) -> None:
        browser = BrowserGame(pool(), seed=3)
        browser.spin()
        with self.assertRaisesRegex(ValueError, "all three"):
            browser.spin(["season", "team", "player"])

    def test_unknown_category_is_rejected(self) -> None:
        browser = BrowserGame(pool(), seed=3)
        browser.spin()
        with self.assertRaisesRegex(ValueError, "Unknown score category"):
            browser.score("not-a-category")

    def test_complete_browser_game_reports_final_state(self) -> None:
        browser = BrowserGame(pool(), seed=9)
        state = None
        for category in Category:
            browser.spin()
            state = browser.score(category.value)
        self.assertIsNotNone(state)
        self.assertTrue(state["complete"])
        self.assertEqual(state["turn"], 14)
        self.assertEqual(sum(item["used"] for item in state["categories"]), 14)

    def test_player_card_exposes_team_colors_and_vertical_awards(self) -> None:
        record = replace(
            make_record("S1", "BOS", 50, "Winner"),
            all_nba=1,
            all_defense=2,
            champion=True,
            mvp=True,
        )
        player = BrowserGame._player(record)
        self.assertEqual(player["team_colors"]["primary"], "#007A33")
        self.assertEqual(
            [award["label"] for award in player["awards"]],
            ["All-NBA First", "All-Defense Second", "Champion", "MVP"],
        )
        self.assertTrue(all("icon" in award for award in player["awards"]))

    def test_animation_uses_all_seasons_and_valid_locked_warriors(self):
        from nba_roulette.data import load_records
        from nba_roulette.game import TurnState
        rows=load_records()
        browser=BrowserGame(rows,seed=7)
        first=browser.spin()
        self.assertEqual(set(first['animation_choices']['season']),{r.season for r in rows})
        current=next(r for r in rows if r.season=='2015-16' and r.team=='GSW' and r.player_id==201939)
        browser.game.turn=TurnState(current)
        result=browser.spin(['season','team'])
        expected={r.player for r in rows if r.season=='2015-16' and r.team=='GSW' and r.player_id!=201939}
        self.assertEqual(set(result['animation_choices']['player']),expected)
        self.assertEqual(result['animation_choices']['season'],['2015-16'])
        self.assertEqual(result['animation_choices']['team'],['GSW'])
        self.assertNotIn('Nikola Jokić',result['animation_choices']['player'])

    def test_animation_excludes_drafted_players_and_uses_jackpot_dataset(self):
        from nba_roulette.data import load_records,load_goat_pools
        rows=load_records();goats=load_goat_pools()
        browser=BrowserGame(rows,seed=1,goat_pools=goats,dev_jackpots=True)
        browser.spin(force_pool='award')
        scored=browser.game.turn.current.player_id
        browser.score(Category.POINTS.value)
        result=browser.spin(force_pool='award')
        current=browser.game.turn.current
        eligible=[r for r in goats['award'] if r.player_id!=scored]
        self.assertEqual(set(result['animation_choices']['season']),{r.season for r in eligible})
        self.assertEqual(set(result['animation_choices']['player']),{r.player for r in eligible if r.season==current.season and r.team==current.team})

    def test_reroll_preview_matches_legal_outcomes_without_consuming_randomness(self):
        from nba_roulette.models import Lock
        browser = BrowserGame(pool(), seed=7)
        browser.spin()
        rng = browser.game.roulette.rng.getstate()
        current = browser.game.turn.current
        expected = browser.game.roulette.valid_outcomes(current, (Lock.TEAM, Lock.PLAYER))
        preview = browser.state()["reroll_preview"]
        self.assertEqual([r["season"] for r in preview], sorted(r.season for r in expected))
        self.assertEqual(browser.game.roulette.rng.getstate(), rng)
        browser.game.scorecard[Category.POINTS] = 10
        self.assertTrue(all(c["id"] != "points" for r in browser._reroll_preview() for c in r["categories"]))

    def test_preview_excludes_current_year_when_alternative_exists_and_reports_fallback(self):
        from nba_roulette.game import TurnState
        rows = (make_record("2000-01", "BOS", 1), make_record("2001-02", "BOS", 1), make_record("2000-01", "LAL", 2))
        browser = BrowserGame(rows, seed=1)
        browser.game.turn = TurnState(rows[0])
        self.assertEqual([r["season"] for r in browser._reroll_preview()], ["2001-02"])
        single = BrowserGame((rows[0], rows[2]), seed=1)
        single.game.turn = TurnState(rows[0])
        self.assertTrue(single._reroll_preview()[0]["same_season"])
        single.game.turn.spins_used = 3
        self.assertEqual(single._reroll_preview(), [])


if __name__ == "__main__":
    unittest.main()
