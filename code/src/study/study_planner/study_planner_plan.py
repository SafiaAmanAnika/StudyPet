from .study_planner_config_helpers import load_data, manual_len, save_data, manual_max, manual_min
from .study_planner_ui_input import clear_screen, ask_float
from .study_planner_ui_subjects import (
    ask_subjects_type, ask_single_subject_with_difficulty,
    ask_multiple_subjects_with_difficulty
)
from src.interface.ui import print_fancy_box, pause

# ============================================================================
# PLAN GENERATION CORE
# ============================================================================

def _build_plan(total_minutes_goal, subjects, subject_difficulty, mood):
    if "Motivated" in mood:
        mood_multiplier, base_break = 1.2, 10
    elif "Happy" in mood:
        mood_multiplier, base_break = 1.1, 8
    elif "Neutral" in mood:
        mood_multiplier, base_break = 1.0, 7
    elif "Stressed" in mood:
        mood_multiplier, base_break = 0.9, 8
    elif "Tired" in mood:
        mood_multiplier, base_break = 0.7, 5
    else:
        mood_multiplier, base_break = 1.0, 7

    difficulty_times = {"Easy": 25, "Medium": 35, "Hard": 50}
    difficulty_weights = {"Easy": 1, "Medium": 2, "Hard": 3}

    available_minutes = total_minutes_goal

    # Calculate total weight
    total_weight = 0
    for subject in subjects:
        difficulty = subject_difficulty.get(subject, "Medium")
        total_weight += difficulty_weights.get(difficulty, 2)

    # Allocate minutes per subject based on weight
    subject_allocated = {}
    subjects_list = []
    for s in subjects:
        subjects_list.append(s)

    total_allocated = 0
    n = manual_len(subjects_list)
    idx = 0
    for subject in subjects_list:
        idx += 1
        if idx < n:
            difficulty = subject_difficulty.get(subject, "Medium")
            weight = difficulty_weights.get(difficulty, 2)
            allocated = int((weight / total_weight) * available_minutes)
            subject_allocated[subject] = allocated
            total_allocated += allocated
        else:
            # Last subject gets remaining minutes
            subject_allocated[subject] = available_minutes - total_allocated

    study_plan = []
    session_num = 1

    for subject in subjects:
        allocated = subject_allocated.get(subject, 0)
        used_for_subject = 0
        difficulty = subject_difficulty.get(subject, "Medium")
        base_duration = difficulty_times.get(difficulty, 35)
        duration = int(base_duration * mood_multiplier)
        duration = manual_max(15, manual_min(duration, 90))

        while used_for_subject < allocated:
            remaining = allocated - used_for_subject
            session_duration = manual_min(duration, remaining)
            if session_duration <= 0:
                break
            study_plan.append({
                "session": session_num, "subject": subject,
                "duration": session_duration, "difficulty": difficulty,
                "type": "study"
            })
            used_for_subject += session_duration
            session_num += 1

            if used_for_subject < allocated:
                study_plan.append({
                    "session": session_num, "subject": "Break",
                    "duration": base_break, "type": "break"
                })
                session_num += 1
                # Break between subjects
        study_plan.append({
            "session": session_num, "subject": "Break",
            "duration": base_break, "type": "break"
        })
        session_num += 1
 
 
    return study_plan

# ============================================================================
# GENERATE STUDY PLAN
# ============================================================================

