import os
import sqlite3
from typing import Any, Dict, List, Optional


# DB_NAME can be overridden by the ACEEST_DB_PATH environment variable (set in test mode)
def get_db_path():
    return os.environ.get(
        "ACEEST_DB_PATH",
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), "data", "aceest_fitness.db")
        ),
    )


print("ENV DB:", os.environ.get("ACEEST_DB_PATH"))


def get_db_conn():
    db_path = get_db_path()

    # 🔥 critical fix for Docker/CI
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    print(os.path.dirname(__file__))
    print(f"Connecting to DB at: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_conn()
    cur = conn.cursor()
    # Check if clients table exists and has all required columns
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
    exists = cur.fetchone() is not None

    if exists:
        cur.execute("PRAGMA table_info(clients)")
        cols = [row[1] for row in cur.fetchall()]
        required = {
            "id",
            "name",
            "age",
            "height",
            "weight",
            "program",
            "calories",
            "target_weight",
            "target_adherence",
            "adherence",
        }
        if not required.issubset(set(cols)):
            cur.execute("DROP TABLE clients")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            target_weight REAL,
            target_adherence INTEGER,
            adherence INTEGER
        )
        """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            week TEXT,
            adherence INTEGER
        )
        """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            workout_type TEXT,
            duration_min INTEGER,
            notes TEXT
        )
        """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER,
            name TEXT,
            sets INTEGER,
            reps INTEGER,
            weight REAL
        )
        """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            weight REAL,
            waist REAL,
            bodyfat REAL
        )
        """)

    conn.commit()
    conn.close()


def add_client(client: Dict[str, Any]) -> None:
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM clients WHERE name=?", (client.get("name"),))
    row = cur.fetchone()
    if row:
        cur.execute(
            """
            UPDATE clients SET
                age=?, height=?, weight=?, program=?, calories=?,
                target_weight=?, target_adherence=?, adherence=?
            WHERE name=?
            """,
            (
                client.get("age"),
                client.get("height"),
                client.get("weight"),
                client.get("program"),
                client.get("calories"),
                client.get("target_weight"),
                client.get("target_adherence"),
                client.get("adherence"),
                client.get("name"),
            ),
        )
    else:
        cur.execute(
            """
            INSERT INTO clients (
                name, age, height, weight, program,
                calories, target_weight, target_adherence, adherence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                client.get("name"),
                client.get("age"),
                client.get("height"),
                client.get("weight"),
                client.get("program"),
                client.get("calories"),
                client.get("target_weight"),
                client.get("target_adherence"),
                client.get("adherence"),
            ),
        )
    conn.commit()
    conn.close()


def get_clients() -> List[Dict[str, Any]]:
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients")
    rows = cur.fetchall()
    clients = []
    for row in rows:
        clients.append(
            {
                "id": row["id"],
                "name": row["name"],
                "age": row["age"],
                "height": row["height"],
                "weight": row["weight"],
                "program": row["program"],
                "calories": row["calories"],
                "target_weight": row["target_weight"],
                "target_adherence": row["target_adherence"],
                "adherence": row["adherence"],
            }
        )
    conn.close()
    return clients


def get_client_by_name(name: str) -> Optional[Dict[str, Any]]:
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE name=?", (name,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "id": row["id"],
            "name": row["name"],
            "age": row["age"],
            "height": row["height"],
            "weight": row["weight"],
            "program": row["program"],
            "calories": row["calories"],
            "target_weight": row["target_weight"],
            "target_adherence": row["target_adherence"],
        }
    return None


def clear_clients() -> None:
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM clients")
    conn.commit()
    conn.close()


def save_progress(client_name: str, week: str, adherence: int) -> None:
    print(f"Saving progress for {client_name} - Week: {week}, Adherence: {adherence}")
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO progress (client_name, week, adherence)
        VALUES (?, ?, ?)
    """,
        (client_name, week, adherence),
    )
    conn.commit()
    conn.close()


def get_progress(client_name: str) -> List[Dict[str, Any]]:
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM progress WHERE client_name=? ORDER BY week DESC", (client_name,)
    )
    rows = cur.fetchall()
    progress = []
    for row in rows:
        progress.append(
            {
                "id": row["id"],
                "client_name": row["client_name"],
                "week": row["week"],
                "adherence": row["adherence"],
            }
        )
    conn.close()
    return progress
