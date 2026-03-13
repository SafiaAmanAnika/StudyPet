from src.interface.ui import (
    menu,
    pause,
    show_user_summary,
    show_user_stats,
    choose_mood,
    clear_screen,
    reflection_menu,
    print_fancy_box,
    print_brand_header,
    print_intro_splash,
    choose_theme,
    choose_animation_style,
    set_ui_theme,
    get_theme_display_name,
)
from src.pet.animation import set_animation_style, get_animation_style_display
from src.system.storage import load_users, save_users
from src.pet import show_status, apply_pet_abilities
from src.core.shop import feed_pet, open_shop
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
from src.core.analytics import run as analytics_run
from src.study.weekly_report import run as weekly_run 
from src.pet.evolution import check_pet_evolution
from src.study.study_planner import main_menu as study_planner_menu
from src.study.user_reflection import handle_post_study, handle_view_achievements, handle_view_journal_history
from src.system.navigation import install_global_navigation_input, NavigateBack, ExitApplication
from src.audio.ui_sfx import play_ui_click, play_ui_back
from src.audio.soundscape import (
    ensure_user_sound_defaults,
    apply_user_soundscape,
    stop_soundscape,
    get_ambience_display_name,
    soundscape_available,
)

import json, os
from datetime import date, timedelta

install_global_navigation_input()

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(_HERE, "data")

LOG_FILE = os.path.join(_DATA, "study_log.json")
QUIZ_FILE = os.path.join(_DATA, "quiz_marks.json")
MOOD_FILE = os.path.join(_DATA, "mood_log.json")
WEEKLY_REPORT_FILE = os.path.join(_DATA, "weekly_reports.json")


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
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
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


def _safe_load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _safe_save_json(path, data):
    try:
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except OSError:
        return False


def _migrate_user_key_file(path, old_user_id, new_user_id):
    db = _safe_load_json(path, {})
    if not isinstance(db, dict) or old_user_id not in db or old_user_id == new_user_id:
        return

    old_records = db.pop(old_user_id)
    if new_user_id in db and isinstance(db[new_user_id], list) and isinstance(old_records, list):
        db[new_user_id].extend(old_records)
    elif new_user_id not in db:
        db[new_user_id] = old_records

    _safe_save_json(path, db)


def _migrate_study_log_user_ids(old_user_id, new_user_id):
    logs = _safe_load_json(LOG_FILE, [])
    if not isinstance(logs, list) or old_user_id == new_user_id:
        return

    changed = False
    for entry in logs:
        if isinstance(entry, dict) and entry.get("user_id") == old_user_id:
            entry["user_id"] = new_user_id
            changed = True

    if changed:
        _safe_save_json(LOG_FILE, logs)


def migrate_user_identity_data(old_user_id, new_user_id):
    if old_user_id == new_user_id:
        return
    _migrate_study_log_user_ids(old_user_id, new_user_id)
    _migrate_user_key_file(MOOD_FILE, old_user_id, new_user_id)
    _migrate_user_key_file(WEEKLY_REPORT_FILE, old_user_id, new_user_id)


def _prompt_non_empty_value(prompt, error_title):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        clear_screen()
        print_fancy_box(error_title, ["This field cannot be empty."], theme="yellow")


def _prompt_goal_hours():
    while True:
        raw = input("📘 Enter new daily study hours (1-24): ").strip()
        if raw.isdigit():
            hours = int(raw)
            if 1 <= hours <= 24:
                return hours

        clear_screen()
        print_fancy_box(
            "Invalid Daily Goal",
            ["Please enter a whole number from 1 to 24."],
            theme="yellow",
        )


def _volume_to_percent(value):
    return int(round(float(value) * 100.0))


def _prompt_volume(label):
    while True:
        raw = input(f"🔉 Enter {label} volume (0-100): ").strip()
        if raw.isdigit():
            pct = int(raw)
            if 0 <= pct <= 100:
                return pct / 100.0

        clear_screen()
        print_fancy_box(
            "Invalid Volume",
            ["Please enter a whole number from 0 to 100."],
            theme="yellow",
        )


