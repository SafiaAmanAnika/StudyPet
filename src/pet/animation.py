import time, os

animation_indexes = {}


ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
}


DEFAULT_MOOD_ACCENTS = {
    "Happy": 186,
    "Neutral": 189,
    "Tired": 147,
    "Stressed": 210,
    "Motivated": 220,
}


ANIMATION_STYLE_PROFILES = {
    "soft": {
        "label": "Soft 🌸",
        "mood_accents": DEFAULT_MOOD_ACCENTS,
        "sparkles": ["✿", "｡", "⋆", "｡"],
        "bar_width": 20,
        "bar_full": "▰",
        "bar_empty": "▱",
        "info_fg": 224,
        "progress_fg": 223,
        "pet_bold": False,
        "evolution_accents": [182, 189, 218],
        "frame_width": 48,
    },
    "sparkly": {
        "label": "Sparkly ✨",
        "mood_accents": {
            "Happy": 220,
            "Neutral": 189,
            "Tired": 147,
            "Stressed": 210,
            "Motivated": 226,
        },
        "sparkles": ["✦", "✧", "⋆", "✧"],
        "bar_width": 24,
        "bar_full": "█",
        "bar_empty": "░",
        "info_fg": 224,
        "progress_fg": 223,
        "pet_bold": True,
        "evolution_accents": [219, 218, 183],
        "frame_width": 50,
    },
    "minimal": {
        "label": "Minimal ◻️",
        "mood_accents": {
            "Happy": 250,
            "Neutral": 248,
            "Tired": 246,
            "Stressed": 245,
            "Motivated": 252,
        },
        "sparkles": ["•", "·", "•", "·"],
        "bar_width": 18,
        "bar_full": "■",
        "bar_empty": "·",
        "info_fg": 252,
        "progress_fg": 250,
        "pet_bold": False,
        "evolution_accents": [250, 247, 244],
        "frame_width": 46,
    },
}


CURRENT_ANIMATION_STYLE = "sparkly"


def set_animation_style(style_name: str) -> str:
    global CURRENT_ANIMATION_STYLE
    style_name = str(style_name or "sparkly")
    if style_name not in ANIMATION_STYLE_PROFILES:
        style_name = "sparkly"
    CURRENT_ANIMATION_STYLE = style_name
    return style_name


def get_animation_style() -> str:
    return CURRENT_ANIMATION_STYLE


def get_animation_style_display(style_name: str) -> str:
    profile = ANIMATION_STYLE_PROFILES.get(style_name, ANIMATION_STYLE_PROFILES["sparkly"])
    return profile["label"]


def list_animation_style_options():
    return [(key, profile["label"]) for key, profile in ANIMATION_STYLE_PROFILES.items()]


def _current_animation_profile() -> dict:
    return ANIMATION_STYLE_PROFILES.get(CURRENT_ANIMATION_STYLE, ANIMATION_STYLE_PROFILES["sparkly"])


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


def _progress_bar(remaining: int, total: int, width: int = 24, full_char: str = "█", empty_char: str = "░"):
    if total <= 0:
        return empty_char * width, 100

    completed = max(0, total - remaining)
    ratio = min(1.0, max(0.0, completed / total))
    filled = int(round(width * ratio))
    bar = (full_char * filled) + (empty_char * (width - filled))
    percent = int(round(ratio * 100))
    return bar, percent


def _colorize_pet_frame(frame: str, mood: str):
    profile = _current_animation_profile()
    accent = profile.get("mood_accents", DEFAULT_MOOD_ACCENTS).get(mood, 189)
    bold_pet = bool(profile.get("pet_bold", True))
    colored_lines = []
    for line in frame.splitlines():
        colored_lines.append(_paint_256(line, fg=accent, bold=bold_pet))
    return "\n".join(colored_lines)


