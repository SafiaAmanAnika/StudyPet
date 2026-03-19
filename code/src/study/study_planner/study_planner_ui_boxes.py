from src.custom.custom_text import count_emojis
from .study_planner_config_helpers import (
    BOX_INNER, manual_max, visible_width, truncate_to_width,
    pad_to_width, wrap_text_to_width
)

BORDER_FILL = "═" * (BOX_INNER + 2)

# ============================================================================
# BOX DRAWING
# ============================================================================

def box_title_only(title):
    t = str(title)
    emoji_count = count_emojis(t)
    extra = emoji_count % 2
    inner_width = BOX_INNER + extra
    print("╔" + "═" * inner_width + "╗")
    t = truncate_to_width(t, inner_width)
    left = manual_max(0, (inner_width - visible_width(t)) // 2)
    right = manual_max(0, inner_width - visible_width(t) - left)
    print("║ " + " " * left + t + " " * right + " ║")
    print("╚" + "═" * inner_width + "╝")


def box_top():
    print("╔" + BORDER_FILL + "╗")


def box_title(title):
    t = truncate_to_width(str(title), BOX_INNER)
    left = manual_max(0, (BOX_INNER - visible_width(t)) // 2)
    right = manual_max(0, BOX_INNER - visible_width(t) - left)
    print("║ " + " " * left + t + " " * right + " ║")


def box_sep():
    print("╠" + BORDER_FILL + "╣")


def box_bottom():
    print("╚" + BORDER_FILL + "╝")


def box_line(text):
    s = truncate_to_width(str(text), BOX_INNER)
    print("║ " + pad_to_width(s, BOX_INNER) + " ║")


def box_empty_line():
    print("║ " + " " * BOX_INNER + " ║")


def box_kv(key, value):
    k = str(key)
    v = str(value)
    k_with_colon = k + ":"
    kw_colon = visible_width(k_with_colon)
    if kw_colon >= BOX_INNER - 5:
        ktr = truncate_to_width(k_with_colon, BOX_INNER - 2)
        print("║ " + pad_to_width(ktr, BOX_INNER) + " ║")
        for w in wrap_text_to_width(v, BOX_INNER - 2):
            print("║ " + pad_to_width(w, BOX_INNER - 2) + " ║")
        return
    first_value_width = BOX_INNER - kw_colon - 2
    wrapped = wrap_text_to_width(v, first_value_width)
    if not wrapped:
        print("║ " + pad_to_width(k_with_colon + " " * (BOX_INNER - kw_colon - 1), BOX_INNER) + " ║")
        return
    print("║ " + pad_to_width(k_with_colon + " " + wrapped[0], BOX_INNER) + " ║")
    for w in wrapped[1:]:
        print("║ " + pad_to_width(" " * (kw_colon + 1) + w, BOX_INNER) + " ║")