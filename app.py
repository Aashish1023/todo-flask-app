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