def render_countdown_scene(label: str, time_str: str, pet_theme: str, mood: str, level: int, remaining: int, total: int):
    profile = _current_animation_profile()

    frame = get_animation_frame(pet_theme, mood, level)
    stage = get_pet_stage(level)
    mood_accents = profile.get("mood_accents", DEFAULT_MOOD_ACCENTS)
    accent = mood_accents.get(mood, 189)

    step = max(0, total - remaining)
    sparkles = profile.get("sparkles", ["✦", "✧", "⋆", "✧"])
    sparkle = sparkles[step % len(sparkles)]
    bar, percent = _progress_bar(
        remaining,
        total,
        width=int(profile.get("bar_width", 24)),
        full_char=str(profile.get("bar_full", "█")),
        empty_char=str(profile.get("bar_empty", "░")),
    )

    width = int(profile.get("frame_width", 50))
    top = _paint_256("╭" + ("─" * width) + "╮", fg=accent)
    title = f" {sparkle} {label.upper()} MODE {sparkle} "
    title_line = _paint_256("│" + title.center(width) + "│", fg=accent, bold=True)
    middle = _paint_256("├" + ("─" * width) + "┤", fg=accent)

    pet_line = f"Pet: {pet_theme}  •  Stage: {stage}  •  Mood: {mood}"
    timer_line = f"Time Left: {time_str}"
    progress_line = f"Progress: {bar} {percent:>3}%"

    info_fg = int(profile.get("info_fg", 224))
    progress_fg = int(profile.get("progress_fg", 223))
    info_1 = _paint_256("│" + pet_line.ljust(width)[:width] + "│", fg=info_fg)
    info_2 = _paint_256("│" + timer_line.ljust(width)[:width] + "│", fg=info_fg, bold=True)
    info_3 = _paint_256("│" + progress_line.ljust(width)[:width] + "│", fg=progress_fg)
    bottom = _paint_256("╰" + ("─" * width) + "╯", fg=accent)

    return "\n".join(
        [
            top,
            title_line,
            middle,
            info_1,
            info_2,
            info_3,
            bottom,
            "",
            _colorize_pet_frame(frame, mood),
        ]
    )


def render_evolution_scene(frame: str, step: int, total_steps: int):
    profile = _current_animation_profile()

    width = int(profile.get("frame_width", 50))
    accents = profile.get("evolution_accents", [219, 218, 183])
    accent = accents[step % len(accents)]
    sparkles = profile.get("sparkles", ["✦", "✧", "⋆", "✧"])
    sparkle = sparkles[step % len(sparkles)]
    title = f" {sparkle} PET EVOLUTION {sparkle} "
    phase = f"Evolution pulse {step + 1}/{total_steps}"

    top = _paint_256("╭" + ("─" * width) + "╮", fg=accent)
    line_1 = _paint_256("│" + title.center(width) + "│", fg=accent, bold=True)
    line_2 = _paint_256("│" + phase.center(width) + "│", fg=int(profile.get("info_fg", 224)))
    bottom = _paint_256("╰" + ("─" * width) + "╯", fg=accent)
    pet = _paint_256(
        frame,
        fg=int(profile.get("progress_fg", 225)),
        bold=bool(profile.get("pet_bold", True)),
    )
    return "\n".join([top, line_1, line_2, bottom, "", pet])

