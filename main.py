from src.ui import menu, pause, show_user_summary, show_user_stats, choose_mood, clear_screen
from src.storage import load_users, save_users
from src.pet import show_status
from src.shop import feed_pet, open_shop
from src.study import start_session
from src.wellbeing import log_mood, apply_tired_penalty, tired_streak_days
from src.recreation import recreation_menu, count_today_sessions
from src.quiz import run as quiz_run
from src.analytics import run as analytics_run
from src.weekly_report import run as weekly_run 

import json, os

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


# ---------------- HANDLERS ---------------- #

def handle_study_session(user_id, user_data):
    user_data, session_log = start_session(user_id, user_data)

    #track number of sessions
    session_count = count_today_sessions(user_id)

    #after every session we check two conditions
    tired_streak = tired_streak_days(user_id)

    if tired_streak >= 5 or session_count >= 3:
        recreation_menu(user_id)

    return user_data, session_log
    
def handle_feed_pet(user_data):
    return feed_pet(user_data)

def handle_shop(user_data):
    return open_shop(user_data)

def handle_wellbeing(user_id, user_data):
    print("╔═══════════════════════════════════════════╗")
    print("║             Short Check-In 🤗             ║")
    print("╚═══════════════════════════════════════════╝")
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
        print("╔══════════════════════════════════════╗")
        print("║      🐾 STUDYPET DASHBOARD 🐾        ║")
        print("╚══════════════════════════════════════╝")
        show_user_summary(user_data)

        print("╔══════════════════════════════════════╗")
        print("║       Your virtual pet awaits!       ║")
        print("╚══════════════════════════════════════╝")
        choice = menu([
            "Start Study Session ⏳", 
            "Feed Pet 🍖", 
            "Pet Shop 🛒", 
            "View Pet Status 🐱", 
            "View Stats 📊", 
            "Wellbeing 🌼", 
            "Quiz 📚", 
            "Analytics 📈", 
            "Weekly Report 📅",
            "Logout 👋"])
        clear_screen()

        if choice == 1: 
            user_data ,session_log = handle_study_session(user_id, user_data)
            save_user_data(user_id, user_data)
            append_study_log(session_log)
            pause()
            clear_screen()

        elif choice == 2: 
            user_data = handle_feed_pet(user_data)
            save_user_data(user_id, user_data)
            pause()
            clear_screen()

        elif choice == 3: 
            user_data = handle_shop(user_data)
            save_user_data(user_id, user_data)
            pause()
            clear_screen()

        elif choice == 4: 
            show_status(user_data)
            pause()
            clear_screen()
        
        elif choice == 5: 
            show_user_stats(user_id, user_data)
            pause()
            clear_screen()
        
        elif choice == 6:
            user_data = handle_wellbeing(user_id, user_data)

        elif choice == 7: 
            quiz_run(user_id, user_data)

        elif choice == 8: 
            user_data = analytics_run(user_id, user_data)

        elif choice == 9: 
            weekly_run(user_id, user_data)

        elif choice == 0: 
            clear_screen()
            print("╔══════════════════════════════════════╗")
            print("║   Logged out. Alvida mere dost 👋    ║")
            print("╚══════════════════════════════════════╝")                
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
        print("╔════════════════════════════════╗")
        print("║           MAIN MENU            ║")
        print("╚════════════════════════════════╝")
        choice = menu(["Register 📝", "Login 💻", "Exit 🚪"])

        if choice == 1: 
            user_id, user_data = register_user()
            if user_id: 
                dashboard(user_id, user_data)

        elif choice == 2: 
            user_id, user_data = login_user()
            if user_id: 
                mood = choose_mood(menu)
                if mood != "Skip": 
                    user_data["mood_today"] = mood
                    print("╔═══════════════════════════════════════════╗")
                    print("║              Mood Check-in 🤗             ║")
                    print("╚═══════════════════════════════════════════╝")
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

        elif choice == 0: 
            clear_screen()
            break 

if __name__ == "__main__": 
    main()