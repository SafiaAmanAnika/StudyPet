
from quiz_config_helpers import manual_strip
from quiz_ui_input import clear_screen, box_top, box_title, box_bottom, add_marks_menu
from quiz_analytics import (
    syllabus_coverage_tracker,
    result_overview_and_advisor,
    view_dashboard
)

def main():
    """Main menu and program loop"""
    while True:
        clear_screen()
        box_top()
        box_title("ACADEMIC PERFORMANCE TRACKER")
        box_bottom()
        
        print("[1] Add Marks")
        print("[2] Curriculum Progress Report")
        print("[3] Performance Trend Monitor")
        print("[4] View Dashboard")
        print("[0] Exit")
        
        choice = manual_strip(input("Choose: "))
        clear_screen()
        
        if choice == "1":
            add_marks_menu()
        elif choice == "2":
            syllabus_coverage_tracker()
        elif choice == "3":
            result_overview_and_advisor()
        elif choice == "4":
            view_dashboard()
        elif choice == "0":
            clear_screen()
            print("Goodbye!")
            break
        else:
            print("Invalid choice")
            input("Press Enter...")
        
        clear_screen()

