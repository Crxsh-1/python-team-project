"""
data_interpretation.py - Experiential Learning Activity 7 (Data Interpretation).

Uses the project's own functions (task_logic.py) on a fixed sample dataset to
produce summary tables, a ranking-over-time table, an alternative-approach
comparison and a sensitivity grid. If matplotlib is installed it also saves two
charts into docs/images/.

Run from the project folder:  python analysis/data_interpretation.py
"""

import os
import statistics
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import task_logic as logic  # noqa: E402

TODAY = date(2026, 11, 21)  # fixed so the results are reproducible
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "images")

# (course, description, due date, weight %)
SAMPLE = [
    ("CTP",  "Final project report", date(2026, 11, 30), 10),
    ("MATH", "Assignment 4",         date(2026, 11, 23), 15),
    ("PHY",  "Lab record",           date(2026, 11, 26), 20),
    ("ENG",  "Essay draft",          date(2026, 12, 5),  25),
    ("CHEM", "Quiz revision",        date(2026, 11, 21), 5),
]


def build_tasks(today):
    """Build task dictionaries (same shape as logic.load_tasks) for a given day."""
    return [{"course": c, "desc": d, "due": due, "days": logic.days_until(due, today), "weight": w}
            for c, d, due, w in SAMPLE]


def print_table(title, header, rows):
    print(f"\n{title}")
    widths = [max(len(str(x)) for x in col) for col in zip(header, *rows)]
    print(" | ".join(str(h).ljust(w) for h, w in zip(header, widths)))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(" | ".join(str(x).ljust(w) for x, w in zip(row, widths)))


def summary_table():
    tasks = logic.rank_tasks(build_tasks(TODAY))
    scores = [t["score"] for t in tasks]
    days = [t["days"] for t in tasks]
    weights = [t["weight"] for t in tasks]
    rows = [
        ("Number of tasks", len(tasks)),
        ("Total weightage (%)", sum(weights)),
        ("Average days left", round(statistics.mean(days), 1)),
        ("Highest score", f"{max(scores)} ({tasks[0]['course']})"),
        ("Lowest score", f"{min(scores)} ({tasks[-1]['course']})"),
        ("Average score", round(statistics.mean(scores), 2)),
        ("Median score", round(statistics.median(scores), 2)),
        ("Tasks due within 3 days", sum(1 for d in days if d <= 3)),
    ]
    print_table(f"Table 1 - Summary of the sample dataset (today = {TODAY})", ("Measure", "Value"), rows)


def rank_over_time(offsets):
    """Return {course: [rank on each offset day]} for the sample dataset."""
    history = {c: [] for c, _, _, _ in SAMPLE}
    for offset in offsets:
        ranked = logic.rank_tasks(build_tasks(TODAY + timedelta(days=offset)))
        for position, task in enumerate(ranked, start=1):
            history[task["course"]].append(position)
    return history


def rank_table():
    offsets = list(range(0, 15, 2))
    history = rank_over_time(offsets)
    header = ["Course"] + [f"+{o}d" for o in offsets]
    rows = [[course] + ranks for course, ranks in history.items()]
    print_table("Table 2 - Rank of each task as days pass (1 = do first)", header, rows)
    return history


def compare_approaches():
    tasks = build_tasks(TODAY)
    by_deadline = [t["course"] for t in sorted(tasks, key=lambda t: t["days"])]
    by_weight = [t["course"] for t in sorted(tasks, key=lambda t: -t["weight"])]
    by_formula = [t["course"] for t in logic.rank_tasks(build_tasks(TODAY))]
    rows = [(i + 1, by_deadline[i], by_weight[i], by_formula[i]) for i in range(len(tasks))]
    print_table("Table 3 - Ranking under three alternative approaches",
                ("Rank", "Deadline only", "Weight only", "Weight / (days + 0.1)"), rows)


def sensitivity_grid():
    weights = [5, 10, 25, 50, 100]
    days = [0, 1, 3, 7, 14, 30]
    header = ["Weight \\ Days left"] + days
    rows = [[f"{w}%"] + [logic.calculate_priority_score(d, w) for d in days] for w in weights]
    print_table("Table 4 - Priority score for different weights and days left", header, rows)


def anomaly_check():
    light_today = logic.calculate_priority_score(0, 1)
    heavy_later = logic.calculate_priority_score(10, 100)
    print("\nPattern check - how strongly does urgency dominate?")
    print(f"  1% task due today          -> score {light_today}")
    print(f"  100% task due in 10 days   -> score {heavy_later}")
    print(f"  The small task ranks higher: {light_today > heavy_later}")


def save_charts(history):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib not installed - charts skipped)")
        return

    os.makedirs(IMAGE_DIR, exist_ok=True)
    colours = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]  # fixed order
    ink, muted, grid = "#0b0b0b", "#52514e", "#e1e0d9"

    def style(ax):
        ax.set_facecolor("#fcfcfb")
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#c3c2b7")
        ax.tick_params(colors=muted)
        ax.grid(axis="y", color=grid, linewidth=0.8)
        ax.set_axisbelow(True)

    # Chart 1 - rank over the next 14 days
    offsets = list(range(15))
    full = rank_over_time(offsets)
    fig, ax = plt.subplots(figsize=(8, 4.2), facecolor="#fcfcfb")
    style(ax)
    for colour, (course, ranks) in zip(colours, full.items()):
        ax.plot(offsets, ranks, color=colour, linewidth=2, marker="o", markersize=4, label=course)
        ax.annotate(course, (offsets[-1], ranks[-1]), xytext=(6, 0), textcoords="offset points",
                    va="center", color=ink, fontsize=9)
    ax.set_ylim(5.4, 0.6)
    ax.set_yticks(range(1, 6))
    ax.set_xlim(-0.3, 15.5)
    ax.set_xlabel("Days from 21 Nov 2026", color=muted)
    ax.set_ylabel("Rank (1 = do first)", color=muted)
    ax.set_title("Task ranking changes as deadlines approach", color=ink, loc="left")
    ax.legend(frameon=False, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.18), labelcolor=ink)
    fig.tight_layout()
    fig.savefig(os.path.join(IMAGE_DIR, "rank_over_time.png"), dpi=150)
    plt.close(fig)

    # Chart 2 - score against days left for four weights
    days = list(range(0, 31))
    fig, ax = plt.subplots(figsize=(8, 4.2), facecolor="#fcfcfb")
    style(ax)
    for colour, weight in zip(colours, [5, 10, 25, 50]):
        scores = [logic.calculate_priority_score(d, weight) for d in days]
        ax.plot(days, scores, color=colour, linewidth=2, label=f"{weight}% weight")
        ax.annotate(f"{weight}%", (days[-1], scores[-1]), xytext=(6, 0), textcoords="offset points",
                    va="center", color=ink, fontsize=9)
    ax.set_yscale("log")
    ax.set_xlim(-0.5, 32.5)
    ax.set_xlabel("Days left", color=muted)
    ax.set_ylabel("Priority score (log scale)", color=muted)
    ax.set_title("Score falls steeply in the last few days", color=ink, loc="left")
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.18), labelcolor=ink)
    fig.tight_layout()
    fig.savefig(os.path.join(IMAGE_DIR, "score_vs_days.png"), dpi=150)
    plt.close(fig)
    print(f"\nCharts saved to {os.path.normpath(IMAGE_DIR)}")


if __name__ == "__main__":
    summary_table()
    history = rank_table()
    compare_approaches()
    sensitivity_grid()
    anomaly_check()
    save_charts(history)
