from src.ui import title, menu, pause 

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

def dashboard(user_id, user_data):
    while True: 
        title(f"StudyPet Dashboard - {user_data.get('name', 'User')}")
        choice = menu("Select an action: ", ["Start Study Session", "Feed Pet", "Pet Shop", "View Stats", "Logout"])

        if choice == 1: 
            print("[TODO]")
            pause()

        elif choice == 2: 
            print("[TODO]")
            pause()

        elif choice == 3: 
            print("[TODO]")
            pause()
        
        elif choice == 4: 
            print("[TODO]")
            pause()

        elif choice == 5: 
            print("[TODO]")
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