import time, random
from datetime import datetime, timedelta
from src.ui import clear_screen, print_fancy_box

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


# ---------------- REFLECTION JOURNAL ---------------- #
def log_reflection(user_data):
    if 'reflections' not in user_data:
        user_data['reflections'] = []
    if 'daily_sessions' not in user_data:
        user_data['daily_sessions'] = {}

    clear_screen()
    print_fancy_box(
        "📓 Reflection Journal",
        [
            "Log today's study and reflect on progress.",
            "Reflection text is optional. Study time still counts.",
        ],
        theme="yellow",
    )

    study_date = input_study_date()
    hours = input_study_hours()

    user_data['daily_sessions'][study_date] = user_data['daily_sessions'].get(study_date, 0) + 1
    # Keep reflection metrics separate from core study-session totals.
    user_data['reflection_total_hours'] = user_data.get('reflection_total_hours', 0) + hours
    user_data['reflection_total_sessions'] = user_data.get('reflection_total_sessions', 0) + 1

    positive_feedback = input("✨ What went well today?          : ").strip()
    challenges = input("🧩 What was hard today?           : ").strip()

    if positive_feedback == "" and challenges == "":
        clear_screen()
        print_fancy_box(
            "Study Logged ✅",
            [
                f"Date: {study_date}",
                f"Hours: {hours}",
                "No reflection text entered, but your study was recorded.",
            ],
            theme="green",
        )
    else:
        entry = {
            "date": study_date,
            "positive_feedback": positive_feedback,
            "challenges": challenges,
            "hours": hours
        }
        user_data['reflections'].append(entry)
        clear_screen()
        print_fancy_box(
            "Reflection Saved ✅",
            [
                f"Date: {study_date}",
                f"Hours: {hours}",
                "Nice work capturing your learning progress.",
            ],
            theme="green",
        )

    #  Surprise achievement: 5 sessions in a single day
    if user_data['daily_sessions'][study_date] == 5:
        surprise_coins = random.choice([20, 25, 30])
        user_data['coins'] = user_data.get('coins', 0) + surprise_coins
        print_fancy_box(
            "✨ Surprise Achievement Unlocked",
            [f"You completed 5 sessions today!", f"+{surprise_coins} coins added."],
            theme="magenta",
        )

    return user_data


        
# ---------------- STREAK & INACTIVITY ---------------- #
def calculate_streaks(user_data):
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

# ---------------- INTEGRATED HANDLER ---------------- #
def handle_post_study(user_data):
    """Called from reflection journal flow."""
    user_data = log_reflection(user_data)
    user_data = calculate_streaks(user_data)
    user_data = check_achievements(user_data)
    user_data = random_encouragement(user_data)
    return user_data

# ---------------- MENU HANDLER (for Achievement option in menu) ---------------- #
def handle_view_achievements(user_data):
    """Called when user selects 'Achievements' from the main menu."""
    user_data = calculate_streaks(user_data)  # Recalculate in case day changed
    user_data, _ = check_and_award_achievements(user_data)  # Award any pending badges
    display_achievements(user_data)
    return user_data
