import sqlite3

DB_NAME = "comments.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        summary TEXT,
        gap TEXT,
        weakness TEXT,
        comment1 TEXT,
        comment2 TEXT,
        comment3 TEXT,
        status TEXT DEFAULT 'new',
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()