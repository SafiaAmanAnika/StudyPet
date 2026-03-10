from src.ui import (
    menu,
    pause,
    show_user_summary,
    show_user_stats,
    choose_mood,
    clear_screen,
    reflection_menu,
    print_fancy_box,
    print_brand_header,
    choose_theme,
    choose_animation_style,
    set_ui_theme,
    get_theme_display_name,
)
from src.pet.animation import set_animation_style, get_animation_style_display
from src.system.storage import load_users, save_users
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
from src.wellbeing.recreation import recreation_menu, count_today_sessions
from src.study.quiz import run as quiz_run
from src.analytics import run as analytics_run
from src.study.weekly_report import run as weekly_run 
from src.pet.evolution import check_pet_evolution
from src.study.study_planner import main_menu as study_planner_menu
from src.study.user_reflection import handle_post_study, handle_view_achievements
from src.system.navigation import install_global_navigation_input, NavigateBack, ExitApplication

import json, os
from datetime import date, timedelta

install_global_navigation_input()

LOG_FILE = "data/study_log.json"
QUIZ_FILE = "data/quiz_marks.json"


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

    # Recover from legacy/corrupted structure so Pomodoro writes never crash.
    if not isinstance(logs, list):
        if isinstance(logs, dict) and "subjects" in logs:
            os.makedirs(os.path.dirname(QUIZ_FILE), exist_ok=True)
            try:
                should_migrate = True
                if os.path.exists(QUIZ_FILE):
                    with open(QUIZ_FILE, "r") as qf:
                        existing = json.load(qf)
                    if isinstance(existing, dict) and existing.get("subjects"):
                        should_migrate = False
                if should_migrate:
                    with open(QUIZ_FILE, "w") as qf:
                        json.dump(logs, qf, indent=2)
            except (json.JSONDecodeError, OSError):
                pass

        backup_path = LOG_FILE + ".backup"
        try:
            if not os.path.exists(backup_path):
                with open(backup_path, "w") as bf:
                    json.dump(logs, bf, indent=2)
        except OSError:
            pass

        logs = []

    logs.append(session_log)

    with open(LOG_FILE, "w") as f: 
        json.dump(logs, f, indent = 2)


def save_user_data(user_id, user_data):
    users = load_users()
    users[user_id] = user_data
    save_users(users)

def register_user():
    from src.system.auth import register
    return register()

def login_user():
    from src.system.auth import login
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
    from src.pet.evolution import check_pet_evolution

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
    # Current session is not written to study_log yet, so include it here.
    session_count = count_today_sessions(user_id) + 1

    # ---------------- CHECK TIRED STREAK ----------------
    tired_streak = tired_streak_days(user_id)

    # ---------------- PET EVOLUTION CHECK ----------------
    user_data, evolved = check_pet_evolution(user_data, tired_streak)

    if evolved:
        print_fancy_box(
            "✨ YOUR PET EVOLVED! ✨",
            ["Your study companion grew stronger! 🐾📚"],
            theme="yellow",
        )

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
    print_fancy_box(
        "Short Check-In 🤗",
        ["Let’s capture your mood before the next study burst."],
        theme="green",
    )
    mood = choose_mood(menu)

    if mood != "Skip":
        user_data["mood_today"] = mood
        clear_screen()
        print_fancy_box("Mood Check-in 🤗", [mood_message(mood)], theme="yellow")
        pause()
        clear_screen()
        log_mood(user_id, mood)
    else:
        log_mood(user_id, user_data.get("mood_today", ""))
    
    user_data, penalty_message = apply_tired_penalty(user_id, user_data)
    if penalty_message: 
        print(f"Penalty message!! {penalty_message}")
        pause()
    
    recreation_menu(user_id)
    return user_data


def handle_delete_account(user_id, user_data):
    from src.system.auth import masked_input, verify_password
    clear_screen()
    print_fancy_box(
        "⚠️ DELETE ACCOUNT",
        [
            "This will permanently delete your account.",
            "This action cannot be undone!",
        ],
        theme="magenta",
    )
    confirm = input("Type 'DELETE' to confirm, or anything else to cancel: ").strip()
    if confirm != "DELETE":
        clear_screen()
        print_fancy_box("Cancelled", ["Account deletion cancelled."], theme="green")
        pause()
        return False

    password = masked_input("🔑 Enter your password to confirm: ")
    if not verify_password(password, user_data["password_salt"], user_data["password_hash"]):
        clear_screen()
        print_fancy_box("❌ Wrong Password", ["Account deletion cancelled."], theme="magenta")
        pause()
        return False

    users = load_users()
    if user_id in users:
        del users[user_id]
        save_users(users)

    clear_screen()
    print_fancy_box(
        "Account Deleted 👋",
        ["Your account has been permanently deleted.", "Goodbye!"],
        theme="magenta",
    )
    pause()
    return True


# ---------------- DASHBOARD ---------------- #