def generate_study_plan(user_id=None, user_data=None, recovery_minutes=None):
    planner_data = load_data(user_id=user_id)

    if user_data:
        name = user_data.get("user_name") or user_data.get("name") or planner_data.get("user_name", "")
        mood = user_data.get("mood_today") or planner_data.get("mood_today", "Neutral")
    else:
        name = planner_data.get("user_name", "")
        mood = planner_data.get("mood_today", "Neutral")

    planner_data["user_name"] = name
    planner_data["mood_today"] = mood

    clear_screen()
    print_fancy_box("📋 Subject Setup", ["Choose one or more subjects and set difficulty."], theme="cyan")
    subject_type = ask_subjects_type()
    if subject_type == "single":
        subject, difficulty = ask_single_subject_with_difficulty()
        planner_data["subjects"] = [subject]
        planner_data["subject_difficulty"] = {subject: difficulty}
    else:
        subjects, subject_difficulty = ask_multiple_subjects_with_difficulty()
        planner_data["subjects"] = subjects
        planner_data["subject_difficulty"] = subject_difficulty

    planner_data["subject_study_minutes"] = {}
    for subject in planner_data["subjects"]:
        planner_data["subject_study_minutes"][subject] = 0

    if recovery_minutes is not None:
        total_minutes_goal = recovery_minutes
        custom_goal = round(recovery_minutes / 60, 2)
    else:
        clear_screen()
        print_fancy_box("⏰ Set Study Duration", ["Enter how many hours you want to study today."], theme="blue")
        while True:
            custom_goal = ask_float("How many hours do you want to study today? ", 0.5, 24.0)
            if custom_goal > 15.0:
                print_fancy_box("Healthy Goal Reminder", ["Please aim for a healthy study goal (max 15 hours)."], theme="yellow")
                continue
            break
        total_minutes_goal = int(custom_goal * 60)

    planner_data["goal_hours"] = custom_goal
    planner_data["shortfall_minutes"] = 0

    subjects = planner_data.get("subjects", [])
    subject_difficulty = planner_data.get("subject_difficulty", {})
    study_plan = _build_plan(total_minutes_goal, subjects, subject_difficulty, mood)
    planner_data["study_plan"] = study_plan
    save_data(planner_data, user_id=user_id)

    clear_screen()
    if recovery_minutes is not None:
        goal_minutes = int(custom_goal * 60)
        label = f"{custom_goal} hours ({goal_minutes} minutes) for recovery"
    else:
        goal_minutes = int(custom_goal * 60)
        label = f"{custom_goal} hours ({goal_minutes} minutes)"
    print_fancy_box("✅ Plan Generated", [f"Your plan is ready for {label} today."], theme="green")
    pause()

# ============================================================================
# VIEW STUDY PLAN
# ============================================================================

def view_study_plan(user_id=None):
    clear_screen()
    data = load_data(user_id=user_id)
    if not data.get("study_plan"):
        clear_screen()
        print_fancy_box("⚠️ No Study Plan", ["No study plan generated yet."], theme="yellow")
        pause()
        return

    study_plan = data["study_plan"]
    mood = data.get("mood_today", "Unknown")
    goal_hours = data.get("goal_hours", 0)
    goal_minutes = int(goal_hours * 60)
    lines = [f"Mood: {mood}", f"Today's Goal: {goal_hours} hours ({goal_minutes} minutes)", ""]

    total_study_minutes = 0
    total_break_minutes = 0
    session_count = 0

    for session in study_plan:
        if session["type"] == "study":
            difficulty = session.get("difficulty", "")
            if difficulty == "Easy":
                emoji = "🟢"
            elif difficulty == "Medium":
                emoji = "🟡"
            else:
                emoji = "🔴"
            lines.append(f"{emoji} {session['subject']}: {session['duration']} min ({difficulty})")
            total_study_minutes += session["duration"]
            session_count += 1
        elif session["type"] == "break":
            lines.append(f"☕ Break: {session['duration']} min")
            total_break_minutes += session["duration"]

    total_hours = total_study_minutes / 60
    lines.append("")
    lines.append(f"Total Study Time: {total_study_minutes} min ({total_hours:.2f} hours)")
    lines.append(f"Total Break Time: {total_break_minutes} min")
    lines.append(f"Study Sessions: {session_count} sessions")
    print_fancy_box("📅 Today's Study Plan", lines, theme="magenta")
    pause()