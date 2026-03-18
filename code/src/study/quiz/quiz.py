from src.study.quiz.quiz_ui_input import clear_screen
from src.study.quiz.quiz_ui_marks import add_marks_menu
from src.study.quiz.quiz_analytics import (
    syllabus_coverage_tracker,
    result_overview_and_advisor,
    view_dashboard,
    set_goal,
)
from src.interface.ui import print_fancy_box, menu, pause


def main(user_id=None):
    while True:
        clear_screen()
        print_fancy_box(
            "📊 Academic Performance Tracker",
            ["Track quiz/mid results, trends, and dashboard insights."],
            theme="cyan",
        )
        choice = menu([
            "Add Marks",
            "Set Your Target Grade",
            "Curriculum Progress Report",
            "Performance Trend Monitor",
            "View Dashboard",
            "Exit",
        ])
        clear_screen()

        if choice == 1:
            add_marks_menu(user_id=user_id)
        elif choice == 2:
            set_goal(user_id=user_id)
        elif choice == 3:
            syllabus_coverage_tracker(user_id=user_id)
        elif choice == 4:
            result_overview_and_advisor(user_id=user_id)
        elif choice == 5:
            view_dashboard(user_id=user_id)
        elif choice == 0:
            clear_screen()
            print_fancy_box("Goodbye 👋", ["Returning to StudyPet dashboard."], theme="green")
            pause()
            break

        clear_screen()


def run(user_id: str, user_data: dict) -> dict:
    main(user_id=user_id)
    return user_data