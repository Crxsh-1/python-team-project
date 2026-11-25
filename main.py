"""
EduPulse - Academic Assignment Priority Organizer (entry point / GUI layer).

Run with:  python main.py

This file only handles the dialog windows. The data handling and the priority
algorithm live in task_logic.py so they can be tested without a GUI.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog

import task_logic as logic


def show_report(root, report_text):
    """Show the ranked table in a scrollable, monospace window.

    A monospace font keeps the table columns aligned (a message box uses a
    proportional font, which breaks the alignment).
    """
    lines = report_text.splitlines()
    window = tk.Toplevel(root)
    window.title("Current Academic Tasks (Ranked)")

    text_box = tk.Text(window, font=("Courier", 10), wrap="none",
                       width=min(max(len(line) for line in lines), 110),
                       height=min(len(lines), 25))
    y_scroll = tk.Scrollbar(window, orient="vertical", command=text_box.yview)
    x_scroll = tk.Scrollbar(window, orient="horizontal", command=text_box.xview)
    text_box.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    text_box.insert("1.0", report_text)
    text_box.configure(state="disabled")  # read-only

    text_box.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")
    tk.Button(window, text="Close", command=window.destroy).grid(row=2, column=0, pady=6)
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight=1)

    window.lift()
    window.focus_force()
    root.wait_window(window)  # pause the menu loop until the window is closed


def add_task_ui(root):
    """Ask for a new assignment's details, validate them and save the task."""
    course = simpledialog.askstring("Input", "Enter Course Code/Name (e.g., CTP):")
    if not course or not course.strip():
        return  # cancelled or left blank

    desc = simpledialog.askstring("Input", "Enter Assignment Description:")
    if not desc or not desc.strip():
        return

    days = simpledialog.askinteger("Input", "Enter days remaining until deadline:")
    if days is None:
        return  # user pressed Cancel
    error = logic.validate_days(days)
    if error:
        messagebox.showerror("Error", "Invalid: " + error)
        return

    weight = simpledialog.askfloat(
        "Input", f"Enter task weightage percentage ({logic.MIN_WEIGHT}-{logic.MAX_WEIGHT}):")
    if weight is None:
        return
    error = logic.validate_weight(weight)
    if error:
        messagebox.showerror("Error", "Invalid: " + error)
        return

    try:
        logic.save_task(course, desc, days, weight)
    except OSError as problem:
        messagebox.showerror("Error", f"Could not save the task: {problem}")
        return
    messagebox.showinfo("Success", "Task recorded successfully!")


def view_tasks_ui(root):
    """Load all tasks, rank them by priority score and display the ranking."""
    try:
        tasks, skipped = logic.load_tasks()
    except OSError as problem:
        messagebox.showerror("Error", f"Could not read the task file: {problem}")
        return

    if not tasks:
        message = "No active tasks found. Your schedule is clear!"
        if skipped:
            message += f"\n({skipped} unreadable line(s) in the data file were skipped.)"
        messagebox.showinfo("EduPulse Status", message)
        return

    logic.rank_tasks(tasks)
    show_report(root, logic.format_report(tasks, skipped))


def run_menu():
    """Main menu loop built from dialog boxes (no console input needed)."""
    root = tk.Tk()
    root.withdraw()  # hide the empty main window; only dialogs are shown

    while True:
        choice = simpledialog.askstring(
            "EduPulse Organizer",
            "============================\n"
            "    EDUPULSE MAIN MENU      \n"
            "============================\n"
            "1. Add New Assignment\n"
            "2. View Priority Task Ranking\n"
            "3. Exit System\n\n"
            "Select an option (1-3):"
        )
        if choice is not None:
            choice = choice.strip()

        if choice == "1":
            add_task_ui(root)
        elif choice == "2":
            view_tasks_ui(root)
        elif choice == "3" or choice is None:
            messagebox.showinfo("Exit", "Shutting down EduPulse tracking engine. Goodbye!")
            break
        else:
            messagebox.showerror("Error", "Invalid selection. Please choose 1, 2, or 3.")

    root.destroy()


if __name__ == "__main__":
    run_menu()
