# --- User Authentication Functions ---
import hashlib
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
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    print("Initializing database...")
    with get_db_conn() as conn:
        cur = conn.cursor()
    # Users table for authentication
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT
        )
    """)
    # Create default admin user if not exists
    cur.execute("SELECT id FROM users WHERE username=?", ("admin",))
    if not cur.fetchone():
        import hashlib

        admin_pw = hashlib.sha256("admin".encode()).hexdigest()
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", admin_pw, "Admin"),
        )
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
            adherence INTEGER,
            membership_expiry TEXT
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
    with get_db_conn() as conn:
        cur = conn.cursor()
    cur.execute("SELECT id FROM clients WHERE name=?", (client.get("name"),))
    row = cur.fetchone()
    if row:
        cur.execute(
            """
            UPDATE clients SET
                age=?, height=?, weight=?, program=?, calories=?,
                target_weight=?, target_adherence=?, adherence=?, membership_expiry=?
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
                client.get("membership_expiry"),
                client.get("name"),
            ),
        )
    else:
        cur.execute(
            """
            INSERT INTO clients (
                name, age, height, weight, program,
                calories, target_weight, target_adherence, adherence, membership_expiry
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                client.get("membership_expiry"),
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
                "membership_expiry": row["membership_expiry"],
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
            "membership_expiry": row["membership_expiry"],
        }
    return None


def clear_clients() -> None:
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM clients")
        conn.commit()


def save_progress(client_name: str, week: str, adherence: int) -> None:
    print(f"Saving progress for {client_name} - Week: {week}, Adherence: {adherence}")
    with get_db_conn() as conn:
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


def get_workout_history(client_name: str) -> list:
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT date, workout_type, duration_min, notes
        FROM workouts
        WHERE client_name=?
        ORDER BY date DESC, id DESC
        """,
        (client_name,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_workout(
    client_name: str, date: str, workout_type: str, duration_min: int, notes: str
) -> None:
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
                INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
            (client_name, date, workout_type, duration_min, notes),
        )
        conn.commit()


def save_metrics(
    client_name: str, date: str, weight: float, waist: float, bodyfat: float
) -> None:
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
                INSERT INTO metrics (client_name, date, weight, waist, bodyfat)
                VALUES (?, ?, ?, ?, ?)
                """,
            (client_name, date, weight, waist, bodyfat),
        )
        conn.commit()


def create_user(username: str, password: str, role: str = "User") -> None:
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    with get_db_conn() as conn:
        cur = conn.cursor()
        # Avoid duplicate users
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, pw_hash, role),
            )
            conn.commit()


def get_user_by_username(username: str):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def check_password(username: str, password: str) -> bool:
    user = get_user_by_username(username)
    if not user:
        return False
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    return user["password_hash"] == pw_hash
