"""
task_logic.py - core (non-GUI) logic for the EduPulse Assignment Organizer.

Everything here is plain Python (functions, lists, dictionaries, file handling,
exception handling, string formatting, lambda sorting) with no tkinter imports,
so it can be unit-tested without opening any window.

Storage format (assignments.txt), one task per line:
    course|description|due_date(YYYY-MM-DD)|weight
The due date is stored (not "days remaining") so the number of days left stays
correct every time the program is opened.
"""

import os
from datetime import date, datetime, timedelta

# The data file lives next to the program, whatever folder it is launched from.
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assignments.txt")

FIELD_SEPARATOR = "|"
DATE_FORMAT = "%Y-%m-%d"
MIN_WEIGHT = 1
MAX_WEIGHT = 100
MAX_DAYS = 3650  # about 10 years; also keeps the due date inside Python's date range
URGENCY_OFFSET = 0.1  # keeps the score finite for a task that is due today


def clean_text(text):
    """Make free text safe to store on a single line of the data file.

    The field separator is replaced and all whitespace (including newlines)
    is collapsed, so one task can never break the file format.
    """
    text = text.replace(FIELD_SEPARATOR, "/")
    return " ".join(text.split())


def validate_days(days):
    """Return an error message if days remaining is invalid, else None."""
    if days < 0:
        return "Days remaining cannot be negative."
    if days > MAX_DAYS:
        return f"Days remaining cannot be more than {MAX_DAYS}."
    return None


def validate_weight(weight):
    """Return an error message if the weightage is invalid, else None."""
    if not (MIN_WEIGHT <= weight <= MAX_WEIGHT):
        return f"Weightage must be between {MIN_WEIGHT} and {MAX_WEIGHT}."
    return None


def calculate_priority_score(days, weight):
    """Priority rule: weight / (days left + 0.1), rounded to 2 decimals.

    A heavier and/or closer task gets a higher score. Overdue tasks
    (negative days) are treated as due today, so they stay at the top.
    """
    days = max(days, 0)
    return round(weight / (days + URGENCY_OFFSET), 2)


def days_until(due, today=None):
    """Whole days from today until the due date (negative if overdue)."""
    today = today or date.today()
    return (due - today).days


def save_task(course, desc, days, weight, path=None, today=None):
    """Append one task to the data file, storing its due date."""
    path = path or DATA_FILE
    today = today or date.today()
    due = today + timedelta(days=days)
    fields = [clean_text(course), clean_text(desc), due.strftime(DATE_FORMAT), str(weight)]
    with open(path, "a", encoding="utf-8") as file:
        file.write(FIELD_SEPARATOR.join(fields) + "\n")


def load_tasks(path=None, today=None):
    """Read all tasks from the data file.

    Returns (tasks, skipped) where `tasks` is a list of dictionaries and
    `skipped` counts lines that could not be read (wrong field count, bad
    date or number) instead of letting one bad line crash the program.
    """
    path = path or DATA_FILE
    today = today or date.today()
    tasks = []
    skipped = 0
    if not os.path.exists(path):
        return tasks, skipped

    with open(path, "r", encoding="utf-8", errors="replace") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            parts = line.split(FIELD_SEPARATOR)
            try:
                if len(parts) != 4:
                    raise ValueError("wrong number of fields")
                due = datetime.strptime(parts[2], DATE_FORMAT).date()
                weight = float(parts[3])
                if validate_weight(weight):  # also rejects nan, inf, 0 and negatives
                    raise ValueError("weight out of range")
            except ValueError:
                skipped += 1
                continue
            tasks.append({
                "course": parts[0],
                "desc": parts[1],
                "due": due,
                "days": days_until(due, today),
                "weight": weight,
            })
    return tasks, skipped


def rank_tasks(tasks):
    """Add a score to every task and sort them, highest priority first."""
    for task in tasks:
        task["score"] = calculate_priority_score(task["days"], task["weight"])
    # Ties are broken by the sooner deadline so the order is predictable.
    tasks.sort(key=lambda t: (-t["score"], t["days"]))
    return tasks


def _fit(text, width):
    """Shorten text with '..' so it never breaks the table column width."""
    return text if len(text) <= width else text[:width - 2] + ".."


def format_report(tasks, skipped=0):
    """Build the ranked task table as plain text (for a monospace display)."""
    header = (f"{'#':<3} | {'Course':<10} | {'Description':<24} | {'Due Date':<10} | "
              f"{'Days Left':<9} | {'Weight':<7} | {'Priority Score':>14}")
    lines = [header, "-" * len(header)]
    for rank, t in enumerate(tasks, start=1):
        days_left = "OVERDUE" if t["days"] < 0 else str(t["days"])
        weight = f"{t['weight']:g}%"
        lines.append(
            f"{rank:<3} | {_fit(t['course'], 10):<10} | {_fit(t['desc'], 24):<24} | "
            f"{t['due'].strftime(DATE_FORMAT):<10} | {days_left:<9} | {weight:<7} | "
            f"{t['score']:>14.2f}"
        )
    if skipped:
        lines.append("")
        lines.append(f"Note: {skipped} unreadable line(s) in the data file were skipped.")
    return "\n".join(lines)
