from src.study.quiz.quiz_config_helpers import (
    load_data, calculate_grade, print_progress_bar, manual_len, manual_sum,
    wrap_text_to_width, truncate_to_width, BOX_INNER,
)
from src.study.quiz.quiz_ui_input import (
    clear_screen
)
from src.study.quiz.quiz_charts import build_vertical_trend, build_overall_chart
from src.interface.ui import print_fancy_box, pause

CARD_WIDTH = 73

# ============================================================================
# TREND ANALYSIS FUNCTIONS
# ============================================================================

def determine_trend_label(percentages, threshold=0.5):
    """Determine if performance is improving, declining, or stable"""
    n = manual_len(percentages)
    
    # Not enough data
    if n < 2:
        return "⚠️ Not enough exams for trend"
    
    # Only two exams
    if n == 2:
        diff = percentages[-1] - percentages[-2]
        if diff > threshold:
            return "📈 Improving"
        if diff < -threshold:
            return "📉 Declining"
        return "🔄 Stable"
    
    # Multiple exams - analyze all differences
    diffs = []
    for i in range(1, n):
        diffs.append(percentages[i] - percentages[i-1])
    
    # Count positive and negative changes
    pos = sum(1 for d in diffs if d > threshold)
    neg = sum(1 for d in diffs if d < -threshold)
    
    # All positive differences
    if pos == len(diffs):
        return "📈 Improving"
    
    # All negative differences
    if neg == len(diffs):
        return "📉 Declining"
    
    # Mixed changes
    return "🔄 Stable"

def predict_final_grade(current_percent, syllabus_done):
    """Predict final grade based on current performance and syllabus coverage"""
    if syllabus_done == 0:
        return "N/A"
    
    remaining = 100 - syllabus_done
    predicted = current_percent
    
    # Boost prediction for good students
    if current_percent >= 75:
        predicted += remaining * 0.05
    # Lower prediction for struggling students
    elif current_percent < 50:
        predicted -= remaining * 0.03
    
    # Clamp between 0 and 100
    predicted = max(0, min(100, predicted))
    
    return calculate_grade(predicted)

# ============================================================================
# SYLLABUS COVERAGE TRACKER
# ============================================================================

def syllabus_coverage_tracker(user_id=None):
    """Display curriculum progress report showing syllabus coverage per subject"""
    clear_screen()
    print_fancy_box(
        "📚 Curriculum Progress Report",
        ["Subject-wise quiz and syllabus coverage."],
        width=CARD_WIDTH,
        theme="cyan",
    )
    
    data = load_data(user_id=user_id)
    subjects = data["subjects"]
    
    if manual_len(list(subjects.keys())) == 0:
        clear_screen()
        print_fancy_box(
            "No Subjects Found",
            ["Add quiz or mid marks first to view curriculum progress."],
            theme="yellow",
        )
        pause()
        return
    
    # Process each subject
    for subject in subjects:
        sub = subjects[subject]
        quizzes = sub.get("quiz", [])
        mids = sub.get("mid", [])
        lines = []
        
        # Calculate syllabus coverage
        total_completed = 0
        for q in quizzes:
            total_completed += q.get("syllabus", 0)
        for m in mids:
            total_completed += m.get("syllabus", 0)
        
        if total_completed > 100:
            total_completed = 100
        
        remaining = 100 - total_completed
        
        # Show quizzes
        if manual_len(quizzes) > 0:
            lines.append("📚 Quizzes:")
            for q in quizzes:
                quiz_info = f"{q.get('title','Quiz')}: {q.get('obtained',0)} / {q.get('total',0)}  {q.get('syllabus',0)}% syllabus"
                lines.append("- " + truncate_to_width(quiz_info, 66))
        
        # Show mids
        if manual_len(mids) > 0:
            mid_total = sum(m.get("syllabus", 0) for m in mids)
            lines.append("📝 Mid Coverage:")
            lines.append(f"- Total -> {mid_total}%")

        lines.append("")
        
        # Show overall progress
        lines.append(f"Overall Progress: {total_completed:.1f}%")
        lines.append(print_progress_bar(total_completed, show_percent=False))
        lines.append(f"Syllabus Completed: {total_completed:.1f}%")
        lines.append(f"Syllabus Remaining: {remaining:.1f}%")

        print_fancy_box(subject.upper(), lines, width=CARD_WIDTH, theme="blue")
    
    pause()

