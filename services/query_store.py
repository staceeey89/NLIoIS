import os
import json
import sqlite3
from datetime import datetime

from config import Config


def _connect():
    os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)
    return sqlite3.connect(Config.DB_PATH)


def init_query_db():
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY,
            query TEXT UNIQUE,
            results_json TEXT,
            times_searched INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
        '''
    )
    conn.commit()
    conn.close()


def get_cached_results(query: str, page: int = 1):
    conn = _connect()
    cur = conn.cursor()
    key = f"{query}::p{page}"
    cur.execute('SELECT results_json, times_searched FROM queries WHERE query = ?', (key,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    results_json, _ = row
    try:
        return json.loads(results_json) if results_json else None
    except json.JSONDecodeError:
        return None


def save_results(query: str, results: list, page: int = 1):
    now = datetime.utcnow().isoformat()
    payload = json.dumps(results, ensure_ascii=False)
    conn = _connect()
    cur = conn.cursor()
    key = f"{query}::p{page}"
    cur.execute(
        '''
        INSERT INTO queries (query, results_json, times_searched, created_at, updated_at)
        VALUES (?, ?, 1, ?, ?)
        ON CONFLICT(query) DO UPDATE SET
            results_json=excluded.results_json,
            times_searched=queries.times_searched + 1,
            updated_at=excluded.updated_at
        ''',
        (key, payload, now, now)
    )
    conn.commit()
    conn.close()


def increment_usage(query: str, page: int = 1):
    now = datetime.utcnow().isoformat()
    conn = _connect()
    cur = conn.cursor()
    key = f"{query}::p{page}"
    cur.execute('UPDATE queries SET times_searched = times_searched + 1, updated_at = ? WHERE query = ?', (now, key))
    conn.commit()
    conn.close()


def get_popular_queries(limit: int = 15):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        'SELECT query FROM queries ORDER BY times_searched DESC, updated_at DESC LIMIT ?',
        (limit,)
    )
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows


def find_similar_queries(prefix: str, limit: int = 15):
    like = f"{prefix}%"
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        'SELECT query FROM queries WHERE query LIKE ? ORDER BY times_searched DESC, updated_at DESC LIMIT ?',
        (like, limit)
    )
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows


