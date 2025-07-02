import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;
import org.json.JSONArray;
import org.json.JSONObject;

public class ToDoList {

    private static final String TODO_FILE = "todo_list.json";
    private static final Scanner scanner = new Scanner(System.in);

    public static List<JSONObject> loadTasks() {
        try (FileReader reader = new FileReader(TODO_FILE)) {
            JSONArray tasks = new JSONArray(new org.json.JSONTokener(reader));
            List<JSONObject> taskList = new ArrayList<>();
            for (int i = 0; i < tasks.length(); i++) {
                taskList.add(tasks.getJSONObject(i));
            }
            return taskList;

        } catch (IOException | org.json.JSONException e) {
            return new ArrayList<>();
        }
    }

    public static void saveTasks(List<JSONObject> tasks) {
        try (FileWriter writer = new FileWriter(TODO_FILE)) {
            JSONArray jsonArray = new JSONArray(tasks);
            writer.write(jsonArray.toString(2));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void addTask(List<JSONObject> tasks) {
        System.out.print("Enter the task: ");
        String task = scanner.nextLine().strip();
        if (task.isEmpty()) {
            System.out.println("Empty task not added.");
            return;
        }
        System.out.print("Enter due date (YYYY-MM-DD) or leave blank: ");
        String dueDateStr = scanner.nextLine().strip();
        LocalDate dueDate = null;
        if (!dueDateStr.isEmpty()) {
            try {
                dueDate = LocalDate.parse(dueDateStr, DateTimeFormatter.ISO_DATE);
            } catch (DateTimeParseException e) {
                System.out.println("Invalid date format. Task not added.");
                return;
            }
        }
        System.out.print("Enter priority (High/Medium/Low, default Medium): ");
        String priority = scanner.nextLine().strip().toLowerCase();
        if (!priority.equals("high") && !priority.equals("medium") && !priority.equals("low")) {
            priority = "medium";
        }
        JSONObject newTask = new JSONObject();
        newTask.put("task", task);
        newTask.put("done", false);
        newTask.put("due_date", dueDate != null ? dueDate.format(DateTimeFormatter.ISO_DATE) : null);
        newTask.put("priority", priority);
        tasks.add(newTask);
        System.out.println("Task added.");
    }


    public static void viewTasks(List<JSONObject> tasks) {
        if (tasks.isEmpty()) {
            System.out.println("No tasks found.");
            return;
        }
        LocalDate today = LocalDate.now();
        for (int i = 0; i < tasks.size(); i++) {
            JSONObject task = tasks.get(i);
            String status = task.getBoolean("done") ? "✔️" : "❌";
            String dueDateStr = task.optString("due_date");
            String dueStr = "";
            boolean overdue = false;
            if (dueDateStr != null && !dueDateStr.isEmpty()) {
                try {
                    LocalDate dueDate = LocalDate.parse(dueDateStr, DateTimeFormatter.ISO_DATE);
                    if (!task.getBoolean("done") && dueDate.isBefore(today)) {
                        overdue = true;
                    }
                    dueStr = " (Due: " + dueDateStr + (overdue ? " - OVERDUE" : "") + ")";
                } catch (DateTimeParseException e) {
                    dueStr = " (Due: " + dueDateStr + " - INVALID DATE)";
                }
            }
            String priority = task.optString("priority", "Medium");
            System.out.println((i + 1) + ". [" + status + "] " + task.getString("task") + " [Priority: " + priority + "]" + dueStr);
        }
    }

    public static void markTaskDone(List<JSONObject> tasks) {
        viewTasks(tasks);
        int index = getValidTaskIndex(tasks);
        if (index != -1) {
            tasks.get(index).put("done", true);
            System.out.println("Task marked as done.");
        }
    }

    public static void removeTask(List<JSONObject> tasks) {
        viewTasks(tasks);
        int index = getValidTaskIndex(tasks);
        if (index != -1) {
            JSONObject removedTask = tasks.remove(index);
            System.out.println("Removed task: " + removedTask.getString("task"));
        }
    }

    public static void showReminders(List<JSONObject> tasks) {
        LocalDate today = LocalDate.now();
        List<String> reminders = new ArrayList<>();
        for (JSONObject task : tasks) {
            if (task.getBoolean("done")) continue;
            String dueDateStr = task.optString("due_date");
            if (dueDateStr != null && !dueDateStr.isEmpty()) {
                try {
                    LocalDate dueDate = LocalDate.parse(dueDateStr, DateTimeFormatter.ISO_DATE);
                    if (dueDate.isBefore(today)) {
                        reminders.add("OVERDUE: " + task.getString("task") + " (was due " + dueDateStr + ")");
                    } else if (dueDate.isEqual(today)) {
                        reminders.add("DUE TODAY: " + task.getString("task"));
                    }
                } catch (DateTimeParseException ignored) {}
            }
        }
        if (!reminders.isEmpty()) {
            System.out.println("\nReminders:");
            reminders.forEach(r -> System.out.println("- " + r));
        }
    }

    public static void editTask(List<JSONObject> tasks) {
        viewTasks(tasks);
        int index = getValidTaskIndex(tasks);
        if (index != -1) {
            JSONObject task = tasks.get(index);
            System.out.print("Editing task: " + task.getString("task") + "\n");
            System.out.print("New description (press Enter to keep '" + task.getString("task") + "'): ");
            String newDesc = scanner.nextLine().strip();
            System.out.print("New due date (YYYY-MM-DD, press Enter to keep '" + task.optString("due_date", "None") + "'): ");
            String newDue = scanner.nextLine().strip();
            System.out.print("New priority (High/Medium/Low, press Enter to keep '" + task.optString("priority", "Medium") + "'): ");
            String newPriority = scanner.nextLine().strip().toLowerCase();

            if (!newDesc.isEmpty()) task.put("task", newDesc);
            if (!newDue.isEmpty()) {
                try {
                    LocalDate.parse(newDue, DateTimeFormatter.ISO_DATE);
                    task.put("due_date", newDue);
                } catch (DateTimeParseException e) {
                    System.out.println("Invalid date format. Due date not updated.");
                }
            }
            if (!newPriority.isEmpty() && newPriority.matches("high|medium|low")) {
                task.put("priority", newPriority);
            } else if (!newPriority.isEmpty()){
                System.out.println("Invalid priority. Priority not updated.");
            }
            System.out.println("Task updated.");
        }
    }

    public static void searchTasks(List<JSONObject> tasks) {
        if (tasks.isEmpty()) {
            System.out.println("No tasks to search.");
            return;
        }
        System.out.println("\nSearch Tasks");
        System.out.println("1. By keyword");
        System.out.println("2. By due date (YYYY-MM-DD)");
        System.out.println("3. By priority (High/Medium/Low)");
        System.out.print("Choose search type (1-3): ");
        String choice = scanner.nextLine().strip();
        List<JSONObject> results = new ArrayList<>();
        switch (choice) {
            case "1":
                System.out.print("Enter keyword to search: ");
                String keyword = scanner.nextLine().strip().toLowerCase();
                results = tasks.stream().filter(t -> t.getString("task").toLowerCase().contains(keyword)).toList();
                break;
            case "2":
                System.out.print("Enter due date (YYYY-MM-DD): ");
                String date = scanner.nextLine().strip();
                results = tasks.stream().filter(t -> date.equals(t.optString("due_date", ""))).toList();
                break;
            case "3":
                System.out.print("Enter priority (High/Medium/Low): ");
                String priority = scanner.nextLine().strip().toLowerCase();
                if (priority.equals("high") || priority.equals("medium") || priority.equals("low")) {
                    results = tasks.stream().filter(t -> priority.equals(t.optString("priority", "medium"))).toList();
                } else {
                    System.out.println("Invalid priority.");
                    return;
                }
                break;
            default:
                System.out.println("Invalid choice.");
                return;
        }
        if (!results.isEmpty()) {
            System.out.println("\nFound " + results.size() + " matching task(s):");
            viewTasks(results);
        } else {
            System.out.println("No matching tasks found.");
        }
    }

    private static int getValidTaskIndex(List<JSONObject> tasks) {
        if (tasks.isEmpty()) return -1;
        System.out.print("Enter task number: ");
        try {
            int index = Integer.parseInt(scanner.nextLine().strip()) - 1;
            if (index >= 0 && index < tasks.size()) {
                return index;
            } else {
                System.out.println("Invalid task number.");
            }
        } catch (NumberFormatException e) {
            System.out.println("Please enter a valid number.");
        }
        return -1;
    }

    public static void main(String[] args) {
        List<JSONObject> tasks = loadTasks();
        showReminders(tasks);
        while (true) {
            System.out.println("\nTo-Do List Menu");
            System.out.println("1. View tasks");
            System.out.println("2. Add task");
            System.out.println("3. Mark task as done");
            System.out.println("4. Remove task");
            System.out.println("5. Edit task");
            System.out.println("6. Exit");
            System.out.println("7. Search tasks");
            System.out.print("Choose an option (1-7): ");
            String choice = scanner.nextLine().strip();
            switch (choice) {
                case "1":
                    viewTasks(tasks);
                    break;
                case "2":
                    addTask(tasks);
                    break;
                case "3":
                    markTaskDone(tasks);
                    break;
                case "4":
                    removeTask(tasks);
                    break;
                case "5":
                    editTask(tasks);
                    break;
                case "6":
                    saveTasks(tasks);
                    System.out.println("Goodbye!");
                    return;
                case "7":
                    searchTasks(tasks);
                    break;
                default:
                    System.out.println("Invalid choice.");
            }
        }
    }
}