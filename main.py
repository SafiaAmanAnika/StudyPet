from src.ui import title, menu, pause, show_user_summary, show_user_stats
import json 
import os

LOG_FILE = "data/study_log.json"

def append_study_log(session_log):
    if session_log is None: 
        return 
    if not os.path


def save_user_data(user_id, user_data):
    """
    Day 4: integration hook.
    Later this will call Person 2's load_users/save_users.
    """
    # TODO: replace with:
    # users = load_users()
    # users[user_id] = user_data
    # save_users(users)
    return


#todo 
def register_user():
    print("[TODO]")
    pause()
    return None 

#todo 
def login_user():
    print("[TODO]")
    pause()
    return None, None

def handle_study_session(user_id, user_data):
    # Later: from src.study import start_session
    print("[TODO] Start study session will be connected (Person 4).")
    session_log = None #later will be dict 
    pause()
    return user_data, session_log

def handle_feed_pet(user_id, user_data):
    # Later: from src.shop import feed_pet
    print("[TODO] Feed pet will be connected (Person 3).")
    pause()
    return user_data

def handle_shop(user_id, user_data):
    # Later: from src.shop import open_shop
    print("[TODO] Pet shop will be connected (Person 3).")
    pause()
    return user_data


def dashboard(user_id, user_data):

    while True: 
        title(f"StudyPet Dashboard - {user_data.get('name', 'User')}")
        
        show_user_summary(user_data)
        
        choice = menu("Select an action: ", ["Start Study Session", "Feed Pet", "Pet Shop", "View Stats", "Logout"])

        if choice == 1: 
            user_data ,session_log = handle_study_session(user_id, user_data)
            save_user_data(user_id, user_data)
            print("[TODO] connects study.start_session(user_data) (nuzhat)")
            pause()

        elif choice == 2: 
            user_data = handle_study_session(user_id, user_data)
            save_user_data(user_id, user_data)
            print("[TODO] connects shop.feed_pet(user_data) (riya)")
            pause()

        elif choice == 3: 
            user_data = handle_shop(user_id, user_data)
            save_user_data(user_id, user_data)
            print("[TODO] connects shop.open_shop(user_data) (riya)")
            pause()
        
        elif choice == 4: 
            show_user_stats(user_id, user_data)
            pause()

        elif choice == 5: 
            title("Logged out.")
            pause()
            return 
        
def main(): 
    while True: 
        title("StudyPet - Your Virtual Study Companion")
        choice = menu("Main Menu: ", ["Register", "Login", "Exit"])

        if choice == 1: 
            register_user()

        elif choice == 2: 
            user_id, user_data = login_user()
            if user_id: 
                dashboard(user_id, user_data)

        elif choice == 3: 
            title("Come back soon! I'll be waiting for you!")
            break 

if __name__ == "__main__": 
    main()