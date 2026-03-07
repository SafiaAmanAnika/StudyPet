import json
import os
import unicodedata
from datetime import datetime

BOX_INNER = 48
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "study_planner.json")

# -------- Minimal helpers --------
def visible_width(s):
    width = 0
    for ch in s:
        if unicodedata.east_asian_width(ch) in ("F", "W"):
            width += 2
        else:
            width += 1
    return width

def truncate_to_width(s, maxw):
    if maxw <= 0:
        return ""
    return s[:maxw]

def pad_to_width(s, width):
    cur = visible_width(s)
    if cur >= width:
        return s
    return s + " " * (width - cur)

def wrap_text_to_width(s, maxw):
    if maxw <= 0:
        return [""]
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        if cur == "":
            if visible_width(w) <= maxw:
                cur = w
            else:
                i = 0
                while i < len(w):
                    part = w[i:i+maxw]
                    lines.append(part)
                    i += maxw
                cur = ""
        else:
            if visible_width(cur) + 1 + visible_width(w) <= maxw:
                cur = cur + " " + w
            else:
                lines.append(cur)
                if visible_width(w) <= maxw:
                    cur = w
                else:
                    i = 0
                    while i < len(w):
                        part = w[i:i+maxw]
                        lines.append(part)
                        i += maxw
                    cur = ""
    if cur != "":
        lines.append(cur)
    return [truncate_to_width(line, maxw) for line in lines]

def manual_strip(s):
    start = 0
    end = len(s) - 1
    while start <= end and s[start] in " \t\n\r":
        start += 1
    while end >= start and s[end] in " \t\n\r":
        end -= 1
    return s[start:end+1]

def manual_is_number(s):
    if s == "":
        return False
    parts = s.split(".")
    if len(parts) == 1:
        return parts[0].isdigit()
    if len(parts) == 2:
        a, b = parts
        return (a.isdigit() and b.isdigit() and b != "")
    return False

def is_only_letters(s):
    """Check if string contains only letters and spaces"""
    s = manual_strip(s)
    if s == "":
        return False
    for ch in s:
        if not (ch.isalpha() or ch == " "):
            return False
    return True

def manual_len(lst):
    count = 0
    for _ in lst:
        count += 1
    return count

def manual_sum(lst):
    total = 0
    for v in lst:
        total += v
    return total

# -------- File I/O --------
def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_data():
    ensure_data_dir()
    if not os.path.exists(DATA_FILE):
        default_data = {
            "user_name": "",
            "subjects": [],
            "subject_difficulty": {},
            "subject_study_minutes": {},
            "goal_hours": 0,
            "mood_today": "",
            "study_minutes_today": 0,
            "missed_goal": False,
            "goal_recovery_increase": 0,
            "last_study_date": "",
            "study_plan": []
        }
        save_data(default_data)
        return default_data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        default_data = {
            "user_name": "",
            "subjects": [],
            "subject_difficulty": {},
            "subject_study_minutes": {},
            "goal_hours": 0,
            "mood_today": "",
            "study_minutes_today": 0,
            "missed_goal": False,
            "goal_recovery_increase": 0,
            "last_study_date": "",
            "study_plan": []
        }
        save_data(default_data)
        return default_data

def save_data(data):
    ensure_data_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# -------- Screen & boxes --------
def clear_screen():
    try:
        if os.name == "nt":
            os.system("cls")
        else:
            print("\033[2J\033[H", end="")
    except Exception:
        print("\n" * 60)

BORDER_FILL = "═" * (BOX_INNER + 2)

