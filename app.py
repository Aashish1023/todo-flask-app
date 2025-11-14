from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

