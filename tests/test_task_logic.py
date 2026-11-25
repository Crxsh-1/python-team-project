"""Unit tests for the EduPulse logic layer. Run:  python -m unittest discover -s tests -v"""

import os
import sys
import tempfile
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import task_logic as logic  # noqa: E402

TODAY = date(2026, 11, 21)


class PriorityScoreTests(unittest.TestCase):
    def test_formula(self):
        self.assertEqual(logic.calculate_priority_score(2, 30), round(30 / 2.1, 2))

    def test_due_today_is_finite_and_high(self):
        self.assertEqual(logic.calculate_priority_score(0, 10), 100.0)

    def test_overdue_treated_as_due_today(self):
        self.assertEqual(logic.calculate_priority_score(-5, 10), 100.0)

    def test_closer_and_heavier_rank_higher(self):
        self.assertGreater(logic.calculate_priority_score(1, 20), logic.calculate_priority_score(5, 20))
        self.assertGreater(logic.calculate_priority_score(3, 40), logic.calculate_priority_score(3, 10))


class ValidationTests(unittest.TestCase):
    def test_days(self):
        self.assertIsNone(logic.validate_days(0))
        self.assertIsNotNone(logic.validate_days(-1))
        self.assertIsNone(logic.validate_days(logic.MAX_DAYS))
        self.assertIsNotNone(logic.validate_days(logic.MAX_DAYS + 1))
        self.assertIsNotNone(logic.validate_days(10**12))  # would overflow the date calculation

    def test_weight_bounds(self):
        self.assertIsNone(logic.validate_weight(1))
        self.assertIsNone(logic.validate_weight(100))
        self.assertIsNotNone(logic.validate_weight(0.5))
        self.assertIsNotNone(logic.validate_weight(100.1))
        self.assertIsNotNone(logic.validate_weight(-3))


class StorageTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = os.path.join(folder.name, "tasks.txt")

    def test_missing_file_gives_empty_list(self):
        self.assertEqual(logic.load_tasks(self.path, TODAY), ([], 0))

    def test_round_trip(self):
        logic.save_task("CTP", "Final project", 9, 10.0, self.path, TODAY)
        tasks, skipped = logic.load_tasks(self.path, TODAY)
        self.assertEqual(skipped, 0)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["course"], "CTP")
        self.assertEqual(tasks[0]["days"], 9)
        self.assertEqual(tasks[0]["due"], date(2026, 11, 30))
        self.assertEqual(tasks[0]["weight"], 10.0)

    def test_separator_in_text_does_not_lose_the_task(self):
        logic.save_task("MA|TH", "Sheet 1 | part A\nand B", 3, 5, self.path, TODAY)
        tasks, skipped = logic.load_tasks(self.path, TODAY)
        self.assertEqual(skipped, 0)
        self.assertEqual(tasks[0]["course"], "MA/TH")
        self.assertEqual(tasks[0]["desc"], "Sheet 1 / part A and B")

    def test_days_left_updates_as_time_passes(self):
        logic.save_task("PHY", "Lab report", 5, 20, self.path, TODAY)
        later = date(2026, 11, 24)
        self.assertEqual(logic.load_tasks(self.path, later)[0][0]["days"], 2)
        overdue = date(2026, 11, 30)
        self.assertEqual(logic.load_tasks(self.path, overdue)[0][0]["days"], -4)

    def test_bad_lines_are_skipped_not_fatal(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("CTP|ok|2026-11-25|10\n")
            f.write("garbage line\n")
            f.write("CTP|bad date|not-a-date|10\n")
            f.write("CTP|bad weight|2026-11-25|abc\n")
            f.write("CTP|legacy|5|30.0\n")  # old "days remaining" format
            f.write("CTP|zero weight|2026-11-25|0\n")
            f.write("CTP|nan weight|2026-11-25|nan\n")
            f.write("\n")
        tasks, skipped = logic.load_tasks(self.path, TODAY)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(skipped, 6)


class RankingAndReportTests(unittest.TestCase):
    def make(self, course, desc, days, weight):
        return {"course": course, "desc": desc, "due": TODAY, "days": days, "weight": weight}

    def test_ranking_order(self):
        tasks = [self.make("A", "far light", 20, 5),
                 self.make("B", "near heavy", 1, 40),
                 self.make("C", "mid", 7, 25)]
        ranked = logic.rank_tasks(tasks)
        self.assertEqual([t["course"] for t in ranked], ["B", "C", "A"])

    def test_tie_broken_by_earlier_deadline(self):
        a = self.make("A", "x", 0, 0.1)    # due today
        b = self.make("B", "y", -3, 0.1)   # overdue -> same score as due today, earlier deadline
        ranked = logic.rank_tasks([a, b])
        self.assertEqual(ranked[0]["course"], "B")

    def test_report_layout(self):
        tasks = logic.rank_tasks([self.make("CTP", "An extremely long assignment description here", 2, 12.5),
                                  self.make("ENG", "Essay", -1, 30)])
        report = logic.format_report(tasks, skipped=2)
        lines = report.splitlines()
        self.assertIn("Priority Score", lines[0])
        self.assertIn("12.5%", report)
        self.assertIn("OVERDUE", report)
        self.assertIn("..", report)  # long description was shortened
        self.assertNotIn("An extremely long assignment description here", report)
        self.assertIn("2 unreadable", report)
        table_rows = [ln for ln in lines[2:4]]
        self.assertTrue(all(len(r) == len(lines[0]) for r in table_rows))  # columns line up


if __name__ == "__main__":
    unittest.main()
