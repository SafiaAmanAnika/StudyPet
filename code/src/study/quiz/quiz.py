from src.study.quiz.quiz_ui_input import clear_screen, add_marks_menu
from src.study.quiz.quiz_analytics import (
    syllabus_coverage_tracker,
    result_overview_and_advisor,
    view_dashboard
)
from src.interface.ui import print_fancy_box, menu, pause

def main():
    """Main menu and program loop"""
    while True:
        clear_screen()
        print_fancy_box(
            "📊 Academic Performance Tracker",
            ["Track quiz/mid results, trends, and dashboard insights."],
            theme="cyan",
        )
        choice = menu(
            [
                "Add Marks",
                "Curriculum Progress Report",
                "Performance Trend Monitor",
                "View Dashboard",
                "Exit",
            ]
        )
        clear_screen()

        if choice == 1:
            add_marks_menu()
        elif choice == 2:
            syllabus_coverage_tracker()
        elif choice == 3:
            result_overview_and_advisor()
        elif choice == 4:
            view_dashboard()
        elif choice == 0:
            clear_screen()
            print_fancy_box("Goodbye 👋", ["Returning to StudyPet dashboard."], theme="green")
            pause()
            break

        clear_screen()


def run(user_id: str, user_data: dict) -> dict:
    main()
    return user_data

