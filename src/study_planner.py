from .study_planner_config_helpers import manual_strip
from .study_planner_ui_input import clear_screen, box_title_only
from .study_planner_profile import (
    setup_profile, view_profile, view_user_dashboard
)
from .study_planner_plan import (
    set_mood_and_generate_plan, view_study_plan
)
from .study_planner_progress import (
    log_study_session, view_progress_dashboard
)
from .study_planner_recovery import check_missed_goal_recovery

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """
    Main menu for Study Planner
    Options:
    1. Setup Profile
    2. View Profile
    3. Set Mood & Generate Plan
    4. View Today's Study Plan
    5. Log Study Session
    6. View Progress Dashboard
    7. Check Missed Goal Recovery
    8. View User Dashboard
    0. Exit
    """
    while True:
        clear_screen()
        box_title_only("📚 STUDY PLANNER")
        print()
        print("[1] Setup Profile")
        print("[2] View Profile")
        print("[3] Set Mood & Generate Plan")
        print("[4] View Today's Study Plan")
        print("[5] Log Study Session")
        print("[6] View Progress Dashboard")
        print("[7] Check Missed Goal Recovery")
        print("[8] View User Dashboard")
        print("[0] Exit")
        
        choice = manual_strip(input("\nChoose: "))
        
        if choice == "1":
            setup_profile()
        elif choice == "2":
            view_profile()
        elif choice == "3":
            set_mood_and_generate_plan()
        elif choice == "4":
            view_study_plan()
        elif choice == "5":
            log_study_session()
        elif choice == "6":
            view_progress_dashboard()
        elif choice == "7":
            check_missed_goal_recovery()
        elif choice == "8":
            view_user_dashboard()
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
            print("Please enter a valid option (0-8)")
            input("\nPress Enter to continue...")

# ============================================================================
# PROGRAM ENTRY POINT
# ============================================================================

def main():
    """Entry point for Study Planner program"""
    main_menu()