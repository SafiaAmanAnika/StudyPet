import json, os, time, random
from datetime import datetime, timedelta
from src.interface.ui import clear_screen, print_fancy_box

# ---------------- UTILITY ---------------- #
def today_str():
    t = time.localtime()
    return f"{t.tm_year}-{t.tm_mon:02}-{t.tm_mday:02}"

def input_study_date():
    date_str = input("📅 Enter study date (YYYY-MM-DD) or press Enter for today: ").strip()
    if date_str == "":
        return today_str()
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        clear_screen()
        print_fancy_box(
            "⚠️ Invalid Date Format",
            ["Please use YYYY-MM-DD.", "Using today's date instead."],
            theme="yellow",
        )
        return today_str()
    

def input_study_hours():
    while True:
        hours_str = input("⏱️ How many hours did you study today? (1-24): ").strip()
        try:
            hours = float(hours_str)
            if 0 < hours <= 24:
                return hours
            else:
                print_fancy_box(
                    "Invalid Hours",
                    ["Please enter a number between 1 and 24."],
                    theme="yellow",
                )
        except ValueError:
            print_fancy_box(
                "Invalid Input",
                ["Please enter a valid number between 1 and 24."],
                theme="yellow",
            )


def _project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _study_log_path():
    return os.path.join(_project_root(), "data", "study_log.json")


def _safe_load_study_logs():
    path = _study_log_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
        return []


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _compute_user_study_metrics(user_id):
    daily_sessions = {}
    total_minutes = 0
    total_sessions = 0

    if not user_id:
        return daily_sessions, total_minutes, total_sessions

    for log in _safe_load_study_logs():
        if not isinstance(log, dict):
            continue
        if log.get("user_id") != user_id:
            continue

        date_key = log.get("date")
        if not isinstance(date_key, str) or not date_key:
            continue

        minutes = max(0, _safe_int(log.get("study_minutes", 0), 0))
        sessions = max(1, _safe_int(log.get("sessions_completed", 1), 1))

        total_minutes += minutes
        total_sessions += sessions
        daily_sessions[date_key] = daily_sessions.get(date_key, 0) + sessions

    return daily_sessions, total_minutes, total_sessions


def _sync_reflection_stats_from_logs(user_data, user_id=None):
    daily_sessions, total_minutes, total_sessions = _compute_user_study_metrics(user_id)

    user_data['daily_sessions'] = daily_sessions
    user_data['reflection_total_hours'] = round(total_minutes / 60.0, 2)
    user_data['reflection_total_sessions'] = total_sessions

    return user_data


def _metrics_for_date(user_id, study_date):
    daily_sessions, total_minutes, _ = _compute_user_study_metrics(user_id)
    sessions = daily_sessions.get(study_date, 0)

    date_minutes = 0
    if user_id:
        for log in _safe_load_study_logs():
            if not isinstance(log, dict):
                continue
            if log.get("user_id") != user_id or log.get("date") != study_date:
                continue
            date_minutes += max(0, _safe_int(log.get("study_minutes", 0), 0))

    return sessions, date_minutes, round(date_minutes / 60.0, 2)


