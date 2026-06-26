import json, os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "users.json")

def load_users() -> dict:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}

    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Warning: users.json is corrupted. Starting fresh.")
        return {}
    except Exception as e:
        print("Error loading users:", e)
        return {}

def save_users(users: dict) -> None:
    if not isinstance(users, dict):
        print("Error: users must be a dictionary.")
        return
    
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print("Error saving users:", e)


# =============== SHARED UTILITY FUNCTIONS =============== #

def _project_root():
    """Get the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _data_path(filename: str) -> str:
    """Get the full path to a file in the data directory."""
    return os.path.join(_project_root(), "data", filename)


def today_str() -> str:
    """Get today's date as a YYYY-MM-DD string."""
    today = datetime.now().date()
    return today.strftime("%Y-%m-%d")


def _safe_load_json(path: str, default):
    """Safely load JSON from file, returning default if file doesn't exist or is corrupted."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, OSError):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)
        return default


def _safe_save_json(path: str, data) -> None:
    """Safely save data to JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving to {path}: {e}")