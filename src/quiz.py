import json
import os
import unicodedata

BOX_INNER = 48   
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "study_log.json")

CHART_COL_W = 5
CHART_SPACING = 2
CHART_MAX_BARS = 6
CHART_HEIGHT = 6
CHART_LABELS_POS = "above"
CHART_SHOW_NUMBERS = True

# -------- Minimal helpers --------
def visible_width(s):
    width = 0
    for ch in s:
        
        if unicodedata.east_asian_width(ch) in ("F", "W"):
            width += 2
        else:
            width += 1
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
                    part = w[i:i+maxw]
                    lines.append(part)
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
                        part = w[i:i+maxw]
                        lines.append(part)
                        i += maxw
                    cur = ""
    if cur != "":
        lines.append(cur)
    return [truncate_to_width(line, maxw) for line in lines]

def manual_strip(s):
    start = 0
    end = len(s) - 1
    while start <= end and s[start] in " \t\n\r":
        start += 1
    while end >= start and s[end] in " \t\n\r":
        end -= 1
    return s[start:end+1]

def manual_is_number(s):
    if s == "":
        return False
    parts = s.split(".")
    if len(parts) == 1:
        return parts[0].isdigit()
    if len(parts) == 2:
        a,b = parts
        return (a.isdigit() and b.isdigit() and b != "")
    return False

def date_valid_simple(s):
    parts = s.split("-")
    if len(parts) != 3:
        return False
    y,m,d = parts
    if not (y.isdigit() and len(y) == 4): return False
    if not (m.isdigit() and 1 <= len(m) <= 2): return False
    if not (d.isdigit() and 1 <= len(d) <= 2): return False
    return True

# -------- File I/O --------
def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_data():
    ensure_data_dir()
    if not os.path.exists(DATA_FILE):
        return {"subjects": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"subjects": {}}

def save_data(data):
    ensure_data_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# -------- Screen & boxes (use fixed BOX_INNER) --------
def clear_screen():
    try:
        if os.name == "nt":
            os.system("cls")
        else:
            print("\033[2J\033[H", end="")
    except Exception:
        print("\n" * 60)

