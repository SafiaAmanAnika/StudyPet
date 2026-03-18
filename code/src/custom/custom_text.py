# Text/emoji width helpers to avoid regex/unicodedata dependencies.


def _ord(ch):
    if not ch:
        return 0
    return ord(ch)


def is_zero_width(ch):
    cp = _ord(ch)
    # ZWJ and variation selectors commonly used in emoji sequences.
    return cp == 0x200D or cp == 0xFE0F


def is_emoji(ch):
    cp = _ord(ch)
    return (
        0x1F300 <= cp <= 0x1FAFF
        or 0x2600 <= cp <= 0x26FF
        or 0x2700 <= cp <= 0x27BF
    )


def is_wide_char(ch):
    cp = _ord(ch)
    # Common wide East Asian ranges.
    return (
        0x1100 <= cp <= 0x115F
        or 0x2E80 <= cp <= 0xA4CF
        or 0xAC00 <= cp <= 0xD7A3
        or 0xF900 <= cp <= 0xFAFF
        or 0xFE10 <= cp <= 0xFE19
        or 0xFE30 <= cp <= 0xFE6F
        or 0xFF00 <= cp <= 0xFF60
        or 0xFFE0 <= cp <= 0xFFE6
    )


def char_width(ch):
    if is_zero_width(ch):
        return 0
    if is_emoji(ch) or is_wide_char(ch):
        return 2
    return 1


def visible_width(text):
    width = 0
    for ch in str(text):
        width += char_width(ch)
    return width


def count_emojis(text):
    count = 0
    for ch in str(text):
        if is_emoji(ch):
            count += 1
    return count
