"""Shared test helpers: build a fresh in-memory copy of the wildlife database."""
import os
import sqlite3

import run_sql

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_DIR = os.path.join(PROJECT_ROOT, "sql")

BUILD_SCRIPTS = [
    "01_schema.sql",
    "02_seed.sql",
    "03_views.sql",
    "04_procedure.sql",
    "05_trigger.sql",
]


def script_text(name):
    return run_sql.read_script(os.path.join(SQL_DIR, name))


def build_database():
    """A brand-new in-memory database with every build script applied."""
    connection = run_sql.connect(":memory:")
    for name in BUILD_SCRIPTS:
        run_sql.run_script(connection, script_text(name))
    return connection


def run_file(connection, name):
    return run_sql.run_script(connection, script_text(name))


def today(connection):
    return connection.execute("SELECT date('now')").fetchone()[0]


def days_ago(connection, days):
    return connection.execute("SELECT date('now', ?)", (f"-{days} days",)).fetchone()[0]


IntegrityError = sqlite3.IntegrityError