from .study_planner_config_helpers import load_data
from .study_planner_ui_input import clear_screen
from src.interface.ui import print_fancy_box, pause

# ============================================================================
# USER DASHBOARD
# ============================================================================

def _join_subjects(subjects):
    result = ""
    first = True
    for s in subjects:
        if first:
            result += s
            first = False
        else:
            result += ", " + s
    return result


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

    subjects_list = planner_data.get("subjects", [])
    subjects_str = _join_subjects(subjects_list) if subjects_list else "Not set"
    
    goal_hours = planner_data.get("goal_hours", 0)
    if goal_hours > 0:
        goal_minutes = round(goal_hours * 60)
        goal_str = f"{goal_hours} hours ({goal_minutes} minutes)"
    else:
        goal_str = "Not set"
    
    mood_str = mood if mood else "Not set"
    last_date = planner_data.get("last_study_date") or "N/A"
    shortfall = planner_data.get("shortfall_minutes", 0)

    lines = [
        f"Name: {name}",
        f"Subjects: {subjects_str}",
        f"Today's Study Goal: {goal_str}", 
        f"Current Mood: {mood_str}",
        f"Today's Actual Study: {planner_data.get('study_minutes_today', 0)} minutes",
        f"Last Study Date: {last_date}",
    ]

    if shortfall > 0:
        lines.append(f"⚠️ Shortfall from yesterday: {shortfall} min")

    print_fancy_box("📊 User Dashboard", lines, theme="blue")
    pause()