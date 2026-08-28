from typing import List, Optional
from database import db_session

def get_all_bookers() -> List[dict]:
    with db_session() as conn:
        cursor = conn.cursor()
        # Get bookers with their total assigned customers and total outstanding amount
        cursor.execute('''
            SELECT 
                b.id, b.name, b.is_active,
                COUNT(DISTINCT c.id) as total_customers,
                COALESCE(
                    SUM(
                        c.opening_balance + 
                        COALESCE((SELECT SUM(amount) FROM transactions WHERE customer_id = c.id AND type = 'Bill'), 0) - 
                        COALESCE((SELECT SUM(amount) FROM transactions WHERE customer_id = c.id AND type = 'Recovery'), 0)
                    ), 0
                ) as total_outstanding
            FROM bookers b
            LEFT JOIN customers c ON b.id = c.booker_id AND c.is_active = 1
            GROUP BY b.id
            ORDER BY b.name
        ''')
        return [dict(row) for row in cursor.fetchall()]

def get_active_bookers() -> List[dict]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM bookers WHERE is_active = 1 ORDER BY name')
        return [dict(row) for row in cursor.fetchall()]

def get_booker_by_id(booker_id: int) -> Optional[dict]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                b.id, b.name, b.is_active,
                COUNT(DISTINCT c.id) as total_customers,
                COALESCE(
                    SUM(
                        c.opening_balance + 
                        COALESCE((SELECT SUM(amount) FROM transactions WHERE customer_id = c.id AND type = 'Bill'), 0) - 
                        COALESCE((SELECT SUM(amount) FROM transactions WHERE customer_id = c.id AND type = 'Recovery'), 0)
                    ), 0
                ) as total_outstanding
            FROM bookers b
            LEFT JOIN customers c ON b.id = c.booker_id AND c.is_active = 1
            WHERE b.id = ?
            GROUP BY b.id
        ''', (booker_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def create_booker(name: str) -> int:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO bookers (name) VALUES (?)', (name,))
        conn.commit()
        return cursor.lastrowid

def update_booker(booker_id: int, name: str, is_active: bool) -> bool:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE bookers
            SET name = ?, is_active = ?
            WHERE id = ?
        ''', (name, is_active, booker_id))
        conn.commit()
        return cursor.rowcount > 0
