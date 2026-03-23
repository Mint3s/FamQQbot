import sqlite3
from config import MAX_WARNS

DB_NAME = "majestic.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Таблица пользователей
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT DEFAULT 'recruit',
            warns INTEGER DEFAULT 0,
            rank INTEGER DEFAULT 1,
            full_given TEXT DEFAULT '',
            cars TEXT DEFAULT '',
            invited_by INTEGER DEFAULT NULL
        )
    ''')

    # Таблица каптов (захватов территорий)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS caps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,  -- 'attack' or 'defense'
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user


def add_user(user_id, username, invited_by=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users (user_id, username, invited_by) VALUES (?, ?, ?)",
        (user_id, username, invited_by)
    )
    conn.commit()
    conn.close()


def update_user_field(user_id, field, value):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
    conn.commit()
    conn.close()


def add_warn(user_id):
    user = get_user(user_id)
    if user:
        warns = user[3] + 1
        update_user_field(user_id, "warns", warns)
        return warns
    return 0


def clear_warns(user_id):
    update_user_field(user_id, "warns", 0)


def add_cap(user_id, cap_type):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO caps (user_id, type) VALUES (?, ?)",
        (user_id, cap_type)
    )
    conn.commit()
    conn.close()


def get_caps_count(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT type, COUNT(*) FROM caps WHERE user_id = ? GROUP BY type",
        (user_id,)
    )
    data = cur.fetchall()
    conn.close()
    result = {"attack": 0, "defense": 0}
    for typ, count in data:
        result[typ] = count
    return result