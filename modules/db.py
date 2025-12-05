import sqlite3
import os
from typing import Optional, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'game_data.db')


def get_connection():
    path = os.path.abspath(DB_PATH)
    conn = sqlite3.connect(path)
    return conn


def init_db():
    """inicaliza la base de datos creando las tablas necesarias si no existen"""
    conn = get_connection()
    c = conn.cursor()
    # Settings table (key-value)
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    # Players table
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Scores table
    c.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(player_id) REFERENCES players(id)
        )
    ''')
    conn.commit()
    conn.close()


def set_setting(key: str, value: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute('REPLACE INTO settings(key, value) VALUES(?, ?)', (key, value))
    conn.commit()
    conn.close()


def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT value FROM settings WHERE key = ?', (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default


def add_player(name: str) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO players(name) VALUES(?)', (name,))
    conn.commit()
    pid = c.lastrowid
    conn.close()
    return pid


def add_score(player_id: Optional[int], score: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO scores(player_id, score) VALUES(?, ?)', (player_id, score))
    conn.commit()
    conn.close()


def get_high_score() -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT MAX(score) FROM scores')
    row = c.fetchone()
    conn.close()
    return int(row[0]) if row and row[0] is not None else 0


def get_top_scores(limit: int = 10):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT s.score, p.name, s.created_at
        FROM scores s
        LEFT JOIN players p ON s.player_id = p.id
        ORDER BY s.score DESC, s.created_at ASC
        LIMIT ?
    ''', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
