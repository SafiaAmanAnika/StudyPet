import json, os

from src.study.quiz.quiz_config_helpers import (
    BOX_INNER, visible_width, truncate_to_width, pad_to_width, 
    wrap_text_to_width, manual_strip, manual_is_number, date_valid_simple,
    load_data, save_data
)
from src.interface.ui import (
    clear_screen as shared_clear_screen,
    print_fancy_box,
    menu as ui_menu,
    pause,
)

# ============================================================================
# SCREEN MANAGEMENT
# ============================================================================

def clear_screen():
    """Clear terminal screen"""
    shared_clear_screen()


def _error_box(message: str):
    print_fancy_box("❌ Invalid Input", [message], theme="yellow")

BORDER_FILL = "═" * (BOX_INNER + 2)


def _project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _data_path(filename: str):
    return os.path.join(_project_root(), "data", filename)


def _safe_load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (OSError, json.JSONDecodeError):
        return default


def _study_topics_for_user(user_id):
    if not user_id:
        return []

    logs = _safe_load_json(_data_path("study_log.json"), [])
    if not isinstance(logs, list):
        return []

    topics = []
    for row in logs:
        if not isinstance(row, dict):
            continue
        if row.get("user_id") != user_id:
            continue
        topic = str(row.get("topic", "")).strip()
        if topic:
            topics.append(topic)
    return topics


def _planner_topics_for_user(user_id):
    planner = _safe_load_json(_data_path("study_planner.json"), {})
    if not isinstance(planner, dict):
        return []

    payload = {}
    users = planner.get("users")
    if isinstance(users, dict) and user_id in users and isinstance(users.get(user_id), dict):
        payload = users.get(user_id)
    elif isinstance(planner.get("subjects"), list):
        payload = planner

    subjects = payload.get("subjects", []) if isinstance(payload, dict) else []
    if not isinstance(subjects, list):
        return []

    out = []
    for item in subjects:
        text = str(item).strip()
        if text:
            out.append(text)
    return out


def _subject_suggestions(user_id, quiz_data):
    suggestions = []

    subjects_map = quiz_data.get("subjects", {}) if isinstance(quiz_data, dict) else {}
    if isinstance(subjects_map, dict):
        for subject in subjects_map.keys():
            text = str(subject).strip()
            if text:
                suggestions.append(text)

    suggestions.extend(_study_topics_for_user(user_id))
    suggestions.extend(_planner_topics_for_user(user_id))

    deduped = []
    seen = set()
    for subject in suggestions:
        key = subject.casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(subject)

    deduped.sort(key=lambda item: item.casefold())
    return deduped


def ask_subject(user_id, quiz_data):
    suggestions = _subject_suggestions(user_id, quiz_data)

    if not suggestions:
        return ask_title("Subject name: ")

    while True:
        lines = [
            "Pick from studied/planned topics or enter custom.",
            "",
        ]

        for idx, subject in enumerate(suggestions, start=1):
            lines.append(f"[{idx}] {subject}")

        lines.append("[M] Enter custom subject")
        print_fancy_box("📚 Subject Picker", lines, theme="cyan")

        raw = manual_strip(input("Choose subject option: "))
        lowered = raw.lower()

        if lowered in {"m", "manual"}:
            return ask_title("Subject name: ")

        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(suggestions):
                return suggestions[idx - 1]

        _error_box("Choose a listed number or type M for manual subject.")

# ============================================================================
# BOX DRAWING FUNCTIONS
# ============================================================================

def box_top():
    """Print top border of box"""
    print("╔" + BORDER_FILL + "╗")