def _soundscape_status_lines(user_data):
    music_enabled = user_data.get("music_enabled", True)
    ambience_enabled = user_data.get("ambience_enabled", False)
    ambience_type = get_ambience_display_name(user_data.get("ambience_type", "rain"))

    return [
        f"Lofi Music      : {'ON' if music_enabled else 'OFF'}",
        f"Music Volume    : {_volume_to_percent(user_data.get('music_volume', 0.35))}%",
        f"Ambience        : {'ON' if ambience_enabled else 'OFF'}",
        f"Ambience Type   : {ambience_type}",
        f"Ambience Volume : {_volume_to_percent(user_data.get('ambience_volume', 0.30))}%",
    ]


def _save_soundscape_settings(user_id, user_data):
    ensure_user_sound_defaults(user_data)
    save_user_data(user_id, user_data)


def handle_soundscape_studio(user_id, user_data):
    ensure_user_sound_defaults(user_data)

    try:
        while True:
            clear_screen()
            lines = _soundscape_status_lines(user_data)
            lines.append(f"Audio Engine    : {'READY' if soundscape_available() else 'UNAVAILABLE'}")
            lines.append("")
            lines.append("Tip: combine lofi + ambience for a cozy study vibe.")
            print_fancy_box("Soundscape Studio 🎧", lines, theme="cyan")

            sound_choice = menu([
                "Toggle Lofi Music",
                "Set Lofi Volume",
                "Toggle Ambience",
                "Choose Ambience Type",
                "Set Ambience Volume",
                "Preview Current Soundscape",
                "Stop Soundscape Now",
                "Back",
            ])
            clear_screen()

            if sound_choice == 1:
                user_data["music_enabled"] = not user_data.get("music_enabled", True)
                _save_soundscape_settings(user_id, user_data)
                print_fancy_box(
                    "Lofi Updated ✨",
                    [f"Lofi Music is now {'ON' if user_data['music_enabled'] else 'OFF'}."],
                    theme="green",
                )
                pause()

            elif sound_choice == 2:
                user_data["music_volume"] = _prompt_volume("lofi")
                _save_soundscape_settings(user_id, user_data)
                clear_screen()
                print_fancy_box(
                    "Lofi Volume Updated ✨",
                    [f"Music volume: {_volume_to_percent(user_data['music_volume'])}%"],
                    theme="green",
                )
                pause()

            elif sound_choice == 3:
                user_data["ambience_enabled"] = not user_data.get("ambience_enabled", False)
                _save_soundscape_settings(user_id, user_data)
                print_fancy_box(
                    "Ambience Updated ✨",
                    [f"Ambience is now {'ON' if user_data['ambience_enabled'] else 'OFF'}."],
                    theme="green",
                )
                pause()

            elif sound_choice == 4:
                ambience_choice = menu([
                    "Rain 🌧️",
                    "Ocean Waves 🌊",
                    "Fire Crackling 🔥",
                    "None",
                    "Back",
                ])

                if ambience_choice == 1:
                    user_data["ambience_type"] = "rain"
                    user_data["ambience_enabled"] = True
                elif ambience_choice == 2:
                    user_data["ambience_type"] = "ocean"
                    user_data["ambience_enabled"] = True
                elif ambience_choice == 3:
                    user_data["ambience_type"] = "fire"
                    user_data["ambience_enabled"] = True
                elif ambience_choice == 4:
                    user_data["ambience_type"] = "none"
                    user_data["ambience_enabled"] = False
                elif ambience_choice == 0:
                    continue

                _save_soundscape_settings(user_id, user_data)
                clear_screen()
                print_fancy_box(
                    "Ambience Type Updated ✨",
                    [f"Current ambience: {get_ambience_display_name(user_data['ambience_type'])}"],
                    theme="green",
                )
                pause()

            elif sound_choice == 5:
                user_data["ambience_volume"] = _prompt_volume("ambience")
                _save_soundscape_settings(user_id, user_data)
                clear_screen()
                print_fancy_box(
                    "Ambience Volume Updated ✨",
                    [f"Ambience volume: {_volume_to_percent(user_data['ambience_volume'])}%"],
                    theme="green",
                )
                pause()

            elif sound_choice == 6:
                _save_soundscape_settings(user_id, user_data)
                ok = apply_user_soundscape(user_data)
                if ok:
                    print_fancy_box(
                        "Preview Playing ▶",
                        ["Current soundscape settings are now active."],
                        theme="green",
                    )
                else:
                    print_fancy_box(
                        "Sound Unavailable",
                        ["Pygame audio is not available in this runtime."],
                        theme="yellow",
                    )
                pause()

            elif sound_choice == 7:
                stop_soundscape()
                print_fancy_box(
                    "Soundscape Stopped",
                    ["All ambient music has been stopped for now."],
                    theme="yellow",
                )
                pause()

            elif sound_choice == 0:
                return user_data
    finally:
        # Keep preview playback scoped to this studio screen only.
        stop_soundscape()


