from src.study.quiz.quiz_config_helpers import (
    BOX_INNER, CHART_COL_W, CHART_SPACING, CHART_MAX_BARS, CHART_HEIGHT,
    CHART_LABELS_POS, CHART_SHOW_NUMBERS, visible_width, truncate_to_width,
    manual_len, wrap_text_to_width
)

# ============================================================================
# BUILD VERTICAL TREND CHART
# ============================================================================

def build_vertical_trend(records):
    if manual_len(records) < 2:
        return []
    recs = list(records)
    last = recs[-CHART_MAX_BARS:]
    pcts, titles = [], []
    for idx, r in enumerate(last, start=1):
        tot = r.get("total", 0)
        obt = r.get("obtained", 0)
        pcts.append((obt / tot) * 100 if tot > 0 else 0)
        t = r.get("title") or (f"mid{idx}" if r.get("kind") == "mid" else f"quiz{idx}")
        titles.append(str(t))
    n = manual_len(pcts)
    spacing = CHART_SPACING
    desired_w = [max(8, visible_width(t)) for t in titles]
    total_desired = sum(desired_w) + spacing * (n - 1)
    use_variable = total_desired <= BOX_INNER
    col_widths = desired_w if use_variable else [CHART_COL_W] * n
    total_w = sum(col_widths) + spacing * (n - 1)
    max_pct = 0
    for p in pcts:
        if p > max_pct:
            max_pct = p
    scale = max_pct if max_pct > 0 else 1
    lines = []

    if CHART_LABELS_POS == "above":
        cells = []
        for i, title in enumerate(titles):
            w = col_widths[i]
            txt = title if use_variable else truncate_to_width(title, w)
            left = max(0, (w - visible_width(txt)) // 2)
            cells.append(" " * left + txt + " " * (w - left - visible_width(txt)))
        lbl = (" " * spacing).join(cells)
        lines.append(truncate_to_width(" " * max(0, (BOX_INNER - visible_width(lbl)) // 2) + lbl, BOX_INNER))

    for row in range(CHART_HEIGHT):
        row_level = CHART_HEIGHT - row
        cells = []
        for i, pct in enumerate(pcts):
            level = int((pct / scale) * CHART_HEIGHT + 0.0001)
            w = col_widths[i]
            cells.append("█" * w if level >= row_level else " " * w)
        row_line = (" " * spacing).join(cells)
        lines.append(truncate_to_width(" " * max(0, (BOX_INNER - visible_width(row_line)) // 2) + row_line, BOX_INNER))

    baseline = "─" * total_w
    left_base = max(0, (BOX_INNER - visible_width(baseline)) // 2)
    lines.append(truncate_to_width(" " * left_base + baseline, BOX_INNER))

    tick_chars = [" "] * total_w
    pos = 0
    for w in col_widths:
        center = pos + w // 2
        if center < manual_len(tick_chars):
            tick_chars[center] = "|"
        pos += w + spacing
    lines.append(truncate_to_width(" " * left_base + "".join(tick_chars), BOX_INNER))

    if CHART_SHOW_NUMBERS:
        cells = []
        for i, pct in enumerate(pcts):
            w = col_widths[i]
            t = truncate_to_width(f"{pct:.2f}%", w)
            left = max(0, (w - visible_width(t)) // 2)
            cells.append(" " * left + t + " " * (w - left - visible_width(t)))
        num_raw = (" " * spacing).join(cells)
        lines.append(truncate_to_width(" " * max(0, (BOX_INNER - visible_width(num_raw)) // 2) + num_raw, BOX_INNER))

    date_cells = []
    for i, r in enumerate(last):
        w = col_widths[i]
        date_str = r.get("date", "")
        if len(date_str) == 10:
            date_str = date_str[2:]
        t = truncate_to_width(date_str, w)
        left = max(0, (w - visible_width(t)) // 2)
        date_cells.append(" " * left + t + " " * (w - left - visible_width(t)))
    date_raw = (" " * spacing).join(date_cells)
    lines.append(truncate_to_width(" " * max(0, (BOX_INNER - visible_width(date_raw)) // 2) + date_raw, BOX_INNER))

    return lines


# ============================================================================
# BUILD OVERALL COMPARISON CHART
# ============================================================================

def build_overall_chart(subject_names, percentages, max_bars=None):
    if not subject_names or not percentages:
        return []
    max_bars = CHART_MAX_BARS if max_bars is None else max_bars
    spacing = CHART_SPACING
    height = CHART_HEIGHT
    names = subject_names[-max_bars:]
    pcts = percentages[-max_bars:]
    n = manual_len(pcts)
    col_widths = [8] * n
    total_w = sum(col_widths) + spacing * (n - 1)
    max_pct = 0
    for p in pcts:
        if p > max_pct:
            max_pct = p
    scale = max_pct if max_pct > 0 else 1
    out = []

    for row in range(height):
        row_level = height - row
        cells = []
        for i, pct in enumerate(pcts):
            level = int((pct / scale) * height + 0.0001)
            w = col_widths[i]
            cells.append("█" * w if level >= row_level else " " * w)
        row_line = (" " * spacing).join(cells)
        out.append(truncate_to_width(" " * max(0, (BOX_INNER - visible_width(row_line)) // 2) + row_line, BOX_INNER))

    baseline = "─" * total_w
    left_base = max(0, (BOX_INNER - visible_width(baseline)) // 2)
    out.append(truncate_to_width(" " * left_base + baseline, BOX_INNER))

    tick_chars = [" "] * total_w
    pos = 0
    for w in col_widths:
        center = pos + w // 2
        if center < manual_len(tick_chars):
            tick_chars[center] = "|"
        pos += w + spacing
    out.append(truncate_to_width(" " * left_base + "".join(tick_chars), BOX_INNER))

    cells = []
    for i, pct in enumerate(pcts):
        w = col_widths[i]
        t = truncate_to_width(f"{pct:.2f}%", w)
        left = max(0, (w - visible_width(t)) // 2)
        cells.append(" " * left + t + " " * (w - left - visible_width(t)))
    num_raw = (" " * spacing).join(cells)
    out.append(truncate_to_width(" " * max(0, (BOX_INNER - visible_width(num_raw)) // 2) + num_raw, BOX_INNER))

    wrapped_labels = []
    max_lines = 1
    for name in names:
        wrapped = wrap_text_to_width(name, 8)
        wrapped_labels.append(wrapped)
        if manual_len(wrapped) > max_lines:
            max_lines = manual_len(wrapped)

    for line_idx in range(max_lines):
        label_cells = []
        for i in range(n):
            w = col_widths[i]
            wrapped = wrapped_labels[i]
            txt = wrapped[line_idx] if line_idx < manual_len(wrapped) else ""
            left = max(0, (w - visible_width(txt)) // 2)
            label_cells.append(" " * left + txt + " " * (w - left - visible_width(txt)))
        label_line = (" " * spacing).join(label_cells)
        out.append(truncate_to_width(" " * max(0, (BOX_INNER - visible_width(label_line)) // 2) + label_line, BOX_INNER))

    return out