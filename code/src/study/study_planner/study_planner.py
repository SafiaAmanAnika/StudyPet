from .study_planner_ui_input import clear_screen
from .study_planner_plan import generate_study_plan, view_study_plan
from .study_planner_progress import log_study_session, view_progress_dashboard
from .study_planner_recovery import check_missed_goal_recovery, check_and_handle_shortfall
from .study_planner_profile import view_user_dashboard
from src.interface.ui import print_fancy_box, menu, pause

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu(user_id=None, user_data=None):
    while True:
        clear_screen()
        print_fancy_box(
            "📚 Study Planner",
            ["Generate plans, log sessions, and monitor progress."],
            theme="cyan",
        )
        choice = menu([
            "Generate Study Plan",
            "View Today's Study Plan",
            "Log Study Session",
            "View Progress Dashboard",
            "Check Missed Goal Recovery",
            "View User Dashboard",
            "Exit",
        ])

        if choice == 1:
            should_generate, recovery_minutes = check_and_handle_shortfall(
                user_id=user_id, user_data=user_data
            )
            if should_generate:
                generate_study_plan(
                    user_id=user_id,
                    user_data=user_data,
                    recovery_minutes=recovery_minutes
                )
        elif choice == 2:
            view_study_plan(user_id=user_id)
        elif choice == 3:
            log_study_session(user_id=user_id)
        elif choice == 4:
            view_progress_dashboard(user_id=user_id)
        elif choice == 5:
            check_missed_goal_recovery(user_id=user_id)
        elif choice == 6:
            view_user_dashboard(user_id=user_id, user_data=user_data)
        elif choice == 0:
            clear_screen()
            print_fancy_box(
                "Thank You!",
                ["Keep studying and stay motivated! 🎯"],
                theme="green",
            )
            pause()
            break


def main():
    main_menu()