from datetime import datetime
from .study_planner_config_helpers import (
    load_data, save_data, manual_len, print_progress_bar, manual_max, manual_min
)
from .study_planner_ui_input import clear_screen, ask_float
from src.interface.ui import print_fancy_box, pause

# ============================================================================
# LOG STUDY SESSION
# ============================================================================

def log_study_session(user_id=None):
    clear_screen()
    data = load_data(user_id=user_id)

    if not data.get("study_plan"):
        clear_screen()
        print_fancy_box("⚠️ No Study Plan", ["No study plan generated yet."], theme="yellow")
        pause()
        return

    clear_screen()
    print_fancy_box("Today's Session", ["How many minutes did you study today?"], theme="cyan")
    total_minutes = ask_float("Total minutes: ", 0, 1440)

    if "subject_study_minutes" not in data:
        data["subject_study_minutes"] = {}
    for subject in data["subjects"]:
        if subject not in data["subject_study_minutes"]:
            data["subject_study_minutes"][subject] = 0

    if manual_len(data["subjects"]) == 1:
        subject = data["subjects"][0]
        data["subject_study_minutes"][subject] = int(total_minutes)
    else:
        clear_screen()
        print_fancy_box(
            "Subject Breakdown",
            [
                f"Total minutes studied: {int(total_minutes)} min",
                "Now enter minutes for each subject.",
                "(Last subject will be auto-calculated)",
            ],
            theme="blue",
        )
        subject_minutes = {}
        total_entered = 0
        subjects_list = data["subjects"]
        n_subjects = manual_len(subjects_list)
        
        for idx, subject in enumerate(subjects_list):
            print(f"[{idx + 1}] {subject}")
            
            if idx == n_subjects - 1:
                remaining_minutes = int(total_minutes) - total_entered
                subject_minutes[subject] = remaining_minutes
                print(f"Minutes for {subject}: {remaining_minutes} (auto-calculated)")
                print()
                continue
            
            while True:
                minutes = ask_float(f"Minutes for {subject}: ", 0, int(total_minutes - total_entered))
                if total_entered + minutes > total_minutes:
                    remaining = int(total_minutes - total_entered)
                    print_fancy_box("Minutes Exceeded", [f"You only have {remaining} minutes left."], theme="yellow")
                    continue
                subject_minutes[subject] = int(minutes)
                total_entered += int(minutes)
                break
        
        data["subject_study_minutes"] = subject_minutes

    data["study_minutes_today"] = int(total_minutes)
    data["last_study_date"] = str(datetime.now().date())
    goal_minutes = round(data.get("goal_hours", 0) * 60)
    clear_screen()

    if total_minutes < goal_minutes:
        shortfall = goal_minutes - int(total_minutes)
        data["missed_goal"] = True
        data["shortfall_minutes"] = shortfall
        
        lines = [
            f"Studied: {int(total_minutes)} min",
        ]
        
        # Add subject-wise breakdown only for multiple subjects
        if manual_len(data.get("subjects", [])) > 1:
            subject_minutes = data.get("subject_study_minutes", {})
            for subject, minutes in subject_minutes.items():
                lines.append(f"  ├─ {subject}: {minutes} min")
        
        lines.extend([
            f"Goal: {goal_minutes} min",
            f"Shortfall: {shortfall} min",
            "Don't worry! You can recover this tomorrow.",
        ])
        
        print_fancy_box(
            "⚠️ Goal Not Met",
            lines,
            theme="yellow",
        )
    else:
        data["missed_goal"] = False
        data["shortfall_minutes"] = 0
        
        lines = [
            f"Studied: {int(total_minutes)} min",
        ]
        
        # Add subject-wise breakdown only for multiple subjects
        if manual_len(data.get("subjects", [])) > 1:
            subject_minutes = data.get("subject_study_minutes", {})
            for subject, minutes in subject_minutes.items():
                lines.append(f"  ├─ {subject}: {minutes} min")
        
        lines.extend([
            f"Goal: {goal_minutes} min",
            "You met your goal! Great job! 🎉",
        ])
        
        print_fancy_box(
            "✅ Goal Met",
            lines,
            theme="green",
        )

    save_data(data, user_id=user_id)
    pause()

# ============================================================================
# VIEW PROGRESS DASHBOARD
# ============================================================================

def view_progress_dashboard(user_id=None):
    clear_screen()
    data = load_data(user_id=user_id)

    if not data["subjects"]:
        clear_screen()
        print_fancy_box("⚠️ Profile Required", ["Please set up your profile first."], theme="yellow")
        pause()
        return

    goal_hours = data.get("goal_hours", 0)
    goal_minutes = round(goal_hours * 60)
    study_minutes = data.get("study_minutes_today", 0)
    subject_minutes = data.get("subject_study_minutes", {})

    if goal_minutes > 0:
        progress_percentage = int(study_minutes / goal_minutes * 100)
    else:
        progress_percentage = 0
    if progress_percentage > 100:
        progress_percentage = 100

    # Extract planned minutes per subject from study plan
    planned_minutes = {}
    for subject in data["subjects"]:
        planned_minutes[subject] = 0
    for session in data.get("study_plan", []):
        if session.get("type") == "study":
            subject = session.get("subject", "")
            if subject in planned_minutes:
                planned_minutes[subject] += session.get("duration", 0)

    lines = ["📈 Overall Daily Progress", ""]
    lines.append(f"Progress: {print_progress_bar(progress_percentage)}")
    lines.append(f"Studied Today: {study_minutes} min")
    lines.append(f"Daily Goal: {goal_minutes} min")
    remaining = goal_minutes - study_minutes
    if remaining < 0:
        remaining = 0
    lines.append(f"Remaining: {remaining} min")
    lines.append("")
    lines.append("📚 Subject-wise (Planned vs Actual)")
    lines.append("")

    for subject in data["subjects"]:
        actual_minutes = subject_minutes.get(subject, 0)
        planned = planned_minutes.get(subject, 0)
        if planned > 0:
            subject_percentage = int(actual_minutes / planned * 100)
        else:
            subject_percentage = 0
        if subject_percentage > 100:
            subject_percentage = 100
        lines.append(f"{subject}: {print_progress_bar(subject_percentage)}")
        lines.append(f"↳ Planned: {planned} min | Actual: {actual_minutes} min")
        if actual_minutes >= planned:
            lines.append(f"↳ ✅ Completed! (+{actual_minutes - planned} min)")
        elif actual_minutes > 0:
            lines.append(f"↳ ⏳ In progress ({planned - actual_minutes} min left)")
        else:
            lines.append(f"↳ ❌ Not started")
        lines.append("")

    print_fancy_box("📊 Progress Dashboard", lines, theme="magenta")
    pause()