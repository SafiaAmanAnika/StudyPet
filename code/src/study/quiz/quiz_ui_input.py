from src.study.quiz.quiz_config_helpers import (
    BOX_INNER, manual_strip, manual_is_number, date_valid_simple, manual_len
)
from src.interface.ui import (
    clear_screen as shared_clear_screen,
    print_fancy_box,
)

# ============================================================================
# SCREEN & ERROR
# ============================================================================

def clear_screen():
    shared_clear_screen()


def _error_box(message):
    print_fancy_box("❌ Invalid Input", [message], theme="yellow")

# ============================================================================
# MANUAL LOWER
# ============================================================================

def manual_lower(s):
    result = ""
    for ch in s:
        if "A" <= ch <= "Z":
            result += chr(ord(ch) + 32)
        else:
            result += ch
    return result

# ============================================================================
# SUBJECT SUGGESTIONS
# ============================================================================

def _subject_suggestions(quiz_data):
    suggestions = []
    subjects_map = quiz_data.get("subjects", {}) if isinstance(quiz_data, dict) else {}
    if isinstance(subjects_map, dict):
        for subject in subjects_map.keys():
            text = manual_strip(str(subject))
            if text:
                suggestions.append(text)
    deduped = []
    seen = []
    for subject in suggestions:
        lower = manual_lower(subject)
        found = False
        for s in seen:
            if s == lower:
                found = True
                break
        if not found:
            seen.append(lower)
            deduped.append(subject)
    n = manual_len(deduped)
    for i in range(n):
        for j in range(0, n - i - 1):
            if manual_lower(deduped[j]) > manual_lower(deduped[j + 1]):
                deduped[j], deduped[j + 1] = deduped[j + 1], deduped[j]
    return deduped


def ask_subject(user_id, quiz_data):
    suggestions = _subject_suggestions(quiz_data)
    if not suggestions:
        return ask_title("Subject name: ")
    while True:
        lines = ["Pick from your existing subjects or enter a new one.", ""]
        for idx, subject in enumerate(suggestions, start=1):
            lines.append(f"[{idx}] {subject}")
        lines.append("[M] Enter new subject")
        lines.append("[B] Back")
        print_fancy_box("📚 Subject Picker", lines, theme="cyan")
        raw = manual_strip(input("Choose subject option: "))
        lowered = manual_lower(raw)
        if lowered in ("b", "back"):
            return None
        if lowered in ("m", "manual"):
            return ask_title("Subject name: ")
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= manual_len(suggestions):
                return suggestions[idx - 1]
        _error_box("Choose a listed number, M for new subject, or B to go back.")

# ============================================================================
# INPUT FUNCTIONS
# ============================================================================

def ask_title(prompt):
    while True:
        v = manual_strip(input(prompt))
        if v == "":
            _error_box("Title cannot be empty.")
            continue
        if "\n" in v or "\r" in v:
            _error_box("Invalid title.")
            continue
        has_letter = False
        for ch in v:
            if ch.isalpha():
                has_letter = True
                break
        if not has_letter:
            _error_box("Title must contain at least one letter (e.g., quiz1, mid 2).")
            continue
        valid = True
        for ch in v:
            if not (ch.isalpha() or ch.isdigit() or ch == " "):
                valid = False
                break
        if not valid:
            _error_box("Only letters, numbers, and spaces allowed.")
            continue
        if len(v) < 2:
            _error_box("Title must be at least 2 characters.")
            continue
        return v


def ask_float(prompt, min_v=None, max_v=None):
    while True:
        v = manual_strip(input(prompt))
        if not manual_is_number(v):
            _error_box("Enter a valid number.")
            continue
        num = float(v)
        if min_v is not None and num < min_v:
            _error_box(f"Value must be >= {min_v}")
            continue
        if max_v is not None and num > max_v:
            _error_box(f"Value must be <= {max_v}")
            continue
        return num


def ask_date(prompt):
    while True:
        v = manual_strip(input(prompt))
        if date_valid_simple(v):
            return v
        _error_box("Enter date as YYYY-MM-DD")