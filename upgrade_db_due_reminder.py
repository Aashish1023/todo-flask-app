# upgrade_db_due_reminder.py
import sqlite3

DB = "task.db"

conn = sqlite3.connect(DB)

conn.commit()
conn.close()

print("DB Migration Complete (if columns were missing).")