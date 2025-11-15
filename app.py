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