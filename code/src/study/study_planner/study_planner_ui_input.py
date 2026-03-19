from .study_planner_config_helpers import (
    manual_strip, manual_is_number, is_only_letters, manual_len
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


def _error_box(message: str):
    print_fancy_box("❌ Invalid Input", [message], theme="yellow")

# ============================================================================
# INPUT FUNCTIONS
# ============================================================================

def ask_name(prompt):
    while True:
        v = manual_strip(input(prompt))
        if v == "":
            _error_box("Name cannot be empty.")
            continue
        if not is_only_letters(v):
            _error_box("Name can only contain letters.")
            continue
        if manual_len(v) < 2:
            _error_box("Name must be at least 2 characters.")
            continue
        return v


def ask_float(prompt, min_v=None, max_v=None):
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