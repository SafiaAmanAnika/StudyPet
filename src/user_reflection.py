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
    
    # ✅ Check daily_sessions instead of reflections so skipped journals don't break the streak
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
