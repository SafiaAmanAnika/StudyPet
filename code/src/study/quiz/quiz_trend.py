from src.study.quiz.quiz_config_helpers import (
    load_data, calculate_grade, manual_len, wrap_text_to_width, truncate_to_width
)
from src.study.quiz.quiz_ui_input import clear_screen
from src.study.quiz.quiz_charts import build_vertical_trend
from src.interface.ui import print_fancy_box, pause

CARD_WIDTH = 73

# ============================================================================
# TREND ANALYSIS
# ============================================================================

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
    pos = neg = 0
    for d in diffs:
        if d > threshold: pos += 1
        elif d < -threshold: neg += 1
    total_diffs = manual_len(diffs)
    if pos == total_diffs: return "📈 Improving"
    if neg == total_diffs: return "📉 Declining"
    return "🔄 Stable"

# ============================================================================
# PERFORMANCE TREND MONITOR
# ============================================================================

def result_overview_and_advisor(user_id=None):
    clear_screen()
    print_fancy_box(
        "📈 Performance Trend Monitor",
        ["Exam trend, status, and actionable advice per subject."],
        width=CARD_WIDTH, theme="cyan",
    )
    data = load_data(user_id=user_id)
    subjects = data["subjects"]
    if manual_len(list(subjects.keys())) == 0:
        clear_screen()
        print_fancy_box("No Subjects Found", ["Add quiz or mid marks first."], theme="yellow")
        pause()
        return

    printed_any = False
    for subject in subjects:
        sub = subjects[subject]
        quizzes = sub.get("quiz", [])
        mids = sub.get("mid", [])
        if manual_len(quizzes) == 0 and manual_len(mids) == 0:
            continue
        printed_any = True
        lines = []

        combined = []
        for q in quizzes:
            r = dict(q); r['kind'] = 'quiz'; combined.append(r)
        for m in mids:
            r = dict(m); r['kind'] = 'mid'; combined.append(r)

        n = manual_len(combined)
        for i in range(n):
            for j in range(0, n - i - 1):
                if combined[j].get("date", "") > combined[j+1].get("date", ""):
                    combined[j], combined[j+1] = combined[j+1], combined[j]

        qcnt = mcnt = 0
        for r in combined:
            if not r.get('title'):
                if r.get('kind') == 'mid':
                    mcnt += 1; r['title'] = f"mid{mcnt}"
                else:
                    qcnt += 1; r['title'] = f"quiz{qcnt}"

        if manual_len(quizzes) > 0:
            lines.append("📚 Quizzes:")
            for q in quizzes:
                tot = q.get('total', 0); obt = q.get('obtained', 0)
                pct = (obt / tot * 100) if tot > 0 else 0
                lines.append("- " + truncate_to_width(
                    f"{q.get('title','Quiz')} ({q.get('date','N/A')}): {obt} / {tot} ({pct:.2f}%)", 66))

        if manual_len(mids) > 0:
            lines.append("📝 Mids:")
            for m in mids:
                tot = m.get('total', 0); obt = m.get('obtained', 0)
                pct = (obt / tot * 100) if tot > 0 else 0
                lines.append("- " + truncate_to_width(
                    f"{m.get('title','Mid')} ({m.get('date','N/A')}): {obt} / {tot} ({pct:.2f}%)", 66))

        total_marks = obtained_marks = 0
        for r in combined:
            total_marks += r.get("total", 0)
            obtained_marks += r.get("obtained", 0)

        percent = (obtained_marks / total_marks) * 100 if total_marks > 0 else 0
        grade = calculate_grade(percent)
        perc_list = [(r.get("obtained",0)/r.get("total",1)*100) if r.get("total",0)>0 else 0 for r in combined]
        trend_label = determine_trend_label(perc_list)

        lines.append("")
        lines.append(f"Total: {obtained_marks} / {total_marks} ({percent:.2f}%)")
        lines.append(f"Grade: {grade}")

        if manual_len(combined) >= 2:
            lines.append(""); lines.append("Trend:")
            for ln in build_vertical_trend(combined):
                lines.append(truncate_to_width(ln, 66))
            lines.append(f"Status: {trend_label}")
        else:
            lines.append("Trend: Not enough exams to show the trend")
            lines.append("Status: Not enough exams to show the status")

        advice = []
        if percent < 50: advice.append("Focus on revising basics to improve grades.")
        elif percent < 65: advice.append("Maintain consistency and review weak topics.")
        elif percent < 80: advice.append("Push for mastery in upcoming exams to reach A+.")
        else: advice.append("Keep up the excellent work!")
        if manual_len(combined) >= 2:
            if perc_list[-1] > perc_list[-2]: advice.append("Recent exam improved vs previous.")
            elif perc_list[-1] < perc_list[-2]: advice.append("Recent exam declined vs previous.")

        if advice:
            lines.append(""); lines.append("Advice:")
            for a in advice:
                wrapped = wrap_text_to_width(a, 66)
                for i, w in enumerate(wrapped):
                    lines.append(("- " if i == 0 else "  ") + w)

        print_fancy_box(subject.upper(), lines, width=CARD_WIDTH, theme="magenta")

    if not printed_any:
        print_fancy_box("No Exam Data", ["Add quiz or mid marks to generate trend insights."],
                        width=CARD_WIDTH, theme="yellow")
    pause()