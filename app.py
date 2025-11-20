from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv() # Load environment variables from .env file

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

#Helper: parse ISO date/datetime string
def parse_date(s):
    #ecpects 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS'
    try:
        return datetime.strptime(s, "%y-%m-%d").date()
    except Exception:
        return None

def parse_datetime(s):
    # expects 'YYYY-MM-DD HH:MM' or None
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M")
    except Exception:
        return None

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
    due_date = request.form.get("due_date") or None   # e.g., "2025-11-12"
    reminder_at = request.form.get("reminder_at") or None # e.g., "2025-11-12 14:30"
   
    if task_title:
        conn = get_db_connection()
        conn.execute("INSERT INTO tasks (title, due_date, reminder_at, reminder_sent) VALUES (?, ?, ?, ?)",
                      (task_title, due_date, reminder_at, 0)
                    )
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
    new_title = request.form.get("task", "").strip()
    due_date = request.form.get("due_date") or None  # e.g., "2025-11-12"
    reminder_at = request.form.get("reminder_at") or None # e.g., "2025-11-12 14:30"
   
    
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET title = ?, due_date = ?, reminder_at = ?, reminder_sent = 0 WHERE id = ?",
                  (new_title, due_date, reminder_at, id)
                )
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

#update add_task to accept due_date & reminder_at
def send_reminder_email(to_email, subject, body):
    #Uses SMTP Seettings from environment variables
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    FROM = os.getenv("FROM_EMAIL")

    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS or not FROM:
         # fallback: print the message (safe for dev)
        print("Reminder (mock);" , to_email, subject, body)
        return
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = FROM
    msg['To'] = to_email

    s = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    s.starttls()
    s.login(SMTP_USER, SMTP_PASS)
    s.sendmail(FROM, [to_email], msg.as_string())
    s.quit()


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db() 
    app.run(debug=True)