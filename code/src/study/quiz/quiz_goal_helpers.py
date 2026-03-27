from src.study.quiz.quiz_config_helpers import manual_len, manual_strip
from src.study.quiz.quiz_ui_input import manual_lower, ask_float, _error_box
from src.interface.ui import print_fancy_box

GRADE_THRESHOLDS = [
    ("A+", 80), ("A", 75), ("A-", 70), ("B+", 65),
    ("B", 60), ("C", 50), ("D", 40), ("F", 0),
]

# ============================================================================
# GRADE HELPERS
# ============================================================================

def grade_min_percent(grade):
    for g, threshold in GRADE_THRESHOLDS:
        if g == grade:
            return threshold
    return 0


# ============================================================================
# INPUT HELPERS
# ============================================================================

def ask_int(prompt, min_v=None, max_v=None):
    while True:
        v = manual_strip(input(prompt))
        if not v.isdigit():
            _error_box("Enter a valid whole number.")
            continue
        num = int(v)
        if min_v is not None and num < min_v:
            _error_box(f"Value must be >= {min_v}")
            continue
        if max_v is not None and num > max_v:
            _error_box(f"Value must be <= {max_v}")
            continue
        return num


# ============================================================================
# MARKS DISTRIBUTION
# ============================================================================
def distribute_marks(required, slots, target_min_pct=80):
    result = []
    remaining_required = required
    n = manual_len(slots)
    
    only_one_exam_left = (n == 1)

    for i, (title, total) in enumerate(slots):
        slots_left = n - i
        if slots_left == 0:
            break

        target = remaining_required / slots_left
        target = min(target, total)
        target = max(target, 0)

        if only_one_exam_left:
            min_n = max(0, remaining_required)
            max_n = min(total, remaining_required)
        else:
            
            buffer = 2.0
            min_n = max(0, target - buffer)
            max_n = min(total, target + buffer)
            
            remaining_required -= target
        
        result.append((title, min_n, max_n, total))

    return result

# ============================================================================
# SUBJECT PICKER FOR GOAL
# ============================================================================

def pick_subject_for_goal(data):
    subject_list = [manual_strip(str(s)) for s in data.get("subjects", {}).keys()]
    if manual_len(subject_list) == 0:
        return None
    while True:
        lines = ["Pick a subject to set your goal.", ""]
        for idx, s in enumerate(subject_list, start=1):
            lines.append(f"[{idx}] {s}")
        lines.append("[B] Back")
        print_fancy_box("🎯 Subject Picker", lines, theme="cyan")
        raw = manual_strip(input("Choose: "))
        if manual_lower(raw) in ("b", "back"):
            return None
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= manual_len(subject_list):
                return subject_list[idx - 1]
        _error_box("Choose a listed number or B to go back.")