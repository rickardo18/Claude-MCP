import os
import json
import datetime

TODO_FILE = "todo_list.json"

def load_tasks():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TODO_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def add_task(tasks):
    task = input("Enter the task: ").strip()
    if task:
        due_date = input("Enter due date (YYYY-MM-DD) or leave blank: ").strip()
        if due_date:
            try:
                datetime.datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format. Task not added.")
                return
        else:
            due_date = None
        priority = input("Enter priority (High/Medium/Low, default Medium): ").strip().capitalize()
        if priority not in ("High", "Medium", "Low"):
            priority = "Medium"
        tasks.append({"task": task, "done": False, "due_date": due_date, "priority": priority})
        print("Task added.")
    else:
        print("Empty task not added.")

def view_tasks(tasks):
    if not tasks:
        print("No tasks found.")
        return
    today = datetime.date.today()
    for i, t in enumerate(tasks):
        status = "✔️" if t["done"] else "❌"
        due = t.get("due_date")
        overdue = False
        due_str = ""
        if due:
            try:
                due_date = datetime.datetime.strptime(due, "%Y-%m-%d").date()
                if not t["done"] and due_date < today:
                    overdue = True
                due_str = f" (Due: {due}{' - OVERDUE' if overdue else ''})"
            except Exception:
                due_str = f" (Due: {due} - INVALID DATE)"
        priority = t.get("priority", "Medium")
        print(f"{i+1}. [{status}] {t['task']} [Priority: {priority}]{due_str}")

def mark_task_done(tasks):
    view_tasks(tasks)
    try:
        index = int(input("Enter task number to mark as done: ")) - 1
        if 0 <= index < len(tasks):
            tasks[index]["done"] = True
            print("Task marked as done.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

def remove_task(tasks):
    view_tasks(tasks)
    try:
        index = int(input("Enter task number to remove: ")) - 1
        if 0 <= index < len(tasks):
            removed = tasks.pop(index)
            print(f"Removed task: {removed['task']}")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

def show_reminders(tasks):
    today = datetime.date.today()
    reminders = []
    for t in tasks:
        if t.get("done"):
            continue
        due = t.get("due_date")
        if due:
            try:
                due_date = datetime.datetime.strptime(due, "%Y-%m-%d").date()
                if due_date < today:
                    reminders.append(f"OVERDUE: {t['task']} (was due {due})")
                elif due_date == today:
                    reminders.append(f"DUE TODAY: {t['task']}")
            except Exception:
                continue
    if reminders:
        print("\nReminders:")
        for r in reminders:
            print("-", r)

def edit_task(tasks):
    view_tasks(tasks)
    try:
        index = int(input("Enter task number to edit: ")) - 1
        if 0 <= index < len(tasks):
            task = tasks[index]
            print(f"Editing task: {task['task']}")
            new_desc = input(f"New description (press Enter to keep '{task['task']}'): ").strip()
            new_due = input(f"New due date (YYYY-MM-DD, press Enter to keep '{task.get('due_date') or 'None'}'): ").strip()
            new_priority = input(f"New priority (High/Medium/Low, press Enter to keep '{task.get('priority', 'Medium')}'): ").strip().capitalize()
            if new_desc:
                task['task'] = new_desc
            if new_due:
                try:
                    datetime.datetime.strptime(new_due, "%Y-%m-%d")
                    task['due_date'] = new_due
                except ValueError:
                    print("Invalid date format. Due date not updated.")
            elif new_due == '':
                pass  # keep existing due date
            if new_priority in ("High", "Medium", "Low"):
                task['priority'] = new_priority
            elif new_priority == '':
                pass  # keep existing priority
            else:
                print("Invalid priority. Priority not updated.")
            print("Task updated.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

def main():
    tasks = load_tasks()
    show_reminders(tasks)
    while True:
        print("\nTo-Do List Menu")
        print("1. View tasks")
        print("2. Add task")
        print("3. Mark task as done")
        print("4. Remove task")
        print("5. Edit task")
        print("6. Exit")
        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            view_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            mark_task_done(tasks)
        elif choice == "4":
            remove_task(tasks)
        elif choice == "5":
            edit_task(tasks)
        elif choice == "6":
            save_tasks(tasks)
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()