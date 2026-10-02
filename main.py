import os
import tkinter as tk
from tkinter import messagebox, simpledialog

# Configuration files
DATA_FILE = "assignments.txt"

def load_tasks():
    """Reads tasks from text file storage."""
    tasks = []
    if not os.path.exists(DATA_FILE):
        return tasks
    with open(DATA_FILE, "r") as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split("|")
                if len(parts) == 4:
                    tasks.append({
                        "course": parts[0],
                        "desc": parts[1],
                        "days": int(parts[2]),
                        "weight": float(parts[3])
                    })
    return tasks

def save_task(course, desc, days, weight):
    """Appends task parameters to persistent text log."""
    with open(DATA_FILE, "a") as file:
        file.write(f"{course}|{desc}|{days}|{weight}\n")

def calculate_priority_score(days, weight):
    """Computational Feature: Algorithmic task prioritizing rule."""
    return round((weight) / (days + 0.1), 2)

def add_task_ui(root):
    """Opens dialogue windows to safely take input credentials."""
    course = simpledialog.askstring("Input", "Enter Course Code/Name (e.g., CTP):")
    if not course: return
    
    desc = simpledialog.askstring("Input", "Enter Assignment Description:")
    if not desc: return
    
    try:
        days = simpledialog.askinteger("Input", "Enter days remaining until deadline:")
        if days is None or days < 0:
            messagebox.showerror("Error", "Invalid: Days remaining cannot be negative.")
            return
            
        weight = simpledialog.askfloat("Input", "Enter task weightage percentage (1-100):")
        if weight is None or weight <= 0 or weight > 100:
            messagebox.showerror("Error", "Invalid: Weightage must be between 1 and 100.")
            return
    except ValueError:
        messagebox.showerror("Error", "System Error: Invalid numeric formatting.")
        return

    save_task(course.strip(), desc.strip(), days, weight)
    messagebox.showinfo("Success", "Task recorded successfully!")

def view_tasks_ui():
    """Displays sorted tasks in a structured popup dialog box."""
    tasks = load_tasks()
    if not tasks:
        messagebox.showinfo("EduPulse Status", "No active tasks found. Your schedule is clear!")
        return

    # Calculate operational priority metrics dynamically
    for task in tasks:
        task["score"] = calculate_priority_score(task["days"], task["weight"])

    # Sorting priority via descending lambda configurations
    tasks.sort(key=lambda x: x["score"], reverse=True)

    # String Formatting for clean matrix look inside popup box
    report_string = f"{'Course':<10} | {'Description':<20} | {'Days Left':<10} | {'Weight':<8} | {'Priority Score'}\n"
    report_string += "-" * 70 + "\n"
    
    for t in tasks:
        report_string += f"{t['course']:<10} | {t['desc']:<20} | {t['days']:<10} | {t['weight']:<8}% | {t['score']}\n"

    messagebox.showinfo("Current Academic Tasks (Ranked)", report_string)

def run_menu():
    """Builds interactive navigation loops that won't freeze VS Code."""
    root = tk.Tk()
    root.withdraw() # Keep background layout clean
    
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
        
        if choice == "1":
            add_task_ui(root)
        elif choice == "2":
            view_tasks_ui()
        elif choice == "3" or choice is None:
            messagebox.showinfo("Exit", "Shutting down EduPulse tracking engine. Goodbye!")
            break
        else:
            messagebox.showerror("Error", "Invalid selection. Please choose 1, 2, or 3.")
            
    root.destroy()

if __name__ == "__main__":
    run_menu()