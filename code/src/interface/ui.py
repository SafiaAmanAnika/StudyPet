import time
from src.custom.custom_text import count_emojis, visible_width


CURRENT_STYLE = "disabled"


def _safe_text(value):
    if value is None:
        return ""
    return str(value)


def _visual_width(text):
    text = _safe_text(text)
    # Treat emoji as double-width and ignore zero-width joiners/selectors.
    emoji_count = count_emojis(text)
    zero_width_count = text.count("\u200d") + text.count("\ufe0f")
    return len(text) + emoji_count - zero_width_count


def _truncate(text, width):
    if width <= 0:
        return ""
    text = _safe_text(text)
    if _visual_width(text) <= width:
        return text

    out = []
    cur_width = 0
    for ch in text:
        ch_width = visible_width(ch)
        if cur_width + ch_width > width:
            break
        out.append(ch)
        cur_width += ch_width
    return "".join(out)


def _pad(text, width):
    text = _truncate(text, width)
    spaces = max(0, width - _visual_width(text))
    return text + (" " * spaces)


def _paint(text: str, *styles: str) -> str:
    return text


def _paint_256(text: str, fg=None, bg=None, bold: bool = False, dim: bool = False) -> str:
    return text


def set_ui_theme(style_name: str) -> str:
    # Theme system removed; keep no-op for compatibility.
    CURRENT_STYLE = "disabled"
    return CURRENT_STYLE


def get_ui_theme() -> str:
    return CURRENT_STYLE


def get_theme_display_name(style_name: str) -> str:
    return "Disabled"


def list_theme_options():
    return []


def print_fancy_box(title: str, lines, width: int = 73, theme: str = "cyan"):
    w = max(20, int(width))
    horizontal = "━" * w
    print("┏" + horizontal + "┓")
    print("┃" + _pad(_safe_text(title), w) + "┃")
    print("┣" + horizontal + "┫")

    for line in lines:
        print("┃" + _pad(_safe_text(line), w) + "┃")

    print("┗" + horizontal + "┛")


def print_brand_header():
    lines = [
        "Where productivity meets your virtual companion",
        "Stay focused. Stay playful. Keep evolving.",
    ]
    print_fancy_box("STUDYPET", lines, width=73, theme="magenta")


def print_intro_splash():
    clear_screen()
    lines = [
        "Welcome to StudyPet",
        "Simple Text UI Mode",
        "No fancy visuals loaded",
    ]
    print_fancy_box("Launch", lines, width=73, theme="magenta")
    time.sleep(0.4)


def clear_screen():
    # Full clear: visible screen + scrollback + cursor home.
    print("\033[2J\033[3J\033[H", end="", flush=True)


def pause():
    try:
        input("\nPress Enter to continue...")
    except KeyboardInterrupt:
        print("\nExiting pause.")


def menu(options):
    while True:
        menu_lines = []
        for i, option in enumerate(options[:-1], start=1):
            menu_lines.append(f"[{i}] {_safe_text(option)}")
        menu_lines.append(f"[0] {_safe_text(options[-1])}")

        print_fancy_box("Choose An Option", menu_lines, width=73, theme="blue")
        choice = input("Choose your option: ").strip()

        if choice.isdigit():
            value = int(choice)
            if value == 0:
                return 0
            if 1 <= value < len(options):
                return value

        clear_screen()
        print("Invalid choice. Please try again.\n")


def choose_theme(menu_func):
    # Theme system removed.
    return None


def choose_animation_style(menu_func):
    from src.pet.animation import (
        list_animation_style_options,
        get_animation_style,
        get_animation_style_display,
        set_animation_style,
    )

    style_options = list_animation_style_options()
    options = [label for _, label in style_options] + ["Back"]

    lines = [
        f"Current Style: {get_animation_style_display(get_animation_style())}",
        "",
        "Pick the animation vibe for study countdown and evolution scenes.",
    ]
    print_fancy_box("Animation Studio", lines, theme="cyan")

    choice = menu_func(options)
    if choice == 0:
        return None

    selected_key, _ = style_options[choice - 1]
    set_animation_style(selected_key)
    return selected_key


def print_kv(label, value):
    print(f"{_safe_text(label):<15}: {_safe_text(value)}")


def show_user_summary(user_data):
    name = user_data.get("name", "User")
    health = user_data.get("health", 10)
    energy = user_data.get("energy", 100)
    coins = user_data.get("coins", 5)
    pet_theme = user_data.get("pet_theme", "Unknown")
    goal_hours = user_data.get("goal_hours", "?")
    academic_goal = user_data.get("academic_goal", "")
    pet_personality = user_data.get("pet_personality", "Neutral")
    mood = user_data.get("mood_today", "")

    health = max(0, min(20, int(health)))
    energy = max(0, min(100, int(energy)))
    health_bar_len = health
    energy_bar_len = energy // 5
    health_bar = "█" * health_bar_len + "░" * (20 - health_bar_len)
    energy_bar = "▓" * energy_bar_len + "▒" * (20 - energy_bar_len)

    lines = [
        f"Name          : {name}",
        f"Pet           : {pet_theme}",
        f"Personality   : {pet_personality}",
        f"Health        : {health}/20  [{health_bar}]",
        f"Energy        : {energy}/100 [{energy_bar}]",
        f"Coins         : {coins}",
        f"Daily Goal    : {goal_hours} hours",
    ]

    if mood:
        lines.insert(0, f"Mood Today    : {mood}")

    if academic_goal:
        lines.append(f"Academic Goal : {academic_goal}")

    if health <= 3:
        lines.append("⚠️ Pet is very weak. Feed it soon!")

    print_fancy_box("Quick Status", lines, theme="magenta")


def show_user_stats(user_id, user_data):
    lines = [
        f"🐱 Email         : {user_id}",
        f"🐱 Nickname      : {user_data.get('name', 'User')}",
        f"🐱 Goal Hours    : {user_data.get('goal_hours', '?')}",
        f"🐱 Academic Goal : {user_data.get('academic_goal', '')}",
        f"🐱 Pet Theme     : {user_data.get('pet_theme', 'Unknown')}",
        f"🐱 Personality   : {user_data.get('pet_personality', 'Neutral')}",
        f"🐱 Health        : {user_data.get('health', 10)}",
        f"🐱 Energy        : {user_data.get('energy', 100)}",
        f"🐱 Coins         : {user_data.get('coins', 5)}",
        f"🐱 Last Login    : {user_data.get('last_login', '')}",
        f"🐱 Mood Today    : {user_data.get('mood_today', '')}",
    ]
    print_fancy_box("🐱 USER STATISTICS 🐱", lines, theme="blue")


def choose_mood(menu_func):
    moods = ["Happy 😊", "Neutral 😐", "Tired 😞", "Stressed 😫", "Motivated 🥳", "Skip"]
    print_fancy_box(
        "How Are You Feeling Today?",
        ["Pick your mood and let your pet react with you."],
        theme="yellow",
    )
    choice = menu_func(moods)
    return moods[choice - 1]


def analytics_menu():
    print_fancy_box("📈 STUDY ANALYTICS 📈", ["Pick a time range for your progress heatmap."], theme="green")
    options = [
        "View last 7 days",
        "View last 28 days",
        "View last 56 days",
        "Back",
    ]
    return menu(options)


def reflection_menu():
    print_fancy_box("📓 REFLECTION JOURNAL", ["Capture your day and track achievements."], theme="yellow")
    options = [
        "Log Study Session & Reflection",
        "View Achievements",
        "Journal History",
        "Back",
    ]
    return menu(options)


set_ui_theme("disabled")