from src.study.quiz.quiz_config_helpers import load_data, save_data
from src.study.quiz.quiz_ui_input import (
    clear_screen, ask_subject, ask_title, ask_float, ask_date, _error_box
)
from src.interface.ui import print_fancy_box, menu as ui_menu, pause

# ============================================================================
# SYLLABUS COVERAGE HELPER
# ============================================================================

def _calc_already_covered(subject_data):
    total = 0.0
    for q in subject_data.get("quiz", []):
        total += q.get("syllabus_coverage", q.get("syllabus", 0))
    for m in subject_data.get("mid", []):
        total += m.get("syllabus_coverage", m.get("syllabus", 0))
    return total

# ============================================================================
# ADD QUIZ MARKS
# ============================================================================

def add_quiz_marks(user_id=None):
    clear_screen()
    print_fancy_box("📝 Add Quiz Marks", ["Enter quiz details below."], theme="blue")
    data = load_data(user_id=user_id)
    subject = ask_subject(user_id, data)
    if subject is None:
        return
    existing_titles = [q.get("title", "") for q in data["subjects"].get(subject, {}).get("quiz", [])]
    while True:
        title = ask_title("Quiz title (e.g., quiz1): ")
        if title not in existing_titles:
            break
        _error_box(f"Quiz '{title}' already exists for {subject}. Use a different title.")
    total = ask_float("Total marks: ", 1)
    obtained = ask_float("Obtained marks: ", 0, total)
    subject_data = data["subjects"].get(subject, {"quiz": [], "mid": []})
    already_covered = _calc_already_covered(subject_data)
    remaining_syllabus = 100.0 - already_covered
    if remaining_syllabus <= 0:
        clear_screen()
        print_fancy_box("⚠️ Syllabus Fully Covered",
                        ["Your institute has already covered 100% of the syllabus."],
                        theme="yellow")
        pause()
        return
    print(f"\n{title} covered what % of your whole syllabus?")
    print(f"(already covered: {already_covered:.2f}%, remaining: {remaining_syllabus:.2f}%)")
    while True:
        syllabus_coverage = ask_float(f"Enter % (0 - {remaining_syllabus:.2f}): ", 0, 100)
        if syllabus_coverage > remaining_syllabus:
            _error_box(f"Cannot exceed {remaining_syllabus:.2f}%.")
            continue
        break
    print(f"\nYou personally completed what % of {title}? (0-100)")
    personal_coverage = ask_float("Enter %: ", 0, 100)
    date_str = ask_date("Date (YYYY-MM-DD): ")
    if subject not in data["subjects"]:
        data["subjects"][subject] = {"quiz": [], "mid": []}
    data["subjects"][subject]["quiz"].append({
        "title": title, "total": total, "obtained": obtained,
        "syllabus_coverage": syllabus_coverage,
        "personal_coverage": personal_coverage, "date": date_str
    })
    save_data(data, user_id=user_id)
    clear_screen()
    print_fancy_box("✅ Quiz Added", [f"{subject} - {title} added successfully."], theme="green")
    pause()

# ============================================================================
# ADD MID MARKS
# ============================================================================

def add_mid_marks(user_id=None):
    clear_screen()
    print_fancy_box("📝 Add Mid Marks", ["Enter mid exam details below."], theme="blue")
    data = load_data(user_id=user_id)
    subject = ask_subject(user_id, data)
    if subject is None:
        return
    existing_titles = [q.get("title", "") for q in data["subjects"].get(subject, {}).get("quiz", [])]
    while True:
        title = ask_title("Quiz title (e.g., quiz1): ")
        if title not in existing_titles:
            break
        _error_box(f"Quiz '{title}' already exists for {subject}. Use a different title.")
    total = ask_float("Total marks: ", 1)
    obtained = ask_float("Obtained marks: ", 0, total)
    subject_data = data["subjects"].get(subject, {"quiz": [], "mid": []})
    already_covered = _calc_already_covered(subject_data)
    remaining_syllabus = 100.0 - already_covered
    if remaining_syllabus <= 0:
        clear_screen()
        print_fancy_box("⚠️ Syllabus Fully Covered",
                        ["Your institute has already covered 100% of the syllabus."],
                        theme="yellow")
        pause()
        return
    print(f"\n{title} covered what % of your whole syllabus?")
    print(f"(already covered: {already_covered:.2f}%, remaining: {remaining_syllabus:.2f}%)")
    while True:
        syllabus_coverage = ask_float(f"Enter % (0 - {remaining_syllabus:.2f}): ", 0, 100)
        if syllabus_coverage > remaining_syllabus:
            _error_box(f"Cannot exceed {remaining_syllabus:.2f}%.")
            continue
        break
    print(f"\nYou personally completed what % of {title}? (0-100)")
    personal_coverage = ask_float("Enter %: ", 0, 100)
    date_str = ask_date("Date (YYYY-MM-DD): ")
    if subject not in data["subjects"]:
        data["subjects"][subject] = {"quiz": [], "mid": []}
    data["subjects"][subject]["mid"].append({
        "title": title, "total": total, "obtained": obtained,
        "syllabus_coverage": syllabus_coverage,
        "personal_coverage": personal_coverage, "date": date_str
    })
    save_data(data, user_id=user_id)
    clear_screen()
    print_fancy_box("✅ Mid Added", [f"{subject} - {title} added successfully."], theme="green")
    pause()

# ============================================================================
# ADD MARKS MENU
# ============================================================================

def add_marks_menu(user_id=None):
    while True:
        clear_screen()
        print_fancy_box("📝 Add Marks", ["Choose which exam type to record."], theme="cyan")
        c = ui_menu(["Add Quiz Marks", "Add Mid Marks", "Back"])
        if c == 1:
            add_quiz_marks(user_id=user_id)
        elif c == 2:
            add_mid_marks(user_id=user_id)
        elif c == 0:
            return