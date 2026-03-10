from src.ui import clear_screen, print_fancy_box
from src.pet.animation import clear, render_countdown_scene
import time, os
import pygame

DEV_MODE = True

MAX_STUDY_MIN = 180
MAX_BREAK_MIN = 60

RAW_TO_BASE_MOOD = {
    "Happy 😊": "Happy",
    "Neutral 😐": "Neutral",
    "Tired 😞": "Tired",
    "Stressed 😫": "Stressed",
    "Motivated 🥳": "Motivated",
}

# ------------------ SOUND ------------------ #

pygame.mixer.init()

def play_pet_sound(pet_type: str):
    
    sound_map = {
        "Cat": "meow.mp3",
        "Dog": "woof.mp3",
        "Bunny": "bunny.mp3",
    }
    filename = sound_map.get(pet_type)
    if not filename:
        return

    sound_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sounds", filename)
    if not os.path.exists(sound_path):
        print(f"⚠️ Sound file not found: {sound_path}")
        return

    try:
        sound = pygame.mixer.Sound(sound_path)
        channel = sound.play()

        # Wait only for this sound's channel so ambient loops do not block forever.
        while channel is not None and channel.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"⚠️ Sound error: {e}")


# ------------------ UTILITY FUNCTIONS ------------------ #

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


def is_alpha_space(s):
    if s is None or s == "":
        return False

    for ch in s:
        if ch != " " and not ("a" <= ch <= "z") and not ("A" <= ch <= "Z"):
            return False
        
    return True


def get_topic(prompt):
    while True:
        t = trim(input(prompt))
        if t != "" and is_alpha_space(t):
            return t
        
        print("❌ Invalid choice. Use letters and spaces only.")
        print()
        

def get_choice(prompt, allowed):
    while True:
        v = trim(input(prompt))
        if v in allowed:
            return v
        
        print("❌ Invalid choice. Try again.")
        print()  


def today_date_str():
    t = time.localtime()
    return f"{t.tm_year}-{t.tm_mon:02}-{t.tm_mday:02}"


# ------------------ SESSION SELECTION ------------------ #

def select_topic():
    return get_topic("Enter study topic: ")


DIFFICULTY = {
    "1": ("Easy", 1.0, 1),     # multiplier, health loss
    "2": ("Medium", 1.5, 2),
    "3": ("Hard", 2.0, 3)
}


def select_difficulty():
    print_fancy_box(
        "DIFFICULTY",
        [
            "[1] Easy",
            "[2] Medium",
            "[3] Hard",
        ],
        theme="yellow",
    )
    choice = get_choice("Choose a difficulty: ", {"1", "2", "3"})
    clear_screen()
    return DIFFICULTY[choice]  # returns (diff_name, diff_multiplier, health_loss)


def select_pomodoro():
    print_fancy_box(
        "POMODORO MODE",
        [
            "[1] 25 min Study / 5 min Break",
            "[2] 50 min Study / 10 min Break",
            "[3] Custom",
            "[0] Cancel",
        ],
        theme="green",
    )
    
    pm = get_choice("Choose your option: ", {"1", "2", "3", "0"})
    clear_screen()

    if pm == "0":
        return None, None  # canceled

    if pm == "1":
        return 25, 5
    elif pm == "2":
        return 50, 10
    elif pm == "3":
        while True:
            try:
                s = int(trim(input("Study minutes (1–180): ")))
                b = int(trim(input("Break minutes  (0–60): ")))
            except (TypeError, ValueError):
                print("❌ Invalid input. Enter valid integers.\n")
                continue

            if 1 <= s <= MAX_STUDY_MIN and 0 <= b <= MAX_BREAK_MIN:
                return s, b
            print("Study: 1–180, Break: 0–60\n")


# ------------------ COUNTDOWNS ------------------ #


def animated_countdown(seconds: int, label: str, mood: str = "Neutral", pet_type: str = "Cat", level: int = 1) -> bool:
    if seconds <= 0:
        return True

    try:
        for remaining in range(seconds, 0, -1):
            mins = remaining // 60
            secs = remaining % 60
            time_str = f"{mins:02d}:{secs:02d}"

            scene = render_countdown_scene(label, time_str, pet_type, mood, level, remaining, seconds)

            clear()
            print(scene)

            time.sleep(1)

        clear()
        print(f"{label} finished. Well done!👍\n")
        return True

    except KeyboardInterrupt:
        clear()
        print(f"{label} cancelled.\n")
        return False


def run_countdowns(study_seconds, break_seconds, mood, pet_type):
    ok = animated_countdown(study_seconds, "Study", mood=mood, pet_type=pet_type)
    if not ok:
        print("Session cancelled! No rewards earned.\n")
        return False

    play_pet_sound(pet_type)  # 🔊 Plays fully after study ends

    if break_seconds > 0:
        ok = animated_countdown(break_seconds, "Break", mood=mood, pet_type=pet_type)
        if not ok:
            print("Break cancelled!\n")
            return False
        play_pet_sound(pet_type)  # 🔊 Plays fully after break ends

    return True


# ------------------ REWARDS ------------------ #

def calculate_rewards(user_data, study_minutes, diff_multiplier, health_loss):
    coins_earned = int(study_minutes * diff_multiplier)
    user_data["coins"] += coins_earned
    user_data["health"] -= health_loss
    if user_data["health"] < 0:
        user_data["health"] = 0
    return coins_earned


def display_session_summary(topic, diff_name, study_minutes, coins_earned, health_loss, user_data):
    print_fancy_box(
        "Session Complete ✅",
        [
            f"Topic          : {topic}",
            f"Difficulty     : {diff_name}",
            f"Study time     : {study_minutes} minutes",
            f"Coins earned   : {coins_earned}",
            f"Health lost    : {health_loss}",
            f"Current coins  : {user_data['coins']}",
            f"Current health : {user_data['health']}",
        ],
        theme="magenta",
    )


# ------------------ MAIN SESSION ------------------ #

def start_session(user_id, user_data):
    raw_mood = user_data.get("mood_today", "Neutral 😐")
    mood = RAW_TO_BASE_MOOD.get(raw_mood, "Neutral")
    pet_type = user_data.get("pet_theme", "Cat")

    user_data.setdefault("coins", 5)
    user_data.setdefault("health", 10)

    topic = select_topic()
    diff_name, diff_multiplier, health_loss = select_difficulty()
    study_minutes, break_minutes = select_pomodoro()

    if study_minutes is None:
        print("Session cancelled!")
        return user_data, None

    study_seconds = study_minutes if DEV_MODE else study_minutes * 60
    break_seconds = break_minutes if DEV_MODE else break_minutes * 60

    ok = run_countdowns(study_seconds, break_seconds, mood, pet_type)
    if not ok:
        return user_data, None

    coins_earned = calculate_rewards(user_data, study_minutes, diff_multiplier, health_loss)
    display_session_summary(topic, diff_name, study_minutes, coins_earned, health_loss, user_data)

    session_log = {
        "user_id": user_id,
        "date": today_date_str(),
        "topic": topic,
        "difficulty": diff_name,
        "study_minutes": study_minutes,
        "break_minutes": break_minutes,
        "coins_earned": coins_earned,
        "health_lost": health_loss,
        "mood": raw_mood
    }

    return user_data, session_log