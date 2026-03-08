from src.ui import menu, pause, show_user_summary, show_user_stats, choose_mood, clear_screen
from src.storage import load_users, save_users
from src.pet import show_status, apply_pet_abilities
from src.shop import feed_pet, open_shop
from src.study import start_session
from src.wellbeing import (
    log_mood,
    apply_tired_penalty,
    tired_streak_days,
    handle_burnout,
    update_energy,
    restore_energy,
)
from src.recreation import recreation_menu, count_today_sessions
from src.quiz import run as quiz_run
from src.analytics import run as analytics_run
from src.weekly_report import run as weekly_run 
from src.evolution import check_pet_evolution
from src.study_planner import main_menu as study_planner_menu

import json, os
from datetime import date, timedelta

LOG_FILE = "data/study_log.json"


# ---------------- MOOD MESSAGE ---------------- #

def mood_message(mood):
    messages = {
        "Happy 😊": "Nice! Let’s use that energy and study well today 😊 you GOT THISSSSS 👊",
        "Neutral 😐": "Steady and calm — small progress today is still progress 🥳",
        "Tired 😞": "Take it slow. Try JUST one short session, then rest ☝️",
        "Stressed 😫": "Breathe. One Pomodoro at a time. You’ve got this. YOU CAN DO THISSSSS!!!!! 🤗",
        "Motivated 🥳": "Love the energy! Let’s complete a strong session today! GO KYLIEEEE GOOOOO 🏃"
    }
    return messages.get(mood, "")

   
# ---------------- STUDY LOG ---------------- #

def append_study_log(session_log):
    if session_log is None: 
        return 
    
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f: 
            json.dump([], f)
    
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        logs = []

    logs.append(session_log)

    with open(LOG_FILE, "w") as f: 
        json.dump(logs, f, indent = 2)


def save_user_data(user_id, user_data):
    users = load_users()
    users[user_id] = user_data
    save_users(users)

def register_user():
    from src.auth import register
    return register()

def login_user():
    from src.auth import login
    return login()


def update_study_streak(user_data: dict) -> dict:
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))

    last_study_date = str(user_data.get("last_study_date", ""))

    try:
        current_streak = int(user_data.get("study_streak", 0))
    except (TypeError, ValueError):
        current_streak = 0

    if last_study_date == today:
        return user_data

    if last_study_date == yesterday:
        user_data["study_streak"] = current_streak + 1
    else:
        user_data["study_streak"] = 1

    user_data["last_study_date"] = today
    return user_data


# ---------------- HANDLERS ---------------- #

def handle_study_session(user_id, user_data):
    from src.evolution import check_pet_evolution

    # Start study session
    user_data, session_log = start_session(user_id, user_data)

    # If session was cancelled
    if session_log is None:
        return user_data, None

    # ---------------- UPDATE TOTAL STUDY HOURS ----------------
    minutes = session_log.get("study_minutes", 0)
    user_data["total_study_hours"] = user_data.get("total_study_hours", 0) + (minutes / 60)
    user_data["total_study_minutes"] = user_data.get("total_study_minutes", 0) + minutes
    user_data["last_study_minutes"] = minutes

    # ---------------- STREAK + PET ABILITIES ----------------
    user_data = update_study_streak(user_data)
    user_data = apply_pet_abilities(user_data)

    # ---------------- ENERGY UPDATE ----------------
    user_data = update_energy(user_data, minutes)
    if session_log.get("break_minutes", 0) > 0:
        user_data = restore_energy(user_data)

    # ---------------- BURNOUT CHECK ----------------
    burnout_detected = handle_burnout(user_id, user_data)
    if burnout_detected:
        pause()

    # ---------------- TRACK SESSION COUNT ----------------
    session_count = count_today_sessions(user_id)

    # ---------------- CHECK TIRED STREAK ----------------
    tired_streak = tired_streak_days(user_id)

    # ---------------- PET EVOLUTION CHECK ----------------
    user_data, evolved = check_pet_evolution(user_data, tired_streak)

    if evolved:
        print("╔═════════════════════════════════════════════════════════════════════════╗")
        print("║                         ✨ YOUR PET EVOLVED! ✨                         ║")
        print("╚═════════════════════════════════════════════════════════════════════════╝")
        print("Your study companion grew stronger! 🐾📚")

        show_status(user_data)

    # ---------------- RECREATION CHECK ----------------
    if tired_streak >= 5 or session_count >= 3:
        recreation_menu(user_id)

    return user_data, session_log

    
def handle_feed_pet(user_data):
    return feed_pet(user_data)

def handle_shop(user_data):
    return open_shop(user_data)

def handle_wellbeing(user_id, user_data):
    print("╔═════════════════════════════════════════════════════════════════════════╗")
    print("║                             Short Check-In 🤗                           ║")
    print("╚═════════════════════════════════════════════════════════════════════════╝")
    print(mood_message(user_data.get("mood_today", "")))
    pause()
    clear_screen()
    
    log_mood(user_id, user_data.get("mood_today", ""))
    
    user_data, penalty_message = apply_tired_penalty(user_id, user_data)
    if penalty_message: 
        print(f"Penalty message!! {penalty_message}")
        pause()
    
    recreation_menu(user_id)
    return user_data

