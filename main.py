from src.ui import title, menu, pause, show_user_summary, show_user_stats, choose_mood, clear_screen
from src.storage import load_users, save_users
from src.pet import show_status
from src.shop import feed_pet, open_shop
from src.study import start_session

import json 
import os

LOG_FILE = "data/study_log.json"

def mood_message(mood):
    messages = {
        "Happy 😊": "Nice! Let’s use that energy and study well today 😊 you GOT THISSSSS 👊👊👊👊",
        "Neutral 😐": "Steady and calm — small progress today is still progress 🥳🥳🥳🥳🥳",
        "Tired 😞": "Take it slow. Try JUST one short session, then rest ☝️",
        "Stressed 😫": "Breathe. One Pomodoro at a time. You’ve got this. YOU CAN DO THISSSSS!!!!! 🤗🤗🤗🤗🤗",
        "Motivated 🥳": "Love the energy! Let’s complete a strong session today! GO KYLIEEEE GOOOOO 🏃🏃‍♀️"
    }
    return messages.get(mood, "")

def append_study_log(session_log):
    if session_log is None: 
        return 
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f: 
            json.dump([], f)
    
    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    logs.append(session_log)
    with open(LOG_FILE, "w") as f: 
        json.dump(logs, f, indent = 2)


def save_user_data(user_id, user_data):
    users = load_users()
    users[user_id] = user_data
    save_users(users)

def apply_inactivity_penalty_if_needed(user_data):
    try: 
        from src.auth import check_inactivity_penalty
        updated_user_data, msg = check_inactivity_penalty(user_data)
        return updated_user_data, msg
    
    except ImportError: 
        return user_data, None
    except Exception: 
        return user_data, None


def register_user():
    from src.auth import register
    user_id, user_data = register()
    if user_id: 
        user_data["user_id"] = user_id
    return user_id, user_data 


def login_user():
    from src.auth import login
    user_id, user_data = login()
    if user_id: 
        user_data["user_id"] = user_id
    return user_id, user_data

def handle_study_session(user_id, user_data):
    try: 
        from src.study import start_session
        user_data, session_log = start_session(user_data)
        return user_data, session_log
    except ImportError: 
        print("[TODO] Start study session will be connected (Person 4).") 
        pause()
        return user_data, None

def handle_feed_pet(user_id, user_data):
    user_data = feed_pet(user_data)
    return user_data

def handle_shop(user_id, user_data):
    user_data = open_shop(user_data)
    return user_data


def dashboard(user_id, user_data):

    while True: 
        title(f"StudyPet Dashboard - {user_data.get('name', 'User')}")
        
        show_user_summary(user_data)
        
        choice = menu("Select an action: ", ["Start Study Session ⏳", "Feed Pet 🍖", "Pet Shop 🛒", "View Pet Status 🐱", "View Stats 📊", "Logout 👋"])

        if choice == 1: 
            user_data ,session_log = handle_study_session(user_id, user_data)
            save_user_data(user_id, user_data)
            append_study_log(session_log)
            pause()

        elif choice == 2: 
            user_data = handle_feed_pet(user_id, user_data)
            save_user_data(user_id, user_data)
            pause()

        elif choice == 3: 
            user_data = handle_shop(user_id, user_data)
            save_user_data(user_id, user_data)
            pause()

        elif choice == 4: 
            show_status(user_data)
            pause()
        
        elif choice == 5: 
            show_user_stats(user_id, user_data)
            pause()

        elif choice == 6: 
            clear_screen()
            title("Logged out. Albida mere dost 👋")
            pause()
            return 
        
def main(): 
    while True: 
        title("StudyPet - Your Virtual Study Companion")
        choice = menu("Main Menu: ", ["Register 📝", "Login 💻", "Exit 🚪"])

        if choice == 1: 
            user_id, user_data = register_user()
            if user_id: 
                save_user_data(user_id, user_data)
                dashboard(user_id, user_data)

        elif choice == 2: 
            user_id, user_data = login_user()
            if user_id: 
                #penalty given 
                user_data, penatly_msg = apply_inactivity_penalty_if_needed(user_data)
                if penatly_msg: 
                    title("Inactivity Penalty Applied")
                    print(penatly_msg)
                    pause()
                
                #choose mood 
                mood = choose_mood(menu)
                if mood != "Skip": 
                    user_data["mood_today"] = mood
                    title("Mood Check-in 🤗")
                    print(mood_message(mood))
                    pause()

                save_user_data(user_id, user_data)    
                dashboard(user_id, user_data)

        elif choice == 3: 
            title("Come back soon! I'll be waiting for you!")
            break 

if __name__ == "__main__": 
    main()