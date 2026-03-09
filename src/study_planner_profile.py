from .study_planner_config_helpers import (
    load_data, save_data
)
from .study_planner_ui_input import (
    clear_screen, box_title_only, box_top, box_title, box_sep, box_bottom,
    box_line, box_kv, ask_name, ask_subjects_type, ask_single_subject_with_difficulty,
    ask_multiple_subjects_with_difficulty, BOX_INNER
)

# ============================================================================
# PROFILE SETUP
# ============================================================================

def setup_profile():
    """
    Complete profile setup wizard
    Collects:
    - User name
    - Study mode (single/multiple subjects)
    - Subject(s) and difficulty levels
    """
    clear_screen()
    box_title_only("📋 PROFILE SETUP")
    
    data = load_data()
    
    print()
    data["user_name"] = ask_name("Enter your name: ")
    
    subject_type = ask_subjects_type()
    
    if subject_type == "single":
        # Single subject mode
        subject, difficulty = ask_single_subject_with_difficulty()
        data["subjects"] = [subject]
        data["subject_difficulty"] = {subject: difficulty}
    else:
        # Multiple subjects mode
        subjects, subject_difficulty = ask_multiple_subjects_with_difficulty()
        data["subjects"] = subjects
        data["subject_difficulty"] = subject_difficulty
    
    # Initialize study minutes tracking
    data["subject_study_minutes"] = {}
    for subject in data["subjects"]:
        data["subject_study_minutes"][subject] = 0
    
    save_data(data)
    
    clear_screen()
    box_title_only("✅ PROFILE SAVED")
    input("\nPress Enter to continue...")

# ============================================================================
# PROFILE VIEWING
# ============================================================================

def view_profile():
    """
    Display user profile with:
    - User name
    - Study subjects
    - Difficulty levels for each subject
    """
    clear_screen()
    data = load_data()
    
    if not data["user_name"]:
        box_title_only("⚠️ ERROR")
        print("\nNo profile setup yet!")
        input("\nPress Enter to continue...")
        return
    
    box_top()
    box_title("👤 YOUR PROFILE")
    box_sep()
    
    box_kv("Name", data["user_name"])
    box_sep()
    
    box_line("📚 Today's Study Topics:")
    box_line("")
    
    subjects_list = data.get("subjects", [])
    diff_map = data.get("subject_difficulty", {})
    
    if subjects_list:
        for i, s in enumerate(subjects_list, 1):
            difficulty = diff_map.get(s, "N/A")
            box_kv(f"  Subject {i}", s)
            box_kv(f"  Difficulty", difficulty)
            if i < len(subjects_list):
                box_line("  " + "-" * (BOX_INNER - 6))
    else:
        box_line("  No topics set yet.")
    
    box_bottom()
    input("\nPress Enter to continue...")

# ============================================================================
# USER DASHBOARD
# ============================================================================

def view_user_dashboard():
    """
    View complete user dashboard with:
    - Name
    - Subjects
    - Study goal
    - Current mood
    - Study minutes today
    - Last study date
    """
    clear_screen()
    data = load_data()
    
    if not data["user_name"]:
        box_title_only("⚠️ ERROR")
        print()
        print("No profile setup yet!")
        input("\nPress Enter to continue...")
        return
    
    box_top()
    box_title("📊 USER DASHBOARD")
    box_sep()
    
    box_kv("Name", data["user_name"])
    
    subjects_str = ", ".join(data["subjects"]) if data["subjects"] else "Not set"
    box_kv("Subjects", subjects_str)
    
    goal_str = f"{data['goal_hours']} hours" if data['goal_hours'] > 0 else "Not set"
    box_kv("Today's Study Goal", goal_str)
    
    mood_str = data["mood_today"] if data["mood_today"] else "Not set"
    box_kv("Current Mood", mood_str)
    
    box_kv("Today's Actual Study", f"{data['study_minutes_today']} minutes")
    
    last_date = data["last_study_date"] if data["last_study_date"] else "N/A"
    box_kv("Last Study Date", last_date)
    
    box_bottom()
    input("\nPress Enter to continue...")