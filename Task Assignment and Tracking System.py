import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import date

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="piyush",    
)

cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS task_management")
cursor.execute("USE task_management")
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255) NOT NULL)")
cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id INT AUTO_INCREMENT PRIMARY KEY,title VARCHAR(255) NOT NULL,description TEXT,assigned_to INT,status ENUM('Pending', 'In Progress', 'Completed') DEFAULT 'Pending',deadline DATE,FOREIGN KEY (assigned_to) REFERENCES users(id))")
# For testing
#cursor.execute("INSERT INTO users (name) VALUES ('Alice'), ('Bob'), ('Charlie')")

# Function to load users for assignment dropdown
def load_users():
    cursor.execute("SELECT id,name FROM users")
    users = cursor.fetchall()
    return {user[1]: user[0] for user in users}  # Returns a dictionary with name as key and id as value

# Function to add a task
def add_task():
    title = entry_title.get()
    description = entry_description.get("1.0", tk.END).strip()
    assigned_user = users_dict.get(combo_assigned.get())
    deadline = entry_deadline.get()
    
    if title and description and assigned_user and deadline:
        cursor.execute("INSERT INTO tasks (title, description, assigned_to, deadline) VALUES (%s, %s, %s, %s)",
                       (title, description, assigned_user, deadline))
        conn.commit()
        messagebox.showinfo("Success", "Task added successfully!")
        clear_entries()
        load_tasks()
    else:
        messagebox.showwarning("Input Error", "Please fill all fields")

# Function to update task status
def update_task_status():
    selected_item = tree.selection()
    if selected_item:
        task_id = tree.item(selected_item)["values"][0]
        new_status = combo_status.get()
        cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (new_status, task_id))
        conn.commit()
        messagebox.showinfo("Success", "Task status updated successfully!")
        load_tasks()
    else:
        messagebox.showwarning("Selection Error", "Please select a task to update")

# Function to load tasks into the tree view
def load_tasks():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("""
    SELECT tasks.id, tasks.title, users.name, tasks.status, tasks.deadline
    FROM tasks
    LEFT JOIN users ON tasks.assigned_to = users.id
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

# Function to clear entry fields
def clear_entries():
    entry_title.delete(0, tk.END)
    entry_description.delete("1.0", tk.END)
    combo_assigned.set("")
    entry_deadline.delete(0, tk.END)
        
def add_people():
    add_employee_window = tk.Tk()
    add_employee_window.title("Add people")

    tk.Label(add_employee_window, text="Name").pack()
    emp_id_entry = tk.Entry(add_employee_window)
    emp_id_entry.pack()
    emp_id_entry1=emp_id_entry.get()
    # a=cursor.execute("INSERT INTO users (name) VALUES(%s)",(emp_id_entry1))
    tk.Button(add_employee_window, text="Add", command=print()).pack()
    

# GUI setup
app = tk.Tk()
app.title("Task Assignment and Tracking System")
app.geometry("1020x560")

# Load users into a dictionary
users_dict = load_users()

# Input fields
tk.Label(app, text="Task Title").grid(row=0, column=0, padx=10, pady=10)
entry_title = tk.Entry(app)
entry_title.grid(row=0, column=1, padx=10, pady=10)

tk.Label(app, text="Description").grid(row=1, column=0, padx=10, pady=10)
entry_description = tk.Text(app, height=4, width=30)
entry_description.grid(row=1, column=1, padx=10, pady=10)

tk.Label(app, text="Assign to").grid(row=2, column=0, padx=10, pady=10)
combo_assigned = ttk.Combobox(app, values=list(users_dict.keys()))
combo_assigned.grid(row=2, column=1, padx=10, pady=10)

tk.Label(app, text="Deadline (YYYY-MM-DD)").grid(row=3, column=0, padx=10, pady=10)
entry_deadline = tk.Entry(app)
entry_deadline.grid(row=3, column=1, padx=10, pady=10)

# Buttons
tk.Button(app, text="Add Task", command=add_task).grid(row=4, column=0, columnspan=2, padx=10, pady=10)
tk.Button(app, text="Add People", command=add_people).grid(row=4, column=1, columnspan=2, padx=20, pady=20)
# Tree view for tasks
columns = ("ID", "Title", "Assigned To", "Status", "Deadline")
tree = ttk.Treeview(app, columns=columns, show="headings")
tree.heading("ID", text="ID")
tree.heading("Title", text="Title")
tree.heading("Assigned To", text="Assigned To")
tree.heading("Status", text="Status")
tree.heading("Deadline", text="Deadline")
tree.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

# Status selection and update button
tk.Label(app, text="Update Status").grid(row=6, column=0, padx=10, pady=10)
combo_status = ttk.Combobox(app, values=["Pending", "In Progress", "Completed"])
combo_status.grid(row=6, column=1, padx=10, pady=10)
tk.Button(app, text="Update Task Status", command=update_task_status).grid(row=6, column=2, padx=10, pady=10)

# Load tasks initially
load_tasks()

app.mainloop()

# Close MySQL connection
conn.close()
