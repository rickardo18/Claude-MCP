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
        priority = input("Enter priority (High/Medium/Low): ").strip().capitalize()
        if priority not in ["High", "Medium", "Low"]:
            priority = "Medium"
        due_date = input("Enter due date (YYYY-MM-DD) or leave blank: ").strip()
        if due_date == "":
            due_date = None
        recurrence = input("Enter recurrence (None/Daily/Weekly/Monthly): ").strip().capitalize()
        if recurrence not in ["None", "Daily", "Weekly", "Monthly"]:
            recurrence = "None"
        tasks.append({"task": task, "done": False, "priority": priority, "due_date": due_date, "recurrence": recurrence})
        print("Task added.")
    else:
        print("Empty task not added.")

def view_tasks(tasks):
    if not tasks:
        print("No tasks found.")
        return
    for i, t in enumerate(tasks):
        status = "✔️" if t["done"] else "❌"
        priority = t.get("priority", "Medium")
        due_date = t.get("due_date")
        due_str = f" | Due: {due_date}" if due_date else ""
        recurrence = t.get("recurrence", "None")
        rec_str = f" | Recurs: {recurrence}" if recurrence and recurrence != "None" else ""
        print(f"{i+1}. [{status}] {t['task']} (Priority: {priority}{due_str}{rec_str})")

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
            due_date = task.get("due_date")
            if recurrence != "None" and due_date:
                from datetime import datetime, timedelta
                try:
                    dt = datetime.strptime(due_date, "%Y-%m-%d")
                    if recurrence == "Daily":
                        next_due = dt + timedelta(days=1)
                    elif recurrence == "Weekly":
                        next_due = dt + timedelta(weeks=1)
                    elif recurrence == "Monthly":
                        # Add 1 month (approximate by adding 30 days)
                        next_due = dt + timedelta(days=30)
                    else:
                        next_due = None
                    if next_due:
                        tasks.append({
                            "task": task["task"],
                            "done": False,
                            "priority": task.get("priority", "Medium"),
                            "due_date": next_due.strftime("%Y-%m-%d"),
                            "recurrence": recurrence
                        })
                        print(f"Recurring task created for {next_due.strftime('%Y-%m-%d')}.")
                except Exception as e:
                    print("Could not create recurring task:", e)
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

def filter_tasks(tasks):
    print("\nFilter Options:")
    print("1. Show only completed tasks")
    print("2. Show only incomplete tasks")
    print("3. Search by keyword")
    print("4. Show tasks due today")
    print("5. Show overdue tasks")
    print("6. Back to main menu")
    choice = input("Choose a filter option (1-6): ").strip()

    today = datetime.date.today().isoformat()

    if choice == "1":
        filtered = [t for t in tasks if t["done"]]
        print("\nCompleted Tasks:")
        view_tasks(filtered)
    elif choice == "2":
        filtered = [t for t in tasks if not t["done"]]
        print("\nIncomplete Tasks:")
        view_tasks(filtered)
    elif choice == "3":
        keyword = input("Enter keyword to search: ").strip().lower()
        filtered = [t for t in tasks if keyword in t["task"].lower()]
        print(f"\nTasks containing '{keyword}':")
        view_tasks(filtered)
    elif choice == "4":
        filtered = [t for t in tasks if t.get("due_date") == today]
        print("\nTasks Due Today:")
        view_tasks(filtered)
    elif choice == "5":
        filtered = [t for t in tasks if t.get("due_date") and t["due_date"] < today and not t["done"]]
        print("\nOverdue Tasks:")
        view_tasks(filtered)
    elif choice == "6":
        return
    else:
        print("Invalid choice.")

def edit_task(tasks):
    view_tasks(tasks)
    try:
        index = int(input("Enter task number to edit: ")) - 1
        if 0 <= index < len(tasks):
            new_desc = input(f"Enter new description for task '{tasks[index]['task']}': ").strip()
            if new_desc:
                tasks[index]["task"] = new_desc
                print("Task updated.")
            else:
                print("Empty description. Task not updated.")
            new_priority = input(f"Enter new priority (High/Medium/Low) [current: {tasks[index].get('priority', 'Medium')}]: ").strip().capitalize()
            if new_priority in ["High", "Medium", "Low"]:
                tasks[index]["priority"] = new_priority
                print("Priority updated.")
            else:
                print("Priority unchanged.")
            new_due = input(f"Enter new due date (YYYY-MM-DD) [current: {tasks[index].get('due_date', 'None')}]: ").strip()
            if new_due:
                tasks[index]["due_date"] = new_due
                print("Due date updated.")
            else:
                print("Due date unchanged.")
            new_recur = input(f"Enter new recurrence (None/Daily/Weekly/Monthly) [current: {tasks[index].get('recurrence', 'None')}]: ").strip().capitalize()
            if new_recur in ["None", "Daily", "Weekly", "Monthly"]:
                tasks[index]["recurrence"] = new_recur
                print("Recurrence updated.")
            else:
                print("Recurrence unchanged.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

def main():
    tasks = load_tasks()
    while True:
        print("\nTo-Do List Menu")
        print("1. View tasks")
        print("2. Add task")
        print("3. Mark task as done")
        print("4. Remove task")
        print("5. Filter tasks")
        print("6. Edit task")
        print("7. Exit")
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
            filter_tasks(tasks)
        elif choice == "6":
            edit_task(tasks)
        elif choice == "7":
            save_tasks(tasks)
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()