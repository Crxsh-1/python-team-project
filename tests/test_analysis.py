"""Checks that the Activity 7 analysis script runs and gives the documented results."""

import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis"))

import data_interpretation as analysis  # noqa: E402


class AnalysisTests(unittest.TestCase):
    def test_rank_history_matches_documented_table(self):
        history = analysis.rank_over_time([0, 2, 4, 6, 8, 10, 12, 14])
        self.assertEqual(history["CHEM"], [1, 2, 2, 3, 3, 4, 4, 5])
        self.assertEqual(history["PHY"], [3, 3, 3, 1, 1, 1, 1, 2])

    def test_tables_print_without_error(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            analysis.summary_table()
            analysis.compare_approaches()
            analysis.sensitivity_grid()
            analysis.anomaly_check()
        text = buffer.getvalue()
        self.assertIn("Median score", text)
        self.assertIn("The small task ranks higher: True", text)


if __name__ == "__main__":
    unittest.main()
