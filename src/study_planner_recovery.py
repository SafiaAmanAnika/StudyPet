"""
STUDY_PLANNER Module - Part 6: Missed Goal Recovery System
Lines: 150+
"""
from study_planner_config_helpers import load_data, save_data
from study_planner_ui_input import (
    clear_screen, box_top, box_title, box_sep, box_bottom, box_line, BOX_INNER, truncate_to_width
)

# ============================================================================
# MISSED GOAL RECOVERY
# ============================================================================

def check_missed_goal_recovery():
    """
    Check if goal was missed and provide recovery plan
    If goal missed: add 30 minutes recovery to tomorrow's goal
    If goal met: encourage to keep going
    """
    clear_screen()
    data = load_data()
    
    if data.get("missed_goal", False):
        # ---- GOAL WAS MISSED ----
        box_top()
        box_title("🔄 MISSED GOAL RECOVERY")
        box_sep()
        box_line(truncate_to_width("You missed your goal today!!!", BOX_INNER))
        box_sep()
        box_line(truncate_to_width("💪 RECOVERY PLAN:", BOX_INNER))
        box_line("")
        box_line(truncate_to_width("Tomorrow's goal +30 minutes", BOX_INNER))
        box_line("")
        box_sep()
        box_line(truncate_to_width("📝 Tips:", BOX_INNER))
        box_line(truncate_to_width("  • Take breaks every 25 min", BOX_INNER))
        box_line(truncate_to_width("  • Study in quiet place", BOX_INNER))
        box_line(truncate_to_width("  • Start with easier subjects", BOX_INNER))
        box_line(truncate_to_width("  • You can do this! 💪", BOX_INNER))
        box_sep()
        
        data["goal_recovery_increase"] = 0.5
    else:
        # ---- GOAL WAS MET ----
        box_top()
        box_title("✅ YOU'RE ON TRACK!")
        box_sep()
        box_line(truncate_to_width("Great job! Keep up the work!", BOX_INNER))
        box_line(truncate_to_width("No recovery needed for today. 🎉", BOX_INNER))
        box_sep()
        
        data["goal_recovery_increase"] = 0
    
    box_bottom()
    save_data(data)
    input("\nPress Enter to continue...")