def box_title(title):
    """Print centered title inside box"""
    t = str(title)
    t = truncate_to_width(t, BOX_INNER)
    left = max(0, (BOX_INNER - visible_width(t)) // 2)
    right = max(0, BOX_INNER - visible_width(t) - left)
    print("║ " + " " * left + t + " " * right + " ║")

def box_sep():
    """Print separator line in box"""
    print("╠" + BORDER_FILL + "╣")

def box_bottom():
    """Print bottom border of box"""
    print("╚" + BORDER_FILL + "╝")

def box_line(text):
    """Print text line inside box"""
    s = str(text)
    s_trunc = truncate_to_width(s, BOX_INNER)
    s_pad = pad_to_width(s_trunc, BOX_INNER)
    print("║ " + s_pad + " ║")

def box_kv(key, value):
    """Print key-value pair inside box with automatic wrapping"""
    k = str(key)
    v = str(value)
    kw = visible_width(k)
    
    # If key is too long, put value on next line
    if kw >= BOX_INNER:
        ktr = truncate_to_width(k, BOX_INNER - 1)
        print("║ " + pad_to_width(ktr + " ", BOX_INNER) + " ║")
        wrapped = wrap_text_to_width(v, BOX_INNER)
        for w in wrapped:
            print("║ " + pad_to_width(w, BOX_INNER) + " ║")
        return
    
    # Key fits, try to fit value on same line
    first_value_width = BOX_INNER - kw - 1
    wrapped = wrap_text_to_width(v, first_value_width)
    
    if not wrapped:
        print("║ " + pad_to_width(k + " " * (BOX_INNER - kw), BOX_INNER) + " ║")
        return
    
    # Print key and first line of value
    first = wrapped[0]
    line = k + " " + first
    print("║ " + pad_to_width(line, BOX_INNER) + " ║")
    
    # Print remaining lines with proper indentation
    for w in wrapped[1:]:
        pad = " " * (kw + 1)
        line = pad + w
        print("║ " + pad_to_width(line, BOX_INNER) + " ║")

# ============================================================================
# INPUT FUNCTIONS WITH VALIDATION
# ============================================================================

def ask_title(prompt):
    """Ask user for title/subject name with validation"""
    while True:
        v = manual_strip(input(prompt))
        if v == "":
            _error_box("Enter a short title (e.g., quiz1).")
            continue
        if "\n" in v or "\r" in v:
            _error_box("Invalid title.")
            continue
        return v

def ask_float(prompt, min_v=None, max_v=None):
    """Ask user for floating point number with validation"""
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
    """Ask user for date in YYYY-MM-DD format"""
    while True:
        v = manual_strip(input(prompt))
        if date_valid_simple(v):
            return v
        _error_box("Enter date as YYYY-MM-DD")

# ============================================================================
# MARKS ENTRY FUNCTIONS
# ============================================================================

def add_quiz_marks(user_id=None):
    """Add quiz marks for a subject"""
    clear_screen()
    print_fancy_box(
        "📝 Add Quiz Marks",
        ["Enter quiz details below."],
        theme="blue",
    )
    
    data = load_data(user_id=user_id)
    
    subject = ask_subject(user_id, data)
    title = ask_title("Quiz title (e.g., quiz1): ")
    total = ask_float("Total marks: ", 1)
    obtained = ask_float("Obtained marks: ", 0, total)
    syllabus = ask_float("Syllabus covered in this exam (%): ", 0, 100)
    date_str = ask_date("Date (YYYY-MM-DD): ")
    
    if subject not in data["subjects"]:
        data["subjects"][subject] = {"quiz": [], "mid": []}
    
    data["subjects"][subject]["quiz"].append({
        "title": title,
        "total": total,
        "obtained": obtained,
        "syllabus": syllabus,
        "date": date_str
    })
    
    save_data(data, user_id=user_id)
    clear_screen()
    print_fancy_box("✅ Quiz Added", [f"{subject} - {title} saved successfully."], theme="green")
    pause()

def add_mid_marks(user_id=None):
    """Add mid exam marks for a subject"""
    clear_screen()
    print_fancy_box(
        "📝 Add Mid Marks",
        ["Enter mid exam details below."],
        theme="blue",
    )
    
    data = load_data(user_id=user_id)
    
    subject = ask_subject(user_id, data)
    title = ask_title("Mid title (e.g., mid1): ")
    total = ask_float("Total marks: ", 1)
    obtained = ask_float("Obtained marks: ", 0, total)
    syllabus = ask_float("Syllabus covered in this exam (%): ", 0, 100)
    date_str = ask_date("Date (YYYY-MM-DD): ")
    
    if subject not in data["subjects"]:
        data["subjects"][subject] = {"quiz": [], "mid": []}
    
    data["subjects"][subject]["mid"].append({
        "title": title,
        "total": total,
        "obtained": obtained,
        "syllabus": syllabus,
        "date": date_str
    })
    
    save_data(data, user_id=user_id)
    clear_screen()
    print_fancy_box("✅ Mid Added", [f"{subject} - {title} saved successfully."], theme="green")
    pause()

def add_marks_menu(user_id=None):
    """Menu for adding quiz or mid marks"""
    while True:
        clear_screen()
        print_fancy_box(
            "📝 Add Marks",
            ["Choose which exam type to record."],
            theme="cyan",
        )
        c = ui_menu(["Add Quiz Marks", "Add Mid Marks", "Back"])

        if c == 1:
            add_quiz_marks(user_id=user_id)
        elif c == 2:
            add_mid_marks(user_id=user_id)
        elif c == 0:
            return