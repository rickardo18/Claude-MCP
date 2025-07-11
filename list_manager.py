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
        recurrence = input("Enter recurrence (None/Daily/Weekly/Monthly, default None): ").strip().capitalize()
        if recurrence not in ("None", "Daily", "Weekly", "Monthly"):
            recurrence = "None"
        tasks.append({"task": task, "done": False, "due_date": due_date, "priority": priority, "recurrence": recurrence})
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
        recurrence = t.get("recurrence", "None")
        rec_str = f" [Recurs: {recurrence}]" if recurrence and recurrence != "None" else ""
        print(f"{i+1}. [{status}] {t['task']} [Priority: {priority}]{due_str}{rec_str}")

def mark_task_done(tasks):
    view_tasks(tasks)
    try:
        index = int(input("Enter task number to mark as done: ")) - 1
        if 0 <= index < len(tasks):
            task = tasks[index]
            tasks[index]["done"] = True
            print("Task marked as done.")
            # Handle recurrence
            recurrence = task.get("recurrence", "None")
            due = task.get("due_date")
            if recurrence and recurrence != "None" and due:
                try:
                    due_date = datetime.datetime.strptime(due, "%Y-%m-%d").date()
                    if recurrence == "Daily":
                        next_due = due_date + datetime.timedelta(days=1)
                    elif recurrence == "Weekly":
                        next_due = due_date + datetime.timedelta(weeks=1)
                    elif recurrence == "Monthly":
                        # Add one month, simple version
                        month = due_date.month + 1 if due_date.month < 12 else 1
                        year = due_date.year if due_date.month < 12 else due_date.year + 1
                        day = min(due_date.day, 28)  # avoid invalid dates
                        next_due = datetime.date(year, month, day)
                    else:
                        next_due = None
                    if next_due:
                        new_task = task.copy()
                        new_task["done"] = False
                        new_task["due_date"] = next_due.strftime("%Y-%m-%d")
                        tasks.append(new_task)
                        print(f"Recurring task created for next {recurrence.lower()} (due {next_due})")
                except Exception:
                    pass
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
            new_recurrence = input(f"New recurrence (None/Daily/Weekly/Monthly, press Enter to keep '{task.get('recurrence', 'None')}'): ").strip().capitalize()
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
            if new_recurrence in ("None", "Daily", "Weekly", "Monthly"):
                task['recurrence'] = new_recurrence
            elif new_recurrence == '':
                pass  # keep existing recurrence
            else:
                print("Invalid recurrence. Recurrence not updated.")
            print("Task updated.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

def search_tasks(tasks):
    if not tasks:
        print("No tasks to search.")
        return
    print("\nSearch Tasks")
    print("1. By keyword")
    print("2. By due date (YYYY-MM-DD)")
    print("3. By priority (High/Medium/Low)")
    choice = input("Choose search type (1-3): ").strip()
    results = []
    if choice == "1":
        keyword = input("Enter keyword to search: ").strip().lower()
        results = [t for t in tasks if keyword in t["task"].lower()]
    elif choice == "2":
        date = input("Enter due date (YYYY-MM-DD): ").strip()
        results = [t for t in tasks if t.get("due_date") == date]
    elif choice == "3":
        priority = input("Enter priority (High/Medium/Low): ").strip().capitalize()
        if priority in ("High", "Medium", "Low"):
            results = [t for t in tasks if t.get("priority", "Medium") == priority]
        else:
            print("Invalid priority.")
            return
    else:
        print("Invalid choice.")
        return
    if results:
        print(f"\nFound {len(results)} matching task(s):")
        view_tasks(results)
    else:
        print("No matching tasks found.")

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
        print("7. Search tasks")
        choice = input("Choose an option (1-7): ").strip()

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
        elif choice == "7":
            search_tasks(tasks)
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()