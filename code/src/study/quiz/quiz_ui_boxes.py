from src.study.quiz.quiz_config_helpers import (
    BOX_INNER, visible_width, truncate_to_width, pad_to_width, wrap_text_to_width
)

BORDER_FILL = "═" * (BOX_INNER + 2)

# ============================================================================
# BOX DRAWING FUNCTIONS
# ============================================================================

def box_top():
    print("╔" + BORDER_FILL + "╗")


def box_title(title):
    t = truncate_to_width(str(title), BOX_INNER)
    left = max(0, (BOX_INNER - visible_width(t)) // 2)
    right = max(0, BOX_INNER - visible_width(t) - left)
    print("║ " + " " * left + t + " " * right + " ║")


def box_sep():
    print("╠" + BORDER_FILL + "╣")


def box_bottom():
    print("╚" + BORDER_FILL + "╝")


def box_line(text):
    s = truncate_to_width(str(text), BOX_INNER)
    print("║ " + pad_to_width(s, BOX_INNER) + " ║")


def box_kv(key, value):
    k = str(key)
    v = str(value)
    kw = visible_width(k)
    if kw >= BOX_INNER:
        ktr = truncate_to_width(k, BOX_INNER - 1)
        print("║ " + pad_to_width(ktr + " ", BOX_INNER) + " ║")
        for w in wrap_text_to_width(v, BOX_INNER):
            print("║ " + pad_to_width(w, BOX_INNER) + " ║")
        return
    first_value_width = BOX_INNER - kw - 1
    wrapped = wrap_text_to_width(v, first_value_width)
    if not wrapped:
        print("║ " + pad_to_width(k + " " * (BOX_INNER - kw), BOX_INNER) + " ║")
        return
    print("║ " + pad_to_width(k + " " + wrapped[0], BOX_INNER) + " ║")
    for w in wrapped[1:]:
        print("║ " + pad_to_width(" " * (kw + 1) + w, BOX_INNER) + " ║")