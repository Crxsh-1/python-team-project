# EduPulse – Academic Assignment Priority Organizer

EduPulse is a Python desktop tool that helps students decide **what to work on first**. You enter each assignment with its deadline and weightage, and EduPulse ranks everything with a priority score, so the most urgent and most valuable work is always at the top of the list.

**Course:** Computational Thinking and Programming (2026CSAE100), Bennett University – Experiential Learning collaborative project
**Team:** 5 members (see [Team](#team))

---

## Table of contents

- [The problem](#the-problem)
- [How it works](#how-it-works)
- [Features](#features)
- [Getting started](#getting-started)
- [Using the program](#using-the-program)
- [Sample output](#sample-output)
- [Project structure](#project-structure)
- [Python concepts used](#python-concepts-used)
- [Testing](#testing)
- [Experiential Learning Activities 3–7](#experiential-learning-activities-37)
- [Team](#team)
- [Limitations and future improvements](#limitations-and-future-improvements)

## The problem

Students handle assignments from several courses at once, each with a different deadline and a different share of the final grade. Without a clear method, deciding what to do first is done by feeling, which leads to missed deadlines and time spent on low-value work. EduPulse turns that decision into a simple, transparent calculation.

## How it works

Every task gets a priority score:

```
priority score = weight (%) / (days left + 0.1)
```

- A heavier task scores higher, and a closer deadline scores higher.
- The `+ 0.1` keeps the score finite for a task that is due today.
- Overdue tasks are treated as due today, so they stay at the top and are flagged `OVERDUE`.
- If two tasks have the same score, the earlier deadline is shown first.
- Tasks are stored with their **due date**, not "days remaining". Days left are recalculated every time the program runs, so the ranking never goes out of date.

## Features

- Add an assignment: course, description, days until the deadline, weightage (1–100)
- Input validation with clear error messages; pressing Cancel backs out quietly
- Tasks are saved to a text file and reloaded on every run
- Ranked table in a scrollable, aligned window showing due date, days left, weight and score
- Damaged lines in the data file are skipped and reported instead of crashing the program
- Logic is separated from the interface, so it can be tested without opening a window

## Getting started

**Requirements:** Python 3.8 or newer. The program uses only the standard library (`tkinter`, `os`, `datetime`), so there is nothing to install.

```bash
git clone https://github.com/Crxsh-1/python-team-project.git
cd python-team-project
python main.py
```

On some systems the command is `python3 main.py`.

**Troubleshooting**

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'tkinter'` (Linux) | `sudo apt install python3-tk` |
| `ModuleNotFoundError: No module named 'tkinter'` (Windows / macOS) | Reinstall Python from python.org and keep the "tcl/tk" option ticked |
| Dialog windows do not appear | Check the taskbar; a dialog may be behind the editor window |

## Using the program

The program is controlled through dialog boxes (no console input needed).

1. **Main menu:** type `1` to add an assignment, `2` to view the ranking, or `3` to exit.
2. **Add New Assignment:** enter the course, a description, the days remaining until the deadline (0–3650) and the weightage (1–100). The task is saved straight away.
3. **View Priority Task Ranking:** opens a window with all tasks, highest priority first.

Tasks are stored in `assignments.txt`, which is created next to `main.py` the first time you add a task. It is listed in `.gitignore`, so your personal data is never committed.

## Sample output

```
#   | Course     | Description              | Due Date   | Days Left | Weight  | Priority Score
-----------------------------------------------------------------------------------------------
1   | CHEM       | Quiz revision            | 2026-11-21 | 0         | 5%      |          50.00
2   | MATH       | Assignment 4             | 2026-11-23 | 2         | 15%     |           7.14
3   | PHY        | Lab record               | 2026-11-26 | 5         | 20%     |           3.92
4   | ENG        | Essay draft              | 2026-12-05 | 14        | 25%     |           1.77
5   | CTP        | Final project report     | 2026-11-30 | 9         | 10%     |           1.10
```

More examples, including error cases: [docs/SAMPLE_IO.md](docs/SAMPLE_IO.md). Algorithm and flowchart: [docs/ALGORITHM.md](docs/ALGORITHM.md).

## Project structure

```
python-team-project/
├── main.py                      # Entry point: menu and dialog windows (interface layer)
├── task_logic.py                # Validation, storage, priority algorithm, report formatting
├── requirements.txt             # No third-party packages needed (matplotlib optional)
├── analysis/
│   └── data_interpretation.py   # Tables and charts used in Activity 7
├── tests/
│   ├── test_task_logic.py       # Unit tests for the logic
│   ├── test_ui_flow.py          # Dialog-flow tests (dialogs replaced by mocks)
│   └── test_analysis.py         # Checks the analysis script
├── docs/
│   ├── ALGORITHM.md             # Algorithm, score table and flowchart
│   ├── SAMPLE_IO.md             # Sample inputs and outputs
│   ├── EL_ACTIVITIES.md         # Experiential Learning Activities 3–7
│   └── images/                  # Charts used in the documentation
└── README.md
```

## Python concepts used

| Concept | Where it is used |
|---|---|
| Variables and data types (`int`, `float`, `str`, `date`) | `calculate_priority_score`, `days_until`, task fields |
| Conditional statements | menu in `run_menu`, validation in `add_task_ui`, `validate_days`, `validate_weight` |
| Loops | `while True` menu loop; `for` loops in `load_tasks`, `rank_tasks`, `format_report` |
| Lists, tuples, dictionaries | each task is a dictionary; tasks are a list; sort key is a tuple |
| Functions (docstrings, default arguments, return values) | 14 functions across `main.py` and `task_logic.py` |
| Sorting with `lambda` | `rank_tasks` |
| File handling (`open`, `with`, append / read) | `save_task`, `load_tasks` |
| Exception handling (`try` / `except`) | `load_tasks` (skips damaged lines), `add_task_ui` and `view_tasks_ui` (file errors) |
| String handling and f-strings | `clean_text`, `format_report` |
| Modules and libraries | `tkinter`, `os`, `datetime`; `statistics` and `matplotlib` in the analysis script; `unittest` for tests |

## Testing

```bash
python -m unittest discover -s tests -v
```

24 automated tests cover the score formula, input validation, saving and loading, damaged data, ranking order, report layout, the dialog flow and the analysis script.

To regenerate the analysis tables and charts (`matplotlib` is needed for the charts only):

```bash
python analysis/data_interpretation.py
```

## Experiential Learning Activities 3–7

The five activities were carried out on this project. The full write-up, with diagrams and tables, is in [docs/EL_ACTIVITIES.md](docs/EL_ACTIVITIES.md).

| Activity | What was done in EduPulse |
|---|---|
| 3 – Problem Decomposition | Problem split into 7 sub-problems, each mapped to a function |
| 4 – Card Sorting | Information sorted into groups; three ranking algorithms compared; design choices justified |
| 5 – Decision Tree Design | Decision trees and flowcharts for the menu, input flow and file reading |
| 6 – Object Modelling | Objects, attributes, behaviours and relationships |
| 7 – Data Interpretation | Summary tables, charts and key insights from the program's output |

## Team

| Member | Contribution |
|---|---|
| Bharat Jain : Led overall project coordination, delegated responsibilities, monitored development progress, coordinated the integration of individual components, and reviewed the final project deliverables to ensure consistency and completeness.

| Aniket Kumar : Supported the project’s version-control and collaboration workflow using Git and GitHub, including repository-related tasks and managing code updates during development

| Biswarup Sarma : Prepared and formatted the final project report in DOCX format, organized the project documentation, structured the sections, and ensured consistency in the presentation of technical content and project activities.

| Shubham Brahma : Contributed to the implementation of core application logic, including input validation, task management, priority-score calculation, assignment ranking, and data persistence.

| Abhiraj Kumar Singh : Participated in general project discussions and provided coordination and support during the project process.

## Limitations and future improvements

- No option yet to mark a task as completed, or to edit or delete a task
- The urgency term can outweigh importance: a 1% task due today (score 10.0) ranks above a 100% task due in 10 days (score 9.9). Capping the urgency term would fix this
- No reminders for tasks due soon
- Data is kept in one local text file, so it is not shared across devices