PETS_FRAMES = {

    "Cat": {

        "Baby": {

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
            ]
        },

        "Teen": {

            "Happy": [
                " /\\_/\\  📚\n( ^.^ )\n >  ^  <",
                " /\\_/\\  📚\n( ^o^ )\n >  ^  <",
                " /\\_/\\  📚\n( ^.^ )\n >  o  <",
            ],

            "Neutral": [
                " /\\_/\\  📚\n( -.- )\n >  ^  <",
                " /\\_/\\  📚\n( -_- )\n >  ^  <",
                " /\\_/\\  📚\n( -.- )\n >  _  <",
            ],

            "Tired": [
                " /\\_/\\  📚 zZ\n( -.- )\n >  ^  <",
                " /\\_/\\  📚 zZ\n( -_- )\n >  ^  <",
                " /\\_/\\  📚 zZ\n( -.- )\n >  _  <",
            ],

            "Stressed": [
                " /\\_/\\  📚 !!!\n( o.O )\n >  ^  <",
                " /\\_/\\  📚 !!!\n( O.o )\n >  ^  <",
                " /\\_/\\  📚 !!!\n( o.O )\n >  _  <",
            ],

            "Motivated": [
                " /\\_/\\  📚 🔥\n( >.< )\n >  ^  <",
                " /\\_/\\  📚 🔥\n( >o< )\n >  ^  <",
                " /\\_/\\  📚 🔥\n( >.< )\n >  o  <",
            ]
        },

        "Scholar": {

            "Happy": [
                " /\\_/\\  🎓\n( ^.^ )\n >  ^  <",
                " /\\_/\\  🎓\n( ^o^ )\n >  ^  <",
                " /\\_/\\  🎓\n( ^.^ )\n >  o  <",
            ],

            "Neutral": [
                " /\\_/\\  🎓\n( -.- )\n >  ^  <",
                " /\\_/\\  🎓\n( -_- )\n >  ^  <",
                " /\\_/\\  🎓\n( -.- )\n >  _  <",
            ],

            "Tired": [
                " /\\_/\\  🎓 zZ\n( -.- )\n >  ^  <",
                " /\\_/\\  🎓 zZ\n( -_- )\n >  ^  <",
                " /\\_/\\  🎓 zZ\n( -.- )\n >  _  <",
            ],

            "Stressed": [
                " /\\_/\\  🎓 !!!\n( o.O )\n >  ^  <",
                " /\\_/\\  🎓 !!!\n( O.o )\n >  ^  <",
                " /\\_/\\  🎓 !!!\n( o.O )\n >  _  <",
            ],

            "Motivated": [
                " /\\_/\\  🎓 🔥\n( >.< )\n >  ^  <",
                " /\\_/\\  🎓 🔥\n( >o< )\n >  ^  <",
                " /\\_/\\  🎓 🔥\n( >.< )\n >  o  <",
            ]
        }
    },

# ---------------------------------------------------

    "Dog": {

        "Baby": {

            "Happy": [
                "  /^^^\\  ♪\n / ^ ^ \\\n V\\ v /V",
                "  /^^^\\  ♪\n / o o \\\n V\\ ^ /V",
                "  /^^^\\  ♪\n / ^ ^ \\\n V\\ o /V",
            ],

            "Neutral": [
                "  /^^^\\\n / - - \\ \n V\\ ^ /V", 
                "  /^^^\\\n / -.- \\ \n V\\ ^ /V", 
                "  /^^^\\\n / - - \\ \n V\\ _ /V",
            ],

            "Tired": [
                "  /^^^\\  zZ\n / - - \\\n V\\ ^ /V",
                "  /^^^\\  zZ\n / -.- \\\n V\\ ^ /V",
                "  /^^^\\  zZ\n / - - \\ \n V\\ _ /V",
            ],

            "Stressed": [
                "  /^^^\\  !!!\n / o.O \\\n V\\ ^ /V",
                "  /^^^\\  !!!\n / O.o \\\n V\\ ^ /V",
                "  /^^^\\  !!!\n / o.O \\\n V\\ _ /V",
            ],

            "Motivated": [
                "  /^^^\\  🔥\n / >.< \\\n V\\ ^ /V",
                "  /^^^\\  🔥\n / >o< \\\n V\\ ^ /V",
                "  /^^^\\  🔥\n / >.< \\\n V\\ _ /V",
            ]
        },

        "Teen": {

            "Happy": [
                "  /^^^\\  📚\n / ^ ^ \\\n V\\ v /V",
                "  /^^^\\  📚\n / o o \\\n V\\ ^ /V",
                "  /^^^\\  📚\n / ^ ^ \\\n V\\ o /V",
            ],

            "Neutral": [
                "  /^^^\\  📚\n / - - \\\n V\\ ^ /V",
                "  /^^^\\  📚\n / -.- \\\n V\\ ^ /V",
                "  /^^^\\  📚\n / - - \\\n V\\ _ /V",
            ],

            "Tired": [
                "  /^^^\\  📚 zZ\n / - - \\\n V\\ ^ /V",
                "  /^^^\\  📚 zZ\n / -.- \\\n V\\ ^ /V",
                "  /^^^\\  📚 zZ\n / - - \\\n V\\ _ /V",
            ],

            "Stressed": [
                "  /^^^\\  📚 !!!\n / o.O \\\n V\\ ^ /V",
                "  /^^^\\  📚 !!!\n / O.o \\\n V\\ ^ /V",
                "  /^^^\\  📚 !!!\n / o.O \\\n V\\ _ /V",
            ],

            "Motivated": [
                "  /^^^\\  📚 🔥\n / >.< \\\n V\\ ^ /V",
                "  /^^^\\  📚 🔥\n / >o< \\\n V\\ ^ /V",
                "  /^^^\\  📚 🔥\n / >.< \\\n V\\ _ /V",
            ]
        },

        "Scholar": {

            "Happy": [
                "  /^^^\\  🎓\n / ^ ^ \\\n V\\ v /V",
                "  /^^^\\  🎓\n / o o \\\n V\\ ^ /V",
                "  /^^^\\  🎓\n / ^ ^ \\\n V\\ o /V",
            ],

            "Neutral": [
                "  /^^^\\  🎓\n / - - \\\n V\\ ^ /V",
                "  /^^^\\  🎓\n / -.- \\\n V\\ ^ /V",
                "  /^^^\\  🎓\n / - - \\\n V\\ _ /V",
            ],

            "Tired": [
                "  /^^^\\  🎓 zZ\n / - - \\\n V\\ ^ /V",
                "  /^^^\\  🎓 zZ\n / -.- \\\n V\\ ^ /V",
                "  /^^^\\  🎓 zZ\n / - - \\\n V\\ _ /V",
            ],

            "Stressed": [
                "  /^^^\\  🎓 !!!\n / o.O \\\n V\\ ^ /V",
                "  /^^^\\  🎓 !!!\n / O.o \\\n V\\ ^ /V",
                "  /^^^\\  🎓 !!!\n / o.O \\\n V\\ _ /V",
            ],

            "Motivated": [
                "  /^^^\\  🎓 🔥\n / >.< \\\n V\\ ^ /V",
                "  /^^^\\  🎓 🔥\n / >o< \\\n V\\ ^ /V",
                "  /^^^\\  🎓 🔥\n / >.< \\\n V\\ _ /V",
            ]
        }
    },

