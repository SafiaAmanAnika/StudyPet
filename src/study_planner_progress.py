from datetime import datetime
from .study_planner_config_helpers import (
    load_data, save_data, manual_len, print_progress_bar, BOX_INNER, truncate_to_width
)
from .study_planner_ui_input import (
    clear_screen, box_title_only, box_top, box_title, box_sep, box_bottom,
    box_line, box_kv, ask_float
)

# ============================================================================
# LOG STUDY SESSION
# ============================================================================

def log_study_session():
    """
    Log study session and track minutes per subject
    Checks if goal was met and saves data
    """
    clear_screen()
    data = load_data()
    
    if not data.get("study_plan"):
        clear_screen()
        box_title_only("⚠️ ERROR")
        print()
        print("No study plan generated yet!")
        input("\nPress Enter to continue...")
        return
    
    clear_screen()
    box_title_only("📝 LOG YOUR STUDY SESSION")
    
    print()
    print("How many minutes did you study today?")
    print()
    total_minutes = ask_float("Total minutes: ", 0, 1440)
    
    # ---- INITIALIZE SUBJECT STUDY MINUTES ----
    if "subject_study_minutes" not in data:
        data["subject_study_minutes"] = {}
    
    for subject in data["subjects"]:
        if subject not in data["subject_study_minutes"]:
            data["subject_study_minutes"][subject] = 0
    
    # ---- HANDLE SINGLE VS MULTIPLE SUBJECTS ----
    if manual_len(data["subjects"]) == 1:
        # Single subject - just store the total
        subject = data["subjects"][0]
        data["subject_study_minutes"][subject] = int(total_minutes)
    else:
        # Multiple subjects - ask breakdown
        clear_screen()
        box_title_only("📚 STUDY BREAKDOWN BY SUBJECT")
        
        print()
        print(f"Total minutes studied: {int(total_minutes)} min")
        print("Now, how many minutes for each subject?")
        print()
        
        subject_minutes = {}
        total_entered = 0
        
        for i, subject in enumerate(data["subjects"], 1):
            print(f"[{i}] {subject}")
            while True:
                minutes = ask_float(f"Minutes for {subject}: ", 0, int(total_minutes))
                if total_entered + minutes > total_minutes:
                    remaining = int(total_minutes - total_entered)
                    print(f"❌ You only have {remaining} minutes left!")
                    continue
                subject_minutes[subject] = int(minutes)
                total_entered += int(minutes)
                break
        
        data["subject_study_minutes"] = subject_minutes
    
    # ---- UPDATE DATA ----
    data["study_minutes_today"] = int(total_minutes)
    data["last_study_date"] = str(datetime.now().date())
    
    # ---- CHECK IF GOAL MET ----
    goal_minutes = int(data.get("goal_hours", 0) * 60)
    
    clear_screen()
    
    if total_minutes < goal_minutes:
        data["missed_goal"] = True
        box_top()
        box_title("GOAL NOT MET!!!")
        box_sep()
        box_kv("Studied", f"{int(total_minutes)} min")
        box_kv("Goal", f"{goal_minutes} min")
        box_kv("Shortfall", f"{goal_minutes - int(total_minutes)} min")
        box_sep()
        box_line(truncate_to_width("Don't worry! Recovery plan ready tomorrow.", BOX_INNER))
        box_bottom()
    else:
        data["missed_goal"] = False
        box_top()
        box_title("✅ CONGRATULATIONS!")
        box_sep()
        box_kv("Studied", f"{int(total_minutes)} min")
        box_kv("Goal", f"{goal_minutes} min")
        box_line(truncate_to_width("You met your goal! Great job! 🎉", BOX_INNER))
        box_bottom()
    
    save_data(data)
    input("\nPress Enter to continue...")

# ============================================================================
# VIEW PROGRESS DASHBOARD
# ============================================================================

def view_progress_dashboard():
    """
    Display progress dashboard showing:
    - Overall daily progress
    - Subject-wise breakdown (planned vs actual)
    - Status indicators
    """
    clear_screen()
    data = load_data()
    
    if not data["subjects"]:
        clear_screen()
        box_title_only("⚠️ ERROR")
        print()
        print("Please setup your profile first!")
        input("\nPress Enter to continue...")
        return
    
    goal_hours = data.get("goal_hours", 0)
    goal_minutes = int(goal_hours * 60)
    study_minutes = data.get("study_minutes_today", 0)
    subject_minutes = data.get("subject_study_minutes", {})
    study_plan = data.get("study_plan", [])
    
    # ---- CALCULATE OVERALL PROGRESS ----
    progress_percentage = int((study_minutes / goal_minutes * 100)) if goal_minutes > 0 else 0
    progress_percentage = min(progress_percentage, 100)
    
    # ---- EXTRACT PLANNED MINUTES PER SUBJECT ----
    planned_minutes = {}
    for subject in data["subjects"]:
        planned_minutes[subject] = 0
    
    for session in study_plan:
        if session.get("type") == "study":
            subject = session.get("subject", "")
            if subject in planned_minutes:
                planned_minutes[subject] += session.get("duration", 0)
    
    box_top()
    box_title("📊 PROGRESS DASHBOARD")
    box_sep()
    
    # ---- OVERALL PROGRESS SECTION ----
    box_line(truncate_to_width("📈 OVERALL DAILY PROGRESS", BOX_INNER))
    box_line("")
    bar = print_progress_bar(progress_percentage)
    box_kv("Progress", bar)
    box_kv("Studied Today", f"{study_minutes} min")
    box_kv("Daily Goal", f"{goal_minutes} min")
    box_kv("Remaining", f"{max(0, goal_minutes - study_minutes)} min")
    box_sep()
    
    # ---- SUBJECT-WISE SECTION ----
    box_line(truncate_to_width("📚 SUBJECT-WISE (Planned vs Actual)", BOX_INNER))
    box_line("")
    
    for subject in data["subjects"]:
        actual_minutes = subject_minutes.get(subject, 0)
        planned = planned_minutes.get(subject, 0)
        
        # Calculate percentage for this subject
        subject_percentage = int((actual_minutes / planned * 100)) if planned > 0 else 0
        subject_percentage = min(subject_percentage, 100)
        
        sub_bar = print_progress_bar(subject_percentage)
        
        # Show subject name with percentage
        subject_line = f"  {subject}: {sub_bar}"
        box_line(truncate_to_width(subject_line, BOX_INNER))
        
        # Show comparison: Planned vs Actual
        comparison = f"Planned: {planned} min | Actual: {actual_minutes} min"
        comparison_line = f"    ↳ {comparison}"
        box_line(truncate_to_width(comparison_line, BOX_INNER))
        
        # Show status
        if actual_minutes >= planned:
            status = f"✅ Completed! (+{actual_minutes - planned} min)"
        elif actual_minutes > 0:
            status = f"⏳ In progress ({planned - actual_minutes} min left)"
        else:
            status = f"❌ Not started"
        
        status_line = f"    ↳ {status}"
        box_line(truncate_to_width(status_line, BOX_INNER))
        box_line("")
    
    box_sep()
    box_bottom()
    input("\nPress Enter to continue...")