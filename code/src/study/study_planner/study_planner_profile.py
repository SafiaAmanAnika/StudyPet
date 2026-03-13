from .study_planner_config_helpers import load_data
from .study_planner_ui_input import (
    clear_screen
)
from src.interface.ui import print_fancy_box, pause

# ============================================================================
# USER DASHBOARD
# ============================================================================

def view_user_dashboard(user_id=None, user_data=None):

    clear_screen()
    planner_data = load_data(user_id=user_id)
    
    if user_data:
        name = user_data.get("user_name") or user_data.get("name") or planner_data.get("user_name", "")
        mood = user_data.get("mood_today") or planner_data.get("mood_today", "")
    else:
        name = planner_data.get("user_name", "")
        mood = planner_data.get("mood_today", "")

    if not name:
        print_fancy_box(
            "⚠️ Profile Not Found",
            ["No profile found. Please log in through the main app."],
            theme="yellow",
        )
        pause()
        return

    subjects_str = ", ".join(planner_data["subjects"]) if planner_data.get("subjects") else "Not set"
    goal_str = f"{planner_data['goal_hours']} hours" if planner_data.get("goal_hours", 0) > 0 else "Not set"
    mood_str = mood if mood else "Not set"
    last_date = planner_data.get("last_study_date") or "N/A"

    print_fancy_box(
        "📊 User Dashboard",
        [
            f"Name: {name}",
            f"Subjects: {subjects_str}",
            f"Today's Study Goal: {goal_str}",
            f"Current Mood: {mood_str}",
            f"Today's Actual Study: {planner_data.get('study_minutes_today', 0)} minutes",
            f"Last Study Date: {last_date}",
        ],
        theme="blue",
    )
    pause()