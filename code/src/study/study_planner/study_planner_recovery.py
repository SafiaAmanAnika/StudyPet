from .study_planner_config_helpers import load_data, save_data
from .study_planner_ui_input import clear_screen
from src.interface.ui import print_fancy_box, menu, pause

# ============================================================================
# SHORTFALL RECOVERY CHECK
# ============================================================================

def check_and_handle_shortfall(user_id=None, user_data=None):
    """
    Called before generating a new study plan.
    Returns: (should_generate, recovery_minutes)
    - recovery_minutes = None → fresh start (ask hours normally)
    - recovery_minutes = int → generate plan for that many minutes only
    """
    data = load_data(user_id=user_id)

    shortfall = data.get("shortfall_minutes", 0)
    if not data.get("missed_goal", False) or shortfall <= 0:
        return True, None

    shortfall_hours = shortfall / 60
    clear_screen()
    print_fancy_box(
        "⚠️ Yesterday's Shortfall",
        [
            f"You had a shortfall of {shortfall} min ({shortfall_hours:.1f} hours) yesterday.",
            "",
            "What would you like to do today?",
        ],
        theme="yellow",
    )

    choice = menu([
        f"Recover yesterday's shortfall ({shortfall} min)",
        "Start fresh today (set new hours)",
        "Back",
    ])

    if choice == 0:
        return False, None

    if choice == 1:
        data["shortfall_minutes"] = 0
        data["missed_goal"] = False
        save_data(data, user_id=user_id)
        clear_screen()
        print_fancy_box(
            "💪 Recovery Mode",
            [
                f"Generating a {shortfall} min recovery plan.",
                "Let's complete what you missed!",
            ],
            theme="cyan",
        )
        pause()
        return True, shortfall

    if choice == 2:
        data["shortfall_minutes"] = 0
        data["missed_goal"] = False
        save_data(data, user_id=user_id)
        return True, None

    return False, None

# ============================================================================
# MISSED GOAL RECOVERY MENU OPTION
# ============================================================================

def check_missed_goal_recovery(user_id=None):
    clear_screen()
    data = load_data(user_id=user_id)

    if data.get("missed_goal", False):
        shortfall = data.get("shortfall_minutes", 0)
        shortfall_hours = shortfall / 60
        print_fancy_box(
            "🔄 Missed Goal Recovery",
            [
                "You missed your goal today.",
                f"Shortfall: {shortfall} min ({shortfall_hours:.1f} hours)",
                "",
                "💪 Recovery Plan:",
                "Next time you generate a study plan,",
                "you can choose to recover this shortfall.",
                "",
                "📝 Tips:",
                "- Take breaks every 25 min",
                "- Study in a quiet place",
                "- Start with easier subjects",
                "- You can do this! 💪",
            ],
            theme="yellow",
        )
    else:
        print_fancy_box(
            "✅ You're On Track",
            ["Great job! Keep up the work!", "No recovery needed for today. 🎉"],
            theme="green",
        )

    save_data(data, user_id=user_id)
    pause()