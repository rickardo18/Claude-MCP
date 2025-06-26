import os
import json
import datetime
import threading
import time
try:
    from plyer import notification
except ImportError:
    notification = None
import smtplib
from email.mime.text import MIMEText

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
        reminder_time = input("Enter reminder time (HH:MM 24-hour) or leave blank: ").strip()
        if reminder_time:
            try:
                datetime.datetime.strptime(reminder_time, "%H:%M")
            except ValueError:
                print("Invalid time format. Reminder not set.")
                reminder_time = None
        else:
            reminder_time = None
        tasks.append({"task": task, "done": False, "priority": priority, "due_date": due_date, "recurrence": recurrence, "reminder_time": reminder_time})
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
        reminder_time = t.get("reminder_time")
        reminder_str = f" | Reminder: {reminder_time}" if reminder_time else ""
        print(f"{i+1}. [{status}] {t['task']} (Priority: {priority}{due_str}{rec_str}{reminder_str})")

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
            new_reminder = input(f"Enter new reminder time (HH:MM 24-hour) [current: {tasks[index].get('reminder_time', 'None')}]: ").strip()
            if new_reminder:
                try:
                    datetime.datetime.strptime(new_reminder, "%H:%M")
                    tasks[index]["reminder_time"] = new_reminder
                    print("Reminder time updated.")
                except ValueError:
                    print("Invalid time format. Reminder time unchanged.")
            else:
                print("Reminder time unchanged.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

def save_custom_views(custom_views):
    with open("custom_views.json", "w") as f:
        json.dump(custom_views, f, indent=2)

def load_custom_views():
    if os.path.exists("custom_views.json"):
        with open("custom_views.json", "r") as f:
            return json.load(f)
    return {}

# --- Sorting and Custom Views ---
def sort_tasks(tasks, criterion, reverse=False):
    if criterion == "priority":
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        return sorted(tasks, key=lambda t: priority_order.get(t.get("priority", "Medium"), 1), reverse=reverse)
    elif criterion == "due_date":
        return sorted(tasks, key=lambda t: t.get("due_date") or "9999-12-31", reverse=reverse)
    elif criterion == "status":
        return sorted(tasks, key=lambda t: t.get("done", False), reverse=reverse)
    else:
        return tasks

def manage_custom_views(custom_views):
    while True:
        print("\nCustom Views Menu")
        print("1. List custom views")
        print("2. Add new custom view")
        print("3. Delete custom view")
        print("4. Back to main menu")
        choice = input("Choose an option (1-4): ").strip()
        if choice == "1":
            if not custom_views:
                print("No custom views saved.")
            else:
                for name, conf in custom_views.items():
                    print(f"- {name}: sort by {conf['sort_by']}, reverse: {conf['reverse']}")
        elif choice == "2":
            name = input("Enter a name for the custom view: ").strip()
            if name in custom_views:
                print("A view with this name already exists.")
                continue
            print("Sort by: 1. priority 2. due_date 3. status")
            sort_by = input("Choose sort criterion (priority/due_date/status): ").strip()
            if sort_by not in ["priority", "due_date", "status"]:
                print("Invalid sort criterion.")
                continue
            reverse = input("Sort descending? (y/n): ").strip().lower() == "y"
            custom_views[name] = {"sort_by": sort_by, "reverse": reverse}
            save_custom_views(custom_views)
            print("Custom view saved.")
        elif choice == "3":
            name = input("Enter the name of the custom view to delete: ").strip()
            if name in custom_views:
                del custom_views[name]
                save_custom_views(custom_views)
                print("Custom view deleted.")
            else:
                print("No such custom view.")
        elif choice == "4":
            break
        else:
            print("Invalid choice.")

def view_tasks_with_sort(tasks, custom_views):
    print("\nView Options:")
    print("1. Normal view")
    print("2. Sort by priority")
    print("3. Sort by due date")
    print("4. Sort by status (done/incomplete)")
    print("5. Use custom view")
    choice = input("Choose a view option (1-5): ").strip()
    if choice == "1":
        view_tasks(tasks)
    elif choice == "2":
        sorted_tasks = sort_tasks(tasks, "priority")
        view_tasks(sorted_tasks)
    elif choice == "3":
        sorted_tasks = sort_tasks(tasks, "due_date")
        view_tasks(sorted_tasks)
    elif choice == "4":
        sorted_tasks = sort_tasks(tasks, "status")
        view_tasks(sorted_tasks)
    elif choice == "5":
        if not custom_views:
            print("No custom views available.")
            return
        print("Available custom views:")
        for i, name in enumerate(custom_views.keys()):
            print(f"{i+1}. {name}")
        try:
            idx = int(input("Choose a custom view by number: ")) - 1
            if 0 <= idx < len(custom_views):
                name = list(custom_views.keys())[idx]
                conf = custom_views[name]
                sorted_tasks = sort_tasks(tasks, conf["sort_by"], conf["reverse"])
                print(f"\nCustom View: {name}")
                view_tasks(sorted_tasks)
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
    else:
        print("Invalid choice.")

# --- Notification/Reminder Configuration ---
NOTIFY_CONFIG_FILE = "notify_config.json"
def load_notify_config():
    if os.path.exists(NOTIFY_CONFIG_FILE):
        with open(NOTIFY_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"method": "system", "email": "", "smtp": "", "password": ""}

def save_notify_config(config):
    with open(NOTIFY_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def configure_notifications():
    print("\nNotification Preferences:")
    print("1. System notification (default)")
    print("2. Email reminder")
    print("3. Both")
    method = input("Choose notification method (1-3): ").strip()
    if method == "2" or method == "3":
        email = input("Enter your email address: ").strip()
        smtp = input("Enter SMTP server (e.g., smtp.gmail.com): ").strip()
        password = input("Enter your email password (will be saved locally): ").strip()
    else:
        email = smtp = password = ""
    if method == "1":
        method_str = "system"
    elif method == "2":
        method_str = "email"
    elif method == "3":
        method_str = "both"
    else:
        method_str = "system"
    config = {"method": method_str, "email": email, "smtp": smtp, "password": password}
    save_notify_config(config)
    print("Notification preferences saved.")

# --- Notification Logic ---
def send_system_notification(title, message):
    if notification:
        notification.notify(title=title, message=message, timeout=10)
    else:
        print(f"[NOTIFY] {title}: {message}")

def send_email_reminder(config, subject, body):
    if not config["email"] or not config["smtp"] or not config["password"]:
        print("Email configuration incomplete. Skipping email reminder.")
        return
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = config["email"]
        msg["To"] = config["email"]
        with smtplib.SMTP_SSL(config["smtp"], 465) as server:
            server.login(config["email"], config["password"])
            server.sendmail(config["email"], [config["email"]], msg.as_string())
    except Exception as e:
        print(f"Failed to send email reminder: {e}")

def check_and_send_reminders(tasks, config):
    now = datetime.datetime.now()
    today = now.date().isoformat()
    current_time = now.strftime("%H:%M")
    for t in tasks:
        if t.get("done"):
            continue
        due = t.get("due_date")
        reminder = t.get("reminder_time")
        # Notify if due today and reminder time matches
        if due == today and reminder == current_time:
            msg = f"Task '{t['task']}' is due today."
            if config["method"] in ("system", "both"):
                send_system_notification("Task Reminder", msg)
            if config["method"] in ("email", "both"):
                send_email_reminder(config, "Task Reminder", msg)
        # Notify if overdue and not done
        elif due and due < today:
            msg = f"Task '{t['task']}' is OVERDUE!"
            if config["method"] in ("system", "both"):
                send_system_notification("Overdue Task", msg)
            if config["method"] in ("email", "both"):
                send_email_reminder(config, "Overdue Task", msg)

# --- Reminder Thread ---
def reminder_thread_func(tasks, config):
    while True:
        check_and_send_reminders(tasks, config)
        time.sleep(60)  # Check every minute

def main():
    tasks = load_tasks()
    custom_views = load_custom_views()
    notify_config = load_notify_config()
    # Start reminder thread
    reminder_thread = threading.Thread(target=reminder_thread_func, args=(tasks, notify_config), daemon=True)
    reminder_thread.start()
    while True:
        print("\nTo-Do List Menu")
        print("1. View tasks")
        print("2. Add task")
        print("3. Mark task as done")
        print("4. Remove task")
        print("5. Filter tasks")
        print("6. Edit task")
        print("7. Manage custom views")
        print("8. Configure notifications")
        print("9. Exit")
        choice = input("Choose an option (1-9): ").strip()

        if choice == "1":
            view_tasks_with_sort(tasks, custom_views)
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
            manage_custom_views(custom_views)
        elif choice == "8":
            configure_notifications()
            notify_config = load_notify_config()  # Reload config after change
        elif choice == "9":
            save_tasks(tasks)
            save_custom_views(custom_views)
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()

# Documentation: 
# - System notifications require the 'plyer' package (pip install plyer). 
# - Email reminders require valid SMTP credentials and an internet connection. 
# - Notification preferences are saved in 'notify_config.json'. 
# - Reminders are checked every minute in the background while the app is running.