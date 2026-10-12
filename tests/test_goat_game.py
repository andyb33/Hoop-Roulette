import random
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from nba_roulette.data import load_goat_pools
from nba_roulette.game import GameState
from nba_roulette.models import Lock
from nba_roulette.playtest import PlaytestBatchLogger
from nba_roulette.roulette import RouletteEngine
from nba_roulette.scoring import Category, category_available, category_score
from nba_roulette.web import BrowserGame
from .test_roulette import pool


class GoatGameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.goats = load_goat_pools()

    def game(self):
        return GameState(RouletteEngine(pool(), random.Random(7)), self.goats)

    def test_exact_jackpot_boundary_and_uniform_pool_draw(self):
        game = self.game()
        with patch.object(game.roulette.rng, 'randrange', return_value=0) as chance, \
             patch.object(game.roulette.rng, 'choice', side_effect=lambda values: values[0]) as choose:
            result = game.start_turn()
            self.assertEqual(result.pool, 'award')
            chance.assert_called_once_with(1296)
            self.assertEqual(choose.call_args_list[0].args[0], ('award', 'prehistoric'))
            self.assertEqual(choose.call_args_list[1].args[0], self.goats['award'])
        game.score(Category.POINTS)
        with patch.object(game.roulette.rng, 'randrange', return_value=1295):
            self.assertEqual(game.start_turn().pool, 'normal')

    def test_kept_reroll_never_checks_jackpot(self):
        game = self.game()
        with patch.object(game.roulette.rng, 'randrange', return_value=1295):
            first = game.start_turn()
        with patch.object(game.roulette.rng, 'randrange', return_value=0) as chance:
            result = game.reroll([Lock.SEASON])
            chance.assert_not_called()
            self.assertEqual(result.pool, 'normal')
            self.assertEqual(result.season, first.season)

    def test_jackpot_cannot_be_kept_and_rejection_is_atomic(self):
        game = self.game()
        first = game.start_turn('prehistoric')
        with self.assertRaisesRegex(ValueError, 'cannot be kept'):
            game.reroll([Lock.PLAYER])
        self.assertEqual(game.turn.spins_used, 1)
        self.assertEqual(game.turn.current, first)

    def test_consecutive_identical_jackpots_are_allowed(self):
        game = self.game()
        with patch.object(game.roulette.rng, 'randrange', return_value=0), \
             patch.object(game.roulette.rng, 'choice', side_effect=lambda values: values[0]):
            first = game.start_turn()
            self.assertEqual(game.reroll(), first)
            self.assertEqual(game.reroll(), first)
        with self.assertRaisesRegex(RuntimeError, 'No rerolls'):
            game.reroll()

    def test_reroll_jackpot_can_return_to_normal_pool(self):
        game = self.game()
        game.start_turn('prehistoric')
        with patch.object(game.roulette.rng, 'randrange', return_value=1295):
            self.assertEqual(game.reroll().pool, 'normal')
        self.assertEqual(game.turn.spins_used, 2)

    def test_na_is_visible_and_can_be_sacrificed(self):
        browser = BrowserGame(pool(), goat_pools=self.goats, dev_jackpots=True)
        state = browser.spin(force_pool='prehistoric')
        self.assertIsNone(state['player']['stats']['SPG'])
        steals = next(r for r in state['categories'] if r['id'] == 'steals')
        self.assertTrue(steals['unavailable'])
        self.assertEqual(steals['preview'], 0)
        self.assertFalse(state['keeps_allowed'])
        scored = browser.score('steals')
        self.assertEqual(next(r for r in scored['categories'] if r['id'] == 'steals')['score'], 0)

    def test_early_first_team_still_qualifies_for_third(self):
        wilt = self.goats['prehistoric'][0]
        self.assertTrue(category_available(wilt, Category.ALL_NBA_THIRD))
        self.assertEqual(category_score(wilt, Category.ALL_NBA_THIRD), 20)
        self.assertFalse(category_available(wilt, Category.ALL_DEFENSE_FIRST))

    def test_forcing_requires_development_mode(self):
        browser = BrowserGame(pool(), goat_pools=self.goats)
        with self.assertRaisesRegex(ValueError, 'development mode'):
            browser.spin(force_pool='award')
        self.assertIsNone(browser.game.turn)

    def test_development_games_do_not_pollute_playtest_logs(self):
        with tempfile.TemporaryDirectory() as directory:
            logger = PlaytestBatchLogger(Path(directory), 'test', 'Test')
            browser = BrowserGame(pool(), goat_pools=self.goats, dev_jackpots=True, logger=logger)
            for category in Category:
                browser.spin(force_pool='award')
                browser.score(category.value)
            self.assertEqual(logger.completed_count(), 0)
            self.assertIsNone(browser.state()['playtest'])
            self.assertEqual(browser.events[0]['result']['pool'], 'award')
            self.assertTrue(browser.events[0]['development_forced'])
