from .study_planner_config_helpers import (
    load_data, save_data
)
from .study_planner_ui_input import (
    clear_screen, box_title_only, box_top, box_title, box_sep, box_bottom,
    box_line, box_kv, BOX_INNER
)

# ============================================================================
# USER DASHBOARD
# ============================================================================

def view_user_dashboard(user_data=None):
    """
    View complete user dashboard.
    Name and mood are taken from the main app's user_data when available,
    falling back to planner storage otherwise.

    Shows:
    - Name
    - Subjects
    - Study goal
    - Current mood
    - Study minutes today
    - Last study date
    """
    clear_screen()
    planner_data = load_data()

    # Merge: prefer live user_data for name/mood
    if user_data:
        name = user_data.get("user_name") or user_data.get("name") or planner_data.get("user_name", "")
        mood = user_data.get("mood_today") or planner_data.get("mood_today", "")
    else:
        name = planner_data.get("user_name", "")
        mood = planner_data.get("mood_today", "")

    if not name:
        box_title_only("⚠️ ERROR")
        print()
        print("No profile found. Please log in through the main app.")
        input("\nPress Enter to continue...")
        return

    box_top()
    box_title("📊 USER DASHBOARD")
    box_sep()

    box_kv("Name", name)

    subjects_str = ", ".join(planner_data["subjects"]) if planner_data.get("subjects") else "Not set"
    box_kv("Subjects", subjects_str)

    goal_str = f"{planner_data['goal_hours']} hours" if planner_data.get("goal_hours", 0) > 0 else "Not set"
    box_kv("Today's Study Goal", goal_str)

    mood_str = mood if mood else "Not set"
    box_kv("Current Mood", mood_str)

    box_kv("Today's Actual Study", f"{planner_data.get('study_minutes_today', 0)} minutes")

    last_date = planner_data.get("last_study_date") or "N/A"
    box_kv("Last Study Date", last_date)

    box_bottom()
    input("\nPress Enter to continue...")