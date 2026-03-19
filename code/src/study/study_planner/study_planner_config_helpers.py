from src.study.study_planner.study_planner_text_helpers import (
    visible_width, truncate_to_width, pad_to_width, wrap_text_to_width
)
from src.study.study_planner.study_planner_file_io import (
    load_data, save_data, get_default_data,
    DATA_DIR, DATA_FILE, LEGACY_USER_KEY, DEFAULT_USER_KEY
)

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

BOX_INNER = 48

# ============================================================================
# INPUT VALIDATION
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
    count = 0
    for _ in parts:
        count += 1
    if count == 1:
        return parts[0].isdigit()
    if count == 2:
        a, b = parts[0], parts[1]
        return (a.isdigit() and b.isdigit() and b != "")
    return False


def is_only_letters(s):
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
    count = 0
    for _ in lst:
        count += 1
    return count


def manual_sum(lst):
    total = 0
    for v in lst:
        total += v
    return total


def manual_max(a, b):
    return a if a >= b else b


def manual_min(a, b):
    return a if a <= b else b

# ============================================================================
# PROGRESS BAR
# ============================================================================

def print_progress_bar(percent, total_blocks=15):
    if percent > 0:
        filled = int(percent / 100 * total_blocks)
        if filled < 1:
            filled = 1
        if filled > total_blocks:
            filled = total_blocks
    else:
        filled = 0
    bar = "█" * filled + "░" * (total_blocks - filled)
    return f"[{bar}] {percent:.0f}%"