# ---------------------------------------------------

    "Bunny": {

        "Baby": {

            "Happy": [
                "  (\\_/)  ♪\n ( ^.^ )\n o(   )o",
                "  (\\_/)  ♪\n ( ^o^ )\n o(   )o",
                "  (\\_/)  ♪\n ( ^.^ )\n o(   )o",
            ],

            "Neutral": [
                "  (\\_/)\n ( -.- )\n o(   )o",
                "  (\\_/)\n ( -_- )\n o(   )o",
                "  (\\_/)\n ( -.- )\n o(   )o",
            ],

            "Tired": [
                "  (\\_/)  zZ\n ( -.- )\n o(   )o",
                "  (\\_/)  zZ\n ( -_- )\n o(   )o",
                "  (\\_/)  zZ\n ( -.- )\n o(   )o",
            ],

            "Stressed": [
                "  (\\_/)  !!!\n ( o.O )\n o(   )o",
                "  (\\_/)  !!!\n ( O.o )\n o(   )o",
                "  (\\_/)  !!!\n ( o.O )\n o(   )o",
            ],

            "Motivated": [
                "  (\\_/)  🔥\n ( >.< )\n o(   )o",
                "  (\\_/)  🔥\n ( >o< )\n o(   )o",
                "  (\\_/)  🔥\n ( >.< )\n o(   )o",
            ]
        },

        "Teen": {

            "Happy": [
                "  (\\_/)  📚\n ( ^.^ )\n o(   )o",
                "  (\\_/)  📚\n ( ^o^ )\n o(   )o",
                "  (\\_/)  📚\n ( ^.^ )\n o(   )o",
            ],

            "Neutral": [
                "  (\\_/)  📚\n ( -.- )\n o(   )o",
                "  (\\_/)  📚\n ( -_- )\n o(   )o",
                "  (\\_/)  📚\n ( -.- )\n o(   )o",
            ],

            "Tired": [
                "  (\\_/)  📚 zZ\n ( -.- )\n o(   )o",
                "  (\\_/)  📚 zZ\n ( -_- )\n o(   )o",
                "  (\\_/)  📚 zZ\n ( -.- )\n o(   )o",
            ],

            "Stressed": [
                "  (\\_/)  📚 !!!\n ( o.O )\n o(   )o",
                "  (\\_/)  📚 !!!\n ( O.o )\n o(   )o",
                "  (\\_/)  📚 !!!\n ( o.O )\n o(   )o",
            ],

            "Motivated": [
                "  (\\_/)  📚 🔥\n ( >.< )\n o(   )o",
                "  (\\_/)  📚 🔥\n ( >o< )\n o(   )o",
                "  (\\_/)  📚 🔥\n ( >.< )\n o(   )o",
            ]
        },

        "Scholar": {

            "Happy": [
                "  (\\_/)  🎓\n ( ^.^ )\n o(   )o",
                "  (\\_/)  🎓\n ( ^o^ )\n o(   )o",
                "  (\\_/)  🎓\n ( ^.^ )\n o(   )o",
            ],

            "Neutral": [
                "  (\\_/)  🎓\n ( -.- )\n o(   )o",
                "  (\\_/)  🎓\n ( -_- )\n o(   )o",
                "  (\\_/)  🎓\n ( -.- )\n o(   )o",
            ],

            "Tired": [
                "  (\\_/)  🎓 zZ\n ( -.- )\n o(   )o",
                "  (\\_/)  🎓 zZ\n ( -_- )\n o(   )o",
                "  (\\_/)  🎓 zZ\n ( -.- )\n o(   )o",
            ],

            "Stressed": [
                "  (\\_/)  🎓 !!!\n ( o.O )\n o(   )o",
                "  (\\_/)  🎓 !!!\n ( O.o )\n o(   )o",
                "  (\\_/)  🎓 !!!\n ( o.O )\n o(   )o",
            ],

            "Motivated": [
                "  (\\_/)  🎓 🔥\n ( >.< )\n o(   )o",
                "  (\\_/)  🎓 🔥\n ( >o< )\n o(   )o",
                "  (\\_/)  🎓 🔥\n ( >.< )\n o(   )o",
            ]
        }
    }
}


