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
BOX_WIDTH = 92
BACKDROP_WIDTH = 132


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


def _print_pastel_backdrop(width: int = BACKDROP_WIDTH):
    safe_width = max(40, width)
    palette_top = BACKDROP_PALETTE or [255, 231, 225, 224, 223, 218, 217, 219, 183, 189]
    palette_bottom = list(reversed(palette_top))
    print(_gradient_bg_line(safe_width, palette_top))
    print(_sparkle_line(safe_width))
    print(_gradient_bg_line(safe_width, palette_bottom))


def print_fancy_box(title: str, lines, width: int = BOX_WIDTH, theme: str = "cyan"):
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
    print_fancy_box("🐾 STUDYPET 🐾", lines, width=BOX_WIDTH, theme="magenta")


def print_intro_splash():
    """One-time animated intro screen shown at app launch.

    This version intentionally avoids extra imports (random/shutil/sys/audio).
    """
    TITLE_LINES = [
        " ███████╗████████╗██╗   ██╗██████╗ ██╗   ██╗██████╗ ███████╗████████╗ ",
        " ██╔════╝╚══██╔══╝██║   ██║██╔══██╗╚██╗ ██╔╝██╔══██╗██╔════╝╚══██╔══╝ ",
        " ███████╗   ██║   ██║   ██║██║  ██║ ╚████╔╝ ██████╔╝█████╗     ██║    ",
        " ╚════██║   ██║   ██║   ██║██║  ██║  ╚██╔╝  ██╔═══╝ ██╔══╝     ██║    ",
        " ███████║   ██║   ╚██████╔╝██████╔╝   ██║   ██║     ███████╗   ██║    ",
        " ╚══════╝   ╚═╝    ╚═════╝ ╚═════╝    ╚═╝   ╚═╝     ╚══════╝   ╚═╝    ",
    ]
    GRAD = [225, 224, 219, 218, 217, 183]
    CAT_FACES = ["=^.^=", ">^w^<", "=^o^=", "^-^  ", ">.<  ", "uwu  ", "^v^  ", "=^-^="]
    CAT_FG = [219, 218, 217, 183, 189, 225, 147, 216]
    FLEN = 5
    BFG, BFG2, BFLASH = 219, 218, 255

    title_w = max(_visual_width(line) for line in TITLE_LINES)
    content_w = max(20, int(BOX_WIDTH))
    # Splash uses the same outer box width as print_fancy_box (content + 2 borders).
    bw = content_w + 2
    tw = max(title_w + 8, bw)
    th = 34

    pad_v = 1
    bh = len(TITLE_LINES) + (pad_v * 2) + 2
    bc = max(1, (tw - bw) // 2 + 1)
    br = max(2, (th - bh - 6) // 2)
    title_row = br + 1 + pad_v
    title_col = bc + 1 + max(0, (content_w - title_w) // 2)
    tag_row = br + bh + 2
    sub_row = tag_row + 2

    def _at(row, col=1):
        print(f"\033[{row};{col}H", end="")

    def _write(text):
        print(text, end="")

    def _flush():
        print("", end="", flush=True)

    def _center_col(text):
        return max(1, (tw - _visual_width(text)) // 2 + 1)

    def _draw_box(fg):
        for i in range(bw):
            top_ch = "═" if 0 < i < bw - 1 else ("╔" if i == 0 else "╗")
            bot_ch = "═" if 0 < i < bw - 1 else ("╚" if i == 0 else "╝")
            _at(br, bc + i)
            _write(_paint_256(top_ch, fg=fg, bold=True))
            _at(br + bh - 1, bc + i)
            _write(_paint_256(bot_ch, fg=fg, bold=True))
        for i in range(1, bh - 1):
            _at(br + i, bc)
            _write(_paint_256("║", fg=fg, bold=True))
            _at(br + i, bc + bw - 1)
            _write(_paint_256("║", fg=fg, bold=True))
        _flush()

    def _hide_cursor():
        _write("\033[?25l")
        _flush()

    def _show_cursor():
        _write("\033[?25h")
        _flush()

    def _build_cat_ascii_cells(phase=0):
        cells = []
        stride = FLEN + 1
        cols = max(1, tw // stride)
        for row in range(1, th + 1):
            for ci in range(cols):
                col = 1 + (ci * stride)
                if col + FLEN - 1 > tw:
                    continue
                face_idx = (row + (ci * 2) + phase) % len(CAT_FACES)
                fg_idx = ((row * 3) + ci + phase) % len(CAT_FG)
                cells.append((row, col, CAT_FACES[face_idx], CAT_FG[fg_idx]))
        return cells

    def _draw_cat_ascii_cells(cells, dim=False):
        for row, col, face, fg in cells:
            _at(row, col)
            _write(_paint_256(face, fg=fg, dim=dim, bold=not dim))
        _flush()

    try:
        _hide_cursor()
        _write("\033[2J\033[3J\033[H")
        _flush()

        # Phase 1: deterministic twinkling cat starfield.
        spawn = max(3, (tw * th) // 110)
        for tick in range(26):
            for s in range(spawn):
                row = ((tick * 7) + (s * 11)) % th + 1
                col = ((tick * 13) + (s * 17)) % max(1, tw - FLEN) + 1
                face = CAT_FACES[(tick + s) % len(CAT_FACES)]
                fg = CAT_FG[((tick * 3) + s) % len(CAT_FG)]
                bright = ((tick + s) % 7 == 0)
                _at(row, col)
                _write(_paint_256(face, fg=255 if bright else fg, bold=bright, dim=not bright))
            _flush()
            time.sleep(0.032)

        _write("\033[2J\033[3J\033[H")
        _flush()
        time.sleep(0.03)

        # Phase 2: box build from corners.
        for row, col in [(br, bc), (br, bc + bw - 1), (br + bh - 1, bc), (br + bh - 1, bc + bw - 1)]:
            _at(row, col)
            _write(_paint_256("+", fg=BFLASH, bold=True))
        _flush()
        time.sleep(0.06)

        for i in range(bw - 2):
            _at(br, bc + 1 + i)
            _write(_paint_256("═", fg=BFG, bold=True))
            _at(br + bh - 1, bc + bw - 2 - i)
            _write(_paint_256("═", fg=BFG, bold=True))
            if i % 3 == 0:
                _flush()
            time.sleep(0.0028)

        for i in range(bh - 2):
            _at(br + 1 + i, bc)
            _write(_paint_256("║", fg=BFG, bold=True))
            _at(br + bh - 2 - i, bc + bw - 1)
            _write(_paint_256("║", fg=BFG, bold=True))
            _flush()
            time.sleep(0.005)

        for row, col, ch in [
            (br, bc, "╔"),
            (br, bc + bw - 1, "╗"),
            (br + bh - 1, bc, "╚"),
            (br + bh - 1, bc + bw - 1, "╝"),
        ]:
            _at(row, col)
            _write(_paint_256(ch, fg=BFG, bold=True))
        _flush()

        for pulse_fg in [BFLASH, BFG2, BFG]:
            _draw_box(pulse_fg)
            time.sleep(0.06)

        # Phase 3: title reveal.
        max_len = max(len(line) for line in TITLE_LINES)
        for x in range(max_len):
            for i, line in enumerate(TITLE_LINES):
                if x < len(line):
                    _at(title_row + i, title_col + x)
                    _write(_paint_256(line[x], fg=GRAD[i % len(GRAD)], bold=True))
            _flush()
            time.sleep(0.003)

        # Phase 4: shimmer sweep.
        for step in range(max_len + 7):
            wa = step - 3
            wb = (max_len - step) + 3
            for i, line in enumerate(TITLE_LINES):
                _at(title_row + i, title_col)
                base = GRAD[i % len(GRAD)]
                out = []
                for ci, ch in enumerate(line):
                    dist = min(abs(ci - wa), abs(ci - wb))
                    if dist == 0:
                        out.append(_paint_256(ch, fg=231, bold=True))
                    elif dist == 1:
                        out.append(_paint_256(ch, fg=255, bold=True))
                    elif dist == 2:
                        out.append(_paint_256(ch, fg=225, bold=True))
                    else:
                        out.append(_paint_256(ch, fg=base, bold=True))
                _write("".join(out))
            _flush()
            time.sleep(0.0075)

        # Phase 5: gradient typewriter tagline.
        tagline = "  Where productivity meets your virtual companion  "
        tag_grad = [225, 219, 217, 218, 183, 189]
        tg_start = _center_col(tagline)
        typed = []
        for ci, ch in enumerate(tagline):
            typed.append(ch)
            _at(tag_row, tg_start)
            for ti, tc in enumerate(typed):
                _write(_paint_256(tc, fg=tag_grad[(ci - ti) % len(tag_grad)], bold=True))
            _flush()
            time.sleep(0.014)

        # Phase 6: subtitle blink and border pulse.
        sub = "Stay focused  *  Stay playful  *  Keep evolving"
        if sub_row <= th:
            for fg, is_dim in [(255, False), (183, True), (217, False), (183, True)]:
                _at(sub_row, _center_col(sub))
                _write(_paint_256(sub, fg=fg, dim=is_dim, bold=not is_dim))
                _flush()
                time.sleep(0.08)

        for pulse_fg in [255, BFG2, BFG]:
            _draw_box(pulse_fg)
            time.sleep(0.07)

        # Phase 7: cat-wall bloom and pulse (deterministic, no random module).
        _write("\033[2J\033[3J\033[H")
        _flush()
        base_cells = _build_cat_ascii_cells(phase=0)
        center_r = (th + 1) / 2.0
        center_c = (tw + 1) / 2.0

        cells_by_center = sorted(
            base_cells,
            key=lambda cell: ((cell[0] - center_r) ** 2) + (((cell[1] - center_c) / 2.0) ** 2),
        )

        for fraction in [0.10, 0.22, 0.36, 0.52, 0.68, 0.82, 0.94, 1.00]:
            _write("\033[2J\033[3J\033[H")
            visible = max(1, int(len(cells_by_center) * fraction))
            visible_cells = cells_by_center[:visible]
            _draw_cat_ascii_cells(visible_cells, dim=False)

            sparkle_count = max(2, tw // 24)
            for s in range(sparkle_count):
                idx = (int(fraction * 100) * 37 + s * 19) % len(visible_cells)
                row, col, face, _ = visible_cells[idx]
                _at(row, col)
                _write(_paint_256(face, fg=255, bold=True))
            _flush()
            time.sleep(0.065)

        phase_seq = [1, 3, 5, 2, 4, 0]
        for idx, phase in enumerate(phase_seq):
            _write("\033[2J\033[3J\033[H")
            _draw_cat_ascii_cells(_build_cat_ascii_cells(phase=phase), dim=False)
            scan_row = 1 + ((idx * max(1, th - 1)) // max(1, len(phase_seq) - 1))
            if 1 <= scan_row <= th:
                _at(scan_row, 1)
                _write(_paint_256(" " * tw, bg=225))
            _flush()
            time.sleep(0.06)

        row_scale = max(1.0, th / 2.0)
        col_scale = max(1.0, tw / 2.0)
        for radius in [1.20, 1.02, 0.86, 0.72, 0.58, 0.46, 0.35, 0.26, 0.18, 0.11, 0.06]:
            _write("\033[2J\033[3J\033[H")
            kept = []
            for row, col, face, fg in base_cells:
                dr = (row - center_r) / row_scale
                dc = (col - center_c) / col_scale
                if (dr * dr + dc * dc) <= (radius * radius):
                    kept.append((row, col, face, fg))
            _draw_cat_ascii_cells(kept, dim=True)

            if radius < 0.20:
                core_face = CAT_FACES[(int(radius * 100) + 3) % len(CAT_FACES)]
                core_col = max(1, int(center_c) - (FLEN // 2))
                _at(int(center_r), core_col)
                _write(_paint_256(core_face, fg=255, bold=True))
                _flush()
            time.sleep(0.08)

        _write("\033[2J\033[3J\033[H")
        _flush()
    finally:
        _show_cursor()


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

        print_fancy_box("Choose An Option", menu_lines, width=BOX_WIDTH, theme="blue")
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