# ============================================================================
# PERFORMANCE TREND MONITOR
# ============================================================================

def result_overview_and_advisor(user_id=None):
    """Display detailed performance analysis with trends and advice"""
    clear_screen()
    print_fancy_box(
        "📈 Performance Trend Monitor",
        ["Exam trend, status, and actionable advice per subject."],
        width=CARD_WIDTH,
        theme="cyan",
    )
    
    data = load_data(user_id=user_id)
    subjects = data["subjects"]
    
    if manual_len(list(subjects.keys())) == 0:
        clear_screen()
        print_fancy_box(
            "No Subjects Found",
            ["Add quiz or mid marks first to view performance trends."],
            theme="yellow",
        )
        pause()
        return
    
    printed_any = False

    # Process each subject
    for subject in subjects:
        sub = subjects[subject]
        quizzes = sub.get("quiz", [])
        mids = sub.get("mid", [])
        
        # Skip if no exams
        if manual_len(quizzes) == 0 and manual_len(mids) == 0:
            continue
        printed_any = True
        lines = []
        
        # Get combined exam records
        combined = []
        for q in quizzes:
            r = dict(q)
            r['kind'] = 'quiz'
            combined.append(r)
        for m in mids:
            r = dict(m)
            r['kind'] = 'mid'
            combined.append(r)
        
        combined.sort(key=lambda r: r.get("date", ""))
        
        # Assign default titles if missing
        qcnt = mcnt = 0
        for r in combined:
            if not r.get('title'):
                if r.get('kind') == 'mid':
                    mcnt += 1
                    r['title'] = f"mid{mcnt}"
                else:
                    qcnt += 1
                    r['title'] = f"quiz{qcnt}"
        
        # Show quizzes
        if manual_len(quizzes) > 0:
            lines.append("📚 Quizzes:")
            for q in quizzes:
                quiz_info = f"{q.get('title','Quiz')}: {q.get('obtained',0)} / {q.get('total',0)}  {q.get('syllabus',0)}% syllabus"
                lines.append("- " + truncate_to_width(quiz_info, 66))
        
        # Show mid coverage
        if manual_len(mids) > 0:
            mid_total = sum(m.get("syllabus", 0) for m in mids)
            lines.append("📝 Mid Coverage:")
            lines.append(f"- Syllabus Covered: {mid_total}%")
        
        # Calculate overall statistics
        total_marks = sum(r.get("total", 0) for r in combined)
        obtained_marks = sum(r.get("obtained", 0) for r in combined)
        total_syllabus_done = sum(r.get("syllabus", 0) for r in combined)
        
        if total_syllabus_done > 100:
            total_syllabus_done = 100
        
        remaining = 100 - total_syllabus_done
        
        # Calculate percentage and grade
        percent = (obtained_marks / total_marks) * 100 if total_marks > 0 else 0
        grade = calculate_grade(percent)
        
        # Calculate percentages for trend
        perc_list = []
        for r in combined:
            tot = r.get("total", 0)
            obt = r.get("obtained", 0)
            perc_list.append((obt / tot) * 100 if tot > 0 else 0)
        
        trend_label = determine_trend_label(perc_list)
        
        lines.append("")
        
        # Display summary statistics
        lines.append(f"Total: {obtained_marks} / {total_marks}")
        lines.append(f"Percentage: {percent:.2f}%")
        lines.append(f"Grade: {grade}")
        lines.append(f"Remaining Syllabus: {remaining}%")
        
        # Display trend chart if enough exams
        if manual_len(combined) >= 2:
            lines.append("")
            lines.append("Trend:")
            chart_lines = build_vertical_trend(combined)
            for ln in chart_lines:
                lines.append(truncate_to_width(ln, 66))
            lines.append(f"Status: {trend_label}")
        else:
            lines.append("Trend: Not enough exams to show the trend")
            lines.append("Status: Not enough exams to show the status")
        
        # Provide personalized advice
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
        
        # Display advice
        if advice:
            lines.append("")
            lines.append("Advice:")
            for a in advice:
                wrapped = wrap_text_to_width(a, 66)
                for i, w in enumerate(wrapped):
                    if i == 0:
                        lines.append("- " + w)
                    else:
                        lines.append("  " + w)

        print_fancy_box(subject.upper(), lines, width=CARD_WIDTH, theme="magenta")

    if not printed_any:
        print_fancy_box(
            "No Exam Data",
            ["Add quiz or mid marks to generate trend insights."],
            width=CARD_WIDTH,
            theme="yellow",
        )
    
    pause()

