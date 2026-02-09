from src.ui import clear_screen
import time, os 

DEV_MODE = True

MAX_STUDY_MIN = 180
MAX_BREAK_MIN = 60

CAT_FRAMES = {
    "Happy": [
        " /\\_/\\   ♪\n( ^.^ )\n >  ^  <",
        " /\\_/\\   ♪\n( ^o^ )\n >  ^  <",
        " /\\_/\\   ♪\n( ^.^ )\n >  o  <",
    ],
    "Neutral": [
        " /\\_/\\\n( -.- )\n >  ^  <",
        " /\\_/\\\n( -_- )\n >  ^  <",
        " /\\_/\\\n( -.- )\n >  _  <",
    ],
    "Tired": [
        " /\\_/\\  zZ\n( -.- )\n >  ^  <",
        " /\\_/\\  zZ\n( -_- )\n >  ^  <",
        " /\\_/\\  zZ\n( -.- )\n >  _  <",
    ],
    "Stressed": [
        " /\\_/\\  !!!\n( o.O )\n >  ^  <",
        " /\\_/\\  !!!\n( O.o )\n >  ^  <",
        " /\\_/\\  !!!\n( o.O )\n >  _  <",
    ],
    "Motivated": [
        " /\\_/\\  🔥\n( >.< )\n >  ^  <",
        " /\\_/\\  🔥\n( >o< )\n >  ^  <",
        " /\\_/\\  🔥\n( >.< )\n >  o  <",
    ],
}


#animating the part
def animated_countdown(seconds: int, label: str, mood: str = "Neutral") -> bool:
    if seconds <= 0:
        return True

    frames = CAT_FRAMES.get(mood, CAT_FRAMES["Neutral"])
    frame_i = 0

    try:
        for remaining in range(seconds, 0, -1):
            mins = remaining // 60
            secs = remaining % 60
            time_str = f"{mins:02d}:{secs:02d}"

            frame = frames[frame_i % len(frames)]
            frame_i += 1

            clear_screen()
            print(frame)
            print()
            print(f"{label} - time left: {time_str}")

            time.sleep(1)

        clear_screen()
        print(f"{label} finished. Well done!👍")
        return True

    except KeyboardInterrupt:
        clear_screen()
        print(f"{label} cancelled.")
        return False


# ═════════════════════════════ 
# CHANGE 1: Difficulty updated
# Now each difficulty has:
# - multiplier for coins
# - health decrease
# ═════════════════════════════                                                                                                                                             
DIFFICULTY = {
    "1": ("Easy", 1.0, 1),     # multiplier, health loss
    "2": ("Medium", 1.5, 2),
    "3": ("Hard", 2.0, 3)
}

#removes leading and trailing whitespace characters 
def trim(s):
    if s is None:
        return ""

    start = 0
    end = len(s) - 1

    while start <= end and s[start] in " \t\n\r":
        start += 1
    while end >= start and s[end] in " \t\n\r":
        end -= 1

    if start > end:
        return ""

    return s[start:end + 1]

#checks if the string contains only letters and spaces
def is_alpha_space(s):
    if s is None or s == "":
        return False

    for ch in s:
        if ch != " " and not ("a" <= ch <= "z") and not ("A" <= ch <= "Z"):
            return False
    return True

#keep asking the user for input until they give a valid topic
def get_topic(prompt):
    while True:
        t = trim(input(prompt))
        if t != "" and is_alpha_space(t):
            return t
        print("Use letters and spaces only.")
        
# Keep asking until user enters a valid choice from the allowed list
def get_choice(prompt, allowed):
    while True:
        v = trim(input(prompt))
        if v in allowed:
            return v
        print("Invalid choice, try again.")  

# Counts down from `seconds`, updating a MM:SS timer with `label` on the same line and prints finished message
def countdown(seconds, label):
    last_line = ""
    while seconds > 0:
        mins = seconds // 60
        secs = seconds % 60
        line = f"{label} - {mins:02}:{secs:02}"
        print(line, end="\r")
        last_line = line
        time.sleep(1)
        seconds -= 1

   
    # Clear last countdown line using its length (len)
    if last_line != "":
        print(" " * len(last_line), end="\r")

    print(label + " finished.")


def today_date_str():
    t = time.localtime()
    return f"{t.tm_year}-{t.tm_mon:02}-{t.tm_mday:02}"


def start_session(user_data):
    mood = user_data.get("mood_today", "Neutral")

# Ensure user has coins and health initialized
    if "coins" not in user_data:
        user_data["coins"] = 0
    if "health" not in user_data:
        user_data["health"] = 0

    topic = get_topic("Enter study topic: ")

# Difficulty selection
    print("╔════════════════════════════════╗")
    print("║           DIFFICULTY           ║")
    print("╚════════════════════════════════╝")
    print("[1] Easy\n[2] Medium\n[3] Hard")
    choice = get_choice("Choose a difficulty: ", {"1", "2", "3"})
    clear_screen()
    
    diff_name, diff_multiplier, health_loss = DIFFICULTY[choice]

# Pomodoro mode selection
    print("╔════════════════════════════════╗")
    print("║          POMODORO MODE         ║")
    print("╚════════════════════════════════╝")
    print("[1] 25 min Study/ 5 min Break\n[2] 50 min Study / 10 min Break \n[3] Custom\n[0] Cancel")
    pm = get_choice("Choose your option: ", {"1", "2", "3", "0"})
    clear_screen()

    if pm == "0":
        print("Session cancelled.")
        return user_data, None
    
# Set study and break times
    if pm == "1":
        study_minutes = 25
        break_minutes = 5
    elif pm == "2":
        study_minutes = 50
        break_minutes = 10
    elif pm == "3":
        while True:
            try:
                s = int(trim(input("Study minutes (1–180): ")))
                b = int(trim(input("Break minutes (0–60): ")))
            except:
                print("Enter valid integers.")
                continue

            if 1 <= s <= MAX_STUDY_MIN and 0 <= b <= MAX_BREAK_MIN:
                study_minutes = s
                break_minutes = b
                break
            print("Study: 1–180, Break: 0–60")
            
# DEV_MODE: 1 minute = 1 second for fast testing
    study_seconds = study_minutes if DEV_MODE else study_minutes * 60
    break_seconds = break_minutes if DEV_MODE else break_minutes * 60

    print("\nStarting study...")
    ok = animated_countdown(study_seconds, "Study", mood=mood)
    if not ok:
        print("Session cancelled. No rewards given.")
        return user_data, None

    if break_minutes > 0:
        ok = animated_countdown(break_seconds, "Break", mood="Neutral")
    if not ok:
        print("Break cancelled.")
        return user_data, None


    
    #  base coins = study_minutes
    #  coins earned = base coins * difficulty multiplier
    #  health decreased by difficulty health_loss
    
    base_coins = study_minutes
    coins_earned = int(base_coins * diff_multiplier)

    user_data["coins"] += coins_earned
    user_data["health"] -= health_loss
    if user_data["health"] < 0:
        user_data["health"] = 0

    
    #  Display the info
    
    print("\nSession complete!")
    print("Topic:", topic)
    print("Difficulty:", diff_name)
    print("Study time:", study_minutes, "minutes")
    print("Coins earned:", coins_earned)
    print("Health lost:", health_loss)
    print("Current coins:", user_data["coins"])
    print("Current health:", user_data["health"])

    session_log = {
        "user_id": user_data["user_id"],
        "date": today_date_str(),
        "topic": topic,
        "difficulty": diff_name,
        "study_minutes": study_minutes,
        "coins_earned": coins_earned,
        "health_lost": health_loss
    }

    return user_data, session_log