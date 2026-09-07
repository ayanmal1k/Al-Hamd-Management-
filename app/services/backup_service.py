import os
import shutil
import sqlite3
from datetime import datetime
from paths import get_db_path, get_backup_dir

def has_data(db_path):
    """Checks if the database has any customer or transaction records."""
    if not os.path.exists(db_path):
        return False
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        cust_cnt = c.execute("SELECT count(*) FROM customers").fetchone()[0]
        tx_cnt = c.execute("SELECT count(*) FROM transactions").fetchone()[0]
        conn.close()
        return (cust_cnt > 0 or tx_cnt > 0)
    except Exception:
        return False

def get_backup_info(file_path):
    """Returns metadata about a database backup file."""
    if not os.path.exists(file_path):
        return {'size_kb': 0, 'customers': 0, 'transactions': 0, 'valid': False}
    try:
        size_kb = round(os.path.getsize(file_path) / 1024, 1)
        conn = sqlite3.connect(file_path)
        c = conn.cursor()
        cust_cnt = c.execute("SELECT count(*) FROM customers").fetchone()[0]
        tx_cnt = c.execute("SELECT count(*) FROM transactions").fetchone()[0]
        conn.close()
        return {
            'size_kb': size_kb,
            'customers': cust_cnt,
            'transactions': tx_cnt,
            'valid': True
        }
    except Exception as e:
        return {
            'size_kb': round(os.path.getsize(file_path) / 1024, 1) if os.path.exists(file_path) else 0,
            'customers': 0,
            'transactions': 0,
            'valid': False
        }

def create_backup():
    """Creates a backup of the current database."""
    db_path = get_db_path()
    if not os.path.exists(db_path):
        return False
        
    backup_dir = get_backup_dir()
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"alhamd_{timestamp}.db")
    
    try:
        shutil.copy2(db_path, backup_file)
        
        # Keep up to 30 backups, but never delete backups with data
        backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.db')])
        if len(backups) > 30:
            for old_backup in backups[:-30]:
                old_path = os.path.join(backup_dir, old_backup)
                info = get_backup_info(old_path)
                if info['customers'] == 0 and info['transactions'] == 0:
                    try:
                        os.remove(old_path)
                    except OSError:
                        pass
                
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False

def get_available_backups():
    """Returns a list of available backups with rich details."""
    backup_dir = get_backup_dir()
    if not os.path.exists(backup_dir):
        return []
    
    files = sorted([f for f in os.listdir(backup_dir) if f.endswith('.db')], reverse=True)
    results = []
    for f in files:
        fp = os.path.join(backup_dir, f)
        info = get_backup_info(fp)
        results.append({
            'filename': f,
            'path': fp,
            'size_kb': info['size_kb'],
            'customers': info['customers'],
            'transactions': info['transactions'],
            'valid': info['valid']
        })
    return results

def restore_backup(backup_path_or_filename):
    """
    Restores the database from a backup file (either filename in BACKUP_DIR or full path).
    Returns (success: bool, message: str).
    """
    backup_dir = get_backup_dir()
    db_path = get_db_path()
    
    if os.path.isabs(backup_path_or_filename):
        backup_file = backup_path_or_filename
    else:
        backup_file = os.path.join(backup_dir, backup_path_or_filename)

    if not os.path.exists(backup_file):
        return False, "Backup file does not exist."
        
    info = get_backup_info(backup_file)
    if not info['valid']:
        return False, "Selected file is not a valid SQLite database."
        
    try:
        # Only create a pre-restore backup if current DB actually has data
        if has_data(db_path):
            create_backup()
            
        shutil.copy2(backup_file, db_path)
        return True, f"Database restored successfully ({info['customers']} Customers, {info['transactions']} Transactions)."
    except Exception as e:
        print(f"Restore failed: {e}")
        return False, f"Restore failed: {e}"

