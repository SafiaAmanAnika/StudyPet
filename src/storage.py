import json
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "users.json")

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