import json, os, unicodedata
from datetime import datetime

# ---------------- PROJECT ROOT ----------------
def _project_root():
    """Return absolute path to project root (one level above src)"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# ============================================================================
# CONFIGURATION
# ============================================================================

BOX_INNER = 48
DATA_DIR = os.path.join(_project_root(), "data")
DATA_FILE = os.path.join(DATA_DIR, "study_planner.json")
LEGACY_USER_KEY = "__legacy__"
DEFAULT_USER_KEY = "__default__"

# ============================================================================
# TEXT WIDTH & FORMATTING
# ============================================================================

def visible_width(s):
    """Calculate visible width accounting for wide characters"""
    width = 0
    for ch in s:
        if unicodedata.east_asian_width(ch) in ("F", "W"):
            width += 2
        else:
            width += 1
    return width

def truncate_to_width(s, maxw):
    """Truncate string to maximum width"""
    if maxw <= 0:
        return ""
    return s[:maxw]

def pad_to_width(s, width):
    """Pad string with spaces to reach target width"""
    cur = visible_width(s)
    if cur >= width:
        return s
    return s + " " * (width - cur)

def wrap_text_to_width(s, maxw):
    """Wrap text to fit within maximum width"""
    if maxw <= 0:
        return [""]
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        if cur == "":
            if visible_width(w) <= maxw:
                cur = w
            else:
                i = 0
                while i < len(w):
                    part = w[i:i+maxw]
                    lines.append(part)
                    i += maxw
                cur = ""
        else:
            if visible_width(cur) + 1 + visible_width(w) <= maxw:
                cur = cur + " " + w
            else:
                lines.append(cur)
                if visible_width(w) <= maxw:
                    cur = w
                else:
                    i = 0
                    while i < len(w):
                        part = w[i:i+maxw]
                        lines.append(part)
                        i += maxw
                    cur = ""
    if cur != "":
        lines.append(cur)
    return [truncate_to_width(line, maxw) for line in lines]

# ============================================================================
# INPUT VALIDATION
# ============================================================================

def manual_strip(s):
    """Remove leading and trailing whitespace"""
    start = 0
    end = len(s) - 1
    while start <= end and s[start] in " \t\n\r":
        start += 1
    while end >= start and s[end] in " \t\n\r":
        end -= 1
    return s[start:end+1]

def manual_is_number(s):
    """Check if string is a valid number"""
    if s == "":
        return False
    parts = s.split(".")
    if len(parts) == 1:
        return parts[0].isdigit()
    if len(parts) == 2:
        a, b = parts
        return (a.isdigit() and b.isdigit() and b != "")
    return False

def is_only_letters(s):
    """Check if string contains only letters and spaces"""
    s = manual_strip(s)
    if s == "":
        return False
    for ch in s:
        if not (ch.isalpha() or ch == " "):
            return False
    return True

# ============================================================================
# LIST UTILITIES
# ============================================================================

def manual_len(lst):
    """Get list length without using len()"""
    count = 0
    for _ in lst:
        count += 1
    return count

def manual_sum(lst):
    """Sum list elements without using sum()"""
    total = 0
    for v in lst:
        total += v
    return total

# ============================================================================
# FILE I/O
# ============================================================================

def ensure_data_dir():
    """Create data directory if needed"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def _clone_value(value):
    if isinstance(value, list):
        return list(value)
    if isinstance(value, dict):
        return dict(value)
    return value


def _clone_payload(payload):
    cloned = {}
    for key, value in payload.items():
        cloned[key] = _clone_value(value)
    return cloned


def _is_planner_payload(data):
    if not isinstance(data, dict):
        return False
    marker_keys = {
        "subjects",
        "subject_difficulty",
        "subject_study_minutes",
        "goal_hours",
        "study_plan",
        "study_minutes_today",
    }
    for key in marker_keys:
        if key in data:
            return True
    return False

def get_default_data():
    """Return default data structure"""
    return {
        "user_name": "",
        "subjects": [],
        "subject_difficulty": {},
        "subject_study_minutes": {},
        "goal_hours": 0,
        "mood_today": "",
        "study_minutes_today": 0,
        "missed_goal": False,
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


def _resolve_user_key(user_id):
    if user_id is None:
        return DEFAULT_USER_KEY
    user_key = str(user_id).strip()
    return user_key if user_key else DEFAULT_USER_KEY


def load_data(user_id=None):
    """Load study planner data for a specific user."""
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
            users[user_key] = users.pop(LEGACY_USER_KEY)
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
    """Save study planner data for a specific user."""
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

# ============================================================================
# PROGRESS BAR
# ============================================================================

def print_progress_bar(percent, total_blocks=15):
    """Create visual progress bar string"""
    if percent > 0:
        filled = int(percent / 100 * total_blocks)
        filled = max(1, min(total_blocks, filled))
    else:
        filled = 0
    
    bar = "█" * filled + "░" * (total_blocks - filled)
    return f"[{bar}] {percent:.0f}%"