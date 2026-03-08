import time
import random
from datetime import datetime, timedelta

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
    except:
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
        except:
            print("Please enter a valid number between 1 and 24.")


# ---------------- REFLECTION JOURNAL ---------------- #
def log_reflection(user_data):
    if 'reflections' not in user_data:
        user_data['reflections'] = []
    if 'daily_sessions' not in user_data:
        user_data['daily_sessions'] = {}

    print("╔════════════════════════════════╗")
    print("║        Reflection Journal      ║")
    print("╚════════════════════════════════╝")

    study_date = input_study_date()
    hours = input_study_hours()

    user_data['daily_sessions'][study_date] = user_data['daily_sessions'].get(study_date, 0) + 1
    user_data['total_study_hours'] = user_data.get('total_study_hours', 0) + hours
    user_data['total_sessions'] = user_data.get('total_sessions', 0) + 1 

    positive_feedback = input("What went well today?\n> ").strip()
    challenges = input("What was hard?\n> ").strip()

    if positive_feedback == "" and challenges == "":
        print("\nNo reflection entered, but study time was logged.\n")
    else:
        entry = {
            "date": study_date,
            "positive_feedback": positive_feedback,
            "challenges": challenges,
            "hours": hours
        }
        user_data['reflections'].append(entry)
        print("\nReflection saved!\n")

        
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
    print("╔════════════════════════════════╗")
    print("║        Your Achievements       ║")
    print("╚════════════════════════════════╝")

    streak = user_data.get('current_streak', 0)
    achievements = user_data.get('achievements', [])

    if achievements:
        print("🏆 Badges Earned:")
        for a in achievements:
            print(f"   🎖️  {a}")
    else:
        print("No badges unlocked yet. Keep studying!")

    next_badge = None
    for days, name in STREAK_BADGES:
        if streak < days:
            next_badge = (days, name)
            break

    print()
    if next_badge:
        days_needed = next_badge[0] - streak
        print(f"📈 Current Streak : {streak} day(s)")
        print(f"🎯 Next Badge     : {next_badge[1]} (in {days_needed} more consecutive day(s))")
    else:
        print(f"📈 Current Streak : {streak} day(s)")
        print("🌟 You've unlocked ALL badges! You're a Learning Legend!")

    inactivity = user_data.get('inactivity_days', 0)
    if inactivity > 0:
        print(f"⚠️  Inactive Days  : {inactivity} day(s) (streak breaks on inactive days)")

    print()

def check_achievements(user_data):
    """
    Called after a study session — awards new badges and displays all achievements.
    This is the main function called from the menu/post-study flow.
    """
    user_data, new_achievements = check_and_award_achievements(user_data)

    if new_achievements:
        print("╔════════════════════════════════╗")
        print("║    🎉 New Badge Unlocked!      ║")
        print("╚════════════════════════════════╝")
        for a in new_achievements:
            print(f"   🏆 {a}")
        print()

    display_achievements(user_data)
    return user_data

# ---------------- RANDOM ENCOURAGEMENT ---------------- #
def random_encouragement(user_data):
    """Triggers every 4 total sessions as a surprise reward."""
    total = user_data.get('total_sessions', 0)
    if total > 0 and total % 4 == 0:  
        events = [
            ("Your pet found a rare study note! +20 coins", 20),
            ("Bonus coins discovered! +30 coins", 30),
            ("Surprise reward! +15 coins", 15)
        ]
        event, coins = random.choice(events)
        user_data["coins"] = user_data.get("coins", 0) + coins
        print(f"✨ {event}\n")
    return user_data
