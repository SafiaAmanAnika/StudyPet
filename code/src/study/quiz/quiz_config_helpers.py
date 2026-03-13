import json, os, unicodedata

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

BOX_INNER = 48   
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "quiz_marks.json")
LEGACY_DATA_FILE = os.path.join(DATA_DIR, "study_log.json")
LEGACY_USER_KEY = "__legacy__"
DEFAULT_USER_KEY = "__default__"

CHART_COL_W = 5
CHART_SPACING = 2
CHART_MAX_BARS = 6
CHART_HEIGHT = 6
CHART_LABELS_POS = "above"
CHART_SHOW_NUMBERS = True

# ============================================================================
# TEXT FORMATTING & WIDTH HELPERS
# ============================================================================

def visible_width(s):
    """Calculate visible width of string considering wide characters (CJK)"""
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
    """Wrap text to fit within maximum width, respecting word boundaries"""
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
# INPUT VALIDATION HELPERS
# ============================================================================

def manual_strip(s):
    """Remove leading and trailing whitespace without using strip()"""
    start = 0
    end = len(s) - 1
    while start <= end and s[start] in " \t\n\r":
        start += 1
    while end >= start and s[end] in " \t\n\r":
        end -= 1
    return s[start:end+1]

def manual_is_number(s):
    """Check if string is a valid number (integer or float)"""
    if s == "":
        return False
    parts = s.split(".")
    if len(parts) == 1:
        return parts[0].isdigit()
    if len(parts) == 2:
        a, b = parts
        return (a.isdigit() and b.isdigit() and b != "")
    return False

def date_valid_simple(s):
    """Validate date format YYYY-MM-DD and check calendar constraints."""
    parts = s.split("-")
    if len(parts) != 3:
        return False
    
    y_str, m_str, d_str = parts

    if not (y_str.isdigit() and len(y_str) == 4):
        return False
    if not (m_str.isdigit() and 1 <= len(m_str) <= 2):
        return False
    if not (d_str.isdigit() and 1 <= len(d_str) <= 2):
        return False

    year = int(y_str)
    month = int(m_str)
    day = int(d_str)

    if year <= 0 or month <= 0 or day <= 0:
        return False
    
    if month > 12:
        return False

    if month in [1, 3, 5, 7, 8, 10, 12]:
        max_days = 31
    elif month in [4, 6, 9, 11]:
        max_days = 30
    elif month == 2:
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            max_days = 29
        else:
            max_days = 28
    else:
        return False

    if day > max_days:
        return False

    return True

# ============================================================================
# LIST UTILITY FUNCTIONS
# ============================================================================

def manual_len(lst):
    """Get length of list without using len() builtin"""
    count = 0
    for _ in lst:
        count += 1
    return count

def manual_sum(lst):
    """Sum list elements without using sum() builtin"""
    total = 0
    for v in lst:
        total += v
    return total

# ============================================================================
# FILE I/O OPERATIONS
# ============================================================================

def ensure_data_dir():
    """Create data directory if it doesn't exist"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def _is_quiz_data(data):
    """Validate expected quiz data shape."""
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
    """Load JSON from path and return None on failure."""
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
            db = {"users": {LEGACY_USER_KEY: legacy}}
            return db, True

    return {"users": {}}, True


def load_data(user_id=None):
    """Load quiz/performance tracker data for a specific user."""
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
    """Save quiz/performance tracker data for a specific user."""
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

# ============================================================================
# GRADE CALCULATION
# ============================================================================

def calculate_grade(percent):
    """
    Convert percentage to letter grade
    A+ >= 80, A >= 75, A- >= 70, B+ >= 65, B >= 60, C >= 50, D >= 40, F < 40
    """
    if percent >= 80:
        return "A+"
    if percent >= 75:
        return "A"
    if percent >= 70:
        return "A-"
    if percent >= 65:
        return "B+"
    if percent >= 60:
        return "B"
    if percent >= 50:
        return "C"
    if percent >= 40:
        return "D"
    return "F"

def print_progress_bar(percent, total_blocks=20, show_percent=False):
    """Create visual progress bar with blocks"""
    filled = int(percent / 100 * total_blocks)
    filled = max(0, min(total_blocks, filled))
    bar = "█" * filled + "-" * (total_blocks - filled)
    return f"[{bar}] {percent:.1f}%" if show_percent else f"[{bar}]"