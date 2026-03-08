"""
STUDY_PLANNER Module - Part 4: Study Plan Generation
Lines: 200+
"""
from study_planner_config_helpers import (
    load_data, save_data, manual_len
)
from study_planner_ui_input import (
    clear_screen, box_title_only, box_top, box_title, box_sep, box_bottom,
    box_line, box_kv, ask_float, ask_int
)

# ============================================================================
# STUDY PLAN GENERATION
# ============================================================================

def generate_study_plan(user_data):
    """
    Generate personalized study plan based on:
    - Goal hours
    - User mood
    - Subject difficulty
    - Recovery increase (if missed goal yesterday)
    
    Creates sessions with appropriate duration and breaks
    """
    clear_screen()
    box_title_only("⏰ SET STUDY DURATION")
    
    while True:
        prompt = "How many hours do you want to study today? "
        custom_goal = ask_float(prompt, 0.5, 24.0)
        
        if custom_goal > 15.0:
            print("❌ That's too much! Please aim for a healthy study goal (Max 15h).")
            continue
        break
    
    user_data["goal_hours"] = custom_goal
    goal_recovery = user_data.get("goal_recovery_increase", 0)
    total_minutes_goal = int((custom_goal + goal_recovery) * 60)
    
    mood = user_data.get("mood_today", "Neutral")
    subjects = user_data.get("subjects", [])
    subject_difficulty = user_data.get("subject_difficulty", {})
    
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
    
    return study_plan

# ============================================================================
# SET MOOD AND GENERATE PLAN
# ============================================================================

def set_mood_and_generate_plan():
    """
    Prompt user to set mood and generate study plan
    Moods: Motivated, Neutral, Tired, Stressed
    """
    clear_screen()
    data = load_data()
    
    if not data["subjects"]:
        print("Please setup your profile first!")
        return
    
    moods = ["Motivated 🥳", "Neutral 😐", "Tired 😞", "Stressed 😰"]
    box_title_only("😊 SET YOUR MOOD")
    for i, mood in enumerate(moods, 1):
        print(f"[{i}] {mood}")
    
    choice = ask_int("\nChoose mood (1-4): ", 1, 4)
    data["mood_today"] = moods[choice - 1]
    
    study_plan = generate_study_plan(data)
    data["study_plan"] = study_plan
    save_data(data)
    
    goal_hours = data["goal_hours"]
    box_title_only(f"✅ PLAN GENERATED FOR {goal_hours} HOURS")
    input("\nPress Enter to continue...")

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
        box_title_only("⚠️ ERROR")
        print()
        print("No study plan generated yet!")
        input("\nPress Enter to continue...")
        return
    
    study_plan = data["study_plan"]
    mood = data.get("mood_today", "Unknown")
    goal_hours = data.get("goal_hours", 0)
    
    box_top()
    box_title("📅 TODAY'S STUDY PLAN")
    box_sep()
    box_kv("Mood", mood)
    box_kv("Today's Goal", f"{goal_hours} hours")
    box_sep()
    
    total_study_minutes = 0
    total_break_minutes = 0
    session_count = 0
    
    # ---- DISPLAY SESSIONS ----
    for session in study_plan:
        if session["type"] == "study":
            difficulty = session.get("difficulty", "")
            difficulty_emoji = "🟢" if difficulty == "Easy" else "🟡" if difficulty == "Medium" else "🔴"
            info = f"{difficulty_emoji} {session['subject']}: {session['duration']} min ({difficulty})"
            box_line(f"  {info}")
            total_study_minutes += session["duration"]
            session_count += 1
        elif session["type"] == "break":
            box_line(f"  ☕ Break: {session['duration']} min")
            total_break_minutes += session["duration"]
        elif session["type"] == "revision":
            box_line(f"  🔄 Revision: {session['duration']} min")
            total_study_minutes += session["duration"]
    
    # ---- SHOW TOTALS ----
    box_sep()
    total_hours = total_study_minutes / 60
    box_kv("Total Study Time", f"{total_study_minutes} min ({total_hours:.1f} hours)")
    box_kv("Total Break Time", f"{total_break_minutes} min")
    box_kv("Study Sessions", f"{session_count} sessions")
    box_bottom()
    input("\nPress Enter to continue...")