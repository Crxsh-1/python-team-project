# Sample Input and Output

The output below was produced by running the project's own code (`task_logic.py`) with "today" set to 2026-11-21. Screenshots of the real dialog windows are in the project report.

## Sample input (entered through the "Add New Assignment" dialogs)

| Course | Description | Days remaining | Weightage |
|---|---|---|---|
| CTP | Final project report | 9 | 10 |
| MATH | Assignment 4 | 2 | 15 |
| PHY | Lab record | 5 | 20 |
| ENG | Essay draft | 14 | 25 |
| CHEM | Quiz revision | 0 | 5 |

## Data file created (`assignments.txt`)

```
CTP|Final project report|2026-11-30|10
MATH|Assignment 4|2026-11-23|15
PHY|Lab record|2026-11-26|20
ENG|Essay draft|2026-12-05|25
CHEM|Quiz revision|2026-11-21|5
```

## Output – "View Priority Task Ranking" on 2026-11-21

```
#   | Course     | Description              | Due Date   | Days Left | Weight  | Priority Score
-----------------------------------------------------------------------------------------------
1   | CHEM       | Quiz revision            | 2026-11-21 | 0         | 5%      |          50.00
2   | MATH       | Assignment 4             | 2026-11-23 | 2         | 15%     |           7.14
3   | PHY        | Lab record               | 2026-11-26 | 5         | 20%     |           3.92
4   | ENG        | Essay draft              | 2026-12-05 | 14        | 25%     |           1.77
5   | CTP        | Final project report     | 2026-11-30 | 9         | 10%     |           1.10
```

## Output – same tasks viewed three days later (2026-11-24)

Days left update automatically and overdue tasks rise to the top.

```
#   | Course     | Description              | Due Date   | Days Left | Weight  | Priority Score
-----------------------------------------------------------------------------------------------
1   | MATH       | Assignment 4             | 2026-11-23 | OVERDUE   | 15%     |         150.00
2   | CHEM       | Quiz revision            | 2026-11-21 | OVERDUE   | 5%      |          50.00
3   | PHY        | Lab record               | 2026-11-26 | 2         | 20%     |           9.52
4   | ENG        | Essay draft              | 2026-12-05 | 11        | 25%     |           2.25
5   | CTP        | Final project report     | 2026-11-30 | 6         | 10%     |           1.64
```

## Error cases

| Input | Result |
|---|---|
| Days remaining = -3 | Error: "Invalid: Days remaining cannot be negative." Nothing is saved. |
| Weightage = 0.5 or 150 | Error: "Invalid: Weightage must be between 1 and 100." Nothing is saved. |
| Cancel on any prompt | Returns to the menu quietly. |
| Menu choice = 7 | Error: "Invalid selection. Please choose 1, 2, or 3." |
| View with no tasks saved | "No active tasks found. Your schedule is clear!" |
