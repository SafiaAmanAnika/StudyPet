import json, os, unicodedata
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

BOX_INNER = 48
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "study_planner.json")

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

def load_data():
    """Load study planner data from JSON file"""
    ensure_data_dir()
    if not os.path.exists(DATA_FILE):
        default_data = get_default_data()
        save_data(default_data)
        return default_data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        default_data = get_default_data()
        save_data(default_data)
        return default_data

def save_data(data):
    """Save study planner data to JSON file"""
    ensure_data_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

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