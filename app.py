from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DB_PATH = 'task.db'

# Initialize the database setup
def init_db():

    conn = sqlite3.connect("task.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL
        )            
    """)
    conn.commit()
    conn.close()

 # Initialize the database when the app starts
init_db()

# Helper function to get database connection
def get_db_connection():
    conn = sqlite3.connect("task.db")
    conn.row_factory = sqlite3.Row 
    return conn

# Route to display all tasks
@app.route("/")
def index():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

# Route to add a new task
@app.route("/add", methods=["POST"])
def add_task():
    task_title = request.form.get("task", "").strip()
    if task_title:
        conn = get_db_connection()
        conn.execute("INSERT INTO tasks (title) VALUES (?)", (task_title,))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

# Route to delete a task
@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# --Edit / Update -
@app.route("/edit/<int:id>", methods=["POST", "GET"])
def edit_task(id):
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    conn.close()

    if tasks is None:
        return "Task not Found", 404
    return render_template("edit.html", task=tasks)

@app.route("/update/<int:id>", methods=["POST"])
def update_task(id):
    new_title = request.form["task"]
    
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET title = ? WHERE id = ?", (new_title, id))
    conn.commit()
    conn.close()

    return redirect(url_for("index"))

@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    conn = get_db_connection()

     # Check if column exists
    cursor = conn.execute("PRAGMA table_info(tasks)")
    columns = [col[1] for col in cursor]

    if "completed" not in columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN completed INTEGER DEFAULT 0")

    #Fetch task row
    task = conn.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,)).fetchone()
   
    if task is None:
        conn.close()
        return "Task not found", 404
    
    new_status = 0 if task["completed"] == 1 else 1

    conn.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db() 
    app.run(debug=True)