BORDER_FILL = "═" * (BOX_INNER + 2)
def box_top(): print("╔" + BORDER_FILL + "╗")
def box_title(title):
    t = str(title)
    t = truncate_to_width(t, BOX_INNER)
    left = max(0, (BOX_INNER - visible_width(t)) // 2)
    right = max(0, BOX_INNER - visible_width(t) - left)
    print("║ " + " " * left + t + " " * right + " ║")
def box_sep(): print("╠" + BORDER_FILL + "╣")
def box_bottom(): print("╚" + BORDER_FILL + "╝")
def box_line(text):
    s = str(text)
    s_trunc = truncate_to_width(s, BOX_INNER)
    s_pad = pad_to_width(s_trunc, BOX_INNER)
    print("║ " + s_pad + " ║")
def box_kv(key, value):
    k = str(key); v = str(value)
    kw = visible_width(k)
    if kw >= BOX_INNER:
        ktr = truncate_to_width(k, BOX_INNER - 1)
        print("║ " + pad_to_width(ktr + " ", BOX_INNER) + " ║")
        wrapped = wrap_text_to_width(v, BOX_INNER)
        for w in wrapped:
            print("║ " + pad_to_width(w, BOX_INNER) + " ║")
        return
    first_value_width = BOX_INNER - kw - 1
    wrapped = wrap_text_to_width(v, first_value_width)
    if not wrapped:
        print("║ " + pad_to_width(k + " " * (BOX_INNER - kw), BOX_INNER) + " ║")
        return
    first = wrapped[0]
    line = k + " " + first
    print("║ " + pad_to_width(line, BOX_INNER) + " ║")
    for w in wrapped[1:]:
        pad = " " * (kw + 1)
        line = pad + w
        print("║ " + pad_to_width(line, BOX_INNER) + " ║")

# -------- Input helpers --------
def ask_title(prompt):
    while True:
        v = manual_strip(input(prompt))
        if v == "":
            print("Enter a short title (e.g., quiz1)."); continue
        if "\n" in v or "\r" in v:
            print("Invalid title."); continue
        return v

def ask_float(prompt, min_v=None, max_v=None):
    while True:
        v = manual_strip(input(prompt))
        if not manual_is_number(v):
            print("Enter a valid number."); continue
        num = float(v)
        if min_v is not None and num < min_v:
            print("Value must be >= ", min_v); continue
        if max_v is not None and num > max_v:
            print("Value must be <= ", max_v); continue
        return num

def ask_date(prompt):
    while True:
        v = manual_strip(input(prompt))
        if date_valid_simple(v):
            return v
        print("Enter date as YYYY-MM-DD")

# -------- Add marks --------
def add_quiz_marks():
    clear_screen(); box_top(); box_title("ADD QUIZ MARKS"); box_bottom()
    data = load_data()
    subject = ask_title("Subject name: ")
    title = ask_title("Quiz title (e.g., quiz1): ")
    total = ask_float("Total marks: ", 1)
    obtained = ask_float("Obtained marks: ", 0, total)
    syllabus = ask_float("Syllabus covered in this exam (%): ", 0, 100)
    date_str = ask_date("Date (YYYY-MM-DD): ")
    if subject not in data["subjects"]:
        data["subjects"][subject] = {"quiz": [], "mid": []}
    data["subjects"][subject]["quiz"].append({
        "title": title, "total": total, "obtained": obtained, "syllabus": syllabus, "date": date_str
    })
    save_data(data)
    print("\n✅ Quiz added."); input("Press Enter...")

def add_mid_marks():
    clear_screen(); box_top(); box_title("ADD MID MARKS"); box_bottom()
    data = load_data()
    subject = ask_title("Subject name: ")
    title = ask_title("Mid title (e.g., mid1): ")
    total = ask_float("Total marks: ", 1)
    obtained = ask_float("Obtained marks: ", 0, total)
    syllabus = ask_float("Syllabus covered in this exam (%): ", 0, 100)
    date_str = ask_date("Date (YYYY-MM-DD): ")
    if subject not in data["subjects"]:
        data["subjects"][subject] = {"quiz": [], "mid": []}
    data["subjects"][subject]["mid"].append({
        "title": title, "total": total, "obtained": obtained, "syllabus": syllabus, "date": date_str
    })
    save_data(data)
    print("\n✅ Mid added."); input("Press Enter...")

def add_marks_menu():
    while True:
        clear_screen(); box_top(); box_title("ADD MARKS"); box_bottom()
        print("[1] Add Quiz Marks"); print("[2] Add Mid Marks"); print("[0] Back")
        c = manual_strip(input("Choose: "))
        if c == "1": add_quiz_marks()
        elif c == "2": add_mid_marks()
        elif c == "0": return
        else: print("Invalid choice"); input("Press Enter...")

# -------- Syllabus tracker --------
def syllabus_coverage_tracker():
    clear_screen(); box_top(); box_title("CURRICULUM PROGRESS REPORT"); box_bottom()
    data = load_data(); subjects = data["subjects"]
    if manual_len(list(subjects.keys())) == 0:
        print("\nNo subjects found."); input("Press Enter..."); return
    for subject in subjects:
        sub = subjects[subject]
        quizzes = sub.get("quiz", []); mids = sub.get("mid", [])
        total_completed = 0
        for q in quizzes: total_completed += q.get("syllabus", 0)
        for m in mids: total_completed += m.get("syllabus", 0)
        if total_completed > 100: total_completed = 100
        remaining = 100 - total_completed
        box_top(); box_title(subject.upper()); box_sep()
        if manual_len(quizzes) > 0:
            box_line("📚 Quizzes:")
            for q in quizzes:
                box_line("  " + truncate_to_width(f"{q.get('title','Quiz')}: {q.get('obtained',0)} / {q.get('total',0)}  {q.get('syllabus',0)}% syllabus", BOX_INNER))
        if manual_len(mids) > 0:
            mid_total = sum(m.get("syllabus",0) for m in mids)
            box_line("📝 Mid Coverage:"); box_line("  " + truncate_to_width(f"Total → {mid_total}%", BOX_INNER))
        box_sep()
        box_kv("Overall Progress :", f"{total_completed:.1f}%")
        box_line("  " + truncate_to_width(print_progress_bar(total_completed, show_percent=False), BOX_INNER - 2))
        box_kv("Syllabus Completed :", f"{total_completed:.1f}%")
        box_kv("Syllabus Remaining :", f"{remaining:.1f}%")
        box_bottom(); print()
    input("Press Enter...")

# -------- Grade calc --------
def calculate_grade(percent):
    if percent >= 80: return "A+"
    if percent >= 75: return "A"
    if percent >= 70: return "A-"
    if percent >= 65: return "B+"
    if percent >= 60: return "B"
    if percent >= 50: return "C"
    if percent >= 40: return "D"
    return "F"

# -------- Chart builders (always truncated/padded) --------
def build_vertical_trend(records):
    if manual_len(records) < 2:
        return []
    recs = sorted(records, key=lambda r: r.get("date",""))
    last = recs[-CHART_MAX_BARS:]
    pcts = []; titles = []
    for idx, r in enumerate(last, start=1):
        tot = r.get("total", 0); obt = r.get("obtained", 0)
        pct = (obt / tot) * 100 if tot > 0 else 0
        pcts.append(pct)
        t = r.get("title") or (f"mid{idx}" if r.get("kind") == "mid" else f"quiz{idx}")
        titles.append(str(t))
    n = len(pcts)
    base_w = CHART_COL_W; spacing = CHART_SPACING

    desired_w = [max(base_w, visible_width(t)) for t in titles]
    total_desired = sum(desired_w) + spacing * (n - 1)
    use_variable = total_desired <= BOX_INNER
    col_widths = desired_w if use_variable else [base_w] * n
    total_w = sum(col_widths) + spacing * (n - 1)

    max_pct = max(pcts) if pcts else 1
    scale = max_pct if max_pct > 0 else 1
    lines = []

    label_cells = []
    for i, title in enumerate(titles):
        w = col_widths[i]
        txt = title if use_variable else truncate_to_width(title, w)
        left = max(0, (w - visible_width(txt)) // 2)
        label_cells.append(" " * left + txt + " " * (w - left - visible_width(txt)))
    label_line = (" " * spacing).join(label_cells)
    left_pad_lbl = max(0, (BOX_INNER - visible_width(label_line)) // 2)
    if CHART_LABELS_POS == "above":
        lines.append(truncate_to_width(" " * left_pad_lbl + label_line, BOX_INNER))

    for row in range(CHART_HEIGHT):
        row_level = CHART_HEIGHT - row
        cells = []
        for i, pct in enumerate(pcts):
            level = int((pct / scale) * CHART_HEIGHT + 0.0001)
            w = col_widths[i]
            cells.append("█" * w if level >= row_level else " " * w)
        row_line = (" " * spacing).join(cells)
        left_pad = max(0, (BOX_INNER - visible_width(row_line)) // 2)
        lines.append(truncate_to_width(" " * left_pad + row_line, BOX_INNER))

    baseline = "─" * total_w
    left_pad_base = max(0, (BOX_INNER - visible_width(baseline)) // 2)
    lines.append(truncate_to_width(" " * left_pad_base + baseline, BOX_INNER))

    tick_chars = list(" " * total_w)
    pos = 0
    for w in col_widths:
        center = pos + w // 2
        if center < len(tick_chars):
            tick_chars[center] = "|"
        pos += w + spacing
    tick_line = "".join(tick_chars)
    lines.append(truncate_to_width(" " * left_pad_base + tick_line, BOX_INNER))

    if CHART_SHOW_NUMBERS:
        num_cells = []
        for i, pct in enumerate(pcts):
            w = col_widths[i]
            t = f"{pct:.0f}%"
            t = truncate_to_width(t, w)
            left = max(0, (w - visible_width(t)) // 2)
            num_cells.append(" " * left + t + " " * (w - left - visible_width(t)))
        num_raw = (" " * spacing).join(num_cells)
        left_pad_num = max(0, (BOX_INNER - visible_width(num_raw)) // 2)
        lines.append(truncate_to_width(" " * left_pad_num + num_raw, BOX_INNER))

    if CHART_LABELS_POS != "above":
        lines.append(truncate_to_width(" " * left_pad_lbl + label_line, BOX_INNER))

    return lines

def build_overall_chart(subject_names, percentages, max_bars=None, col_w=None, spacing=None, height=None, show_numbers=True):
    if not subject_names or not percentages:
        return []
    max_bars = CHART_MAX_BARS if max_bars is None else max_bars
    base_col_w = CHART_COL_W if col_w is None else col_w
    spacing = CHART_SPACING if spacing is None else spacing
    height = CHART_HEIGHT if height is None else height

    names = subject_names[-max_bars:]
    pcts = percentages[-max_bars:]
    n = len(pcts)

    desired_w = [max(base_col_w, visible_width(name)) for name in names]
    total_desired = sum(desired_w) + spacing * (n - 1)
    use_variable = total_desired <= BOX_INNER
    col_widths = desired_w if use_variable else [base_col_w] * n
    total_w = sum(col_widths) + spacing * (n - 1)

    max_pct = max(pcts) if pcts else 1
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
        left_pad = max(0, (BOX_INNER - visible_width(row_line)) // 2)
        out.append(truncate_to_width(" " * left_pad + row_line, BOX_INNER))

    baseline = "─" * total_w
    left_pad_base = max(0, (BOX_INNER - visible_width(baseline)) // 2)
    out.append(truncate_to_width(" " * left_pad_base + baseline, BOX_INNER))

    tick_chars = list(" " * total_w)
    pos = 0
    for w in col_widths:
        center = pos + w // 2
        if center < len(tick_chars):
            tick_chars[center] = "|"
        pos += w + spacing
    tick_line = "".join(tick_chars)
    out.append(truncate_to_width(" " * left_pad_base + tick_line, BOX_INNER))

    if show_numbers:
        num_cells = []
        for i, pct in enumerate(pcts):
            w = col_widths[i]
            t = f"{pct:.0f}%"
            t = truncate_to_width(t, w)
            left = max(0, (w - visible_width(t)) // 2)
            num_cells.append(" " * left + t + " " * (w - left - visible_width(t)))
        num_raw = (" " * spacing).join(num_cells)
        left_pad_num = max(0, (BOX_INNER - visible_width(num_raw)) // 2)
        out.append(truncate_to_width(" " * left_pad_num + num_raw, BOX_INNER))

    label_cells = []
    for i, name in enumerate(names):
        w = col_widths[i]
        txt = name if use_variable else truncate_to_width(name, w)
        left = max(0, (w - visible_width(txt)) // 2)
        label_cells.append(" " * left + txt + " " * (w - left - visible_width(txt)))
    label_line = (" " * spacing).join(label_cells)
    left_pad_lbl = max(0, (BOX_INNER - visible_width(label_line)) // 2)
    out.append(truncate_to_width(" " * left_pad_lbl + label_line, BOX_INNER))

    return out

# -------- Trend & views --------
def determine_trend_label(percentages, threshold=0.5):
    n = manual_len(percentages)
    if n < 2:
        return "⚠️ Not enough exams for trend"
    if n == 2:
        diff = percentages[-1] - percentages[-2]
        if diff > threshold: return "📈 Improving"
        if diff < -threshold: return "📉 Declining"
        return "🔄 Stable"
    diffs = []
    for i in range(1, n):
        diffs.append(percentages[i] - percentages[i-1])
    pos = sum(1 for d in diffs if d > threshold)
    neg = sum(1 for d in diffs if d < -threshold)
    if pos == len(diffs): return "📈 Improving"
    if neg == len(diffs): return "📉 Declining"
    return "🔄 Stable"

def result_overview_and_advisor():
    clear_screen(); box_top(); box_title("PERFORMANCE TREND MONITOR"); box_bottom()
    data = load_data(); subjects = data["subjects"]
    if manual_len(list(subjects.keys())) == 0:
        print("No subjects found."); input("Press Enter..."); return
    for subject in subjects:
        sub = subjects[subject]
        quizzes = sub.get("quiz", []); mids = sub.get("mid", [])
        if manual_len(quizzes) == 0 and manual_len(mids) == 0:
            continue
        combined = []
        for q in quizzes:
            r = dict(q); r['kind'] = 'quiz'; combined.append(r)
        for m in mids:
            r = dict(m); r['kind'] = 'mid'; combined.append(r)
        combined.sort(key=lambda r: r.get("date",""))
        qcnt = mcnt = 0
        for r in combined:
            if not r.get('title'):
                if r.get('kind') == 'mid': mcnt += 1; r['title'] = f"mid{mcnt}"
                else: qcnt += 1; r['title'] = f"quiz{qcnt}"
        box_top(); box_title(subject.upper()); box_sep()
        if manual_len(quizzes) > 0:
            box_line("📚 Quizzes:")
            for q in quizzes:
                box_line("  " + truncate_to_width(f"{q.get('title','Quiz')}: {q.get('obtained',0)} / {q.get('total',0)}  {q.get('syllabus',0)}% syllabus", BOX_INNER))
        if manual_len(mids) > 0:
            mid_total = sum(m.get("syllabus",0) for m in mids)
            box_line("📝 Mid Coverage:"); box_line("  " + truncate_to_width(f"Syllabus Covered: {mid_total}%", BOX_INNER))
        total_marks = sum(r.get("total",0) for r in combined)
        obtained_marks = sum(r.get("obtained",0) for r in combined)
        total_syllabus_done = sum(r.get("syllabus",0) for r in combined)
        if total_syllabus_done > 100: total_syllabus_done = 100
        remaining = 100 - total_syllabus_done
        percent = (obtained_marks / total_marks) * 100 if total_marks > 0 else 0
        grade = calculate_grade(percent)
        perc_list = []
        for r in combined:
            tot = r.get("total",0); obt = r.get("obtained",0)
            perc_list.append((obt / tot) * 100 if tot > 0 else 0)
        trend_label = determine_trend_label(perc_list)
        box_sep()
        box_kv("Total:", f"{obtained_marks} / {total_marks}")
        box_kv("Percentage:", f"{percent:.2f}%")
        box_kv("Grade:", grade)
        box_kv("Remaining Syllabus:", f"{remaining}%")
        if manual_len(combined) >= 2:
            box_kv("Trend:", "")
            chart_lines = build_vertical_trend(combined)
            for ln in chart_lines:
                # safe: truncate before printing inside box, with two-space indent
                box_line("  " + truncate_to_width(ln, BOX_INNER - 2))
            box_kv("Status:", trend_label)
        else:
            box_kv("Trend:", "Not enough exams to show the trend")
            box_kv("Status:", "Not enough exams to show the status")
        advice = []
        if percent < 50:
            advice.append("Focus on revising basics to improve grades.")
        elif percent < 65:
            advice.append("Maintain consistency and review weak topics.")
        elif percent < 80:
            advice.append("Push for mastery in upcoming exams to reach A+.")
        else:
            advice.append("Keep up the excellent work!")
        if total_syllabus_done < 100:
            advice.append(f"Cover remaining {100 - total_syllabus_done}% syllabus for full readiness.")
        if manual_len(combined) >= 2:
            if perc_list[-1] > perc_list[-2]:
                advice.append("Recent exam improved vs previous.")
            elif perc_list[-1] < perc_list[-2]:
                advice.append("Recent exam declined vs previous.")
        if advice:
            box_line("Advice:")
            for a in advice:
                wrapped = wrap_text_to_width(a, BOX_INNER - 4)
                for i, w in enumerate(wrapped):
                    if i == 0:
                        box_line("  - " + w)
                    else:
                        box_line("    " + w)
        box_bottom(); print("-" * 60)
    input("\nPress Enter...")

def predict_final_grade(current_percent, syllabus_done):
    if syllabus_done == 0: return "N/A"
    remaining = 100 - syllabus_done
    predicted = current_percent
    if current_percent >= 75:
        predicted += remaining * 0.05
    elif current_percent < 50:
        predicted -= remaining * 0.03
    predicted = max(0, min(100, predicted))
    return calculate_grade(predicted)

def view_dashboard():
    clear_screen(); box_top(); box_title("DASHBOARD"); box_bottom()
    data = load_data(); subjects = data["subjects"]
    if manual_len(list(subjects.keys())) == 0:
        print("No subjects found."); input("Press Enter..."); return
    overall_percents = []
    subject_names = []
    for subject in subjects:
        sub = subjects[subject]
        quizzes = sub.get("quiz", []); mids = sub.get("mid", [])
        combined = quizzes + mids
        total_marks = sum(r.get("total",0) for r in combined)
        obtained_marks = sum(r.get("obtained",0) for r in combined)
        total_syllabus_done = sum(r.get("syllabus",0) for r in combined)
        if total_syllabus_done > 100: total_syllabus_done = 100
        remaining = 100 - total_syllabus_done
        if total_marks == 0:
            continue
        percent = (obtained_marks / total_marks) * 100
        grade = calculate_grade(percent)
        predicted = predict_final_grade(percent, total_syllabus_done)
        overall_percents.append(percent)
        subject_names.append(subject)
        box_top(); box_title(subject.upper()); box_sep()
        box_kv("Overall Percentage     :", f"{percent:6.2f}%")
        box_kv("Current Grade          :", grade)
        box_kv("Syllabus Completed     :", f"{total_syllabus_done:6.2f}%")
        box_kv("Remaining Coverage     :", f"{remaining:6.2f}%")
        box_kv("Predicted Final Grade  :", predicted)
        box_bottom(); print()
    if manual_len(overall_percents) > 0:
        overall_avg = manual_sum(overall_percents) / manual_len(overall_percents)
        print("════════════════════════════════════════")
        print("📊 OVERALL PERFORMANCE CHART\n")
        overall_chart_lines = build_overall_chart(subject_names, overall_percents, max_bars=len(subject_names), show_numbers=True)
        for ln in overall_chart_lines:
            print(truncate_to_width(ln, BOX_INNER))
        print("\nOverall Average Across Subjects: {:.2f}%".format(overall_avg))
    input("\nPress Enter...")

def print_progress_bar(percent, total_blocks=20, show_percent=False):
    filled = int(percent / 100 * total_blocks)
    filled = max(0, min(total_blocks, filled))
    bar = "█" * filled + "-" * (total_blocks - filled)
    return f"[{bar}] {percent:.1f}%" if show_percent else f"[{bar}]"

def manual_len(lst):
    count = 0
    for _ in lst: count += 1
    return count

def manual_sum(lst):
    total = 0
    for v in lst: total += v
    return total

# -------- Main menu --------
def run():
    while True:
        clear_screen(); box_top(); box_title("ACADEMIC PERFORMANCE TRACKER"); box_bottom()
        print("[1] Add Marks")
        print("[2] Curriculum Progress Report")
        print("[3] Performance Trend Monitor")
        print("[4] View Dashboard")
        print("[0] Exit")
        choice = manual_strip(input("Choose: "))
        clear_screen()
        if choice == "1":
            add_marks_menu()
        elif choice == "2":
            syllabus_coverage_tracker()
        elif choice == "3":
            result_overview_and_advisor()
        elif choice == "4":
            view_dashboard()
        elif choice == "0":
            clear_screen(); print("Goodbye!"); break
        else:
            print("Invalid choice"); input("Press Enter...")
        clear_screen()

