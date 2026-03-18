from src.study.quiz.quiz_config_helpers import (
    load_data, print_progress_bar, manual_len
)
from src.study.quiz.quiz_ui_input import clear_screen
from src.interface.ui import print_fancy_box, pause

CARD_WIDTH = 73

# ============================================================================
# SYLLABUS CALCULATION HELPERS
# ============================================================================

def calc_institute_syllabus(records):
    total = 0.0
    for r in records:
        total += r.get("syllabus_coverage", r.get("syllabus", 0))
    return min(total, 100.0)


def calc_personal_syllabus(records):
    total = 0.0
    for r in records:
        sc = r.get("syllabus_coverage", r.get("syllabus", 0))
        pc = r.get("personal_coverage", 100)
        total += sc * pc / 100
    return min(total, 100.0)

# ============================================================================
# SYLLABUS COVERAGE TRACKER
# ============================================================================

def syllabus_coverage_tracker(user_id=None):
    clear_screen()
    print_fancy_box(
        "📚 Curriculum Progress Report",
        ["Subject-wise syllabus coverage."],
        width=CARD_WIDTH, theme="cyan",
    )
    data = load_data(user_id=user_id)
    subjects = data["subjects"]

    if manual_len(list(subjects.keys())) == 0:
        clear_screen()
        print_fancy_box("No Subjects Found",
                        ["Add quiz or mid marks first to view curriculum progress."],
                        theme="yellow")
        pause()
        return

    for subject in subjects:
        sub = subjects[subject]
        quizzes = sub.get("quiz", [])
        mids = sub.get("mid", [])
        lines = []

        all_records = []
        for q in quizzes:
            all_records.append(q)
        for m in mids:
            all_records.append(m)

        institute_covered = calc_institute_syllabus(all_records)
        personal_covered = calc_personal_syllabus(all_records)
        remaining = 100.0 - personal_covered
        gap = institute_covered - personal_covered

        lines.append(f"📚 Institute covered   : {institute_covered:.2f}% of the whole syllabus")
        lines.append(f"📖 Your actual coverage: {personal_covered:.2f}% of the whole syllabus")
        lines.append("")

        if gap <= 0:
            lines.append(f"🎉 Congratulations! You have successfully covered")
            lines.append(f"   {personal_covered:.2f}% of your whole syllabus.")
        else:
            lines.append(f"⚠️  You are {gap:.2f}% behind your institute coverage.")
            lines.append(f"📌 Gap to revise: {gap:.2f}%")

        lines.append("")
        lines.append("📊 Coverage Comparison:")
        lines.append(f"  Your actual coverage  : {print_progress_bar(personal_covered)} {personal_covered:.2f}%")
        lines.append("")
        lines.append(f"  Remaining coverage    : {print_progress_bar(remaining)} {remaining:.2f}%")

        print_fancy_box(subject.upper(), lines, width=CARD_WIDTH, theme="blue")

    pause()