def box_title_only(title):
   
    print("╔" + BORDER_FILL + "╗")
    t = str(title)
    t = truncate_to_width(t, BOX_INNER)
    left = max(0, (BOX_INNER - visible_width(t)) // 2)
    right = max(0, BOX_INNER - visible_width(t) - left)
    print("║ " + " " * left + t + " " * right + " ║")
    print("╚" + BORDER_FILL + "╝")

def box_top():
    print("╔" + BORDER_FILL + "╗")

def box_title(title):
    
    t = str(title)
    t = truncate_to_width(t, BOX_INNER)
    left = max(0, (BOX_INNER - visible_width(t)) // 2)
    right = max(0, BOX_INNER - visible_width(t) - left)
    print("║ " + " " * left + t + " " * right + " ║")

def box_sep():
    print("╠" + BORDER_FILL + "╣")

def box_bottom():
    print("╚" + BORDER_FILL + "╝")

def box_line(text):
    s = str(text)
    s_trunc = truncate_to_width(s, BOX_INNER)
    s_pad = pad_to_width(s_trunc, BOX_INNER)
    print("║ " + s_pad + " ║")

def box_empty_line():
    
    print("║ " + " " * BOX_INNER + " ║")

def box_kv(key, value):
    
    k = str(key)
    v = str(value)
    k_with_colon = k + ":"
    kw_colon = visible_width(k_with_colon)
    
    # If key+colon is too long, put value on next line
    if kw_colon >= BOX_INNER - 5:
        ktr = truncate_to_width(k_with_colon, BOX_INNER - 2)
        print("║ " + pad_to_width(ktr, BOX_INNER) + " ║")
        wrapped = wrap_text_to_width(v, BOX_INNER - 2)
        for w in wrapped:
            padded = " " + pad_to_width(w, BOX_INNER - 2)
            print("║" + padded + " ║")
        return
    
    # Key+colon fits on same line as value
    first_value_width = BOX_INNER - kw_colon - 2
    wrapped = wrap_text_to_width(v, first_value_width)
    
    if not wrapped:
        line = k_with_colon + " " * (BOX_INNER - kw_colon - 1)
        print("║ " + pad_to_width(line, BOX_INNER) + " ║")
        return
    
    # First line with key and first value
    first = wrapped[0]
    line = k_with_colon + " " + first
    print("║ " + pad_to_width(line, BOX_INNER) + " ║")
    
    # Remaining wrapped lines
    for w in wrapped[1:]:
        pad_spaces = " " * (kw_colon + 1)
        line = pad_spaces + w
        print("║ " + pad_to_width(line, BOX_INNER) + " ║")

# -------- Input helpers --------
def ask_name(prompt):
   
    while True:
        v = manual_strip(input(prompt))
        if v == "":
            print("❌ Name cannot be empty!")
            continue
        if not is_only_letters(v):
            print("❌ Name can only contain letters!")
            continue
        if len(v) < 2:
            print("❌ Name must be at least 2 characters!")
            continue
        return v

def ask_float(prompt, min_v=None, max_v=None):
   
    while True:
        v = manual_strip(input(prompt))
        if not manual_is_number(v):
            print("❌ Please enter a valid number!")
            continue
        num = float(v)
        if min_v is not None and num < min_v:
            print(f"❌ Value must be >= {min_v}")
            continue
        if max_v is not None and num > max_v:
            print(f"❌ Value must be <= {max_v}")
            continue
        return num

def ask_int(prompt, min_v=None, max_v=None):
    
    while True:
        v = manual_strip(input(prompt))
        if not v.isdigit():
            print("❌ Please enter a valid number!")
            continue
        num = int(v)
        if min_v is not None and num < min_v:
            print(f"❌ Value must be >= {min_v}")
            continue
        if max_v is not None and num > max_v:
            print(f"❌ Value must be <= {max_v}")
            continue
        return num

def ask_subjects_type():
    while True:
        clear_screen()
        box_title_only("📚 SELECT STUDY MODE")
        print()
        print("Choose your study preference:")
        print()
        print("[1] Single Subject")
        print("[2] Multiple Subjects")
        print()
        choice = manual_strip(input("Choose (1 or 2): "))
        if choice == "1":
            return "single"
        elif choice == "2":
            return "multiple"
        else:
            print("❌ Invalid choice!")

def ask_single_subject_with_difficulty():
    clear_screen()
    box_title_only("📚 YOUR SUBJECT & DIFFICULTY")
    
    print()
    while True:
        subject = manual_strip(input("Enter subject name: "))
        if subject == "":
            print("❌ Subject name cannot be empty!")
            continue
        if not is_only_letters(subject):
            print("❌ Only letters allowed!")
            continue
        if len(subject) < 2:
            print("❌ At least 2 characters!")
            continue
        break
    print()
    print(f"Difficulty level for {subject}:")
    print()
    print("[1] Easy   (20-30 min sessions)")
    print("[2] Medium (30-40 min sessions)")
    print("[3] Hard   (45-60 min sessions)")
    print()
    
    while True:
        choice = manual_strip(input("Choose (1-3): "))
        if choice in ["1", "2", "3"]:
            difficulty = ["Easy", "Medium", "Hard"][int(choice) - 1]
            return subject, difficulty
        print("❌ Invalid choice!")

def ask_multiple_subjects_with_difficulty():
    """Ask how many subjects, then get each with difficulty"""
    clear_screen()
    box_title_only("📚 MULTIPLE SUBJECTS SETUP")
    print()
    
    num_subjects = ask_int("How many subjects do you want to study? ", 2, 10)
    
    subjects = []
    subject_difficulty = {}
    
    for i in range(1, num_subjects + 1):
        clear_screen()
        box_title_only(f"📚 SUBJECT {i} OF {num_subjects}")
        print()
        
        # ---------- Input subject name ----------
        while True:
            subject = manual_strip(input(f"Enter subject {i} name: "))
            
            # Check duplicate
            if subject in subjects:
                print("❌ Subject already added!")
                continue

            # Check empty
            if subject == "":
                print("❌ Subject name cannot be empty!")
                continue

            # Only letters
            if not is_only_letters(subject):
                print("❌ Only letters allowed!")
                continue

            # Minimum length
            if len(subject) < 2:
                print("❌ At least 2 characters!")
                continue

            break  # valid subject entered

        # ---------- Choose difficulty ----------
        print()
        print(f"Difficulty level for {subject}:")
        print()
        print("[1] Easy   (20-30 min sessions)")
        print("[2] Medium (30-40 min sessions)")
        print("[3] Hard   (45-60 min sessions)")
        print()
        
        while True:
            choice = manual_strip(input("Choose (1-3): "))
            if choice in ["1", "2", "3"]:
                difficulty = ["Easy", "Medium", "Hard"][int(choice) - 1]
                break
            print("❌ Invalid choice!")
        
        subjects.append(subject)
        subject_difficulty[subject] = difficulty
    
    return subjects, subject_difficulty

# -------- Setup Profile --------
def setup_profile():
    clear_screen()
    box_title_only("📋 PROFILE SETUP")
    
    data = load_data()
    
    print()
    data["user_name"] = ask_name("Enter your name: ")
    
    subject_type = ask_subjects_type()
    
    if subject_type == "single":
        subject, difficulty = ask_single_subject_with_difficulty()
        data["subjects"] = [subject]
        data["subject_difficulty"] = {subject: difficulty}
    else:
        subjects, subject_difficulty = ask_multiple_subjects_with_difficulty()
        data["subjects"] = subjects
        data["subject_difficulty"] = subject_difficulty
    
    # Initialize subject study minutes
    data["subject_study_minutes"] = {}
    for subject in data["subjects"]:
        data["subject_study_minutes"][subject] = 0
    
    save_data(data)
    
    clear_screen()
    box_title_only("✅ PROFILE SAVED")
    input("\nPress Enter to continue...")

# -------- Generate Study Plan --------
def generate_study_plan(user_data):
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
    
    if "Motivated" in mood:
        mood_multiplier, base_break = 1.2, 10
    elif "Tired" in mood:
        mood_multiplier, base_break = 0.7, 5
    elif "Stressed" in mood:
        mood_multiplier, base_break = 0.9, 8
    else:
        mood_multiplier, base_break = 1.0, 7
    
    difficulty_times = {"Easy": 25, "Medium": 35, "Hard": 50}
    
    study_plan = []
    minutes_used = 0
    session_num = 1
    net_study_goal = total_minutes_goal - 10 

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
    
    study_plan.append({
        "session": session_num,
        "subject": "Revision",
        "duration": 10,
        "type": "revision"
    })
    
    return study_plan

# -------- Set Mood and Generate Plan --------
def set_mood_and_generate_plan():
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
    
    box_title_only("✅ PLAN GENERATED FOR " + str(data["goal_hours"]) + " HOURS")
    input("\nPress Enter to continue...")

# -------- View Study Plan --------
def view_study_plan():
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

    # ---- start loop INSIDE the function ----
    total_study_minutes = 0
    total_break_minutes = 0
    session_count = 0

    for session in study_plan:
        if session["type"] == "study":
            difficulty = session.get("difficulty", "")
            difficulty_emoji = "🟢" if difficulty == "Easy" else "🟡" if difficulty == "Medium" else "🔴"
            box_line(f"  {difficulty_emoji} {session['subject']}: {session['duration']} min ({difficulty})")
            total_study_minutes += session["duration"]
            session_count += 1
        elif session["type"] == "break":
            box_line(f"  ☕ Break: {session['duration']} min")
            total_break_minutes += session["duration"]
        elif session["type"] == "revision":
            box_line(f"  🔄 Revision: {session['duration']} min")
            total_study_minutes += session["duration"]

    # -------- Show totals --------
    box_sep()
    total_hours = total_study_minutes / 60
    box_kv("Total Study Time", f"{total_study_minutes} min ({total_hours:.1f} hours)")
    box_kv("Total Break Time", f"{total_break_minutes} min")
    box_kv("Study Sessions", f"{session_count} sessions")
    box_bottom()
    input("\nPress Enter to continue...")

# -------- Log Study Session --------
def log_study_session():
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
    
    # Initialize subject study minutes if not exists
    if "subject_study_minutes" not in data:
        data["subject_study_minutes"] = {}
    
    for subject in data["subjects"]:
        if subject not in data["subject_study_minutes"]:
            data["subject_study_minutes"][subject] = 0
    
    # Check if single or multiple subjects
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
    
    # Update data
    data["study_minutes_today"] = int(total_minutes)
    data["last_study_date"] = str(datetime.now().date())
    
    # Check if goal is met
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

# -------- View Progress Dashboard --------
def view_progress_dashboard():
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
    
    # Calculate overall progress percentage
    progress_percentage = int((study_minutes / goal_minutes * 100)) if goal_minutes > 0 else 0
    progress_percentage = min(progress_percentage, 100)
    
    # Extract planned minutes per subject from study plan
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
    
    # OVERALL PROGRESS SECTION
    box_line(truncate_to_width("📈 OVERALL DAILY PROGRESS", BOX_INNER))
    box_line("")
    bar = print_progress_bar(progress_percentage)
    box_kv("Progress", bar)
    box_kv("Studied Today", f"{study_minutes} min")
    box_kv("Daily Goal", f"{goal_minutes} min")
    box_kv("Remaining", f"{max(0, goal_minutes - study_minutes)} min")
    box_sep()
    
    # SUBJECT-WISE SECTION WITH COMPARISON
    box_line(truncate_to_width("📚 SUBJECT-WISE (Planned vs Actual)", BOX_INNER))
    box_line("")
    
    for subject in data["subjects"]:
        actual_minutes = subject_minutes.get(subject, 0)
        planned = planned_minutes.get(subject, 0)
        
        # Calculate percentage for this subject based on goal
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
            status = f" In progress ({planned - actual_minutes} min left)"
        else:
            status = f"❌ Not started"
        
        status_line = f"    ↳ {status}"
        box_line(truncate_to_width(status_line, BOX_INNER))
        box_line("")
    
    box_sep()
    box_bottom()
    input("\nPress Enter to continue...")

def print_progress_bar(percent, total_blocks=15):
    if percent > 0:
        filled = int(percent / 100 * total_blocks)
        filled = max(1, min(total_blocks, filled))
    else:
        filled = 0
        
    bar = "█" * filled + "░" * (total_blocks - filled)
    return f"[{bar}] {percent:.0f}%"

# -------- View Profile --------
def view_profile():
    clear_screen()
    data = load_data()
    
    if not data["user_name"]:
        box_title_only("⚠️ ERROR")
        print("\nNo profile setup yet!")
        input("\nPress Enter to continue...")
        return
    
    box_top()
    box_title("👤 YOUR PROFILE")
    box_sep()
   
    box_kv("Name", data["user_name"])
    box_sep()
    
    box_line("📚 Today's Study Topics:")
    box_line("") 
    
    subjects_list = data.get("subjects", [])
    diff_map = data.get("subject_difficulty", {})
    
    if subjects_list:
        for i, s in enumerate(subjects_list, 1):
            difficulty = diff_map.get(s, "N/A")
            box_kv(f"  Subject {i}", s)
            box_kv(f"  Difficulty", difficulty)
            if i < len(subjects_list):
                box_line("  " + "-" * (BOX_INNER - 6))
    else:
        box_line("  No topics set yet.")
    box_bottom()
    input("\nPress Enter to continue...")

# -------- View User Dashboard --------
def view_user_dashboard():
    """View complete user dashboard"""
    clear_screen()
    data = load_data()
    
    if not data["user_name"]:
        box_title_only("⚠️ ERROR")
        print()
        print("No profile setup yet!")
        input("\nPress Enter to continue...")
        return
    
    box_top()
    box_title("📊 USER DASHBOARD")
    box_sep()
    box_kv("Name", data["user_name"])
    box_kv("Subjects", ", ".join(data["subjects"]) if data["subjects"] else "Not set")
    box_kv("Today's Study Goal", f"{data['goal_hours']} hours" if data['goal_hours'] > 0 else "Not set")
    box_kv("Current Mood", data["mood_today"] if data["mood_today"] else "Not set")
    box_kv("Today's Actual Study", f"{data['study_minutes_today']} minutes")
    box_kv("Last Study Date", data["last_study_date"] if data["last_study_date"] else "N/A")
    box_bottom()
    input("\nPress Enter to continue...")

# -------- Missed Goal Recovery --------
def check_missed_goal_recovery():
    clear_screen()
    data = load_data()
    
    if data.get("missed_goal", False):
        box_top()
        box_title("🔄 MISSED GOAL RECOVERY")
        box_sep()
        box_line(truncate_to_width("You missed your goal today!!!", BOX_INNER))
        box_sep()
        box_line(truncate_to_width("💪 RECOVERY PLAN:", BOX_INNER))
        box_line("")
        box_line(truncate_to_width("Tomorrow's goal +30 minutes", BOX_INNER))
        box_line("")
        box_sep()
        box_line(truncate_to_width("📝 Tips:", BOX_INNER))
        box_line(truncate_to_width("  • Take breaks every 25 min", BOX_INNER))
        box_line(truncate_to_width("  • Study in quiet place", BOX_INNER))
        box_line(truncate_to_width("  • Start with easier subjects", BOX_INNER))
        box_line(truncate_to_width("  • You can do this! 💪", BOX_INNER))
        box_sep()
        
        data["goal_recovery_increase"] = 0.5
    else:
        box_top()
        box_title("✅ YOU'RE ON TRACK!")
        box_sep()
        box_line(truncate_to_width("Great job! Keep up the work!", BOX_INNER))
        box_line(truncate_to_width("No recovery needed for today. 🎉", BOX_INNER))
        box_sep()
        data["goal_recovery_increase"] = 0
    
    box_bottom()
    save_data(data)
    input("\nPress Enter to continue...")

# -------- Main Menu --------
def main_menu():
    while True:
        clear_screen()
        box_title_only("📚 STUDY PLANNER")
        print()
        print("[1] Setup Profile")
        print("[2] View Profile")
        print("[3] Set Mood & Generate Plan")
        print("[4] View Today's Study Plan")
        print("[5] Log Study Session")
        print("[6] View Progress Dashboard")
        print("[7] Check Missed Goal Recovery")
        print("[8] View User Dashboard")
        print("[0] Exit")
        
        choice = manual_strip(input("\nChoose: "))
        
        if choice == "1":
            setup_profile()
        elif choice == "2":
            view_profile()
        elif choice == "3":
            set_mood_and_generate_plan()
        elif choice == "4":
            view_study_plan()
        elif choice == "5":
            log_study_session()
        elif choice == "6":
            view_progress_dashboard()
        elif choice == "7":
            check_missed_goal_recovery()
        elif choice == "8":
            view_user_dashboard()
        elif choice == "0":
            clear_screen()
            box_title_only("Thank You!")
            print()
            print("Keep studying and stay motivated! 🎯")
            break
        else:
            clear_screen()
            box_title_only("⚠️ INVALID CHOICE")
            print()
            print("Please enter a valid option (0-8)")
            input("\nPress Enter to continue...")
