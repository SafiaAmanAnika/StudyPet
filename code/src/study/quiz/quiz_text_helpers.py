from src.custom.custom_text import char_width

# ============================================================================
# TEXT FORMATTING & WIDTH HELPERS
# ============================================================================

def visible_width(s):
    width = 0
    for ch in s:
        width += char_width(ch)
    return width


def truncate_to_width(s, maxw):
    if maxw <= 0:
        return ""
    return s[:maxw]


def pad_to_width(s, width):
    cur = visible_width(s)
    if cur >= width:
        return s
    return s + " " * (width - cur)


def wrap_text_to_width(s, maxw):
    if maxw <= 0:
        return [""]
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        if cur == "":
            if visible_width(w) <= maxw:
                cur = w
            else:
                i = 0
                while i < len(w):
                    lines.append(w[i:i+maxw])
                    i += maxw
                cur = ""
        else:
            if visible_width(cur) + 1 + visible_width(w) <= maxw:
                cur = cur + " " + w
            else:
                lines.append(cur)
                if visible_width(w) <= maxw:
                    cur = w
                else:
                    i = 0
                    while i < len(w):
                        lines.append(w[i:i+maxw])
                        i += maxw
                    cur = ""
    if cur != "":
        lines.append(cur)
    return [truncate_to_width(line, maxw) for line in lines]