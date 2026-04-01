import os
import sqlite3
from typing import Any, Dict, List, Optional

DB_NAME = os.environ.get(
    "ACEEST_DB_PATH",
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "data", "aceest_fitness.db")
    ),
)


def get_db_conn():
    print(os.path.dirname(__file__))
    print(f"Connecting to DB at: {DB_NAME}")
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            weight REAL,
            program TEXT,
            calories INTEGER
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
    conn.commit()
    conn.close()


def add_client(client: Dict[str, Any]) -> None:
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO clients (name, age, weight, program, calories)
        VALUES (?, ?, ?, ?, ?)
    """,
        (
            client.get("name"),
            client.get("age"),
            client.get("weight"),
            client.get("program"),
            client.get("calories"),
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
                "weight": row["weight"],
                "program": row["program"],
                "calories": row["calories"],
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
            "weight": row["weight"],
            "program": row["program"],
            "calories": row["calories"],
        }
    return None


def clear_clients() -> None:
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM clients")
    conn.commit()
    conn.close()


def save_progress(client_name: str, week: str, adherence: int) -> None:
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
        "SELECT * FROM progress WHERE client_name=? ORDER BY week DESC",
        (client_name,)
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
