from .study_planner_config_helpers import manual_strip
from .study_planner_ui_input import clear_screen, box_title_only
from .study_planner_plan import (
    generate_study_plan, view_study_plan
)
from .study_planner_progress import (
    log_study_session, view_progress_dashboard
)
from .study_planner_recovery import check_missed_goal_recovery
from .study_planner_profile import view_user_dashboard

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu(user_id=None, user_data=None):

    while True:
        clear_screen()
        box_title_only("📚 STUDY PLANNER")
        print()
        print("[1] Generate Study Plan")
        print("[2] View Today's Study Plan")
        print("[3] Log Study Session")
        print("[4] View Progress Dashboard")
        print("[5] Check Missed Goal Recovery")
        print("[6] View User Dashboard")
        print("[0] Exit")

        choice = manual_strip(input("\nChoose: "))

        if choice == "1":
            generate_study_plan(user_id=user_id, user_data=user_data)
        elif choice == "2":
            view_study_plan()
        elif choice == "3":
            log_study_session()
        elif choice == "4":
            view_progress_dashboard()
        elif choice == "5":
            check_missed_goal_recovery()
        elif choice == "6":
            view_user_dashboard(user_data=user_data)
        elif choice == "0":
            clear_screen()
            box_title_only("Thank You!")
            print()
            print("Keep studying and stay motivated! 🎯")
            break
        else:
            clear_screen()
            box_title_only("⚠️ INVALID CHOICE")
            print()
            print("Please enter a valid option (0-6)")
            input("\nPress Enter to continue...")

# ============================================================================
# PROGRAM ENTRY POINT
# ============================================================================

def main():
    """Entry point for Study Planner program"""
    main_menu()