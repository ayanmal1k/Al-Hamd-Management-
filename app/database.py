import sqlite3
import os
from contextlib import contextmanager

if os.environ.get('TESTING'):
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'test_alhamd.db'))
else:
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'alhamd.db'))

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = 1")
    return conn

@contextmanager
def db_session():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with db_session() as conn:
        cursor = conn.cursor()
        
        # Create Tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS areas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                area_id INTEGER,
                city_id INTEGER,
                booker_id INTEGER,
                opening_date DATE,
                opening_balance INTEGER DEFAULT 0, -- Stored in Paisa to avoid precision loss
                last_order_date DATE,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (area_id) REFERENCES areas (id),
                FOREIGN KEY (city_id) REFERENCES cities (id),
                FOREIGN KEY (booker_id) REFERENCES bookers (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                booker_id INTEGER NOT NULL,
                type TEXT NOT NULL, -- 'Bill' or 'Recovery'
                amount INTEGER NOT NULL, -- Stored in Paisa
                transaction_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (booker_id) REFERENCES bookers (id)
            )
        ''')
        
        # Insert Default Settings & Data if empty
        cursor.execute("SELECT COUNT(*) FROM cities WHERE name = 'Lahore'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO cities (name) VALUES ('Lahore')")
            
        conn.commit()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
