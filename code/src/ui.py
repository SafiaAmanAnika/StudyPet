import random
import shutil
import sys
import time
import unicodedata
from src.ui_sfx import play_ui_click, play_ui_back, play_ui_error


ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "cyan": "\033[96m",
    "magenta": "\033[95m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "white": "\033[97m",
}


STYLE_PROFILES = {
    "pastel_pink": {
        "label": "Pastel Pink 🎀",
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
        "brand_line": "Soft Kawaii Pink Mode: Activated 🎀",
    },
    "ocean_breeze": {
        "label": "Ocean Breeze 🌊",
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
        "brand_line": "Ocean Breeze Mode: Activated 🌊",
    },
    "sunset_glow": {
        "label": "Sunset Glow 🌇",
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
        "brand_line": "Sunset Glow Mode: Activated 🌇",
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


def _display_width(text: str) -> int:
    width = 0
    for ch in text:
        if unicodedata.combining(ch):
            continue
        if unicodedata.east_asian_width(ch) in ("F", "W"):
            width += 2
        else:
            width += 1
    return width


def _truncate_to_width(text: str, max_width: int) -> str:
    if max_width <= 0:
        return ""

    result = ""
    cur = 0
    for ch in text:
        w = 0 if unicodedata.combining(ch) else (2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1)
        if cur + w > max_width:
            break
        result += ch
        cur += w
    return result


def _pad_to_width(text: str, width: int) -> str:
    cut = _truncate_to_width(text, width)
    return cut + (" " * max(0, width - _display_width(cut)))


def _terminal_width(default: int = 80) -> int:
    try:
        return shutil.get_terminal_size((default, 24)).columns
    except OSError:
        return default


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


def _print_pastel_backdrop():
    width = max(40, min(_terminal_width(80), 120))
    palette_top = BACKDROP_PALETTE or [255, 231, 225, 224, 223, 218, 217, 219, 183, 189]
    palette_bottom = list(reversed(palette_top))

    print(_gradient_bg_line(width, palette_top))
    print(_sparkle_line(width))
    print(_gradient_bg_line(width, palette_bottom))


def print_fancy_box(title: str, lines, width: int = 73, theme: str = "cyan"):
    palette = THEME_256.get(theme, THEME_256["default"])
    border_fg = palette["border"]
    title_bg = palette["title_bg"]
    title_fg = palette["title_fg"]
    body_fg = palette["body_fg"]

    border = "─" * width

    title_text = f" {title} "
    title_text = _truncate_to_width(title_text, width)
    left = max(0, (width - _display_width(title_text)) // 2)
    right = max(0, width - _display_width(title_text) - left)

    print(_paint_256("╭" + border + "╮", fg=border_fg))

    title_inside = (" " * left) + title_text + (" " * right)
    print(
        _paint_256("│", fg=border_fg)
        + _paint_256(title_inside, fg=title_fg, bg=title_bg, bold=True)
        + _paint_256("│", fg=border_fg)
    )

    print(_paint_256("├" + border + "┤", fg=border_fg))

    for line in lines:
        content = _pad_to_width(" " + str(line), width)
        print(
            _paint_256("│", fg=border_fg)
            + _paint_256(content, fg=body_fg)
            + _paint_256("│", fg=border_fg)
        )

    print(_paint_256("╰" + border + "╯", fg=border_fg))


def print_brand_header():
    width = 73
    lines = [
        "✨ Where productivity meets your virtual companion ✨",
        "Stay focused. Stay playful. Keep evolving.",
        BRAND_MODE_LINE,
    ]
    print_fancy_box("🐾 STUDYPET 🐾", lines, width=width, theme="magenta")


def print_intro_splash():
    """One-time animated intro screen shown at app launch."""
    tw = shutil.get_terminal_size((80, 24)).columns
    th = shutil.get_terminal_size((80, 24)).lines

    TITLE_LINES = [
        " \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2557   \u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2557   \u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557 ",
        " \u2588\u2588\u2554\u2550\u2550\u2550\u2550\u255d\u255a\u2550\u2550\u2588\u2588\u2554\u2550\u2550\u255d\u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u255a\u2588\u2588\u2557 \u2588\u2588\u2554\u255d\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2554\u2550\u2550\u2550\u2550\u255d\u255a\u2550\u2550\u2588\u2588\u2554\u2550\u2550\u255d ",
        " \u255a\u2588\u2588\u2588\u2588\u2588\u2557    \u2588\u2588\u2551   \u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2551  \u2588\u2588\u2551 \u255a\u2588\u2588\u2588\u2588\u2554\u255d \u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d\u2588\u2588\u2588\u2588\u2588\u2557     \u2588\u2588\u2551    ",
        "  \u255a\u2550\u2550\u2550\u2588\u2588\u2557   \u2588\u2588\u2551   \u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2551  \u2588\u2588\u2551  \u255a\u2588\u2588\u2554\u255d  \u2588\u2588\u2554\u2550\u2550\u2550\u255d \u2588\u2588\u2554\u2550\u2550\u255d     \u2588\u2588\u2551    ",
        " \u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d   \u2588\u2588\u2551   \u255a\u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d\u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d   \u2588\u2588\u2551   \u2588\u2588\u2551     \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557   \u2588\u2588\u2551    ",
        " \u255a\u2550\u2550\u2550\u2550\u2550\u255d    \u255a\u2550\u255d    \u255a\u2550\u2550\u2550\u2550\u2550\u255d \u255a\u2550\u2550\u2550\u2550\u2550\u255d    \u255a\u2550\u255d   \u255a\u2550\u255d     \u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d   \u255a\u2550\u255d    ",
    ]
    GRAD      = [225, 224, 219, 218, 217, 183]
    CAT_FACES = ["=^.^=", ">^w^<", "=^o^=", "^-^  ", ">.<  ", "uwu  ", "^v^  ", "=^-^="]
    CAT_FG    = [219, 218, 217, 183, 189, 225, 147, 216]
    FLEN      = 5
    BFG, BFG2, BFLASH = 219, 218, 255

    title_w = max(_display_width(l) for l in TITLE_LINES)
    PAD_H, PAD_V = 2, 1
    bw = title_w + PAD_H * 2 + 2
    bh = len(TITLE_LINES) + PAD_V * 2 + 2
    bc = max(1, (tw - bw) // 2 + 1)
    br = max(2, (th - bh - 6) // 2)
    title_row = br + 1 + PAD_V
    title_col = bc + 1 + PAD_H
    tag_row   = br + bh + 2
    sub_row   = tag_row + 2

    rng = random.Random(7)

    def _at(row, col=1):
        sys.stdout.write(f"\033[{row};{col}H")

    def _center_col(text):
        return max(1, (tw - _display_width(text)) // 2 + 1)

    def _draw_box(fg):
        for i in range(bw):
            tch = "\u2550" if 0 < i < bw-1 else ("\u2554" if i == 0 else "\u2557")
            bch = "\u2550" if 0 < i < bw-1 else ("\u255a" if i == 0 else "\u255d")
            _at(br,      bc+i); sys.stdout.write(_paint_256(tch, fg=fg, bold=True))
            _at(br+bh-1, bc+i); sys.stdout.write(_paint_256(bch, fg=fg, bold=True))
        for i in range(1, bh-1):
            _at(br+i, bc);       sys.stdout.write(_paint_256("\u2551", fg=fg, bold=True))
            _at(br+i, bc+bw-1);  sys.stdout.write(_paint_256("\u2551", fg=fg, bold=True))
        sys.stdout.flush()

    def _hide_cursor():
        sys.stdout.write("\033[?25l"); sys.stdout.flush()

    def _show_cursor():
        sys.stdout.write("\033[?25h"); sys.stdout.flush()

    def _play_cat_meow():
        try:
            import os
            import importlib
            pygame = importlib.import_module("pygame")
        except Exception:
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            if pygame.mixer.get_num_channels() < 8:
                pygame.mixer.set_num_channels(8)

            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            meow_path = os.path.join(project_root, "src", "sounds", "meow.mp3")
            if not os.path.exists(meow_path):
                return

            sound = pygame.mixer.Sound(meow_path)
            sound.set_volume(0.70)
            pygame.mixer.Channel(7).play(sound)
        except Exception:
            return

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
            sys.stdout.write(_paint_256(face, fg=fg, dim=dim, bold=not dim))
        sys.stdout.flush()

    try:
        _hide_cursor()
        sys.stdout.write("\033[2J\033[3J\033[H")
        sys.stdout.flush()

        # ── Phase 1: twinkling cat face starfield ────────────────────────────
        # Cats are born as a white flash, live in colour, dim-fade, then vanish.
        # [row, col, face, base_fg, age, lifespan]
        active = []
        SPAWN  = max(3, (tw * th) // 100)
        for tick in range(36):
            for _ in range(SPAWN):
                r, c = rng.randint(1, th), rng.randint(1, max(1, tw - FLEN))
                active.append([r, c, rng.choice(CAT_FACES), rng.choice(CAT_FG),
                                0, rng.randint(4, 8)])
            keep = []
            for cat in active:
                r, c, face, fg, age, life = cat
                _at(r, c)
                if age == 0:
                    sys.stdout.write(_paint_256(face, fg=255, bold=True))
                elif age < life - 2:
                    rare = rng.random() < 0.06
                    sys.stdout.write(_paint_256(face, fg=231 if rare else fg, bold=rare))
                elif age < life:
                    sys.stdout.write(_paint_256(face, fg=fg, dim=True))
                else:
                    sys.stdout.write(" " * FLEN)
                if age < life:
                    cat[4] += 1; keep.append(cat)
            active = keep
            sys.stdout.flush()
            time.sleep(0.048)
        for cat in active:
            _at(cat[0], cat[1]); sys.stdout.write(" " * FLEN)
        sys.stdout.write("\033[2J\033[3J\033[H")
        sys.stdout.flush(); time.sleep(0.05)

        # ── Phase 2: double-line box builds from opposing corners ─────────────
        # 2a — corners flash as +
        for r, c in [(br, bc), (br, bc+bw-1), (br+bh-1, bc), (br+bh-1, bc+bw-1)]:
            _at(r, c); sys.stdout.write(_paint_256("+", fg=BFLASH, bold=True))
        sys.stdout.flush(); time.sleep(0.08)

        # 2b — top bar L→R, bottom bar R→L simultaneously
        for i in range(bw - 2):
            _at(br,      bc+1+i);     sys.stdout.write(_paint_256("\u2550", fg=BFG, bold=True))
            _at(br+bh-1, bc+bw-2-i); sys.stdout.write(_paint_256("\u2550", fg=BFG, bold=True))
            sys.stdout.flush(); time.sleep(0.004)

        # 2c — left drops T→B, right rises B→T simultaneously
        for i in range(bh - 2):
            _at(br+1+i,    bc);       sys.stdout.write(_paint_256("\u2551", fg=BFG, bold=True))
            _at(br+bh-2-i, bc+bw-1); sys.stdout.write(_paint_256("\u2551", fg=BFG, bold=True))
            sys.stdout.flush(); time.sleep(0.008)

        # 2d — set proper double-line corners
        for r, c, ch in [(br, bc, "\u2554"), (br, bc+bw-1, "\u2557"),
                         (br+bh-1, bc, "\u255a"), (br+bh-1, bc+bw-1, "\u255d")]:
            _at(r, c); sys.stdout.write(_paint_256(ch, fg=BFG, bold=True))
        sys.stdout.flush(); time.sleep(0.06)

        # 2e — inner glow pulse: flash → BFG2 → BFG
        for pulse_fg in [BFLASH, BFG2, BFG]:
            _draw_box(pulse_fg); time.sleep(0.07)
        time.sleep(0.05)

        # ── Phase 3: vertical curtain reveal ─────────────────────────────────
        # All title rows appear column-by-column simultaneously.
        for x in range(title_w):
            for i, line in enumerate(TITLE_LINES):
                if x < len(line):
                    _at(title_row + i, title_col + x)
                    sys.stdout.write(_paint_256(line[x], fg=GRAD[i % len(GRAD)], bold=True))
            sys.stdout.flush(); time.sleep(0.004)
        time.sleep(0.04)

        # ── Phase 4: dual counter-traveling shimmer waves ─────────────────────
        # Two white-hot waves travel in opposite directions and cross mid-title.
        for step in range(title_w + 7):
            wa = step - 3
            wb = (title_w - step) + 3
            for i, line in enumerate(TITLE_LINES):
                _at(title_row + i, title_col)
                base, out = GRAD[i % len(GRAD)], ""
                for ci, ch in enumerate(line):
                    dist = min(abs(ci - wa), abs(ci - wb))
                    if   dist == 0: out += _paint_256(ch, fg=231, bold=True)
                    elif dist == 1: out += _paint_256(ch, fg=255, bold=True)
                    elif dist == 2: out += _paint_256(ch, fg=225, bold=True)
                    else:           out += _paint_256(ch, fg=base, bold=True)
                sys.stdout.write(out)
            sys.stdout.flush(); time.sleep(0.010)

        # ── Phase 5: gradient-shift typewriter tagline ────────────────────────
        # Each new char causes the whole typed line to shift colour.
        tagline  = "  Where productivity meets your virtual companion  "
        tag_grad = [225, 219, 217, 218, 183, 189]
        tg_start = _center_col(tagline)
        typed    = []
        for ci, ch in enumerate(tagline):
            typed.append(ch)
            _at(tag_row, tg_start)
            for ti, tc in enumerate(typed):
                sys.stdout.write(_paint_256(tc, fg=tag_grad[(ci - ti) % len(tag_grad)], bold=True))
            sys.stdout.flush(); time.sleep(0.022)

        # ── Phase 6: sub-line blink-in + border colour pulse ─────────────────
        sub = "Stay focused  *  Stay playful  *  Keep evolving"
        if sub_row <= th:
            for bfg, is_dim in [(255, False), (183, True), (217, False), (183, True)]:
                _at(sub_row, _center_col(sub))
                sys.stdout.write(_paint_256(sub, fg=bfg, dim=is_dim, bold=not is_dim))
                sys.stdout.flush(); time.sleep(0.12)

        for pulse_fg in [255, BFG2, BFG]:
            _draw_box(pulse_fg); time.sleep(0.09)

        _at(min(sub_row + 3, th), 1)
        time.sleep(1.3)

        # ── Phase 7: 3-pass wipe out ─────────────────────────────────────────
        # Pass A — dense fast cat storm floods the screen
        storm  = [(rng.randint(1, th), rng.randint(1, max(1, tw - FLEN)),
                   rng.choice(CAT_FACES), rng.choice(CAT_FG))
                  for _ in range(tw * th // 18)]
        chunk7 = max(1, len(storm) // 10)
        for i in range(0, len(storm), chunk7):
            for r, c, face, fg in storm[i:i+chunk7]:
                _at(r, c); sys.stdout.write(_paint_256(face, fg=fg, bold=True))
            sys.stdout.flush(); time.sleep(0.013)

        # Pass B — venetian blind: columns blank from both edges inward
        for i in range(tw // 2 + 1):
            for r in range(1, th + 1):
                _at(r, i + 1);  sys.stdout.write(" ")
                _at(r, tw - i); sys.stdout.write(" ")
            sys.stdout.flush(); time.sleep(0.005)

        # Clear terminal, then fill the whole screen with cat ASCII emojis.
        sys.stdout.write("\033[2J\033[3J\033[H")
        sys.stdout.flush()

        base_cells = _build_cat_ascii_cells(phase=0)
        center_r = (th + 1) / 2.0
        center_c = (tw + 1) / 2.0

        # Act I: center-out bloom so the cat wall "expands" onto the screen.
        cells_by_center = sorted(
            base_cells,
            key=lambda cell: ((cell[0] - center_r) ** 2) + (((cell[1] - center_c) / 2.0) ** 2),
        )
        for fraction in [0.10, 0.20, 0.34, 0.50, 0.66, 0.80, 0.92, 1.00]:
            sys.stdout.write("\033[2J\033[3J\033[H")
            visible = max(1, int(len(cells_by_center) * fraction))
            visible_cells = cells_by_center[:visible]
            _draw_cat_ascii_cells(visible_cells, dim=False)

            # White sparkle accents over the visible cats.
            sparkle_count = max(2, tw // 24)
            for _ in range(sparkle_count):
                row, col, face, _ = rng.choice(visible_cells)
                _at(row, col)
                sys.stdout.write(_paint_256(face, fg=255, bold=True))
            sys.stdout.flush()
            time.sleep(0.09)

        # Act II: style pulse to cycle all cat expressions + a soft scan glow.
        phase_seq = [1, 3, 5, 2, 4, 0]
        for idx, phase in enumerate(phase_seq):
            sys.stdout.write("\033[2J\033[3J\033[H")
            _draw_cat_ascii_cells(_build_cat_ascii_cells(phase=phase), dim=False)

            scan_row = 1 + ((idx * max(1, th - 1)) // max(1, len(phase_seq) - 1))
            if 1 <= scan_row <= th:
                _at(scan_row, 1)
                sys.stdout.write(_paint_256(" " * tw, bg=225))
            sys.stdout.flush()
            time.sleep(0.08)

        # Act III: meow-synced iris fade (cats collapse into the center and vanish).
        _play_cat_meow()
        row_scale = max(1.0, th / 2.0)
        col_scale = max(1.0, tw / 2.0)
        for radius in [1.20, 1.02, 0.86, 0.72, 0.58, 0.46, 0.35, 0.26, 0.18, 0.11, 0.06]:
            sys.stdout.write("\033[2J\033[3J\033[H")
            kept = []
            for row, col, face, fg in base_cells:
                dr = (row - center_r) / row_scale
                dc = (col - center_c) / col_scale
                if (dr * dr + dc * dc) <= (radius * radius):
                    kept.append((row, col, face, fg))
            _draw_cat_ascii_cells(kept, dim=True)

            # Final heartbeat cat at center in the last moments.
            if radius < 0.20:
                core_face = CAT_FACES[(int(radius * 100) + 3) % len(CAT_FACES)]
                core_col = max(1, int(center_c) - (FLEN // 2))
                _at(int(center_r), core_col)
                sys.stdout.write(_paint_256(core_face, fg=255, bold=True))
                sys.stdout.flush()
            time.sleep(0.10)

        sys.stdout.write("\033[2J\033[3J\033[H")
        sys.stdout.flush()

    finally:
        _show_cursor()


def clear_screen():
    print("\033[2J\033[3J\033[H", end="")
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
            menu_lines.append(f"[{i}] {option}")
        menu_lines.append(f"[0] {options[-1]}")

        print_fancy_box("Choose An Option", menu_lines, width=73, theme="blue")

        choice = input(_paint_256("Choose your option: ", fg=PASTEL_ACCENTS["prompt_fg"], bold=True)).strip()

        if choice.isdigit():
            choice = int(choice)
            if choice == 0:
                play_ui_back()
                return 0
            elif 1 <= choice < len(options):
                play_ui_click()
                return choice

        clear_screen()
        play_ui_error()
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
    print_fancy_box("Theme Studio 🎨", lines, theme="magenta")

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
    print_fancy_box("Animation Studio 🎞️", lines, theme="cyan")

    choice = menu_func(options)
    if choice == 0:
        return None

    selected_key, _ = style_options[choice - 1]
    set_animation_style(selected_key)
    return selected_key


def print_kv(label, value):
    print(f"{label:<15}: {value}")
    

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

    health_bar_len = max(0, min(20, int((health / 20) * 20)))
    energy_bar_len = max(0, min(20, int((energy / 100) * 20)))
    health_bar = "█" * health_bar_len + "░" * (20 - health_bar_len)
    energy_bar = "█" * energy_bar_len + "░" * (20 - energy_bar_len)

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

    return moods[choice -1]

# ---------------- ANALYTICS UI ---------------- #

def analytics_menu():
    print_fancy_box("📈 STUDY ANALYTICS 📈", ["Pick a time range for your progress heatmap."], theme="green")

    options = [
        "View last 7 days",
        "View last 28 days",
        "View last 56 days",
        "Back"
    ]

    return menu(options)

# ---------------- REFLECTION MENU ---------------- #

def reflection_menu():
    print_fancy_box("📓 REFLECTION JOURNAL", ["Capture your day and track achievements."], theme="yellow")

    options = [
        "Log Study Session & Reflection",
        "View Achievements",
        "Back"
    ]

    return menu(options)