# ---------------- REFLECTION JOURNAL ---------------- #
def log_reflection(user_data, user_id=None):
    if 'reflections' not in user_data:
        user_data['reflections'] = []

    user_data = _sync_reflection_stats_from_logs(user_data, user_id=user_id)

    clear_screen()
    print_fancy_box(
        "📓 Reflection Journal",
        [
            "Reflect on your study and wins.",
            "Study time and session count are auto-synced from your logs.",
        ],
        theme="yellow",
    )

    study_date = input_study_date()
    logged_sessions, logged_minutes, logged_hours = _metrics_for_date(user_id, study_date)

    positive_feedback = input("✨ What went well today?          : ").strip()
    challenges = input("🧩 What was hard today?           : ").strip()

    if positive_feedback == "" and challenges == "":
        clear_screen()
        print_fancy_box(
            "Study Logged ✅",
            [
                f"Date: {study_date}",
                f"Logged sessions: {logged_sessions}",
                f"Logged minutes : {logged_minutes}",
                f"Logged hours   : {logged_hours}",
                "No reflection text entered.",
            ],
            theme="green",
        )
    else:
        entry = {
            "date": study_date,
            "positive_feedback": positive_feedback,
            "challenges": challenges,
            "hours": logged_hours,
            "sessions": logged_sessions,
            "minutes": logged_minutes,
        }
        user_data['reflections'].append(entry)
        clear_screen()
        print_fancy_box(
            "Reflection Saved ✅",
            [
                f"Date: {study_date}",
                f"Logged sessions: {logged_sessions}",
                f"Logged minutes : {logged_minutes}",
                f"Logged hours   : {logged_hours}",
                "Nice work capturing your learning progress.",
            ],
            theme="green",
        )

    user_data = _sync_reflection_stats_from_logs(user_data, user_id=user_id)

    # Surprise achievement: 5+ sessions in a single day (awarded once per day)
    if 'reflection_bonus_dates' not in user_data or not isinstance(user_data.get('reflection_bonus_dates'), list):
        user_data['reflection_bonus_dates'] = []

    if logged_sessions >= 5 and study_date not in user_data['reflection_bonus_dates']:
        surprise_coins = random.choice([20, 25, 30])
        user_data['coins'] = user_data.get('coins', 0) + surprise_coins
        user_data['reflection_bonus_dates'].append(study_date)
        print_fancy_box(
            "✨ Surprise Achievement Unlocked",
            [f"You completed 5 sessions today!", f"+{surprise_coins} coins added."],
            theme="magenta",
        )

    return user_data


        
# ---------------- STREAK & INACTIVITY ---------------- #
def calculate_streaks(user_data, user_id=None):
    user_data = _sync_reflection_stats_from_logs(user_data, user_id=user_id)
    daily_sessions = user_data.get('daily_sessions', {})
    
    # Check daily_sessions instead of reflections so skipped journals don't break the streak
    if not daily_sessions:
        user_data['current_streak'] = 0
        user_data['max_streak'] = 0
        user_data['inactivity_days'] = 0
        return user_data

    active_dates = list(daily_sessions.keys())
    all_dates = sorted([datetime.strptime(d, "%Y-%m-%d") for d in active_dates])
    first_day = all_dates[0]
    today = datetime.strptime(today_str(), "%Y-%m-%d")

    current_streak = 0
    max_streak = 0
    inactivity_days = 0
    streak = 0

    day = first_day
    while day <= today:
        day_str = day.strftime("%Y-%m-%d")
        # If they have 1 or more sessions this day, they studied
        if daily_sessions.get(day_str, 0) > 0:
            streak += 1
            inactivity_days = 0  
            if streak > max_streak:
                max_streak = streak
        else:
            streak = 0
            inactivity_days += 1 
        day += timedelta(days=1)

    user_data['current_streak'] = streak
    user_data['max_streak'] = max_streak
    user_data['inactivity_days'] = inactivity_days

    return user_data

# ---------------- ACHIEVEMENTS & BADGES ---------------- #
STREAK_BADGES = [
    (3,  "Momentum Builder"),
    (7,  "Weekly Warrior"),
    (15, "Persistent Learner"),
    (30, "Master of Habits"),
    (31, "Learning Legend"),   
]

def check_and_award_achievements(user_data):
    """Silently checks and adds newly earned badges. Returns list of new ones."""
    if 'achievements' not in user_data:
        user_data['achievements'] = []

    streak = user_data.get('current_streak', 0)
    new_achievements = []

    for days, name in STREAK_BADGES:
        if streak >= days and name not in user_data['achievements']:
            new_achievements.append(name)
            user_data['achievements'].append(name)

    return user_data, new_achievements

