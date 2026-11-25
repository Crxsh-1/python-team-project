"""Checks the dialog flow in main.py with the dialogs replaced by mocks.

If tkinter is not installed (e.g. a minimal Linux install) a stand-in module is
used, so the control flow can still be tested. Run:  python -m unittest discover -s tests -v
"""

import os
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

try:
    import tkinter  # noqa: F401
except ImportError:  # pragma: no cover - only on machines without tkinter
    fake = types.ModuleType("tkinter")
    fake.messagebox = mock.MagicMock()
    fake.simpledialog = mock.MagicMock()
    for name in ("Tk", "Toplevel", "Text", "Scrollbar", "Button"):
        setattr(fake, name, mock.MagicMock())
    sys.modules["tkinter"] = fake
    sys.modules["tkinter.messagebox"] = fake.messagebox
    sys.modules["tkinter.simpledialog"] = fake.simpledialog

import main  # noqa: E402
import task_logic as logic  # noqa: E402


class UiFlowTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        patcher = mock.patch.object(logic, "DATA_FILE", os.path.join(folder.name, "t.txt"))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.root = mock.MagicMock()

    def add(self, course="CTP", desc="Project", days=5, weight=20.0):
        with mock.patch.object(main.simpledialog, "askstring", side_effect=[course, desc]), \
             mock.patch.object(main.simpledialog, "askinteger", return_value=days), \
             mock.patch.object(main.simpledialog, "askfloat", return_value=weight), \
             mock.patch.object(main.messagebox, "showinfo") as info, \
             mock.patch.object(main.messagebox, "showerror") as err:
            main.add_task_ui(self.root)
        return info, err

    def test_valid_task_is_saved(self):
        info, err = self.add()
        info.assert_called_once()
        err.assert_not_called()
        self.assertEqual(len(logic.load_tasks()[0]), 1)

    def test_negative_days_rejected(self):
        info, err = self.add(days=-2)
        err.assert_called_once()
        self.assertEqual(logic.load_tasks()[0], [])

    def test_weight_out_of_range_rejected(self):
        info, err = self.add(weight=0.5)
        err.assert_called_once()
        self.assertEqual(logic.load_tasks()[0], [])

    def test_cancel_on_days_is_silent(self):
        info, err = self.add(days=None)
        err.assert_not_called()
        info.assert_not_called()
        self.assertEqual(logic.load_tasks()[0], [])

    def test_blank_course_cancels(self):
        info, err = self.add(course="   ")
        info.assert_not_called()
        self.assertEqual(logic.load_tasks()[0], [])

    def test_view_empty_shows_clear_message(self):
        with mock.patch.object(main.messagebox, "showinfo") as info:
            main.view_tasks_ui(self.root)
        self.assertIn("schedule is clear", info.call_args[0][1])

    def test_view_shows_ranked_report(self):
        self.add(course="LOW", desc="later", days=30, weight=5)
        self.add(course="TOP", desc="soon", days=1, weight=50)
        with mock.patch.object(main, "show_report") as show:
            main.view_tasks_ui(self.root)
        report = show.call_args[0][1]
        self.assertLess(report.index("TOP"), report.index("LOW"))

    def test_menu_flow(self):
        with mock.patch.object(main.tk, "Tk"), \
             mock.patch.object(main.simpledialog, "askstring", side_effect=[" 1 ", "9", "3"]), \
             mock.patch.object(main, "add_task_ui") as add_ui, \
             mock.patch.object(main.messagebox, "showerror") as err, \
             mock.patch.object(main.messagebox, "showinfo"):
            main.run_menu()
        add_ui.assert_called_once()
        err.assert_called_once()  # option "9" is invalid


if __name__ == "__main__":
    unittest.main()