def handle_change_name(user_id, user_data):
    clear_screen()
    print_fancy_box(
        "Change Name 👤",
        [f"Current Name: {user_data.get('name', 'User')}", "Enter your new display name."],
        theme="blue",
    )
    new_name = _prompt_non_empty_value("📝 New name                     : ", "Invalid Name")
    user_data["name"] = new_name
    save_user_data(user_id, user_data)

    clear_screen()
    print_fancy_box("Name Updated ✅", [f"New Name: {new_name}"], theme="green")
    pause()
    return user_data


def handle_change_email(user_id, user_data):
    from src.system.auth import EMAIL_REGEX, masked_input, verify_password

    clear_screen()
    print_fancy_box(
        "Change Email 📧",
        [f"Current Email: {user_id}", "Enter a new email for your account."],
        theme="blue",
    )

    new_email = input("📧 New email address            : ").strip().lower()
    if not new_email:
        clear_screen()
        print_fancy_box("No Changes", ["Email update cancelled."], theme="yellow")
        pause()
        return user_id, user_data

    if new_email == user_id:
        clear_screen()
        print_fancy_box("No Changes", ["That is already your current email."], theme="yellow")
        pause()
        return user_id, user_data

    if not EMAIL_REGEX.fullmatch(new_email):
        clear_screen()
        print_fancy_box("Invalid Email", ["Please enter a valid email address."], theme="yellow")
        pause()
        return user_id, user_data

    users = load_users()
    if new_email in users:
        clear_screen()
        print_fancy_box(
            "Email In Use",
            ["This email is already registered.", "Please choose another one."],
            theme="yellow",
        )
        pause()
        return user_id, user_data

    password = masked_input("🔑 Enter current password       : ")
    if not verify_password(password, user_data["password_salt"], user_data["password_hash"]):
        clear_screen()
        print_fancy_box("Wrong Password", ["Email update cancelled."], theme="magenta")
        pause()
        return user_id, user_data

    latest_data = users.get(user_id, user_data)
    users[new_email] = latest_data
    if user_id in users:
        del users[user_id]
    save_users(users)

    migrate_user_identity_data(user_id, new_email)

    clear_screen()
    print_fancy_box(
        "Email Updated ✅",
        [f"Old Email: {user_id}", f"New Email: {new_email}"],
        theme="green",
    )
    pause()
    return new_email, latest_data


def handle_change_password(user_id, user_data):
    from src.system.auth import masked_input, verify_password, is_valid_password, hash_password

    clear_screen()
    print_fancy_box(
        "Change Password 🔒",
        [
            "Use a strong password:",
            "- Minimum 8 characters",
            "- At least 1 capital letter",
            "- At least 1 number",
        ],
        theme="blue",
    )

    current_password = masked_input("🔑 Enter current password       : ")
    if not verify_password(current_password, user_data["password_salt"], user_data["password_hash"]):
        clear_screen()
        print_fancy_box("Wrong Password", ["Password update cancelled."], theme="magenta")
        pause()
        return user_data

    new_password = masked_input("🆕 Enter new password           : ")
    if not is_valid_password(new_password):
        clear_screen()
        print_fancy_box(
            "Weak Password",
            ["Password must be 8+ chars with 1 capital letter and 1 number."],
            theme="yellow",
        )
        pause()
        return user_data

    if verify_password(new_password, user_data["password_salt"], user_data["password_hash"]):
        clear_screen()
        print_fancy_box(
            "No Reuse Allowed",
            ["New password must be different from your current password."],
            theme="yellow",
        )
        pause()
        return user_data

    confirm_password = masked_input("🆕 Confirm new password         : ")
    if new_password != confirm_password:
        clear_screen()
        print_fancy_box("Mismatch", ["Passwords did not match."], theme="yellow")
        pause()
        return user_data

    salt, password_hash = hash_password(new_password)
    user_data["password_salt"] = salt
    user_data["password_hash"] = password_hash
    save_user_data(user_id, user_data)

    clear_screen()
    print_fancy_box("Password Updated ✅", ["Your password has been changed."], theme="green")
    pause()
    return user_data


