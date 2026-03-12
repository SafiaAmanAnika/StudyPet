from src.interface.ui import clear_screen, print_fancy_box
from src.pet.animation import clear, render_countdown_scene
from src.audio.soundscape import ensure_user_sound_defaults, apply_user_soundscape, stop_soundscape
from .study_planner.study_planner_config_helpers import load_data as load_planner_data
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

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sound_path = os.path.join(project_root, "data", "sounds", filename)
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


def _safe_positive_int(value, default):
    try:
        parsed = int(value)
        if parsed > 0:
            return parsed
    except (TypeError, ValueError):
        pass
    return int(default)


def _planner_subject_choices():
    """Return planner-generated subjects with suggested timing/difficulty."""
    try:
        planner_data = load_planner_data()
    except Exception:
        return []

    study_plan = planner_data.get("study_plan", [])
    if not isinstance(study_plan, list) or not study_plan:
        return []

    subject_difficulty = planner_data.get("subject_difficulty", {})
    if not isinstance(subject_difficulty, dict):
        subject_difficulty = {}

    choices = []
    seen = set()

    for idx, session in enumerate(study_plan):
        if not isinstance(session, dict):
            continue

        session_type = str(session.get("type", "")).strip().lower()
        if session_type not in {"study", "revision"}:
            continue

        subject = trim(str(session.get("subject", "")))
        if subject == "" or subject.lower() == "break" or subject in seen:
            continue

        seen.add(subject)

        study_minutes = _safe_positive_int(session.get("duration"), 25)
        difficulty = str(subject_difficulty.get(subject, session.get("difficulty", "Medium"))).strip().title()
        if difficulty not in {"Easy", "Medium", "Hard"}:
            difficulty = "Medium"

        break_minutes = 5
        for later_session in study_plan[idx + 1:]:
            if not isinstance(later_session, dict):
                continue
            later_type = str(later_session.get("type", "")).strip().lower()
            if later_type == "break":
                break_minutes = _safe_positive_int(later_session.get("duration"), 5)
                break
            if later_type == "study":
                break

        choices.append(
            {
                "subject": subject,
                "difficulty": difficulty,
                "study_minutes": study_minutes,
                "break_minutes": break_minutes,
            }
        )

    return choices


def select_topic_from_plan_or_manual():
    planner_choices = _planner_subject_choices()

    if not planner_choices:
        return select_topic(), None

    while True:
        print_fancy_box(
            "TOPIC SOURCE",
            [
                "[1] Choose subject from Study Planner",
                "[2] Enter custom topic",
                "[0] Cancel",
            ],
            theme="cyan",
        )
        source_choice = get_choice("Choose topic source: ", {"1", "2", "0"})
        clear_screen()

        if source_choice == "0":
            return None, None

        if source_choice == "2":
            return select_topic(), None

        while True:
            lines = ["Choose the subject you are starting now:", ""]
            for i, item in enumerate(planner_choices, start=1):
                lines.append(
                    f"[{i}] {item['subject']} ({item['difficulty']} • {item['study_minutes']}m/{item['break_minutes']}m)"
                )
            lines.append("[0] Back")

            print_fancy_box("STUDY PLAN SUBJECTS", lines, theme="magenta")
            allowed = {str(i) for i in range(1, len(planner_choices) + 1)}
            allowed.add("0")
            picked_choice = get_choice("Choose your subject: ", allowed)
            clear_screen()

            if picked_choice == "0":
                break

            picked = planner_choices[int(picked_choice) - 1]
            return picked["subject"], picked


DIFFICULTY = {
    "1": ("Easy", 1.0, 1),     # multiplier, health loss
    "2": ("Medium", 1.5, 2),
    "3": ("Hard", 2.0, 3)
}

DIFFICULTY_BY_LABEL = {value[0]: value for value in DIFFICULTY.values()}


def select_difficulty(planner_difficulty=None):
    planner_difficulty = str(planner_difficulty or "").strip().title()

    if planner_difficulty in DIFFICULTY_BY_LABEL:
        print_fancy_box(
            "DIFFICULTY",
            [
                f"[1] Use Study Planner difficulty ({planner_difficulty})",
                "[2] Choose manually",
                "[0] Cancel",
            ],
            theme="yellow",
        )
        planner_choice = get_choice("Choose your option: ", {"1", "2", "0"})
        clear_screen()

        if planner_choice == "0":
            return None
        if planner_choice == "1":
            return DIFFICULTY_BY_LABEL[planner_difficulty]

    print_fancy_box(
        "DIFFICULTY",
        [
            "[1] Easy",
            "[2] Medium",
            "[3] Hard",
            "[0] Cancel",
        ],
        theme="yellow",
    )
    choice = get_choice("Choose a difficulty: ", {"1", "2", "3", "0"})
    clear_screen()

    if choice == "0":
        return None

    return DIFFICULTY[choice]  # returns (diff_name, diff_multiplier, health_loss)


def select_pomodoro(planner_study_minutes=None, planner_break_minutes=None):
    planner_study = _safe_positive_int(planner_study_minutes, 0)
    planner_break = 0
    if planner_study > 0:
        planner_break = _safe_positive_int(planner_break_minutes, 5)

    options = [
        "[1] 25 min Study / 5 min Break",
        "[2] 50 min Study / 10 min Break",
        "[3] Custom",
    ]
    allowed = {"1", "2", "3", "0"}

    if planner_study > 0:
        options.append(f"[4] Use Planner Session ({planner_study} min Study / {planner_break} min Break)")
        allowed.add("4")

    options.append("[0] Cancel")

    print_fancy_box(
        "POMODORO MODE",
        options,
        theme="green",
    )
    
    pm = get_choice("Choose your option: ", allowed)
    clear_screen()

    if pm == "0":
        return None, None  # canceled

    if pm == "1":
        return 25, 5
    elif pm == "2":
        return 50, 10
    elif pm == "4" and planner_study > 0:
        return planner_study, planner_break
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

    topic, planner_pick = select_topic_from_plan_or_manual()

    if topic is None:
        print("Session cancelled!")
        return user_data, None

    planner_difficulty = planner_pick.get("difficulty") if planner_pick else None
    difficulty_tuple = select_difficulty(planner_difficulty=planner_difficulty)
    if difficulty_tuple is None:
        print("Session cancelled!")
        return user_data, None

    diff_name, diff_multiplier, health_loss = difficulty_tuple

    planner_study_minutes = planner_pick.get("study_minutes") if planner_pick else None
    planner_break_minutes = planner_pick.get("break_minutes") if planner_pick else None
    study_minutes, break_minutes = select_pomodoro(planner_study_minutes, planner_break_minutes)

    if study_minutes is None:
        print("Session cancelled!")
        return user_data, None

    study_seconds = study_minutes if DEV_MODE else study_minutes * 60
    break_seconds = break_minutes if DEV_MODE else break_minutes * 60

    # Play ambience only while the Pomodoro countdowns are active.
    ensure_user_sound_defaults(user_data)
    apply_user_soundscape(user_data)
    try:
        ok = run_countdowns(study_seconds, break_seconds, mood, pet_type)
    finally:
        stop_soundscape()

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