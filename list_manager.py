import os
import json

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
        tasks.append({"task": task, "done": False})
        print("Task added.")
    else:
        print("Empty task not added.")

def view_tasks(tasks):
    if not tasks:
        print("No tasks found.")
        return
    for i, t in enumerate(tasks):
        status = "✔️" if t["done"] else "❌"
        print(f"{i+1}. [{status}] {t['task']}")

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

def filter_tasks(tasks):
    print("\nFilter Options:")
    print("1. Show only completed tasks")
    print("2. Show only incomplete tasks")
    print("3. Search by keyword")
    print("4. Back to main menu")
    choice = input("Choose a filter option (1-4): ").strip()

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
        return
    else:
        print("Invalid choice.")

def main():
    tasks = load_tasks()
    while True:
        print("\nTo-Do List Menu")
        print("1. View tasks")
        print("2. Add task")
        print("3. Mark task as done")
        print("4. Remove task")
        print("5. Filter tasks")
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
            filter_tasks(tasks)
        elif choice == "6":
            save_tasks(tasks)
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()