from .study_planner_config_helpers import load_data, save_data
from .study_planner_ui_input import (
    clear_screen, ask_float,
    ask_subjects_type, ask_single_subject_with_difficulty,
    ask_multiple_subjects_with_difficulty
)
from src.ui import print_fancy_box, pause

# ============================================================================
# STUDY PLAN GENERATION
# ============================================================================

def generate_study_plan(user_id=None, user_data=None):

    planner_data = load_data()

    if user_data:
        name = user_data.get("user_name") or user_data.get("name") or planner_data.get("user_name", "")
        mood = user_data.get("mood_today") or planner_data.get("mood_today", "Neutral")
    else:
        name = planner_data.get("user_name", "")
        mood = planner_data.get("mood_today", "Neutral")

    planner_data["user_name"] = name
    planner_data["mood_today"] = mood

    clear_screen()
    print_fancy_box(
        "📋 Subject Setup",
        ["Choose one or more subjects and set difficulty."],
        theme="cyan",
    )

    subject_type = ask_subjects_type()

    if subject_type == "single":
        subject, difficulty = ask_single_subject_with_difficulty()
        planner_data["subjects"] = [subject]
        planner_data["subject_difficulty"] = {subject: difficulty}
    else:
        subjects, subject_difficulty = ask_multiple_subjects_with_difficulty()
        planner_data["subjects"] = subjects
        planner_data["subject_difficulty"] = subject_difficulty

    # Initialize study minutes tracking
    planner_data["subject_study_minutes"] = {}
    for subject in planner_data["subjects"]:
        planner_data["subject_study_minutes"][subject] = 0

    # ---- ASK FOR STUDY DURATION ----
    clear_screen()
    print_fancy_box(
        "⏰ Set Study Duration",
        ["Enter how many hours you want to study today."],
        theme="blue",
    )

    while True:
        custom_goal = ask_float("How many hours do you want to study today? ", 0.5, 24.0)
        if custom_goal > 15.0:
            print_fancy_box(
                "Healthy Goal Reminder",
                ["Please aim for a healthy study goal (max 15 hours)."],
                theme="yellow",
            )
            continue
        break

    planner_data["goal_hours"] = custom_goal
    goal_recovery = planner_data.get("goal_recovery_increase", 0)
    total_minutes_goal = int((custom_goal + goal_recovery) * 60)

    subjects = planner_data.get("subjects", [])
    subject_difficulty = planner_data.get("subject_difficulty", {})

    # ---- MOOD-BASED MULTIPLIER ----
    if "Motivated" in mood:
        mood_multiplier, base_break = 1.2, 10
    elif "Tired" in mood:
        mood_multiplier, base_break = 0.7, 5
    elif "Stressed" in mood:
        mood_multiplier, base_break = 0.9, 8
    else:
        mood_multiplier, base_break = 1.0, 7

    # ---- SESSION DURATION BY DIFFICULTY ----
    difficulty_times = {"Easy": 25, "Medium": 35, "Hard": 50}

    study_plan = []
    minutes_used = 0
    session_num = 1
    net_study_goal = total_minutes_goal - 10

    # ---- GENERATE SESSIONS ----
    while minutes_used < net_study_goal:
        for subject in subjects:
            if minutes_used >= net_study_goal:
                break

            difficulty = subject_difficulty.get(subject, "Medium")
            base_duration = difficulty_times.get(difficulty, 35)
            duration = int(base_duration * mood_multiplier)
            duration = max(15, min(duration, 90))

            if minutes_used + duration > net_study_goal:
                duration = net_study_goal - minutes_used

            if duration > 0:
                study_plan.append({
                    "session": session_num,
                    "subject": subject,
                    "duration": duration,
                    "difficulty": difficulty,
                    "type": "study"
                })
                minutes_used += duration
                session_num += 1

            if minutes_used < net_study_goal:
                study_plan.append({
                    "session": session_num,
                    "subject": "Break",
                    "duration": base_break,
                    "type": "break"
                })
                session_num += 1

    # ---- ADD FINAL REVISION ----
    study_plan.append({
        "session": session_num,
        "subject": "Revision",
        "duration": 10,
        "type": "revision"
    })

    planner_data["study_plan"] = study_plan
    save_data(planner_data)

    clear_screen()
    print_fancy_box(
        "✅ Plan Generated",
        [f"Your plan is ready for {custom_goal} hours today."],
        theme="green",
    )
    pause()

# ============================================================================
# VIEW STUDY PLAN
# ============================================================================

def view_study_plan():
    """
    Display today's study plan showing:
    - All study sessions with difficulty
    - Break timings
    - Total study time, break time, sessions
    """
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

    study_plan = data["study_plan"]
    mood = data.get("mood_today", "Unknown")
    goal_hours = data.get("goal_hours", 0)

    lines = [
        f"Mood: {mood}",
        f"Today's Goal: {goal_hours} hours",
        "",
    ]

    total_study_minutes = 0
    total_break_minutes = 0
    session_count = 0

    for session in study_plan:
        if session["type"] == "study":
            difficulty = session.get("difficulty", "")
            difficulty_emoji = "🟢" if difficulty == "Easy" else "🟡" if difficulty == "Medium" else "🔴"
            info = f"{difficulty_emoji} {session['subject']}: {session['duration']} min ({difficulty})"
            lines.append(info)
            total_study_minutes += session["duration"]
            session_count += 1
        elif session["type"] == "break":
            lines.append(f"☕ Break: {session['duration']} min")
            total_break_minutes += session["duration"]
        elif session["type"] == "revision":
            lines.append(f"🔄 Revision: {session['duration']} min")
            total_study_minutes += session["duration"]

    total_hours = total_study_minutes / 60
    lines.extend(
        [
            "",
            f"Total Study Time: {total_study_minutes} min ({total_hours:.1f} hours)",
            f"Total Break Time: {total_break_minutes} min",
            f"Study Sessions: {session_count} sessions",
        ]
    )

    print_fancy_box("📅 Today's Study Plan", lines, theme="magenta")
    pause()