import time
from src.custom.custom_text import count_emojis, visible_width


ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
}

STYLE_PROFILES = {
    "pastel_pink": {
        "label": "Pastel Pink",
        "themes": {
            "cyan": {"border": 189, "title_bg": 225, "title_fg": 60, "body_fg": 224},
            "magenta": {"border": 218, "title_bg": 224, "title_fg": 89, "body_fg": 225},
            "green": {"border": 181, "title_bg": 223, "title_fg": 95, "body_fg": 224},
            "yellow": {"border": 223, "title_bg": 230, "title_fg": 95, "body_fg": 224},
            "blue": {"border": 183, "title_bg": 189, "title_fg": 60, "body_fg": 225},
            "default": {"border": 218, "title_bg": 225, "title_fg": 89, "body_fg": 224},
        },
        "accents": {"sparkle_fg": 217, "prompt_fg": 219, "error_fg": 174},
        "backdrop": [255, 231, 225, 224, 223, 218, 217, 219, 183, 189],
        "brand_line": "Soft Kawaii Pink Mode: Activated",
    },
    "ocean_breeze": {
        "label": "Ocean Breeze",
        "themes": {
            "cyan": {"border": 117, "title_bg": 159, "title_fg": 24, "body_fg": 195},
            "magenta": {"border": 147, "title_bg": 189, "title_fg": 24, "body_fg": 195},
            "green": {"border": 116, "title_bg": 153, "title_fg": 24, "body_fg": 194},
            "yellow": {"border": 186, "title_bg": 230, "title_fg": 24, "body_fg": 195},
            "blue": {"border": 111, "title_bg": 152, "title_fg": 24, "body_fg": 195},
            "default": {"border": 117, "title_bg": 159, "title_fg": 24, "body_fg": 195},
        },
        "accents": {"sparkle_fg": 153, "prompt_fg": 117, "error_fg": 109},
        "backdrop": [255, 231, 195, 189, 153, 152, 117, 111, 147, 189],
        "brand_line": "Ocean Breeze Mode: Activated",
    },
    "sunset_glow": {
        "label": "Sunset Glow",
        "themes": {
            "cyan": {"border": 180, "title_bg": 223, "title_fg": 52, "body_fg": 224},
            "magenta": {"border": 217, "title_bg": 224, "title_fg": 52, "body_fg": 225},
            "green": {"border": 187, "title_bg": 230, "title_fg": 52, "body_fg": 224},
            "yellow": {"border": 223, "title_bg": 229, "title_fg": 88, "body_fg": 223},
            "blue": {"border": 181, "title_bg": 217, "title_fg": 52, "body_fg": 224},
            "default": {"border": 217, "title_bg": 224, "title_fg": 52, "body_fg": 224},
        },
        "accents": {"sparkle_fg": 216, "prompt_fg": 217, "error_fg": 167},
        "backdrop": [255, 230, 224, 223, 216, 215, 209, 217, 181, 180],
        "brand_line": "Sunset Glow Mode: Activated",
    },
}

THEME_256 = {}
PASTEL_ACCENTS = {}
BACKDROP_PALETTE = []
BRAND_MODE_LINE = ""
CURRENT_STYLE = "pastel_pink"


def _copy_theme_map(theme_map: dict) -> dict:
    return {key: value.copy() for key, value in theme_map.items()}


def _apply_style_profile(style_name: str) -> str:
    global THEME_256, PASTEL_ACCENTS, BACKDROP_PALETTE, BRAND_MODE_LINE, CURRENT_STYLE

    if style_name not in STYLE_PROFILES:
        style_name = "pastel_pink"

    profile = STYLE_PROFILES[style_name]
    THEME_256 = _copy_theme_map(profile["themes"])
    PASTEL_ACCENTS = profile["accents"].copy()
    BACKDROP_PALETTE = list(profile["backdrop"])
    BRAND_MODE_LINE = profile["brand_line"]
    CURRENT_STYLE = style_name
    return style_name


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
    prefix = ""
    for style in styles:
        prefix += ANSI.get(style, "")
    if not prefix:
        return text
    return f"{prefix}{text}{ANSI['reset']}"


def _paint_256(text: str, fg=None, bg=None, bold: bool = False, dim: bool = False) -> str:
    seq = ""
    if bold:
        seq += ANSI["bold"]
    if dim:
        seq += ANSI["dim"]
    if fg is not None:
        seq += f"\033[38;5;{fg}m"
    if bg is not None:
        seq += f"\033[48;5;{bg}m"
    if not seq:
        return text
    return f"{seq}{text}{ANSI['reset']}"


def set_ui_theme(style_name: str) -> str:
    return _apply_style_profile(str(style_name or "pastel_pink"))


def get_ui_theme() -> str:
    return CURRENT_STYLE


def get_theme_display_name(style_name: str) -> str:
    profile = STYLE_PROFILES.get(style_name, STYLE_PROFILES["pastel_pink"])
    return profile["label"]


def list_theme_options():
    return [(key, profile["label"]) for key, profile in STYLE_PROFILES.items()]


