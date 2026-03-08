
from quiz_config_helpers import (
    BOX_INNER, CHART_COL_W, CHART_SPACING, CHART_MAX_BARS, CHART_HEIGHT,
    CHART_LABELS_POS, CHART_SHOW_NUMBERS, visible_width, truncate_to_width,
    manual_len
)

# ============================================================================
# BUILD VERTICAL TREND CHART
# ============================================================================

def build_vertical_trend(records):
    """Build vertical bar chart showing trend of recent exams"""
    if manual_len(records) < 2:
        return []
    
    recs = sorted(records, key=lambda r: r.get("date", ""))
    last = recs[-CHART_MAX_BARS:]
    pcts = []
    titles = []
    
    for idx, r in enumerate(last, start=1):
        tot = r.get("total", 0)
        obt = r.get("obtained", 0)
        pct = (obt / tot) * 100 if tot > 0 else 0
        pcts.append(pct)
        t = r.get("title") or (f"mid{idx}" if r.get("kind") == "mid" else f"quiz{idx}")
        titles.append(str(t))
    
    n = len(pcts)
    base_w = CHART_COL_W
    spacing = CHART_SPACING
    
    # Calculate desired widths
    desired_w = [max(base_w, visible_width(t)) for t in titles]
    total_desired = sum(desired_w) + spacing * (n - 1)
    use_variable = total_desired <= BOX_INNER
    col_widths = desired_w if use_variable else [base_w] * n
    total_w = sum(col_widths) + spacing * (n - 1)
    
    # Calculate scale
    max_pct = max(pcts) if pcts else 1
    scale = max_pct if max_pct > 0 else 1
    lines = []
    
    # ---- LABELS ABOVE ----
    if CHART_LABELS_POS == "above":
        label_cells = []
        for i, title in enumerate(titles):
            w = col_widths[i]
            txt = title if use_variable else truncate_to_width(title, w)
            left = max(0, (w - visible_width(txt)) // 2)
            right = w - left - visible_width(txt)
            label_cells.append(" " * left + txt + " " * right)
        
        label_line = (" " * spacing).join(label_cells)
        left_pad_lbl = max(0, (BOX_INNER - visible_width(label_line)) // 2)
        lines.append(truncate_to_width(" " * left_pad_lbl + label_line, BOX_INNER))
    
    # ---- CHART ROWS (BARS) ----
    for row in range(CHART_HEIGHT):
        row_level = CHART_HEIGHT - row
        cells = []
        
        for i, pct in enumerate(pcts):
            level = int((pct / scale) * CHART_HEIGHT + 0.0001)
            w = col_widths[i]
            
            if level >= row_level:
                cells.append("█" * w)
            else:
                cells.append(" " * w)
        
        row_line = (" " * spacing).join(cells)
        left_pad = max(0, (BOX_INNER - visible_width(row_line)) // 2)
        lines.append(truncate_to_width(" " * left_pad + row_line, BOX_INNER))
    
    # ---- BASELINE ----
    baseline = "─" * total_w
    left_pad_base = max(0, (BOX_INNER - visible_width(baseline)) // 2)
    lines.append(truncate_to_width(" " * left_pad_base + baseline, BOX_INNER))
    
    # ---- TICK MARKS ----
    tick_chars = list(" " * total_w)
    pos = 0
    for w in col_widths:
        center = pos + w // 2
        if center < len(tick_chars):
            tick_chars[center] = "|"
        pos += w + spacing
    
    tick_line = "".join(tick_chars)
    lines.append(truncate_to_width(" " * left_pad_base + tick_line, BOX_INNER))
    
    # ---- PERCENTAGE NUMBERS ----
    if CHART_SHOW_NUMBERS:
        num_cells = []
        for i, pct in enumerate(pcts):
            w = col_widths[i]
            t = f"{pct:.0f}%"
            t = truncate_to_width(t, w)
            left = max(0, (w - visible_width(t)) // 2)
            right = w - left - visible_width(t)
            num_cells.append(" " * left + t + " " * right)
        
        num_raw = (" " * spacing).join(num_cells)
        left_pad_num = max(0, (BOX_INNER - visible_width(num_raw)) // 2)
        lines.append(truncate_to_width(" " * left_pad_num + num_raw, BOX_INNER))
    
    # ---- LABELS BELOW ----
    if CHART_LABELS_POS != "above":
        label_cells = []
        for i, title in enumerate(titles):
            w = col_widths[i]
            txt = title if use_variable else truncate_to_width(title, w)
            left = max(0, (w - visible_width(txt)) // 2)
            right = w - left - visible_width(txt)
            label_cells.append(" " * left + txt + " " * right)
        
        label_line = (" " * spacing).join(label_cells)
        left_pad_lbl = max(0, (BOX_INNER - visible_width(label_line)) // 2)
        lines.append(truncate_to_width(" " * left_pad_lbl + label_line, BOX_INNER))
    
    return lines

# ============================================================================
# BUILD OVERALL COMPARISON CHART
# ============================================================================

def build_overall_chart(subject_names, percentages, max_bars=None):
    """Build horizontal bar chart comparing multiple subjects"""
    if not subject_names or not percentages:
        return []
    
    max_bars = CHART_MAX_BARS if max_bars is None else max_bars
    base_col_w = CHART_COL_W
    spacing = CHART_SPACING
    height = CHART_HEIGHT
    
    # Get last max_bars subjects
    names = subject_names[-max_bars:]
    pcts = percentages[-max_bars:]
    n = len(pcts)
    
    # Calculate column widths
    desired_w = [max(base_col_w, visible_width(name)) for name in names]
    total_desired = sum(desired_w) + spacing * (n - 1)
    use_variable = total_desired <= BOX_INNER
    col_widths = desired_w if use_variable else [base_col_w] * n
    total_w = sum(col_widths) + spacing * (n - 1)
    
    # Calculate scale
    max_pct = max(pcts) if pcts else 1
    scale = max_pct if max_pct > 0 else 1
    out = []
    
    # ---- BUILD CHART ROWS ----
    for row in range(height):
        row_level = height - row
        cells = []
        
        for i, pct in enumerate(pcts):
            level = int((pct / scale) * height + 0.0001)
            w = col_widths[i]
            
            if level >= row_level:
                cells.append("█" * w)
            else:
                cells.append(" " * w)
        
        row_line = (" " * spacing).join(cells)
        left_pad = max(0, (BOX_INNER - visible_width(row_line)) // 2)
        out.append(truncate_to_width(" " * left_pad + row_line, BOX_INNER))
    
    # ---- BASELINE ----
    baseline = "─" * total_w
    left_pad_base = max(0, (BOX_INNER - visible_width(baseline)) // 2)
    out.append(truncate_to_width(" " * left_pad_base + baseline, BOX_INNER))
    
    # ---- TICK MARKS ----
    tick_chars = list(" " * total_w)
    pos = 0
    for w in col_widths:
        center = pos + w // 2
        if center < len(tick_chars):
            tick_chars[center] = "|"
        pos += w + spacing
    
    tick_line = "".join(tick_chars)
    out.append(truncate_to_width(" " * left_pad_base + tick_line, BOX_INNER))
    
    # ---- PERCENTAGE NUMBERS ----
    num_cells = []
    for i, pct in enumerate(pcts):
        w = col_widths[i]
        t = f"{pct:.0f}%"
        t = truncate_to_width(t, w)
        left = max(0, (w - visible_width(t)) // 2)
        right = w - left - visible_width(t)
        num_cells.append(" " * left + t + " " * right)
    
    num_raw = (" " * spacing).join(num_cells)
    left_pad_num = max(0, (BOX_INNER - visible_width(num_raw)) // 2)
    out.append(truncate_to_width(" " * left_pad_num + num_raw, BOX_INNER))
    
    # ---- SUBJECT LABELS ----
    label_cells = []
    for i, name in enumerate(names):
        w = col_widths[i]
        txt = name if use_variable else truncate_to_width(name, w)
        left = max(0, (w - visible_width(txt)) // 2)
        right = w - left - visible_width(txt)
        label_cells.append(" " * left + txt + " " * right)
    
    label_line = (" " * spacing).join(label_cells)
    left_pad_lbl = max(0, (BOX_INNER - visible_width(label_line)) // 2)
    out.append(truncate_to_width(" " * left_pad_lbl + label_line, BOX_INNER))
    
    return out