# ---------------- DASHBOARD ---------------- #

def dashboard(user_id, user_data):
    while True:
        clear_screen()
        print("╔═════════════════════════════════════════════════════════════════════════╗")
        print("║                         🐾 STUDYPET DASHBOARD 🐾                        ║")
        print("╠═════════════════════════════════════════════════════════════════════════╣")
        show_user_summary(user_data)

        print("╔═════════════════════════════════════════════════════════════════════════╗")
        print("║                         Your virtual pet awaits!                        ║")
        print("╠═════════════════════════════════════════════════════════════════════════╣")
        print("║ [1] Start Study Session ⏳                                              ║")
        print("║ [2] Feed Pet 🍖                                                         ║")
        print("║ [3] Pet Shop 🛒                                                         ║")
        print("║ [4] View Pet Status 🐱                                                  ║")
        print("║ [5] View User Status 📊                                                 ║")
        print("║ [6] Mood Check-in 🌼                                                    ║")
        print("║ [7] Quiz 📚                                                             ║")
        print("║ [8] Analytics 📈                                                        ║")
        print("║ [9] Weekly Report 📅                                                    ║")
        print("║ [10] Study Planner 🗓️                                                  ║")
        print("║ [0] Logout 👋                                                           ║")
        print("╚═════════════════════════════════════════════════════════════════════════╝")

        choice = input("Choose your option: ").strip()
        clear_screen()

        if choice == "1": 
            user_data ,session_log = handle_study_session(user_id, user_data)
            save_user_data(user_id, user_data)
            append_study_log(session_log)
            pause()
            clear_screen()

        elif choice == "2": 
            user_data = handle_feed_pet(user_data)
            save_user_data(user_id, user_data)
            pause()
            clear_screen()

        elif choice == "3": 
            user_data = handle_shop(user_data)
            save_user_data(user_id, user_data)
            pause()
            clear_screen()

        elif choice == "4": 
            show_status(user_data)
            pause()
            clear_screen()
        
        elif choice == "5": 
            show_user_stats(user_id, user_data)
            pause()
            clear_screen()
        
        elif choice == "6":
            user_data = handle_wellbeing(user_id, user_data)
            save_user_data(user_id, user_data)

        elif choice == "7": 
            user_data = quiz_run(user_id, user_data)

        elif choice == "8": 
            user_data = analytics_run(user_id, user_data)

        elif choice == "9": 
            user_data = weekly_run(user_id, user_data)

        elif choice == "10":
            study_planner_menu()

        elif choice == "0": 
            clear_screen()
            print("╔═════════════════════════════════════════════════════════════════════════╗")
            print("║                   Logged out. Alvida mere dost 👋                       ║")
            print("╚═════════════════════════════════════════════════════════════════════════╝")           
            pause()
            clear_screen()
            return 
        
def main(): 
    while True: 
        print(r"""
███████╗ ████████╗ ██╗   ██╗ ██████╗  ██╗   ██╗ ██████╗  ███████╗ ████████╗
██╔════╝ ╚══██╔══╝ ██║   ██║ ██╔══██╗ ╚██╗ ██╔╝ ██╔══██╗ ██╔════╝ ╚══██╔══╝
███████╗    ██║    ██║   ██║ ██║  ██║  ╚████╔╝  ██████╔╝ █████╗      ██║
╚════██║    ██║    ██║   ██║ ██║  ██║   ╚██╔╝   ██╔═══╝  ██╔══╝      ██║
███████║    ██║    ╚██████╔╝ ██████╔╝    ██║    ██║      ███████╗    ██║
╚══════╝    ╚═╝     ╚═════╝  ╚═════╝     ╚═╝    ╚═╝      ╚══════╝    ╚═╝
""")
        print("╔═════════════════════════════════════════════════════════════════════════╗")
        print("║                                 MAIN MENU                               ║")
        print("╠═════════════════════════════════════════════════════════════════════════╣")
        print("║ [1] Register 📝                                                         ║")
        print("║ [2] Login 💻                                                            ║")
        print("║ [0] Exit 🚪                                                             ║")
        print("╚═════════════════════════════════════════════════════════════════════════╝")

        choice = input("Choose your option : ").strip()

        if choice == "1": 
            user_id, user_data = register_user()
            if user_id: 
                dashboard(user_id, user_data)

        elif choice == "2": 
            user_id, user_data = login_user()
            if user_id: 
                mood = choose_mood(menu)
                if mood != "Skip": 
                    user_data["mood_today"] = mood
                    print("╔═════════════════════════════════════════════════════════════════════════╗")
                    print("║                             Mood Check-in 🤗                            ║")
                    print("╚═════════════════════════════════════════════════════════════════════════╝")
                    print(mood_message(mood))
                    pause()
                    clear_screen()
                    log_mood(user_id, mood)
    
                user_data, penalty_message = apply_tired_penalty(user_id, user_data)
                if penalty_message: 
                    print(penalty_message)
                    pause()
    
                recreation_menu(user_id)

                save_user_data(user_id, user_data)    
                dashboard(user_id, user_data)

        elif choice == "0": 
            clear_screen()
            break 

if __name__ == "__main__": 
    main()