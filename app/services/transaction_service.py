from typing import List, Optional
from database import db_session

def add_transaction(customer_id: int, booker_id: int, tx_type: str, amount: int, transaction_date: str, notes: Optional[str] = None) -> int:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (customer_id, booker_id, type, amount, transaction_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (customer_id, booker_id, tx_type, amount, transaction_date, notes))
        
        # Update last_order_date if it's a Bill
        if tx_type == 'Bill':
            cursor.execute('''
                UPDATE customers 
                SET last_order_date = (
                    SELECT MAX(transaction_date) 
                    FROM transactions 
                    WHERE customer_id = ? AND type = 'Bill'
                )
                WHERE id = ?
            ''', (customer_id, customer_id))
            
        conn.commit()
        return cursor.lastrowid

def update_transaction(transaction_id: int, amount: int, transaction_date: str, notes: Optional[str] = None) -> bool:
    with db_session() as conn:
        cursor = conn.cursor()
        
        # Get customer_id and type before update
        cursor.execute('SELECT customer_id, type FROM transactions WHERE id = ?', (transaction_id,))
        row = cursor.fetchone()
        if not row:
            return False
            
        customer_id = row['customer_id']
        tx_type = row['type']
        
        cursor.execute('''
            UPDATE transactions
            SET amount = ?, transaction_date = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (amount, transaction_date, notes, transaction_id))
        
        # Update last_order_date if it was a Bill
        if tx_type == 'Bill':
            cursor.execute('''
                UPDATE customers 
                SET last_order_date = (
                    SELECT MAX(transaction_date) 
                    FROM transactions 
                    WHERE customer_id = ? AND type = 'Bill'
                )
                WHERE id = ?
            ''', (customer_id, customer_id))
            
        conn.commit()
        return cursor.rowcount > 0

def delete_transaction(transaction_id: int) -> bool:
    with db_session() as conn:
        cursor = conn.cursor()
        
        # Get customer_id and type before delete
        cursor.execute('SELECT customer_id, type FROM transactions WHERE id = ?', (transaction_id,))
        row = cursor.fetchone()
        if not row:
            return False
            
        customer_id = row['customer_id']
        tx_type = row['type']
        
        cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        
        # Update last_order_date if it was a Bill
        if tx_type == 'Bill':
            cursor.execute('''
                UPDATE customers 
                SET last_order_date = (
                    SELECT MAX(transaction_date) 
                    FROM transactions 
                    WHERE customer_id = ? AND type = 'Bill'
                )
                WHERE id = ?
            ''', (customer_id, customer_id))
            
        conn.commit()
        return cursor.rowcount > 0

def get_customer_transactions(customer_id: int) -> List[dict]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.*, b.name as booker_name
            FROM transactions t
            LEFT JOIN bookers b ON t.booker_id = b.id
            WHERE t.customer_id = ?
            ORDER BY t.transaction_date ASC, t.id ASC
        ''', (customer_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_filtered_history(start_date: Optional[str] = None, end_date: Optional[str] = None, 
                         customer_id: Optional[int] = None, booker_id: Optional[int] = None,
                         tx_type: Optional[str] = None) -> List[dict]:
    with db_session() as conn:
        cursor = conn.cursor()
        
        query = '''
            SELECT t.*, c.name as customer_name, b.name as booker_name,
                   c.opening_balance + COALESCE((
                       SELECT SUM(CASE WHEN type = 'Bill' THEN amount ELSE -amount END) 
                       FROM transactions 
                       WHERE customer_id = t.customer_id AND 
                             (transaction_date < t.transaction_date OR (transaction_date = t.transaction_date AND id <= t.id))
                   ), 0) as updated_balance
            FROM transactions t
            JOIN customers c ON t.customer_id = c.id
            JOIN bookers b ON t.booker_id = b.id
            WHERE 1=1
        '''
        params = []
        
        if start_date:
            query += ' AND t.transaction_date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND t.transaction_date <= ?'
            params.append(end_date)
        if customer_id:
            query += ' AND t.customer_id = ?'
            params.append(customer_id)
        if booker_id:
            query += ' AND t.booker_id = ?'
            params.append(booker_id)
        if tx_type:
            query += ' AND t.type = ?'
            params.append(tx_type)
            
        query += ' ORDER BY t.transaction_date DESC, t.id DESC'
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