_apply_style_profile("pastel_pink")


def _gradient_bg_line(width: int, palette):
    if width <= 0:
        return ""

    parts = []
    last_code = None
    span = max(1, width - 1)
    for i in range(width):
        idx = int(i * (len(palette) - 1) / span)
        code = palette[idx]
        if code != last_code:
            parts.append(f"\033[48;5;{code}m")
            last_code = code
        parts.append(" ")

    parts.append(ANSI["reset"])
    return "".join(parts)


def _sparkle_line(width: int):
    if width <= 0:
        return ""
    pattern = "✿  ｡  ⋆  ｡  ✿  "
    row = (pattern * ((width // len(pattern)) + 2))[:width]
    return _paint_256(row, fg=PASTEL_ACCENTS["sparkle_fg"], dim=True)


def _print_pastel_backdrop(width: int = 118):
    safe_width = max(40, width)
    palette_top = BACKDROP_PALETTE or [255, 231, 225, 224, 223, 218, 217, 219, 183, 189]
    palette_bottom = list(reversed(palette_top))
    print(_gradient_bg_line(safe_width, palette_top))
    print(_sparkle_line(safe_width))
    print(_gradient_bg_line(safe_width, palette_bottom))


def print_fancy_box(title: str, lines, width: int = 73, theme: str = "cyan"):
    w = max(20, int(width))
    palette = THEME_256.get(theme, THEME_256["default"])
    border_fg = palette["border"]
    title_bg = palette["title_bg"]
    title_fg = palette["title_fg"]
    body_fg = palette["body_fg"]

    horizontal = "─" * w
    title_text = _truncate(f" {title} ", w)
    left = max(0, (w - _visual_width(title_text)) // 2)
    right = max(0, w - _visual_width(title_text) - left)

    print(_paint_256("╭" + horizontal + "╮", fg=border_fg))
    print(
        _paint_256("│", fg=border_fg)
        + _paint_256((" " * left) + title_text + (" " * right), fg=title_fg, bg=title_bg, bold=True)
        + _paint_256("│", fg=border_fg)
    )
    print(_paint_256("├" + horizontal + "┤", fg=border_fg))

    for line in lines:
        content = _pad(" " + _safe_text(line), w)
        print(_paint_256("│", fg=border_fg) + _paint_256(content, fg=body_fg) + _paint_256("│", fg=border_fg))

    print(_paint_256("╰" + horizontal + "╯", fg=border_fg))


def print_brand_header():
    lines = [
        "✨ Where productivity meets your virtual companion ✨",
        "Stay focused. Stay playful. Keep evolving.",
        BRAND_MODE_LINE,
    ]
    print_fancy_box("🐾 STUDYPET 🐾", lines, width=73, theme="magenta")


def print_intro_splash():
    clear_screen()
    banner = [
        "   /\\_/\\   STUDYPET",
        "  ( o.o )  productivity + companion", 
        "   > ^ <   pastel terminal mode", 
    ]
    shades = [225, 219, 217]
    for idx, line in enumerate(banner):
        print(_paint_256(line, fg=shades[idx % len(shades)], bold=True))
        time.sleep(0.05)

    print()
    lines = [
        "✨ Where productivity meets your virtual companion ✨",
        "Stay focused. Stay playful. Keep evolving.",
        BRAND_MODE_LINE,
    ]
    print_fancy_box("Launch", lines, width=73, theme="magenta")
    time.sleep(0.6)


def clear_screen():
    print("\033[2J\033[3J\033[H", end="", flush=True)
    _print_pastel_backdrop()
    print()


def pause():
    try:
        input(_paint("\nPress Enter to continue ✨", "dim"))
    except KeyboardInterrupt:
        print("\nExiting pause.")


def menu(options):
    while True:
        menu_lines = []
        for i, option in enumerate(options[:-1], start=1):
            menu_lines.append(f"[{i}] {_safe_text(option)}")
        menu_lines.append(f"[0] {_safe_text(options[-1])}")

        print_fancy_box("Choose An Option", menu_lines, width=73, theme="blue")
        choice = input(_paint_256("Choose your option: ", fg=PASTEL_ACCENTS["prompt_fg"], bold=True)).strip()

        if choice.isdigit():
            value = int(choice)
            if value == 0:
                return 0
            if 1 <= value < len(options):
                return value

        clear_screen()
        print(_paint_256("❌ Invalid choice. Please try again.", fg=PASTEL_ACCENTS["error_fg"], bold=True))
        print()


def choose_theme(menu_func):
    theme_options = list_theme_options()
    options = [label for _, label in theme_options] + ["Back"]

    lines = [
        f"Current Theme: {get_theme_display_name(get_ui_theme())}",
        "",
        "Pick a color mood for cards, prompts, and background.",
    ]
    print_fancy_box("Theme Studio", lines, theme="magenta")

    choice = menu_func(options)
    if choice == 0:
        return None

    selected_key, _ = theme_options[choice - 1]
    set_ui_theme(selected_key)
    return selected_key


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


set_ui_theme("pastel_pink")