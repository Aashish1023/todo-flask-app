from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DB_PATH = 'task.db'

# Initialize the database setup
def init_db():
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
                id INTEGET PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
            )            
    """)
    conn.commit()
    conn.close()

 # Initialize the database when the app starts
init_db()

# Helper function to get database connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
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

# --Edit / Update need to add later--

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db() 
    app.run(debug=True)