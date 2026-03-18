import json, os

# ============================================================================
# FILE I/O OPERATIONS
# ============================================================================

def _project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


DATA_DIR = os.path.join(_project_root(), "data")
DATA_FILE = os.path.join(DATA_DIR, "quiz_marks.json")
LEGACY_DATA_FILE = os.path.join(DATA_DIR, "study_log.json")
LEGACY_USER_KEY = "__legacy__"
DEFAULT_USER_KEY = "__default__"


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def _is_quiz_data(data):
    return isinstance(data, dict) and isinstance(data.get("subjects"), dict)


def _resolve_user_key(user_id):
    if user_id is None:
        return DEFAULT_USER_KEY
    key = str(user_id).strip()
    return key if key else DEFAULT_USER_KEY


def _normalize_quiz_payload(data):
    changed = False
    if not isinstance(data, dict):
        data = {"subjects": {}}
        changed = True
    subjects = data.get("subjects")
    if not isinstance(subjects, dict):
        subjects = {}
        data["subjects"] = subjects
        changed = True
    for subject, records in list(subjects.items()):
        if not isinstance(records, dict):
            subjects[subject] = {"quiz": [], "mid": []}
            changed = True
            continue
        if not isinstance(records.get("quiz"), list):
            records["quiz"] = []
            changed = True
        if not isinstance(records.get("mid"), list):
            records["mid"] = []
            changed = True
        # Preserve extra fields like target_grade
        for key, value in list(records.items()):
            if key not in ("quiz", "mid"):
                records[key] = value
    return data, changed


def _normalize_db(raw):
    changed = False
    if isinstance(raw, dict) and isinstance(raw.get("users"), dict):
        users = raw.get("users", {})
    elif _is_quiz_data(raw):
        users = {LEGACY_USER_KEY: raw}
        changed = True
    elif isinstance(raw, dict):
        users = {}
        for key, value in raw.items():
            if _is_quiz_data(value):
                users[str(key)] = value
        if users:
            changed = True
    else:
        users = {}
        changed = True
    db = {"users": users}
    for key in list(users.keys()):
        payload, payload_changed = _normalize_quiz_payload(users.get(key))
        if payload_changed:
            users[key] = payload
            changed = True
    return db, changed


def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_db(db):
    ensure_data_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)


def _read_db():
    ensure_data_dir()
    if os.path.exists(DATA_FILE):
        raw = _load_json(DATA_FILE)
        db, changed = _normalize_db(raw)
        return db, changed
    if os.path.exists(LEGACY_DATA_FILE):
        legacy = _load_json(LEGACY_DATA_FILE)
        if _is_quiz_data(legacy):
            return {"users": {LEGACY_USER_KEY: legacy}}, True
    return {"users": {}}, True


def load_data(user_id=None):
    db, changed = _read_db()
    users = db.get("users", {})
    if not isinstance(users, dict):
        users = {}
        db["users"] = users
        changed = True
    user_key = _resolve_user_key(user_id)
    if user_key not in users:
        if LEGACY_USER_KEY in users:
            users[user_key] = users.pop(LEGACY_USER_KEY)
        else:
            users[user_key] = {"subjects": {}}
        changed = True
    payload, payload_changed = _normalize_quiz_payload(users.get(user_key))
    if payload_changed:
        users[user_key] = payload
        changed = True
    if changed:
        _write_db(db)
    return users[user_key]


def save_data(data, user_id=None):
    db, changed = _read_db()
    users = db.get("users", {})
    if not isinstance(users, dict):
        users = {}
        db["users"] = users
        changed = True
    user_key = _resolve_user_key(user_id)
    payload, _ = _normalize_quiz_payload(data)
    users[user_key] = payload
    _write_db(db)