import json, os

# ============================================================================
# FILE I/O FOR STUDY PLANNER
# ============================================================================

def _project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


DATA_DIR = os.path.join(_project_root(), "data")
DATA_FILE = os.path.join(DATA_DIR, "study_planner.json")
LEGACY_USER_KEY = "__legacy__"
DEFAULT_USER_KEY = "__default__"


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def _manual_strip(s):
    start = 0
    end = len(s) - 1
    while start <= end and s[start] in " \t\n\r":
        start += 1
    while end >= start and s[end] in " \t\n\r":
        end -= 1
    return s[start:end+1]


def _clone_value(value):
    if isinstance(value, list):
        result = []
        for item in value:
            result.append(item)
        return result
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            result[k] = v
        return result
    return value


def _clone_payload(payload):
    cloned = {}
    for key, value in payload.items():
        cloned[key] = _clone_value(value)
    return cloned


def _is_planner_payload(data):
    if not isinstance(data, dict):
        return False
    marker_keys = [
        "subjects", "subject_difficulty", "subject_study_minutes",
        "goal_hours", "study_plan", "study_minutes_today",
    ]
    for key in marker_keys:
        if key in data:
            return True
    return False


def get_default_data():
    return {
        "user_name": "",
        "subjects": [],
        "subject_difficulty": {},
        "subject_study_minutes": {},
        "goal_hours": 0,
        "mood_today": "",
        "study_minutes_today": 0,
        "missed_goal": False,
        "shortfall_minutes": 0,
        "goal_recovery_increase": 0,
        "last_study_date": "",
        "study_plan": []
    }


def _normalize_payload(data, default_data):
    changed = False
    if not isinstance(data, dict):
        data = {}
        changed = True
    for key, default_value in default_data.items():
        if key not in data:
            data[key] = _clone_value(default_value)
            changed = True
    if not isinstance(data.get("subjects"), list):
        data["subjects"] = []
        changed = True
    if not isinstance(data.get("subject_difficulty"), dict):
        data["subject_difficulty"] = {}
        changed = True
    if not isinstance(data.get("subject_study_minutes"), dict):
        data["subject_study_minutes"] = {}
        changed = True
    if not isinstance(data.get("study_plan"), list):
        data["study_plan"] = []
        changed = True
    return data, changed


def _normalize_db(raw):
    changed = False
    if isinstance(raw, dict) and isinstance(raw.get("users"), dict):
        users = raw["users"]
    elif _is_planner_payload(raw):
        users = {LEGACY_USER_KEY: raw}
        changed = True
    elif isinstance(raw, dict):
        users = {}
        for key, value in raw.items():
            if _is_planner_payload(value):
                users[str(key)] = value
        if users:
            changed = True
    else:
        users = {}
        changed = True
    db = {"users": users}
    return db, changed


def _resolve_user_key(user_id):
    if user_id is None:
        return DEFAULT_USER_KEY
    user_key = _manual_strip(str(user_id))
    return user_key if user_key else DEFAULT_USER_KEY


def _read_db():
    ensure_data_dir()
    if not os.path.exists(DATA_FILE):
        return {"users": {}}, True
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return {"users": {}}, True
    db, changed = _normalize_db(raw)
    return db, changed


def _write_db(db):
    ensure_data_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)


def _pop_key(d, key):
    value = d[key]
    del d[key]
    return value


def load_data(user_id=None):
    default_data = get_default_data()
    db, changed = _read_db()
    users = db.get("users", {})
    if not isinstance(users, dict):
        users = {}
        db["users"] = users
        changed = True
    user_key = _resolve_user_key(user_id)
    if user_key not in users:
        if LEGACY_USER_KEY in users:
            users[user_key] = _pop_key(users, LEGACY_USER_KEY)
        else:
            users[user_key] = _clone_payload(default_data)
        changed = True
    payload, payload_changed = _normalize_payload(users.get(user_key), default_data)
    if payload_changed:
        users[user_key] = payload
        changed = True
    if changed:
        _write_db(db)
    return users[user_key]


def save_data(data, user_id=None):
    default_data = get_default_data()
    db, changed = _read_db()
    users = db.get("users", {})
    if not isinstance(users, dict):
        users = {}
        db["users"] = users
        changed = True
    user_key = _resolve_user_key(user_id)
    payload, _ = _normalize_payload(data, default_data)
    users[user_key] = payload
    _write_db(db)