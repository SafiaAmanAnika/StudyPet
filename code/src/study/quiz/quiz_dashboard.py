from src.study.quiz.quiz_config_helpers import (
    load_data, calculate_grade, manual_len, truncate_to_width, BOX_INNER
)
from src.study.quiz.quiz_ui_input import clear_screen
from src.study.quiz.quiz_charts import build_overall_chart
from src.study.quiz.quiz_syllabus import calc_personal_syllabus,calc_institute_syllabus
from src.interface.ui import print_fancy_box, pause

CARD_WIDTH = 73

# ============================================================================
# DASHBOARD VIEW
# ============================================================================

def view_dashboard(user_id=None):
    clear_screen()
    print_fancy_box(
        "📊 Performance Dashboard",
        ["Subject overview with grades."],
        width=CARD_WIDTH, theme="cyan",
    )
    data = load_data(user_id=user_id)
    subjects = data["subjects"]

    if manual_len(list(subjects.keys())) == 0:
        clear_screen()
        print_fancy_box("No Subjects Found",
                        ["Add quiz or mid marks first to view the dashboard."],
                        theme="yellow")
        pause()
        return

    overall_percents = []
    subject_names = []
    printed_any = False

    for subject in subjects:
        sub = subjects[subject]
        quizzes = sub.get("quiz", [])
        mids = sub.get("mid", [])

        combined = []
        for q in quizzes: combined.append(q)
        for m in mids: combined.append(m)

        total_marks = 0
        for r in combined: total_marks += r.get("total", 0)
        if total_marks == 0:
            continue
        printed_any = True

        obtained_marks = 0
        for r in combined: obtained_marks += r.get("obtained", 0)

        percent = (obtained_marks / total_marks) * 100
        grade = calculate_grade(percent)
        personal_covered = calc_personal_syllabus(combined)
        remaining = 100.0 - personal_covered
        target_grade = sub.get("target_grade", "Not set")

        overall_percents.append(percent)
        subject_names.append(subject)

        institute_covered = calc_institute_syllabus(combined)

        lines = [
            f"Overall Percentage         : {percent:.2f}%",
            f"Current Grade              : {grade}",
            f"Target Grade               : {target_grade}",
            f"Institute Syllabus Covered : {institute_covered:.2f}%",
            f"Your Actual Coverage       : {personal_covered:.2f}%",
            f"Your Syllabus Remaining    : {remaining:.2f}%",
        ]
        print_fancy_box(subject.upper(), lines, width=CARD_WIDTH, theme="blue")

    if manual_len(overall_percents) > 0:
        overall_chart_lines = build_overall_chart(
            subject_names, overall_percents, max_bars=manual_len(subject_names))
        chart_lines = [truncate_to_width(ln, BOX_INNER) for ln in overall_chart_lines]
        chart_lines.append("")
        print_fancy_box("📊 Overall Performance Chart", chart_lines, theme="green")

    if not printed_any:
        print_fancy_box("No Scored Exams",
                        ["Subjects exist, but no scored quiz/mid entries were found."],
                        width=CARD_WIDTH, theme="yellow")
    pause()