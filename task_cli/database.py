import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.expanduser("~"), ".task_cli.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            title     TEXT NOT NULL,
            category  TEXT DEFAULT 'geral',
            priority  TEXT DEFAULT 'media',
            due_date  TEXT,
            done      INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_task(title: str, category: str, priority: str, due_date: str | None) -> int:
    conn = get_conn()
    cursor = conn.execute(
        "INSERT INTO tasks (title, category, priority, due_date, created_at) VALUES (?, ?, ?, ?, ?)",
        (title, category, priority, due_date, datetime.now().isoformat())
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id


def list_tasks(category: str | None = None, priority: str | None = None,
               show_done: bool = False) -> list[dict]:
    conn = get_conn()
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if not show_done:
        query += " AND done = 0"
    if category:
        query += " AND category = ?"
        params.append(category)
    if priority:
        query += " AND priority = ?"
        params.append(priority)

    query += " ORDER BY CASE priority WHEN 'alta' THEN 1 WHEN 'media' THEN 2 WHEN 'baixa' THEN 3 END, due_date ASC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def search_tasks(term: str) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE title LIKE ? ORDER BY created_at DESC",
        (f"%{term}%",)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def complete_task(task_id: int) -> bool:
    conn = get_conn()
    cursor = conn.execute("UPDATE tasks SET done = 1 WHERE id = ? AND done = 0", (task_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def delete_task(task_id: int) -> bool:
    conn = get_conn()
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def edit_task(task_id: int, title: str | None, category: str | None,
              priority: str | None, due_date: str | None) -> bool:
    fields, params = [], []
    if title:
        fields.append("title = ?"); params.append(title)
    if category:
        fields.append("category = ?"); params.append(category)
    if priority:
        fields.append("priority = ?"); params.append(priority)
    if due_date is not None:
        fields.append("due_date = ?"); params.append(due_date or None)
    if not fields:
        return False
    params.append(task_id)
    conn = get_conn()
    cursor = conn.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def get_stats() -> dict:
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    done = conn.execute("SELECT COUNT(*) FROM tasks WHERE done = 1").fetchone()[0]
    by_category = conn.execute(
        "SELECT category, COUNT(*) FROM tasks WHERE done = 0 GROUP BY category"
    ).fetchall()
    overdue = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE done = 0 AND due_date < ? AND due_date IS NOT NULL",
        (datetime.now().strftime("%Y-%m-%d"),)
    ).fetchone()[0]
    conn.close()
    return {
        "total": total,
        "done": done,
        "pending": total - done,
        "overdue": overdue,
        "by_category": dict(by_category),
    }


def _row_to_dict(row) -> dict:
    return {
        "id": row[0], "title": row[1], "category": row[2],
        "priority": row[3], "due_date": row[4],
        "done": bool(row[5]), "created_at": row[6],
    }