def handle_change_pet(user_id, user_data):
    clear_screen()
    print_fancy_box(
        "Change Pet 🐾",
        [f"Current Pet: {user_data.get('pet_theme', 'Cat')}", "Pick your new pet companion."],
        theme="blue",
    )

    pet_choice = menu(["Cat 😸", "Dog 🐶", "Bunny 🐰", "Back"])
    if pet_choice == 0:
        return user_data

    pet_mapping = {
        1: "Cat",
        2: "Dog",
        3: "Bunny",
    }
    selected_pet = pet_mapping.get(pet_choice, user_data.get("pet_theme", "Cat"))
    user_data["pet_theme"] = selected_pet
    save_user_data(user_id, user_data)

    clear_screen()
    print_fancy_box("Pet Updated ✅", [f"New Pet Theme: {selected_pet}"], theme="green")
    show_status(user_data)
    pause()
    return user_data


def handle_change_daily_goal(user_id, user_data):
    from src.system.auth import assign_personality

    clear_screen()
    print_fancy_box(
        "Change Daily Goal 📘",
        [
            f"Current Daily Goal: {user_data.get('goal_hours', '?')} hours",
            "Set a new study target for each day.",
        ],
        theme="blue",
    )
    new_goal_hours = _prompt_goal_hours()

    user_data["goal_hours"] = new_goal_hours
    user_data["pet_personality"] = assign_personality(new_goal_hours)
    save_user_data(user_id, user_data)

    clear_screen()
    print_fancy_box(
        "Daily Goal Updated ✅",
        [
            f"New Daily Goal: {new_goal_hours} hours",
            f"Pet Personality: {user_data.get('pet_personality', 'Neutral')}",
        ],
        theme="green",
    )
    pause()
    return user_data


def handle_change_academic_goal(user_id, user_data):
    clear_screen()
    print_fancy_box(
        "Change Academic Goal 🎯",
        [
            f"Current Goal: {user_data.get('academic_goal', 'Not set')}",
            "Write your updated academic target.",
        ],
        theme="blue",
    )

    new_goal = _prompt_non_empty_value("🎯 New academic goal            : ", "Invalid Goal")
    user_data["academic_goal"] = new_goal
    save_user_data(user_id, user_data)

    clear_screen()
    print_fancy_box("Academic Goal Updated ✅", [f"New Goal: {new_goal}"], theme="green")
    pause()
    return user_data


def handle_theme_studio(user_id, user_data):
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
            return user_data


