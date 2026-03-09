from src.study.quiz.quiz_config_helpers import (
    BOX_INNER, visible_width, truncate_to_width, pad_to_width, 
    wrap_text_to_width, manual_strip, manual_is_number, date_valid_simple,
    load_data, save_data
)
import os

# ============================================================================
# SCREEN MANAGEMENT
# ============================================================================

def clear_screen():
    """Clear terminal screen"""
    try:
        if os.name == "nt":
            os.system("cls")
        else:
            print("\033[2J\033[H", end="")
    except Exception:
        print("\n" * 60)

BORDER_FILL = "═" * (BOX_INNER + 2)

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
            print("Enter a short title (e.g., quiz1).")
            continue
        if "\n" in v or "\r" in v:
            print("Invalid title.")
            continue
        return v

def ask_float(prompt, min_v=None, max_v=None):
    """Ask user for floating point number with validation"""
    while True:
        v = manual_strip(input(prompt))
        if not manual_is_number(v):
            print("Enter a valid number.")
            continue
        num = float(v)
        if min_v is not None and num < min_v:
            print(f"Value must be >= {min_v}")
            continue
        if max_v is not None and num > max_v:
            print(f"Value must be <= {max_v}")
            continue
        return num

def ask_date(prompt):
    """Ask user for date in YYYY-MM-DD format"""
    while True:
        v = manual_strip(input(prompt))
        if date_valid_simple(v):
            return v
        print("Enter date as YYYY-MM-DD")

# ============================================================================
# MARKS ENTRY FUNCTIONS
# ============================================================================

def add_quiz_marks():
    """Add quiz marks for a subject"""
    clear_screen()
    box_top()
    box_title("ADD QUIZ MARKS")
    box_bottom()
    
    data = load_data()
    
    subject = ask_title("Subject name: ")
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
    
    save_data(data)
    print("\n✅ Quiz added.")
    input("Press Enter...")

def add_mid_marks():
    """Add mid exam marks for a subject"""
    clear_screen()
    box_top()
    box_title("ADD MID MARKS")
    box_bottom()
    
    data = load_data()
    
    subject = ask_title("Subject name: ")
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
    
    save_data(data)
    print("\n✅ Mid added.")
    input("Press Enter...")

def add_marks_menu():
    """Menu for adding quiz or mid marks"""
    while True:
        clear_screen()
        box_top()
        box_title("ADD MARKS")
        box_bottom()
        
        print("[1] Add Quiz Marks")
        print("[2] Add Mid Marks")
        print("[0] Back")
        
        c = manual_strip(input("Choose: "))
        
        if c == "1":
            add_quiz_marks()
        elif c == "2":
            add_mid_marks()
        elif c == "0":
            return
        else:
            print("Invalid choice")
            input("Press Enter...")