import sqlite3

conn = sqlite3.connect("task.db")
cur = conn.cursor()

cur.execute("ALTER TABLE tasks ADD COLUMN completed INTEGER DEFAULT 0;")

conn.commit()
conn.close()

print("Database upgraded successfully.")

# Database schema upgraded to include 'completed' column in 'tasks' table.