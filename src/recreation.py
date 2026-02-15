import time
import random 
from src.ui import clear_screen
from src.wellbeing import load_study_logs, today_str, tired_streak_days

#counting sessions 
def count_today_sessions(user_id: str) -> int: 
    logs = load_study_logs()
    today = today_str

    count = 0
    for log in logs: 
        if isinstance(log, dict) and log.get("user_id") == user_id and log.get("date") == today:
            count += 1
    return count 

#meditation

def meditation_menu():
    print("\n🌿 Meditation Zone")
    print("1. Mindfulness Meditation")
    print("2. Guided Meditation")
    print("3. Body Scan Meditation")
    print("4. Short Meditation")
    print("5. Back")

    choice = input("Choose a meditation type fren: ").strip()

    if choice == "1":
        mindfulness_meditation()
    elif choice == "2": 
        guided_meditation()
    elif choice == "3":
        body_scan_meditation()
    elif choice == "4": 
        short_meditation()
    elif choice == "5":
        print("Going back ... ")
        return 
    else: 
        print("❌ Invalid choice. Please try again.")
        meditation_menu()

def mindfulness_meditation():
    print("\n🧘 Mindfulness Meditation (5-10 minutes)")
    print("1. Find a quiet space and sit comfortably with your back straight.")
    time.sleep(5)
    print("2. Close your eyes and focus on your breathing.")
    time.sleep(5)
    print("3. Feel the air entering and leaving your body.")
    time.sleep(5)
    print("4. Acknowledge thoughts and distractions without judgment, then return focus to your breath.")
    time.sleep(5)
    print("5. Stay present for 5-10 minutes.")
    time.sleep(15)

    input("\nPress Enter when you're ready to begin...")
    print("\nYou can start now. Focus on your breath...")
    time.sleep(5)  # Simulating a period of mindfulness.
    print("✨ Mindfulness meditation complete. Well done!")
    clear_screen()

def guided_meditation():
    print("\n🧘 Guided Meditation (5-10 minutes)")
    print("1. Find a comfortable position, either sitting or lying down.")
    time.sleep(5)
    print("2. Close your eyes and relax.")
    time.sleep(5)
    print("3. Breathe in deeply and slowly through your nose... (Pause 4 seconds)")
    time.sleep(4)
    print("4. Hold your breath for a moment... (Pause 4 seconds)")
    time.sleep(4)
    print("5. Exhale slowly... (Pause 8 seconds)")
    time.sleep(8)
    print("6. Repeat this process, focusing on your breathing.")
    
    input("\nPress Enter when you're ready to begin...")
    print("\nYou can start now. Focus on your breath...")
    time.sleep(15)  # Simulating the meditation session.
    print("✨ Guided meditation complete. Well done!")
    time.sleep(1)
    clear_screen()

def body_scan_meditation():
    print("\n🧘 Body Scan Meditation (5-10 minutes)")
    print("1. Lie down in a quiet place or sit comfortably.")
    time.sleep(5)
    print("2. Close your eyes and take deep breaths.")
    time.sleep(5)
    print("3. Focus on the top of your head. Feel any tension, breathe into it, and release.")
    time.sleep(5)
    print("4. Move down to your face, noticing any tension. Breathe deeply and relax.")
    time.sleep(5)
    print("5. Continue focusing on each part of your body, from your neck to your shoulders, arms, chest, abdomen, legs, and feet.")
    time.sleep(6)
    print("6. With each exhale, visualize tension leaving the body part you're focusing on.")
    time.sleep(5)
    
    input("\nPress Enter when you're ready to begin...")
    print("\nYou can start now. Focus on each body part...")
    time.sleep(5)  # Simulating the body scan session.
    print("✨ Body scan meditation complete. Well done!")
    time.sleep(1)
    clear_screen()


def short_meditation():
    print("\n🧘 GUIDED BREATHING --- 1 minute ")
    for _ in range(3):
        print("Inhale ... 😌")
        time.sleep(3)
        print("Hold ... ")
        time.sleep(2)
        print("Exhale ... 😮‍💨")
        time.sleep(5)
    print("✨ Meditation completed. Sparkle sparkle ✨✨")
    time.sleep(1)
    clear_screen()

#game yey 
def mini_game():
    secret = random.randint(1, 10)
    print("\n🎮 Guess the number (1–10). You have ONLY 3 tries.")

    for _ in range(3):
        try: 
            guess = int(input("Your guess: "))
        except: 
            print("Invalid input.")
            continue 

        if guess == secret: 
            print("🎉 Correct answerrrr! You win!!!! YOU ROCKKKKK !!!")
            return 
        elif guess < secret: 
            print("Too low! Try again ~")
        else: 
            print("Too high! Try again ~")
        
    print(f"😭 youuuu lostttttttt brooo; the correct answer was {secret}")
    time.sleep(2)
    clear_screen()

def recreation_menu(user_id: str):
    sessions = count_today_sessions(user_id)
    tired_streak = tired_streak_days(user_id)

    #unless you finish 3 sessions or more you can't access this feature
    if tired_streak >= 5 or sessions >= 3: 
        print(f"\n 🌿 Recreation Zone Unlocked!!!")
        while True: 
            print("Welcome to Recreation Menu!")
            print("Choose of the following ~")
            print("1. Guided meditation")
            print("2. Mini game")
            print("3. Back")

            choice = input("Choose: ").strip()
            if choice == "1":
                meditation_menu()
            elif choice == "2":
                mini_game()
            elif choice == "3":
                return
            else:
                print("❌ Invalid choice.")
    else: 
                print(f"\n🔒 Recreation locked. im so sorryyy ☹️. Complete {3- sessions} more today to access it 🤗")