# ============================================================================
# DASHBOARD VIEW
# ============================================================================

def view_dashboard(user_id=None):
    """Display comprehensive dashboard with all subjects performance"""
    clear_screen()
    print_fancy_box(
        "📊 Performance Dashboard",
        ["Subject overview with grades and prediction."],
        width=CARD_WIDTH,
        theme="cyan",
    )
    
    data = load_data(user_id=user_id)
    subjects = data["subjects"]
    
    if manual_len(list(subjects.keys())) == 0:
        clear_screen()
        print_fancy_box(
            "No Subjects Found",
            ["Add quiz or mid marks first to view the dashboard."],
            theme="yellow",
        )
        pause()
        return
    
    overall_percents = []
    subject_names = []
    printed_any = False
    
    # Process each subject
    for subject in subjects:
        sub = subjects[subject]
        quizzes = sub.get("quiz", [])
        mids = sub.get("mid", [])
        combined = quizzes + mids
        
        # Skip if no exams
        total_marks = sum(r.get("total", 0) for r in combined)
        if total_marks == 0:
            continue
        printed_any = True
        
        # Calculate statistics
        obtained_marks = sum(r.get("obtained", 0) for r in combined)
        total_syllabus_done = sum(r.get("syllabus", 0) for r in combined)
        
        if total_syllabus_done > 100:
            total_syllabus_done = 100
        
        remaining = 100 - total_syllabus_done
        
        percent = (obtained_marks / total_marks) * 100
        grade = calculate_grade(percent)
        predicted = predict_final_grade(percent, total_syllabus_done)
        
        overall_percents.append(percent)
        subject_names.append(subject)
        
        lines = [
            f"Overall Percentage: {percent:6.2f}%",
            f"Current Grade: {grade}",
            f"Syllabus Completed: {total_syllabus_done:6.2f}%",
            f"Remaining Coverage: {remaining:6.2f}%",
            f"Predicted Final Grade: {predicted}",
        ]

        print_fancy_box(subject.upper(), lines, width=CARD_WIDTH, theme="blue")
    
    # Display overall chart if subjects exist
    if manual_len(overall_percents) > 0:
        overall_avg = manual_sum(overall_percents) / manual_len(overall_percents)

        overall_chart_lines = build_overall_chart(
            subject_names,
            overall_percents,
            max_bars=len(subject_names)
        )

        chart_lines = [truncate_to_width(ln, BOX_INNER) for ln in overall_chart_lines]
        chart_lines.append("")
        chart_lines.append(f"Overall Average Across Subjects: {overall_avg:.2f}%")
        print_fancy_box("📊 Overall Performance Chart", chart_lines, theme="green")

    if not printed_any:
        print_fancy_box(
            "No Scored Exams",
            ["Subjects exist, but no scored quiz/mid entries were found."],
            width=CARD_WIDTH,
            theme="yellow",
        )

    pause()