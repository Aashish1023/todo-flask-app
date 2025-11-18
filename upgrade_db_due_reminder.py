# upgrade_db_due_reminder.py
import sqlite3

DB = "task.db"

def column_exists(cursor, table, col):
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    return col in cols

conn = sqlite3.connect(DB)
# Check and add 'due_date' column
if not column_exists(conn, "tasks", "due_date"):
    conn.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT DEFAULT NULL")

# add reminde_at column (datetime string ' YYYY-MM-DD HH:MM')
if not column_exists(conn, "tasks", "reminder_at"):
    conn.execute("ALTER TABLE tasks ADD COLUMN reminder_at TEXT DEFAULT NULL")

# add reminder_sent flag (integer 0/1)
if not column_exists(conn, "tasks", "reminder_sent"):
    conn.execute("ALTER TABLE tasks ADD COLUMN reminder_sent TEXT DEFAULT 0")

conn.commit()
conn.close()

print("DB Migration Complete (if columns were missing).")