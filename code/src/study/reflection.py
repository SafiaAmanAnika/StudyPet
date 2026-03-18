import time
from datetime import datetime, timedelta
from src.custom.custom_random import choice

# ---------------- UTILITY ---------------- #
def today_str():
    t = time.localtime()
    return f"{t.tm_year}-{t.tm_mon:02}-{t.tm_mday:02}"

def input_study_date():
    date_str = input("Enter study date (YYYY-MM-DD) or leave empty for today:\n> ").strip()
    if date_str == "":
        return today_str()
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        print("Invalid date format. Using today.")
        return today_str()

def input_study_hours():
    while True:
        hours_str = input("How many hours did you study today? (1-24)\n> ").strip()
        try:
            hours = float(hours_str)
            if 0 < hours <= 24:
                return hours
            else:
                print("Please enter a valid number between 1 and 24.")
        except ValueError:
            print("Please enter a valid number between 1 and 24.")

# ---------------- REFLECTION JOURNAL ---------------- #
def log_reflection(user_data):
    if 'reflections' not in user_data:
        user_data['reflections'] = []

    if 'daily_sessions' not in user_data:
        user_data['daily_sessions'] = {}

    print("╔════════════════════════════════╗")
    print("║       Reflection Journal       ║")
    print("╚════════════════════════════════╝")

    study_date = input_study_date()
    positive_feedback = input("What went well today?\n> ").strip()
    challenges = input("What was hard?\n> ").strip()

    if positive_feedback == "" and challenges == "":
        print("No reflection entered.\n")
        return user_data

    hours = input_study_hours()

    # Track daily sessions
    user_data['daily_sessions'][study_date] = user_data['daily_sessions'].get(study_date, 0) + 1
    user_data['total_study_hours'] = user_data.get('total_study_hours', 0) + hours

    entry = {
        "date": study_date,
        "positive_feedback": positive_feedback,
        "challenges": challenges,
        "hours": hours
    }
    user_data['reflections'].append(entry)
    print("\nReflection saved!\n")

    # Surprise achievement: 5 sessions/day
    if user_data['daily_sessions'][study_date] == 5:
        surprise_coins = choice([20, 25, 30])
        user_data['coins'] = user_data.get('coins', 0) + surprise_coins
        print(f"✨ Surprise! You completed 5 sessions today! +{surprise_coins} coins")

    return user_data

# ---------------- STREAK & INACTIVITY ---------------- #
def calculate_streaks(user_data):
    reflections = user_data.get('reflections', [])
    if not reflections:
        user_data['current_streak'] = 0
        user_data['max_streak'] = 0
        user_data['inactivity_days'] = 0
        return user_data

    # Build dict of date -> hours
    date_hours = {}
    for r in reflections:
        date_hours[r['date']] = date_hours.get(r['date'], 0) + r.get('hours', 0)

    all_dates = sorted([datetime.strptime(d, "%Y-%m-%d") for d in date_hours.keys()])
    first_day = all_dates[0]
    last_day = all_dates[-1]

    current_streak = 0
    max_streak = 0
    inactivity_days = 0
    streak = 0

    # iterate from first day to last day
    day = first_day
    while day <= last_day:
        day_str = day.strftime("%Y-%m-%d")
        if date_hours.get(day_str, 0) > 0:
            streak += 1
        else:
            if streak > max_streak:
                max_streak = streak
            streak = 0
            if day != first_day and day != last_day:  # skip first/last for inactivity count
                inactivity_days += 1
        day += timedelta(days=1)

    if streak > max_streak:
        max_streak = streak

    # current streak = streak at last day
    user_data['current_streak'] = streak if date_hours.get(last_day.strftime("%Y-%m-%d"), 0) > 0 else 0
    user_data['max_streak'] = max_streak
    user_data['inactivity_days'] = inactivity_days

    return user_data

# ---------------- ACHIEVEMENTS & BADGES ---------------- #
def check_achievements(user_data):
    if 'achievements' not in user_data:
        user_data['achievements'] = []

    streak = user_data.get('current_streak', 0)
    new_achievements = []

    # Streak-based badges only
    streak_badges = [
        (3, "Momentum Builder"),
        (7, "Weekly Warrior"),
        (15, "Persistent Learner"),
        (30, "Master of Habits"),
        (31, "Learning Legend")
    ]

    for days, name in streak_badges:
        if streak >= days and name not in user_data['achievements']:
            new_achievements.append(name)

    for achievement in new_achievements:
        user_data['achievements'].append(achievement)
        print(f"🏆 New Achievement Unlocked: {achievement}")

    # Always show all badges
    print("╔════════════════════════════════╗")
    print("║       Your Achievements        ║")
    print("╚════════════════════════════════╝")
    if user_data['achievements']:
        for a in user_data['achievements']:
            print(f" - {a}")
    else:
        print("No achievements yet. Keep studying!")
    print()

    return user_data

# ---------------- RANDOM ENCOURAGEMENT ---------------- #
def random_encouragement(user_data):
    # Optional: trigger every 4 total sessions
    if user_data.get('total_sessions', 0) % 4 == 0 and user_data.get('total_sessions', 0) > 0:
        events = [
            ("Your pet found a rare study note! +20 coins", 20),
            ("Bonus coins discovered! +30 coins", 30),
            ("Surprise reward! +15 coins", 15)
        ]
        event, coins = choice(events)
        user_data["coins"] = user_data.get("coins", 0) + coins
        print(f"✨ {event}")
    return user_data

# ---------------- INTEGRATED HANDLER ---------------- #
def handle_post_study(user_data):
    user_data = log_reflection(user_data)
    user_data = calculate_streaks(user_data)
    user_data = check_achievements(user_data)
    user_data = random_encouragement(user_data)
    return user_data