def display_achievements(user_data):
    """Shows the user their current badges and progress toward next badge."""
    streak = user_data.get('current_streak', 0)
    achievements = user_data.get('achievements', [])
    lines = []

    if achievements:
        lines.append("🏆 Badges Earned:")
        for a in achievements:
            lines.append(f"🎖️ {a}")
    else:
        lines.append("No badges unlocked yet. Keep studying!")

    next_badge = None
    for days, name in STREAK_BADGES:
        if streak < days:
            next_badge = (days, name)
            break

    lines.append("")
    if next_badge:
        days_needed = next_badge[0] - streak
        lines.append(f"📈 Current Streak: {streak} day(s)")
        lines.append(f"🎯 Next Badge: {next_badge[1]} ({days_needed} more consecutive day(s))")
    else:
        lines.append(f"📈 Current Streak: {streak} day(s)")
        lines.append("🌟 You've unlocked ALL badges! You're a Learning Legend!")

    inactivity = user_data.get('inactivity_days', 0)
    if inactivity > 0:
        lines.append(f"⚠️ Inactive Days: {inactivity} day(s) (streak breaks on inactive days)")

    print_fancy_box("🏆 Your Achievements", lines, theme="blue")

def check_achievements(user_data):
    """
    Called after a study session — awards new badges and displays all achievements.
    This is the main function called from the menu/post-study flow.
    """
    user_data, new_achievements = check_and_award_achievements(user_data)

    if new_achievements:
        lines = [f"🏆 {badge}" for badge in new_achievements]
        print_fancy_box("🎉 New Badge Unlocked!", lines, theme="magenta")

    display_achievements(user_data)
    return user_data

# ---------------- RANDOM ENCOURAGEMENT ---------------- #
def random_encouragement(user_data):
    """Triggers every 4 total sessions as a surprise reward."""
    total = user_data.get('reflection_total_sessions', user_data.get('total_sessions', 0))
    if total > 0 and total % 4 == 0:  
        events = [
            ("Your pet found a rare study note! +20 coins", 20),
            ("Bonus coins discovered! +30 coins", 30),
            ("Surprise reward! +15 coins", 15)
        ]
        event, coins = random.choice(events)
        user_data["coins"] = user_data.get("coins", 0) + coins
        print_fancy_box("✨ Bonus Reward", [event], theme="cyan")
    return user_data


def view_journal_history(user_data):
    clear_screen()
    reflections = user_data.get('reflections', [])
    if not isinstance(reflections, list) or not reflections:
        print_fancy_box(
            "📚 Journal History",
            ["No journal entries yet.", "Log a reflection after studying to build your history."],
            theme="blue",
        )
        return user_data

    entries = [entry for entry in reflections if isinstance(entry, dict)]
    entries.sort(key=lambda e: str(e.get('date', '')), reverse=True)

    lines = []
    display_limit = 12
    for idx, entry in enumerate(entries[:display_limit], start=1):
        date_label = str(entry.get('date', 'Unknown'))
        hours = entry.get('hours', 0)
        sessions = entry.get('sessions')
        positives = str(entry.get('positive_feedback', '')).strip() or "-"
        challenges = str(entry.get('challenges', '')).strip() or "-"

        if sessions is None:
            lines.append(f"[{idx}] {date_label} | Hours: {hours}")
        else:
            lines.append(f"[{idx}] {date_label} | Hours: {hours} | Sessions: {sessions}")
        lines.append(f"Win : {positives}")
        lines.append(f"Hard: {challenges}")
        lines.append("")

    remaining = len(entries) - display_limit
    if remaining > 0:
        lines.append(f"...and {remaining} older journal(s).")

    print_fancy_box("📚 Journal History", lines, theme="blue")
    return user_data

# ---------------- INTEGRATED HANDLER ---------------- #
def handle_post_study(user_data, user_id=None):
    """Called from reflection journal flow."""
    user_data = log_reflection(user_data, user_id=user_id)
    user_data = calculate_streaks(user_data, user_id=user_id)
    user_data = check_achievements(user_data)
    user_data = random_encouragement(user_data)
    return user_data

# ---------------- MENU HANDLER (for Achievement option in menu) ---------------- #
def handle_view_achievements(user_data, user_id=None):
    """Called when user selects 'Achievements' from the main menu."""
    user_data = calculate_streaks(user_data, user_id=user_id)  # Recalculate in case day changed
    user_data, _ = check_and_award_achievements(user_data)  # Award any pending badges
    display_achievements(user_data)
    return user_data


def handle_view_journal_history(user_data):
    return view_journal_history(user_data)
