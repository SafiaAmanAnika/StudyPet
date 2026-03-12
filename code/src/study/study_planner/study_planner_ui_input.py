import re
from .study_planner_config_helpers import (
    BOX_INNER, visible_width, truncate_to_width, pad_to_width,
    wrap_text_to_width, manual_strip, manual_is_number, is_only_letters
)
from src.interface.ui import (
    clear_screen as shared_clear_screen,
    print_fancy_box,
    menu as ui_menu,
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

# ============================================================================
# BOX DRAWING
# ============================================================================

EMOJI_PATTERN = re.compile(r"[\U0001F300-\U0001FAFF]")

def box_title_only(title):
    """Display title in box (top and bottom borders only)"""
    t = str(title)

    emoji_count = len(EMOJI_PATTERN.findall(t))

    # Only adjust when emoji count is odd
    extra = emoji_count % 2
    inner_width = BOX_INNER + extra

    print("╔" + "═" * inner_width + "╗")

    t = truncate_to_width(t, inner_width)
    left = max(0, (inner_width - visible_width(t)) // 2)
    right = max(0, inner_width - visible_width(t) - left)

    print("║ " + " " * left + t + " " * right + " ║")
    print("╚" + "═" * inner_width + "╝")


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

def box_empty_line():
    """Print empty line inside box"""
    print("║ " + " " * BOX_INNER + " ║")

def box_kv(key, value):
    """Print key-value pair inside box"""
    k = str(key)
    v = str(value)
    k_with_colon = k + ":"
    kw_colon = visible_width(k_with_colon)
    
    if kw_colon >= BOX_INNER - 5:
        ktr = truncate_to_width(k_with_colon, BOX_INNER - 2)
        print("║ " + pad_to_width(ktr, BOX_INNER) + " ║")
        wrapped = wrap_text_to_width(v, BOX_INNER - 2)
        for w in wrapped:
            padded = " " + pad_to_width(w, BOX_INNER - 2)
            print("║" + padded + " ║")
        return
    
    first_value_width = BOX_INNER - kw_colon - 2
    wrapped = wrap_text_to_width(v, first_value_width)
    
    if not wrapped:
        line = k_with_colon + " " * (BOX_INNER - kw_colon - 1)
        print("║ " + pad_to_width(line, BOX_INNER) + " ║")
        return
    
    first = wrapped[0]
    line = k_with_colon + " " + first
    print("║ " + pad_to_width(line, BOX_INNER) + " ║")
    
    for w in wrapped[1:]:
        pad_spaces = " " * (kw_colon + 1)
        line = pad_spaces + w
        print("║ " + pad_to_width(line, BOX_INNER) + " ║")

# ============================================================================
# INPUT FUNCTIONS
# ============================================================================

def ask_name(prompt):
    """Ask user for name with validation"""
    while True:
        v = manual_strip(input(prompt))
        if v == "":
            _error_box("Name cannot be empty.")
            continue
        if not is_only_letters(v):
            _error_box("Name can only contain letters.")
            continue
        if len(v) < 2:
            _error_box("Name must be at least 2 characters.")
            continue
        return v

def ask_float(prompt, min_v=None, max_v=None):
    """Ask user for float with validation"""
    while True:
        v = manual_strip(input(prompt))
        if not manual_is_number(v):
            _error_box("Please enter a valid number.")
            continue
        num = float(v)
        if min_v is not None and num < min_v:
            _error_box(f"Value must be >= {min_v}")
            continue
        if max_v is not None and num > max_v:
            _error_box(f"Value must be <= {max_v}")
            continue
        return num

def ask_int(prompt, min_v=None, max_v=None):
    """Ask user for integer with validation"""
    while True:
        v = manual_strip(input(prompt))
        if not v.isdigit():
            _error_box("Please enter a valid number.")
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
# SUBJECT SELECTION
# ============================================================================

def ask_subjects_type():
    """Ask user to choose single or multiple subjects"""
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
    """Get single subject and difficulty"""
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
        if len(subject) < 2:
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
    """Get multiple subjects and difficulties"""
    clear_screen()
    print_fancy_box(
        "📚 Multiple Subjects Setup",
        ["Set each subject and its difficulty."],
        theme="blue",
    )
    
    num_subjects = ask_int("How many subjects do you want to study? ", 2, 10)
    
    subjects = []
    subject_difficulty = {}
    
    for i in range(1, num_subjects + 1):
        clear_screen()
        print_fancy_box(
            f"📚 Subject {i} of {num_subjects}",
            ["Enter the subject name."],
            theme="cyan",
        )
        
        while True:
            subject = manual_strip(input(f"Enter subject {i} name: "))
            
            if subject in subjects:
                _error_box("Subject already added.")
                continue
            
            if subject == "":
                _error_box("Subject name cannot be empty.")
                continue
            
            if not is_only_letters(subject):
                _error_box("Only letters are allowed.")
                continue
            
            if len(subject) < 2:
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
    
    return subjects, subject_difficulty