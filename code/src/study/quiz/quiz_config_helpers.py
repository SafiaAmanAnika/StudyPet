from src.study.quiz.quiz_text_helpers import (
    visible_width, truncate_to_width, pad_to_width, wrap_text_to_width
)
from src.study.quiz.quiz_file_io import (
    load_data, save_data, DATA_DIR, DATA_FILE,
    LEGACY_USER_KEY, DEFAULT_USER_KEY
)

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

BOX_INNER = 48
CHART_COL_W = 5
CHART_SPACING = 2
CHART_MAX_BARS = 6
CHART_HEIGHT = 6
CHART_LABELS_POS = "above"
CHART_SHOW_NUMBERS = True

# ============================================================================
# INPUT VALIDATION HELPERS
# ============================================================================

def manual_strip(s):
    start = 0
    end = len(s) - 1
    while start <= end and s[start] in " \t\n\r":
        start += 1
    while end >= start and s[end] in " \t\n\r":
        end -= 1
    return s[start:end+1]


def manual_is_number(s):
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
    year, month, day = int(y_str), int(m_str), int(d_str)
    if year <= 0 or month <= 0 or day <= 0 or month > 12:
        return False
    if month in [1, 3, 5, 7, 8, 10, 12]:
        max_days = 31
    elif month in [4, 6, 9, 11]:
        max_days = 30
    elif month == 2:
        max_days = 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28
    else:
        return False
    return day <= max_days

# ============================================================================
# LIST UTILITY FUNCTIONS
# ============================================================================

def manual_len(lst):
    count = 0
    for _ in lst:
        count += 1
    return count


def manual_sum(lst):
    total = 0
    for v in lst:
        total += v
    return total

# ============================================================================
# GRADE CALCULATION
# ============================================================================

def calculate_grade(percent):
    if percent >= 80: return "A+"
    if percent >= 75: return "A"
    if percent >= 70: return "A-"
    if percent >= 65: return "B+"
    if percent >= 60: return "B"
    if percent >= 50: return "C"
    if percent >= 40: return "D"
    return "F"


def print_progress_bar(percent, total_blocks=20, show_percent=False):
    filled = int(percent / 100 * total_blocks)
    filled = max(0, min(total_blocks, filled))
    bar = "█" * filled + "-" * (total_blocks - filled)
    return f"[{bar}] {percent:.1f}%" if show_percent else f"[{bar}]"