def dashboard(user_id, user_data):
    set_ui_theme(user_data.get("ui_theme", "pastel_pink"))
    set_animation_style(user_data.get("animation_style", "sparkly"))

    while True:
        try:
            clear_screen()
            print_fancy_box(
                "🐾 STUDYPET DASHBOARD 🐾",
                ["Your virtual pet is waiting. Let’s make today count."],
                theme="magenta",
            )
            show_user_summary(user_data)

            dashboard_options = [
                "[1] Start Study Session ⏳",
                "[2] Feed Pet 🍖",
                "[3] Pet Shop 🛒",
                "[4] View Pet Status 🐱",
                "[5] View User Status 📊",
                "[6] Mood Check-in 🌼",
                "[7] Study Performance Tracker 📚",
                "[8] Analytics 📈",
                "[9] Weekly Report 📅",
                "[10] Study Planner 🗓️  ",
                "[11] Reflection Journal 📓",
                "[12] Theme Studio 🎨",
                "[13] Delete Account 🗑️",
                "[0] Logout 👋",
            ]
            print_fancy_box("Your virtual pet awaits!", dashboard_options, theme="cyan")
            print("Tip: type ':back' to return to dashboard, ':exit' to close the app.")

            choice = input("Choose your option              : ").strip()
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
                study_planner_menu(user_id=user_id, user_data=user_data)

            elif choice == "11":
                while True:
                    reflection_choice = reflection_menu()
                    clear_screen()

                    if reflection_choice == 1:
                        user_data = handle_post_study(user_data)
                        save_user_data(user_id, user_data)
                        pause()
                    elif reflection_choice == 2:
                        user_data = handle_view_achievements(user_data)
                        save_user_data(user_id, user_data)
                        pause()
                    elif reflection_choice == 0:
                        break

            elif choice == "12":
                while True:
                    clear_screen()
                    print_fancy_box(
                        "Theme Studio 🎨",
                        [
                            f"Color Theme     : {get_theme_display_name(user_data.get('ui_theme', 'pastel_pink'))}",
                            f"Animation Style : {get_animation_style_display(user_data.get('animation_style', 'sparkly'))}",
                            "",
                            "Customize both colors and motion style.",
                        ],
                        theme="magenta",
                    )
                    studio_choice = menu([
                        "Change Color Theme",
                        "Change Animation Style",
                        "Back",
                    ])
                    clear_screen()

                    if studio_choice == 1:
                        selected_theme = choose_theme(menu)
                        if selected_theme:
                            user_data["ui_theme"] = selected_theme
                            save_user_data(user_id, user_data)
                            clear_screen()
                            print_fancy_box(
                                "Theme Updated ✨",
                                [f"Current theme: {get_theme_display_name(selected_theme)}"],
                                theme="magenta",
                            )
                            pause()
                    elif studio_choice == 2:
                        selected_style = choose_animation_style(menu)
                        if selected_style:
                            user_data["animation_style"] = selected_style
                            save_user_data(user_id, user_data)
                            clear_screen()
                            print_fancy_box(
                                "Animation Updated ✨",
                                [f"Current style: {get_animation_style_display(selected_style)}"],
                                theme="cyan",
                            )
                            pause()
                    elif studio_choice == 0:
                        break

            elif choice == "13":
                deleted = handle_delete_account(user_id, user_data)
                if deleted:
                    return

            elif choice == "0": 
                clear_screen()
                print("╔═════════════════════════════════════════════════════════════════════════╗")
                print("║                   Logged out. Alvida mere dost 👋                       ║")
                print("╚═════════════════════════════════════════════════════════════════════════╝")           
                pause()
                clear_screen()
                return
        except NavigateBack:
            clear_screen()
            print("↩ Returning to dashboard...")
            continue
        except ExitApplication:
            raise
        
def main(): 
    while True: 
        try:
            set_ui_theme("pastel_pink")
            set_animation_style("sparkly")
            clear_screen()
            print_brand_header()
            print_fancy_box(
                "MAIN MENU",
                [
                    "[1] Register 📝",
                    "[2] Login 💻",
                    "[0] Exit 🚪",
                ],
                theme="green",
            )
            print("Tip: type ':back' to refresh menu, ':exit' to close the app.")

            choice = input("Choose your option              : ").strip()

            if choice == "1": 
                user_id, user_data = register_user()
                if user_id: 
                    set_ui_theme(user_data.get("ui_theme", "pastel_pink"))
                    set_animation_style(user_data.get("animation_style", "sparkly"))
                    dashboard(user_id, user_data)

            elif choice == "2": 
                user_id, user_data = login_user()
                if user_id: 
                    set_ui_theme(user_data.get("ui_theme", "pastel_pink"))
                    set_animation_style(user_data.get("animation_style", "sparkly"))
                    mood = choose_mood(menu)
                    if mood != "Skip": 
                        user_data["mood_today"] = mood
                        print_fancy_box("Mood Check-in 🤗", [mood_message(mood)], theme="yellow")
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
        except NavigateBack:
            clear_screen()
            continue
        except ExitApplication:
            clear_screen()
            break

if __name__ == "__main__": 
    main()