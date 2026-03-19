from .study_planner_config_helpers import manual_strip, is_only_letters, manual_len
from .study_planner_ui_input import clear_screen, ask_int, _error_box
from src.interface.ui import print_fancy_box, menu as ui_menu

# ============================================================================
# SUBJECT SELECTION
# ============================================================================

def ask_subjects_type():
    while True:
        clear_screen()
        print_fancy_box(
            "📚 Select Study Mode",
            ["Choose your study preference."],
            theme="cyan",
        )
        choice = ui_menu(["Single Subject", "Multiple Subjects", "Back"])
        if choice == 1:
            return "single"
        elif choice == 2:
            return "multiple"
        elif choice == 0:
            return "single"


def ask_single_subject_with_difficulty():
    clear_screen()
    print_fancy_box(
        "📚 Subject & Difficulty",
        ["Enter your subject and choose a difficulty."],
        theme="blue",
    )
    while True:
        subject = manual_strip(input("Enter subject name: "))
        if subject == "":
            _error_box("Subject name cannot be empty.")
            continue
        if not is_only_letters(subject):
            _error_box("Only letters are allowed.")
            continue
        if manual_len(subject) < 2:
            _error_box("Subject must have at least 2 characters.")
            continue
        break

    clear_screen()
    print_fancy_box(
        f"Difficulty For {subject}",
        [
            "Easy   -> 20-30 min sessions",
            "Medium -> 30-40 min sessions",
            "Hard   -> 45-60 min sessions",
        ],
        theme="yellow",
    )
    choice = ui_menu(["Easy", "Medium", "Hard", "Back"])
    if choice == 0:
        choice = 2
    difficulty = ["Easy", "Medium", "Hard"][choice - 1]
    return subject, difficulty


def ask_multiple_subjects_with_difficulty():
    clear_screen()
    print_fancy_box(
        "📚 Multiple Subjects Setup",
        ["Set each subject and its difficulty."],
        theme="blue",
    )
    num_subjects = ask_int("How many subjects do you want to study? ", 2, 10)
    subjects = []
    subject_difficulty = {}

    i = 1
    while i <= num_subjects:
        clear_screen()
        print_fancy_box(
            f"📚 Subject {i} of {num_subjects}",
            ["Enter the subject name."],
            theme="cyan",
        )
        while True:
            subject = manual_strip(input(f"Enter subject {i} name: "))
            found = False
            for s in subjects:
                if s == subject:
                    found = True
                    break
            if found:
                _error_box("Subject already added.")
                continue
            if subject == "":
                _error_box("Subject name cannot be empty.")
                continue
            if not is_only_letters(subject):
                _error_box("Only letters are allowed.")
                continue
            if manual_len(subject) < 2:
                _error_box("Subject must have at least 2 characters.")
                continue
            break

        clear_screen()
        print_fancy_box(
            f"Difficulty For {subject}",
            [
                "Easy   -> 20-30 min sessions",
                "Medium -> 30-40 min sessions",
                "Hard   -> 45-60 min sessions",
            ],
            theme="yellow",
        )
        choice = ui_menu(["Easy", "Medium", "Hard", "Back"])
        if choice == 0:
            choice = 2
        difficulty = ["Easy", "Medium", "Hard"][choice - 1]
        subjects.append(subject)
        subject_difficulty[subject] = difficulty
        i += 1

    return subjects, subject_difficulty