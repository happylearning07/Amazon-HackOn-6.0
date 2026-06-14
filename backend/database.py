import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "trustpass.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_id TEXT,
        item_name TEXT,
        grade TEXT,
        damage_type TEXT,
        confidence REAL,
        route TEXT,
        suggested_price REAL,
        material TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS trust_scores (
        seller_id TEXT PRIMARY KEY,
        total_listings INTEGER DEFAULT 0,
        accurate_listings INTEGER DEFAULT 0,
        trust_score REAL DEFAULT 100.0
    )''')
    conn.commit()
    conn.close()