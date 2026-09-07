import sys
import os

def get_bundle_dir() -> str:
    """
    Returns the directory where bundled read-only resources live.
    In PyInstaller, this is sys._MEIPASS.
    In development, this is the project root directory.
    """
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    # Development mode: project root is parent of 'app' folder
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_app_dir() -> str:
    """
    Returns the writable application root directory where persistent user data lives.
    In PyInstaller, this is the directory containing the .exe.
    In development, this is the project root directory.
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_resource_path(relative_path: str) -> str:
    """
    Finds a bundled read-only resource file (e.g., styles.qss, icons, images).
    Tries multiple candidate paths to ensure it works in:
    - Normal Python execution (python app/main.py or python -m app.main)
    - PyInstaller onedir mode (_internal folder)
    - PyInstaller onefile mode (temp extraction folder)
    """
    bundle_dir = get_bundle_dir()
    app_dir = get_app_dir()
    this_dir = os.path.dirname(__file__)

    # Clean up relative path
    rel_clean = relative_path.replace('\\', '/').lstrip('/')
    
    # Generate candidate variations
    variations = [rel_clean]
    if rel_clean.startswith('app/'):
        variations.append(rel_clean[4:])
    else:
        variations.append(f'app/{rel_clean}')

    candidates = []
    for var in variations:
        candidates.append(os.path.join(bundle_dir, var))
        candidates.append(os.path.join(app_dir, var))
        candidates.append(os.path.join(this_dir, var))
        candidates.append(os.path.join(this_dir, '..', var))

    for path in candidates:
        norm = os.path.abspath(path)
        if os.path.exists(norm):
            return norm

    # Fallback to the first candidate if not found
    return os.path.abspath(candidates[0])

def get_asset_path(filename: str) -> str:
    """Convenience helper for finding assets in the assets directory."""
    return get_resource_path(os.path.join('assets', filename))

def get_data_dir() -> str:
    """Returns the persistent writable data directory."""
    data_dir = os.path.join(get_app_dir(), 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_db_path() -> str:
    """Returns the path to the SQLite database."""
    if os.environ.get('TESTING'):
        return os.path.join(get_data_dir(), 'test_alhamd.db')
    return os.path.join(get_data_dir(), 'alhamd.db')

def get_documents_dir() -> str:
    """Returns the path to the PDF documents directory."""
    doc_dir = os.path.join(get_data_dir(), 'documents')
    os.makedirs(doc_dir, exist_ok=True)
    return doc_dir

def get_backup_dir() -> str:
    """Returns the path to the database backups directory."""
    backup_dir = os.path.join(get_data_dir(), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir
