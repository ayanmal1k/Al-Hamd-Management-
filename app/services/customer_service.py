from typing import List, Optional
from database import db_session
from models import Customer

def get_all_customers() -> List[dict]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                c.id, c.name, a.name as area, ci.name as city, 
                b.name as booker, c.opening_date, c.opening_balance,
                COALESCE(SUM(CASE WHEN t.type = 'Bill' THEN t.amount ELSE 0 END), 0) as total_bills,
                COALESCE(SUM(CASE WHEN t.type = 'Recovery' THEN t.amount ELSE 0 END), 0) as total_recoveries,
                c.opening_balance + 
                COALESCE(SUM(CASE WHEN t.type = 'Bill' THEN t.amount ELSE 0 END), 0) - 
                COALESCE(SUM(CASE WHEN t.type = 'Recovery' THEN t.amount ELSE 0 END), 0) as current_due,
                c.last_order_date
            FROM customers c
            LEFT JOIN areas a ON c.area_id = a.id
            LEFT JOIN cities ci ON c.city_id = ci.id
            LEFT JOIN bookers b ON c.booker_id = b.id
            LEFT JOIN transactions t ON c.id = t.customer_id
            WHERE c.is_active = 1
            GROUP BY c.id
        ''')
        return [dict(row) for row in cursor.fetchall()]

def get_customer_by_id(customer_id: int) -> Optional[dict]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                c.*, a.name as area, ci.name as city, b.name as booker,
                c.opening_balance + 
                COALESCE(SUM(CASE WHEN t.type = 'Bill' THEN t.amount ELSE 0 END), 0) - 
                COALESCE(SUM(CASE WHEN t.type = 'Recovery' THEN t.amount ELSE 0 END), 0) as current_due
            FROM customers c
            LEFT JOIN areas a ON c.area_id = a.id
            LEFT JOIN cities ci ON c.city_id = ci.id
            LEFT JOIN bookers b ON c.booker_id = b.id
            LEFT JOIN transactions t ON c.id = t.customer_id
            WHERE c.id = ?
            GROUP BY c.id
        ''', (customer_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def create_customer(name: str, area_id: Optional[int], city_id: Optional[int], 
                    booker_id: Optional[int], opening_date: str, opening_balance: int) -> int:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customers (name, area_id, city_id, booker_id, opening_date, opening_balance)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, area_id, city_id, booker_id, opening_date, opening_balance))
        conn.commit()
        return cursor.lastrowid

def update_customer(customer_id: int, name: str, area_id: Optional[int], city_id: Optional[int], 
                    booker_id: Optional[int]) -> bool:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE customers 
            SET name = ?, area_id = ?, city_id = ?, booker_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (name, area_id, city_id, booker_id, customer_id))
        conn.commit()
        return cursor.rowcount > 0

def get_or_create_area(name: str) -> int:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM areas WHERE name = ?', (name,))
        row = cursor.fetchone()
        if row:
            return row['id']
        cursor.execute('INSERT INTO areas (name) VALUES (?)', (name,))
        conn.commit()
        return cursor.lastrowid

def get_or_create_city(name: str) -> int:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM cities WHERE name = ?', (name,))
        row = cursor.fetchone()
        if row:
            return row['id']
        cursor.execute('INSERT INTO cities (name) VALUES (?)', (name,))
        conn.commit()
        return cursor.lastrowid

def get_all_areas() -> List[dict]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM areas ORDER BY name')
        return [dict(row) for row in cursor.fetchall()]

def get_all_cities() -> List[dict]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cities ORDER BY name')
        return [dict(row) for row in cursor.fetchall()]
