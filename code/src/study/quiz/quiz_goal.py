from src.study.quiz.quiz_config_helpers import manual_len, manual_strip, calculate_grade
from src.study.quiz.quiz_file_io import load_data, save_data
from src.study.quiz.quiz_ui_input import clear_screen, ask_float, manual_lower, _error_box
from src.study.quiz.quiz_goal_helpers import (
    GRADE_THRESHOLDS, grade_min_percent, ask_int, distribute_marks, pick_subject_for_goal
)
from src.interface.ui import print_fancy_box, pause

CARD_WIDTH = 73

# ============================================================================
# GOAL SETTER
# ============================================================================

def set_goal(user_id=None):
    clear_screen()
    print_fancy_box("🎯 Set Your Target Grade",
                    ["Plan your target grade based on remaining exams."],
                    width=CARD_WIDTH, theme="cyan")

    data = load_data(user_id=user_id)
    if manual_len(list(data.get("subjects", {}).keys())) == 0:
        clear_screen()
        print_fancy_box("No Subjects Found", ["Add quiz or mid marks first."], theme="yellow")
        pause()
        return

    subject = pick_subject_for_goal(data)
    if subject is None:
        return

    sub = data["subjects"][subject]
    quizzes = sub.get("quiz", [])
    mids = sub.get("mid", [])

    clear_screen()
    current_obtained = current_total = 0.0
    lines = []

    if manual_len(quizzes) > 0:
        lines.append("📚 Quizzes so far:")
        for q in quizzes:
            obt, tot = q.get("obtained", 0), q.get("total", 0)
            pct = (obt / tot * 100) if tot > 0 else 0
            lines.append(f"  {q.get('title','Quiz')}: {obt} / {tot} ({pct:.2f}%)")
            current_obtained += obt
            current_total += tot

    if manual_len(mids) > 0:
        lines.append("📝 Mids so far:")
        for m in mids:
            obt, tot = m.get("obtained", 0), m.get("total", 0)
            pct = (obt / tot * 100) if tot > 0 else 0
            lines.append(f"  {m.get('title','Mid')}: {obt} / {tot} ({pct:.2f}%)")
            current_obtained += obt
            current_total += tot

    if current_total > 0:
        current_pct = (current_obtained / current_total) * 100
        lines += ["", f"Current Total  : {current_obtained} / {current_total}",
                  f"Current %      : {current_pct:.2f}%",
                  f"Current Grade  : {calculate_grade(current_pct)}"]
    else:
        lines.append("No marks added yet.")

    print_fancy_box(f"{subject.upper()} — Current Status", lines, width=CARD_WIDTH, theme="blue")

    
    already_quiz_count = manual_len(quizzes)
    total_quizzes = ask_int(
        f"Total quizzes in your course (already done: {already_quiz_count}): ",
        already_quiz_count, 50)
    remaining_quiz_count = total_quizzes - already_quiz_count

    per_quiz_total = 0.0
    if remaining_quiz_count > 0:
        per_quiz_total = ask_float("Each remaining quiz is out of how many marks? ", 1, 1000)


    already_mid_count = manual_len(mids)
    total_mids = ask_int(
        f"Total mids in your course (already done: {already_mid_count}): ",
        already_mid_count, 50)
    remaining_mid_count = total_mids - already_mid_count

    per_mid_total = 0.0
    if remaining_mid_count > 0:
        per_mid_total = ask_float("Each remaining mid is out of how many marks? ", 1, 10000)

    
    final_total = ask_float("Final exam total marks: ", 0, 10000)

    remaining_slots = [(f"Quiz {already_quiz_count + i + 1}", per_quiz_total)
                       for i in range(remaining_quiz_count)]
    remaining_slots += [(f"Mid {already_mid_count + i + 1}", per_mid_total)
                        for i in range(remaining_mid_count)]
    if final_total > 0:
        remaining_slots.append(("Final", final_total))

    max_remaining = sum(tot for _, tot in remaining_slots)
    grand_total = current_total + max_remaining
    max_possible_pct = ((current_obtained + max_remaining) / grand_total * 100) if grand_total > 0 else 0

    clear_screen()
    print_fancy_box("📊 Your Current Situation", [
        f"Current marks      : {current_obtained} / {current_total}",
        f"Max possible total : {grand_total}",
        f"Best possible grade: {calculate_grade(max_possible_pct)} ({max_possible_pct:.2f}%)",
    ], width=CARD_WIDTH, theme="blue")

    print_fancy_box("🎯 Set Target Grade", [
        "[1] A+  (>= 80%)", "[2] A   (>= 75%)", "[3] A-  (>= 70%)",
        "[4] B+  (>= 65%)", "[5] B   (>= 60%)", "[6] C   (>= 50%)", "[7] D   (>= 40%)",
    ], width=CARD_WIDTH, theme="cyan")

    grade_options = ["A+", "A", "A-", "B+", "B", "C", "D"]
    target_grade = None
    while True:
        raw = manual_strip(input("Choose target grade (1-7): "))
        if raw.isdigit() and 1 <= int(raw) <= 7:
            target_grade = grade_options[int(raw) - 1]
            break
        _error_box("Enter a number between 1 and 7.")

    target_min_pct = grade_min_percent(target_grade)
    marks_needed = (target_min_pct / 100) * grand_total
    marks_still_needed = marks_needed - current_obtained

    clear_screen()

    if marks_still_needed <= max_remaining:
        sub["target_grade"] = target_grade
    else:
        for g, threshold in GRADE_THRESHOLDS:
            if (threshold / 100) * grand_total - current_obtained <= max_remaining:
                sub["target_grade"] = g
                break

    save_data(data, user_id=user_id)

    if marks_still_needed <= max_remaining:
        distribution = distribute_marks(marks_still_needed, remaining_slots, target_min_pct)
        result_lines = [
            f"✅ {target_grade} is achievable!", "",
            f"You need {marks_needed:.2f} / {grand_total:.2f} total ({target_min_pct}%)",
            f"You already have : {current_obtained:.2f}",
            f"You still need   : {marks_still_needed:.2f} from remaining exams",
            "", "📋 Best suggestive marks to attain your goal:",
        ]
        for title, min_n, max_n, total in distribution:
            if min_n == max_n:  
                pct = (min_n / total * 100) if total > 0 else 0
                result_lines.append(
                    f"  {title}: {min_n:.0f} / {total:.0f} ({pct:.1f}%)"
                )
            else:  
                min_pct = (min_n / total * 100) if total > 0 else 0
                max_pct = (max_n / total * 100) if total > 0 else 0
                result_lines.append(
                    f"  {title}: {min_n:.1f} - {max_n:.1f} / {total:.0f} "
                    f"({min_pct:.1f}% - {max_pct:.1f}%)"
                )
        print_fancy_box(f"🎯 Goal: {target_grade} — {subject.upper()}",
                        result_lines, width=CARD_WIDTH, theme="green")

    else:
        achievable_grade = achievable_threshold = None
        for g, threshold in GRADE_THRESHOLDS:
            if (threshold / 100) * grand_total - current_obtained <= max_remaining:
                achievable_grade = g
                achievable_threshold = threshold
                break

        not_possible_lines = [
            f"❌ {target_grade} is NOT achievable.", "",
            f"To get {target_grade} you need {marks_needed:.2f} / {grand_total:.2f}",
            f"Max you can get from remaining exams: {max_remaining:.2f}",
            f"Max possible: {current_obtained + max_remaining:.2f} / {grand_total:.2f} ({max_possible_pct:.2f}%)", "",
        ]

        if achievable_grade and achievable_grade != "F":
            marks_needed_best = (achievable_threshold / 100) * grand_total
            marks_still_best = marks_needed_best - current_obtained
            distribution = distribute_marks(marks_still_best, remaining_slots, achievable_threshold)
            not_possible_lines += [
                f"💡 Best possible grade for you: {achievable_grade}", "",
                f"You need {marks_needed_best:.2f} / {grand_total:.2f} total ({achievable_threshold}%)",
                f"You already have : {current_obtained:.2f}",
                f"You still need   : {marks_still_best:.2f} from remaining exams",
                "", "📋 Best suggestive marks to attain your goal:",
            ]
            for title, min_n, max_n, total in distribution:
                if min_n == max_n:  
                    pct = (min_n / total * 100) if total > 0 else 0
                    not_possible_lines.append(
                        f"  {title}: {min_n:.0f} / {total:.0f} ({pct:.1f}%)"
                    )
                else:  
                    min_pct = (min_n / total * 100) if total > 0 else 0
                    max_pct = (max_n / total * 100) if total > 0 else 0
                    not_possible_lines.append(
                        f"  {title}: {min_n:.1f} - {max_n:.1f} / {total:.0f} "
                        f"({min_pct:.1f}% - {max_pct:.1f}%)"
                    )
        else:
            not_possible_lines += [
                "⚠️ Even passing (D) may be difficult.",
                "Focus on improving in all remaining exams.",
            ]

        print_fancy_box(f"🎯 Goal Analysis — {subject.upper()}",
                        not_possible_lines, width=CARD_WIDTH, theme="yellow")
    pause()