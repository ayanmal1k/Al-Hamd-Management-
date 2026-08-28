import os
import shutil
from datetime import datetime
from database import DB_PATH

BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'backups'))

def create_backup():
    """Creates a backup of the current database."""
    if not os.path.exists(DB_PATH):
        return False
        
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"alhamd_{timestamp}.db")
    
    try:
        shutil.copy2(DB_PATH, backup_file)
        
        # Keep only the last 10 backups
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')])
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                os.remove(os.path.join(BACKUP_DIR, old_backup))
                
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False

def get_available_backups():
    """Returns a list of available backups."""
    if not os.path.exists(BACKUP_DIR):
        return []
    
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')], reverse=True)
    return backups

def restore_backup(backup_filename):
    """Restores the database from a backup file."""
    backup_file = os.path.join(BACKUP_DIR, backup_filename)
    if not os.path.exists(backup_file):
        return False
        
    try:
        # Create a pre-restore backup just in case
        create_backup()
        shutil.copy2(backup_file, DB_PATH)
        return True
    except Exception as e:
        print(f"Restore failed: {e}")
        return False
