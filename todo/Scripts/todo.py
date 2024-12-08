import tkinter as tk
from tkinter import messagebox
import json
import os
import threading
from plyer import notification
import time

# File to store tasks
DATA_FILE = "tasks.json"

# Function to save tasks to a file
def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f)

# Function to load tasks from a file
def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            tasks = json.load(f)
            # Validate task data
            validated_tasks = []
            for task in tasks:
                if all(key in task for key in ('id', 'task', 'status')):
                    validated_tasks.append(task)
            return validated_tasks
    return []

# Function to send task notification reminder
def send_reminder(task):
    notification.notify(
        title="Task Reminder",
        message=f"Reminder: Complete your task - '{task}'!",
        timeout=10
    )

# Function to check for incomplete tasks
def task_reminder(app):
    while True:
        time.sleep(60)  # Check every 60 seconds
        for task in app.tasks:
            if task['status'] == 'Incomplete':
                send_reminder(task['task'])

# Main ToDoListApp class
class ToDoListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List App")
        self.root.state('zoomed')  # Fullscreen

        self.root.config(bg="lightblue")

        self.tasks = load_tasks()

        # Title label
        self.title_label = tk.Label(self.root, text="My To-Do List", font=("Arial", 24, "bold"), bg="lightblue", fg="darkblue")
        self.title_label.pack(pady=20)

        # Task input field
        self.task_entry = tk.Text(self.root, font=("Arial", 18), width=40, height=10, fg='black', wrap=tk.WORD)
        self.task_entry.pack(pady=10)

        # Buttons frame
        self.button_frame = tk.Frame(self.root, bg="lightblue")
        self.button_frame.pack(pady=10)

        # Add Tasks button
        self.add_button = tk.Button(self.button_frame, text="Add Tasks", font=("Arial", 14), bg="green", fg="white", command=self.add_tasks)
        self.add_button.grid(row=0, column=0, padx=10)

        # Edit Task button
        self.edit_button = tk.Button(self.button_frame, text="Edit Task", font=("Arial", 14), bg="orange", fg="white", command=self.edit_task)
        self.edit_button.grid(row=0, column=1, padx=10)

        # Delete Task button
        self.delete_button = tk.Button(self.button_frame, text="Delete Task", font=("Arial", 14), bg="red", fg="white", command=self.delete_task)
        self.delete_button.grid(row=0, column=2, padx=10)

        # Status Change button
        self.status_button = tk.Button(self.button_frame, text="Toggle Status", font=("Arial", 14), bg="blue", fg="white", command=self.change_status)
        self.status_button.grid(row=0, column=3, padx=10)

        # Delete All Tasks button
        self.delete_all_button = tk.Button(self.button_frame, text="Delete All Tasks", font=("Arial", 14), bg="purple", fg="white", command=self.delete_all_tasks)
        self.delete_all_button.grid(row=0, column=4, padx=10)

        # Task list box
        self.task_listbox = tk.Listbox(self.root, height=15, width=50, font=("Arial", 16), selectmode=tk.SINGLE)
        self.task_listbox.pack(pady=20)
        self.load_tasks_in_listbox()

        # Start the task reminder thread
        self.start_reminder_thread()

    # Function to start the reminder thread
    def start_reminder_thread(self):
        reminder_thread = threading.Thread(target=task_reminder, args=(self,))
        reminder_thread.daemon = True  # Daemon thread will exit when the main program exits
        reminder_thread.start()

    # Function to get the next task ID
    def get_next_task_id(self):
        if not self.tasks:
            return 1
        # Return the next ID based on the highest current ID
        return max(task['id'] for task in self.tasks) + 1

    # Add tasks function
    def add_tasks(self):
        task_descriptions = self.task_entry.get("1.0", tk.END).strip().split('\n')
        if task_descriptions:
            for description in task_descriptions:
                description = description.strip()
                if description:
                    task_id = self.get_next_task_id()
                    self.tasks.append({"id": task_id, "task": description, "status": "Incomplete"})
            self.reassign_task_ids()  # Ensure IDs are sequential
            self.update_task_listbox()
            self.task_entry.delete("1.0", tk.END)
        else:
            messagebox.showwarning("Input Error", "Please enter at least one task.")

    # Edit task function
    def edit_task(self):
        try:
            selected_index = self.task_listbox.curselection()[0]  # Get the index of the selected task
            selected_task = self.tasks[selected_index]  # Get the task from the list of tasks
            new_task_description = self.task_entry.get("1.0", tk.END).strip()  # Get the new task description from the input field

            if new_task_description:  # Ensure the input field is not empty
                # Preserve the status and ID of the task and only update the task description
                selected_task['task'] = new_task_description
                self.update_task_listbox()  # Refresh the listbox
                self.task_entry.delete("1.0", tk.END)  # Clear the input field
            else:
                messagebox.showwarning("Input Error", "Task cannot be empty.")
        except IndexError:
            messagebox.showwarning("Selection Error", "No task selected.")

    # Delete task function
    def delete_task(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            del self.tasks[selected_index]
            self.reassign_task_ids()
            self.update_task_listbox()
        except IndexError:
            messagebox.showwarning("Selection Error", "No task selected.")

    # Function to reassign task IDs after addition or deletion
    def reassign_task_ids(self):
        # Reassign IDs sequentially starting from 1
        self.tasks = sorted(self.tasks, key=lambda x: x['id'])
        for index, task in enumerate(self.tasks):
            task['id'] = index + 1

    # Change status function to toggle between Incomplete, In-Progress, and Complete
    def change_status(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            selected_task = self.tasks[selected_index]

            # Cycle through the statuses: Incomplete -> In-Progress -> Complete
            if selected_task['status'] == 'Incomplete':
                selected_task['status'] = 'In-Progress'
            elif selected_task['status'] == 'In-Progress':
                selected_task['status'] = 'Complete'
            else:
                selected_task['status'] = 'Incomplete'

            self.update_task_listbox()
        except IndexError:
            messagebox.showwarning("Selection Error", "No task selected.")

    # Function to update task listbox
    def update_task_listbox(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            display_text = f"#{task['id']}: {task['task']} ({task['status']})"
            self.task_listbox.insert(tk.END, display_text)
        save_tasks(self.tasks)

    # Load tasks in the listbox
    def load_tasks_in_listbox(self):
        self.task_listbox.delete(0, tk.END)  # Ensure listbox is empty before loading tasks
        for task in self.tasks:
            display_text = f"#{task['id']}: {task['task']} ({task['status']})"
            self.task_listbox.insert(tk.END, display_text)

    # Delete all tasks function
    def delete_all_tasks(self):
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete all tasks?")
        if confirm:
            self.tasks = []  # Clear all tasks
            self.reassign_task_ids()  # Reassign IDs
            self.update_task_listbox()

# Create the main window and run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoListApp(root)
    root.mainloop()
