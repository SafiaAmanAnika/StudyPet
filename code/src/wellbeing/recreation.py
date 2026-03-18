import time
from src.custom.custom_random import randint
from src.interface.ui import clear_screen, print_fancy_box, menu, pause
from .wellbeing import load_study_logs, today_str, tired_streak_days

#counting sessions 
def count_today_sessions(user_id: str) -> int: 
    logs = load_study_logs()
    today = today_str()

    count = 0
    for log in logs: 
        if isinstance(log, dict) and log.get("user_id") == user_id and log.get("date") == today:
            sessions_completed = log.get("sessions_completed", 1)
            try:
                sessions_completed = int(sessions_completed)
            except (TypeError, ValueError):
                sessions_completed = 1
            count += max(1, sessions_completed)
    return count 

#meditation

def meditation_menu():
    while True:
        clear_screen()
        print_fancy_box(
            "🌿 Meditation Zone",
            ["Choose a guided break that matches your energy."],
            theme="blue",
        )
        choice = menu(
            [
                "Mindfulness Meditation",
                "Guided Meditation",
                "Body Scan Meditation",
                "Short Breathing Meditation",
                "Back",
            ]
        )

        if choice == 1:
            mindfulness_meditation()
        elif choice == 2:
            guided_meditation()
        elif choice == 3:
            body_scan_meditation()
        elif choice == 4:
            short_meditation()
        elif choice == 0:
            clear_screen()
            return


def _run_meditation_session(title: str, steps: list, focus_line: str, duration_seconds: int):
    clear_screen()
    print_fancy_box(title, steps, theme="blue")
    input("\nPress Enter when you're ready to begin... ")
    clear_screen()
    print_fancy_box("🫧 Focus Window", [focus_line], theme="green")
    time.sleep(duration_seconds)
    clear_screen()
    print_fancy_box("✨ Meditation Complete", ["Well done. Your mind got a reset."], theme="magenta")
    pause()
    clear_screen()

def mindfulness_meditation():
    _run_meditation_session(
        "🧘 Mindfulness Meditation (5-10 min)",
        [
            "1. Sit comfortably with your back straight.",
            "2. Close your eyes and focus on breathing.",
            "3. Observe breath in and out.",
            "4. Notice distractions, then return to breath.",
            "5. Stay present for a few calm minutes.",
        ],
        "Breathe naturally and stay present.",
        5,
    )

def guided_meditation():
    _run_meditation_session(
        "🧘 Guided Meditation (5-10 min)",
        [
            "1. Sit or lie down in a comfortable position.",
            "2. Close your eyes and relax your shoulders.",
            "3. Inhale slowly through your nose (4 sec).",
            "4. Hold your breath gently (4 sec).",
            "5. Exhale slowly (8 sec).",
            "6. Repeat with calm attention.",
        ],
        "Follow the guided rhythm: inhale, hold, exhale.",
        15,
    )

def body_scan_meditation():
    _run_meditation_session(
        "🧘 Body Scan Meditation (5-10 min)",
        [
            "1. Sit or lie down somewhere quiet.",
            "2. Take a few deep breaths.",
            "3. Scan from head to toe for tension.",
            "4. Relax each area as you exhale.",
            "5. Continue through shoulders, chest, legs, and feet.",
        ],
        "Move attention slowly through each body part.",
        5,
    )


def short_meditation():
    clear_screen()
    print_fancy_box(
        "🧘 Guided Breathing (1 min)",
        ["Follow 3 calm breathing cycles."],
        theme="blue",
    )
    for _ in range(3):
        print_fancy_box("Breathing", ["Inhale ... 😌"], theme="cyan")
        time.sleep(3)
        print_fancy_box("Breathing", ["Hold ..."], theme="cyan")
        time.sleep(2)
        print_fancy_box("Breathing", ["Exhale ... 😮‍💨"], theme="cyan")
        time.sleep(5)
    print_fancy_box("✨ Meditation Complete", ["Sparkle sparkle. Nice reset!"], theme="magenta")
    pause()
    clear_screen()

#game yey 
def mini_game():
    secret = randint(1, 10)
    clear_screen()
    print_fancy_box(
        "🎮 Mini Game: Guess The Number",
        ["Pick a number from 1 to 10.", "You have 3 tries."],
        theme="cyan",
    )

    for attempt in range(1, 4):
        try: 
            guess = int(input(f"Attempt {attempt}/3 - Your guess: "))
        except (TypeError, ValueError): 
            print_fancy_box("Invalid Input", ["Please enter a whole number."], theme="yellow")
            continue 

        if guess == secret: 
            print_fancy_box("🎉 You Win!", ["Correct answer! You rock!"], theme="green")
            pause()
            clear_screen()
            return 
        elif guess < secret: 
            print_fancy_box("Try Again", ["Too low!"], theme="yellow")
        else: 
            print_fancy_box("Try Again", ["Too high!"], theme="yellow")
        
    print_fancy_box("😿 Round Over", [f"The correct number was {secret}."], theme="magenta")
    pause()
    clear_screen()

def recreation_menu(user_id: str):
    sessions = count_today_sessions(user_id)
    tired_streak = tired_streak_days(user_id)

    #unless you finish 3 sessions or more you can't access this feature
    if tired_streak >= 5 or sessions >= 3: 
        while True: 
            clear_screen()
            print_fancy_box(
                "🌿 Recreation Zone Unlocked",
                ["Take a mindful pause before your next sprint."],
                theme="green",
            )
            print_fancy_box(
                "Recreation Menu",
                ["Pick a break activity:"],
                theme="cyan",
            )
            choice = menu(["Guided Meditation", "Mini Game", "Back"])

            if choice == 1:
                meditation_menu()
            elif choice == 2:
                mini_game()
            elif choice == 0:
                clear_screen()
                return
    else: 
        remaining = max(0, 3 - sessions)
        print_fancy_box(
            "🔒 Recreation Locked",
            [f"Complete {remaining} more session(s) today to unlock it."],
            theme="yellow",
        )
        pause()