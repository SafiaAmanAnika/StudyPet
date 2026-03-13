from .study_planner_config_helpers import load_data, save_data
from .study_planner_ui_input import (
    clear_screen
)
from src.interface.ui import print_fancy_box, pause

# ============================================================================
# MISSED GOAL RECOVERY
# ============================================================================

def check_missed_goal_recovery(user_id=None):
    """
    Check if goal was missed and provide recovery plan
    If goal missed: add 30 minutes recovery to tomorrow's goal
    If goal met: encourage to keep going
    """
    clear_screen()
    data = load_data(user_id=user_id)
    
    if data.get("missed_goal", False):
        print_fancy_box(
            "🔄 Missed Goal Recovery",
            [
                "You missed your goal today.",
                "",
                "💪 Recovery Plan:",
                "Tomorrow's goal +30 minutes",
                "",
                "📝 Tips:",
                "- Take breaks every 25 min",
                "- Study in a quiet place",
                "- Start with easier subjects",
                "- You can do this! 💪",
            ],
            theme="yellow",
        )
        data["goal_recovery_increase"] = 0.5
    else:
        print_fancy_box(
            "✅ You're On Track",
            ["Great job! Keep up the work!", "No recovery needed for today. 🎉"],
            theme="green",
        )
        data["goal_recovery_increase"] = 0

    save_data(data, user_id=user_id)
    pause()