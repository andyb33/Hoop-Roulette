"""Zero-minute log rows are excluded only with scoped aggregate corroboration."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


class LegacyPlaceholderTests(unittest.TestCase):
    def test_exclusion_requires_matching_totals_and_independent_coverage(self):
        with patch.object(sys, 'path', [str(Path(__file__).resolve().parents[1] / 'scripts'), *sys.path]):
            from complete_historical_seasons import final_log_rows
        played = dict(Game_ID='one', MIN=20, PTS=4, REB=3, AST=2, STL=None, BLK=None)
        placeholder = dict(Game_ID='two', MIN=0, PTS=8, REB=None, AST=None, STL=None, BLK=None)
        proof = dict(method='OFFICIAL_TOTALS_CORROBORATED_PLACEHOLDER_EXCLUSION',
                     official_stint_game_log_rows=[played, placeholder],
                     excluded_zero_minute_rows=[placeholder],
                     bounded_matched_fields=['GP','MIN','PTS','REB','AST'],
                     official_row=dict(GP=1, MIN=20, PTS=4, REB=3, AST=2),
                     independent_reference_row=dict(G='1', MP='20'))
        self.assertEqual(final_log_rows(proof), [played])
        self.assertEqual(len(proof['official_stint_game_log_rows']), 2)
        for field in ('GP', 'MIN', 'PTS', 'REB', 'AST'):
            broken = copy.deepcopy(proof)
            broken['official_row'][field] += 1
            with self.assertRaises(AssertionError):
                final_log_rows(broken)
        broken = copy.deepcopy(proof)
        broken['independent_reference_row']['MP'] = '19'
        with self.assertRaises(AssertionError):
            final_log_rows(broken)
        broken = copy.deepcopy(proof)
        broken['bounded_matched_fields'].remove('AST')
        with self.assertRaises(AssertionError):
            final_log_rows(broken)