def handle_settings(user_id, user_data):
    while True:
        ensure_user_sound_defaults(user_data)
        clear_screen()
        print_fancy_box(
            "Settings ⚙️",
            [
                f"Email         : {user_id}",
                f"Name          : {user_data.get('name', 'User')}",
                f"Pet           : {user_data.get('pet_theme', 'Cat')}",
                f"Daily Goal    : {user_data.get('goal_hours', '?')} hours",
                f"Academic Goal : {user_data.get('academic_goal', 'Not set')}",
                f"Lofi Music    : {'ON' if user_data.get('music_enabled', True) else 'OFF'}",
                f"Ambience      : {get_ambience_display_name(user_data.get('ambience_type', 'rain')) if user_data.get('ambience_enabled', False) else 'OFF'}",
            ],
            theme="green",
        )

        settings_choice = menu([
            "Change Name",
            "Change Email",
            "Change Password",
            "Change Pet",
            "Change Daily Goal",
            "Change Academic Goal",
            "Theme Studio",
            "Soundscape Studio",
            "Delete Account",
            "Back",
        ])

        clear_screen()
        if settings_choice == 1:
            user_data = handle_change_name(user_id, user_data)
        elif settings_choice == 2:
            user_id, user_data = handle_change_email(user_id, user_data)
        elif settings_choice == 3:
            user_data = handle_change_password(user_id, user_data)
        elif settings_choice == 4:
            user_data = handle_change_pet(user_id, user_data)
        elif settings_choice == 5:
            user_data = handle_change_daily_goal(user_id, user_data)
        elif settings_choice == 6:
            user_data = handle_change_academic_goal(user_id, user_data)
        elif settings_choice == 7:
            user_data = handle_theme_studio(user_id, user_data)
        elif settings_choice == 8:
            user_data = handle_soundscape_studio(user_id, user_data)
        elif settings_choice == 9:
            deleted = handle_delete_account(user_id, user_data)
            if deleted:
                return user_id, user_data, True
        elif settings_choice == 0:
            return user_id, user_data, False

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
    session_units = session_log.get("sessions_completed", 1)
    try:
        session_units = int(session_units)
    except (TypeError, ValueError):
        session_units = 1
    session_count = count_today_sessions(user_id) + max(1, session_units)

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

    confirm_choice = menu([
        "Yes, permanently delete my account",
        "Cancel",
    ])

    if confirm_choice == 0:
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
    stop_soundscape()
    print_fancy_box(
        "Account Deleted 👋",
        ["Your account has been permanently deleted.", "Goodbye!"],
        theme="magenta",
    )
    pause()
    return True


# ---------------- DASHBOARD ---------------- #


def dashboard(user_id, user_data):
    ensure_user_sound_defaults(user_data)
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
                "[12] Settings ⚙️",
                "[0] Logout 👋",
            ]
            print_fancy_box("Your virtual pet awaits!", dashboard_options, theme="cyan")
            print("Tip: type ':back' to return to dashboard, ':exit' to close the app.")

            choice = input("Choose your option              : ").strip()
            clear_screen()

            if choice in {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"}:
                play_ui_click()
            elif choice == "0":
                play_ui_back()

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
                        user_data = handle_post_study(user_data, user_id=user_id)
                        save_user_data(user_id, user_data)
                        pause()
                    elif reflection_choice == 2:
                        user_data = handle_view_achievements(user_data, user_id=user_id)
                        save_user_data(user_id, user_data)
                        pause()
                    elif reflection_choice == 3:
                        user_data = handle_view_journal_history(user_data)
                        save_user_data(user_id, user_data)
                        pause()
                    elif reflection_choice == 0:
                        break

            elif choice == "12":
                user_id, user_data, deleted = handle_settings(user_id, user_data)
                if deleted:
                    return

            elif choice == "0": 
                stop_soundscape()
                clear_screen()
                print_fancy_box(
                    "Logged Out 👋",
                    ["Alvida mere dost! See you soon in StudyPet."],
                    theme="green",
                )
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
    set_ui_theme("pastel_pink")
    set_animation_style("sparkly")
    print_intro_splash()
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

            if choice in {"1", "2"}:
                play_ui_click()
            elif choice == "0":
                play_ui_back()

            if choice == "1": 
                user_id, user_data = register_user()
                if user_id: 
                    ensure_user_sound_defaults(user_data)
                    save_user_data(user_id, user_data)
                    set_ui_theme(user_data.get("ui_theme", "pastel_pink"))
                    set_animation_style(user_data.get("animation_style", "sparkly"))
                    dashboard(user_id, user_data)

            elif choice == "2": 
                user_id, user_data = login_user()
                if user_id: 
                    ensure_user_sound_defaults(user_data)
                    save_user_data(user_id, user_data)
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
                stop_soundscape()
                clear_screen()
                break
        except NavigateBack:
            clear_screen()
            continue
        except ExitApplication:
            stop_soundscape()
            clear_screen()
            break

if __name__ == "__main__": 
    main()