def get_pet_stage(level):
    if level >= 10:
        return "Scholar"
    elif level >= 5:
        return "Teen"
    else:
        return "Baby"


def get_animation_frame(pet_theme, mood, level):

    stage = get_pet_stage(level)

    pet_data = PETS_FRAMES.get(pet_theme, {})
    stage_data = pet_data.get(stage, {})

    frames = stage_data.get(mood)

    if not frames:
        frames = stage_data.get("Neutral", [])

    if not frames:
        return "🐾 Pet is waiting..."

    key = (pet_theme, stage, mood)
    index = animation_indexes.get(key, 0)
    frame = frames[index]
    animation_indexes[key] = (index + 1) % len(frames)
    return frame


EVOLUTION_ANIMATIONS = {

    "Cat": [
        " /\\_/\\\n( o.o )\n > ^ <",
        " /\\_/\\  ✨\n( o.o )\n > ^ <",
        " /\\_/\\  🎓\n( ^.^ )\n > ^ <"
    ],

    "Dog": [
        "  /^^^\\\n / o o \\\n V\\ ^ /V",
        "  /^^^\\  ✨\n / o o \\\n V\\ ^ /V",
        "  /^^^\\  🎓\n / ^ ^ \\\n V\\ v /V"
    ],

    "Bunny": [
        "  (\\_/)\n ( o.o )\n o(   )o",
        "  (\\_/)  ✨\n ( o.o )\n o(   )o",
        "  (\\_/)  🎓\n ( ^.^ )\n o(   )o"
    ]
}


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        print("\033[2J\033[H", end="")


def play_evolution_animation(pet_theme):

    frames = EVOLUTION_ANIMATIONS.get(pet_theme)

    if not frames:
        return

    for idx, frame in enumerate(frames):
        clear()
        print(render_evolution_scene(frame, idx, len(frames)))
        time.sleep(0.6)

    print(_paint_256("\nYour pet has evolved! 🐾📚", fg=219, bold=True))
    time.sleep(1)


def animate_pet(pet_theme, mood, level, seconds):

    start = time.time()

    while time.time() - start < seconds:

        clear()

        elapsed = int(time.time() - start)
        remaining = max(0, int(seconds) - elapsed)
        mins = remaining // 60
        secs = remaining % 60
        time_str = f"{mins:02d}:{secs:02d}"
        print(render_countdown_scene("Study", time_str, pet_theme, mood, level, remaining, int(seconds)))

        time.sleep(0.6)