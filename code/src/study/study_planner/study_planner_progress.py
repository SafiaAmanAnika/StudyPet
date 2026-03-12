from datetime import datetime
from .study_planner_config_helpers import (
    load_data, save_data, manual_len, print_progress_bar
)
from .study_planner_ui_input import (
    clear_screen, ask_float
)
from src.interface.ui import print_fancy_box, pause

# ============================================================================
# LOG STUDY SESSION
# ============================================================================

def log_study_session():

    clear_screen()
    data = load_data()
    
    if not data.get("study_plan"):
        clear_screen()
        print_fancy_box(
            "⚠️ No Study Plan",
            ["No study plan generated yet."],
            theme="yellow",
        )
        pause()
        return
    
    clear_screen()
    print_fancy_box(
        "Today's Session",
        ["How many minutes did you study today?"],
        theme="cyan",
    )
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
        print_fancy_box(
            "Subject Breakdown",
            [
                f"Total minutes studied: {int(total_minutes)} min",
                "Now enter minutes for each subject.",
            ],
            theme="blue",
        )
        
        subject_minutes = {}
        total_entered = 0
        
        for i, subject in enumerate(data["subjects"], 1):
            print(f"[{i}] {subject}")
            while True:
                minutes = ask_float(f"Minutes for {subject}: ", 0, int(total_minutes))
                if total_entered + minutes > total_minutes:
                    remaining = int(total_minutes - total_entered)
                    print_fancy_box(
                        "Minutes Exceeded",
                        [f"You only have {remaining} minutes left."],
                        theme="yellow",
                    )
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
        print_fancy_box(
            "⚠️ Goal Not Met",
            [
                f"Studied: {int(total_minutes)} min",
                f"Goal: {goal_minutes} min",
                f"Shortfall: {goal_minutes - int(total_minutes)} min",
                "Don't worry! Recovery plan is ready for tomorrow.",
            ],
            theme="yellow",
        )
    else:
        data["missed_goal"] = False
        print_fancy_box(
            "✅ Goal Met",
            [
                f"Studied: {int(total_minutes)} min",
                f"Goal: {goal_minutes} min",
                "You met your goal! Great job! 🎉",
            ],
            theme="green",
        )
    
    save_data(data)
    pause()

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
        print_fancy_box(
            "⚠️ Profile Required",
            ["Please set up your profile first."],
            theme="yellow",
        )
        pause()
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

    lines = ["📈 Overall Daily Progress", ""]
    bar = print_progress_bar(progress_percentage)
    lines.append(f"Progress: {bar}")
    lines.append(f"Studied Today: {study_minutes} min")
    lines.append(f"Daily Goal: {goal_minutes} min")
    lines.append(f"Remaining: {max(0, goal_minutes - study_minutes)} min")
    lines.append("")
    lines.append("📚 Subject-wise (Planned vs Actual)")
    lines.append("")
    
    for subject in data["subjects"]:
        actual_minutes = subject_minutes.get(subject, 0)
        planned = planned_minutes.get(subject, 0)
        
        # Calculate percentage for this subject
        subject_percentage = int((actual_minutes / planned * 100)) if planned > 0 else 0
        subject_percentage = min(subject_percentage, 100)
        
        sub_bar = print_progress_bar(subject_percentage)
        
        # Show subject name with percentage
        lines.append(f"{subject}: {sub_bar}")
        
        # Show comparison: Planned vs Actual
        comparison = f"Planned: {planned} min | Actual: {actual_minutes} min"
        lines.append(f"↳ {comparison}")
        
        # Show status
        if actual_minutes >= planned:
            status = f"✅ Completed! (+{actual_minutes - planned} min)"
        elif actual_minutes > 0:
            status = f"⏳ In progress ({planned - actual_minutes} min left)"
        else:
            status = f"❌ Not started"
        
        lines.append(f"↳ {status}")
        lines.append("")

    print_fancy_box("📊 Progress Dashboard", lines, theme="magenta")
    pause()