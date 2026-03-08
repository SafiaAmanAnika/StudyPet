
from quiz_config_helpers import (
    load_data, calculate_grade, print_progress_bar, manual_len, manual_sum
)
from quiz_ui_input import (
    clear_screen, box_top, box_title, box_sep, box_bottom, box_line, box_kv,
    wrap_text_to_width, truncate_to_width, BOX_INNER
)
from quiz_charts import build_vertical_trend, build_overall_chart

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

def syllabus_coverage_tracker():
    """Display curriculum progress report showing syllabus coverage per subject"""
    clear_screen()
    box_top()
    box_title("CURRICULUM PROGRESS REPORT")
    box_bottom()
    
    data = load_data()
    subjects = data["subjects"]
    
    if manual_len(list(subjects.keys())) == 0:
        print("\nNo subjects found.")
        input("Press Enter...")
        return
    
    # Process each subject
    for subject in subjects:
        sub = subjects[subject]
        quizzes = sub.get("quiz", [])
        mids = sub.get("mid", [])
        
        # Calculate syllabus coverage
        total_completed = 0
        for q in quizzes:
            total_completed += q.get("syllabus", 0)
        for m in mids:
            total_completed += m.get("syllabus", 0)
        
        if total_completed > 100:
            total_completed = 100
        
        remaining = 100 - total_completed
        
        # Display subject report
        box_top()
        box_title(subject.upper())
        box_sep()
        
        # Show quizzes
        if manual_len(quizzes) > 0:
            box_line("📚 Quizzes:")
            for q in quizzes:
                quiz_info = f"{q.get('title','Quiz')}: {q.get('obtained',0)} / {q.get('total',0)}  {q.get('syllabus',0)}% syllabus"
                box_line("  " + truncate_to_width(quiz_info, BOX_INNER - 2))
        
        # Show mids
        if manual_len(mids) > 0:
            mid_total = sum(m.get("syllabus", 0) for m in mids)
            box_line("📝 Mid Coverage:")
            box_line("  " + truncate_to_width(f"Total → {mid_total}%", BOX_INNER - 2))
        
        box_sep()
        
        # Show overall progress
        box_kv("Overall Progress :", f"{total_completed:.1f}%")
        box_line("  " + truncate_to_width(print_progress_bar(total_completed, show_percent=False), BOX_INNER - 2))
        box_kv("Syllabus Completed :", f"{total_completed:.1f}%")
        box_kv("Syllabus Remaining :", f"{remaining:.1f}%")
        
        box_bottom()
        print()
    
    input("Press Enter...")

# ============================================================================
# PERFORMANCE TREND MONITOR
# ============================================================================

def result_overview_and_advisor():
    """Display detailed performance analysis with trends and advice"""
    clear_screen()
    box_top()
    box_title("PERFORMANCE TREND MONITOR")
    box_bottom()
    
    data = load_data()
    subjects = data["subjects"]
    
    if manual_len(list(subjects.keys())) == 0:
        print("No subjects found.")
        input("Press Enter...")
        return
    
    # Process each subject
    for subject in subjects:
        sub = subjects[subject]
        quizzes = sub.get("quiz", [])
        mids = sub.get("mid", [])
        
        # Skip if no exams
        if manual_len(quizzes) == 0 and manual_len(mids) == 0:
            continue
        
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
        
        # Display subject performance
        box_top()
        box_title(subject.upper())
        box_sep()
        
        # Show quizzes
        if manual_len(quizzes) > 0:
            box_line("📚 Quizzes:")
            for q in quizzes:
                quiz_info = f"{q.get('title','Quiz')}: {q.get('obtained',0)} / {q.get('total',0)}  {q.get('syllabus',0)}% syllabus"
                box_line("  " + truncate_to_width(quiz_info, BOX_INNER - 2))
        
        # Show mid coverage
        if manual_len(mids) > 0:
            mid_total = sum(m.get("syllabus", 0) for m in mids)
            box_line("📝 Mid Coverage:")
            box_line("  " + truncate_to_width(f"Syllabus Covered: {mid_total}%", BOX_INNER - 2))
        
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
        
        box_sep()
        
        # Display summary statistics
        box_kv("Total:", f"{obtained_marks} / {total_marks}")
        box_kv("Percentage:", f"{percent:.2f}%")
        box_kv("Grade:", grade)
        box_kv("Remaining Syllabus:", f"{remaining}%")
        
        # Display trend chart if enough exams
        if manual_len(combined) >= 2:
            box_kv("Trend:", "")
            chart_lines = build_vertical_trend(combined)
            for ln in chart_lines:
                box_line("  " + truncate_to_width(ln, BOX_INNER - 2))
            box_kv("Status:", trend_label)
        else:
            box_kv("Trend:", "Not enough exams to show the trend")
            box_kv("Status:", "Not enough exams to show the status")
        
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
            box_line("Advice:")
            for a in advice:
                wrapped = wrap_text_to_width(a, BOX_INNER - 4)
                for i, w in enumerate(wrapped):
                    if i == 0:
                        box_line("  - " + w)
                    else:
                        box_line("    " + w)
        
        box_bottom()
        print("-" * 60)
    
    input("\nPress Enter...")

# ============================================================================
# DASHBOARD VIEW
# ============================================================================

def view_dashboard():
    """Display comprehensive dashboard with all subjects performance"""
    clear_screen()
    box_top()
    box_title("DASHBOARD")
    box_bottom()
    
    data = load_data()
    subjects = data["subjects"]
    
    if manual_len(list(subjects.keys())) == 0:
        print("No subjects found.")
        input("Press Enter...")
        return
    
    overall_percents = []
    subject_names = []
    
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
        
        # Display subject card
        box_top()
        box_title(subject.upper())
        box_sep()
        
        box_kv("Overall Percentage     :", f"{percent:6.2f}%")
        box_kv("Current Grade          :", grade)
        box_kv("Syllabus Completed     :", f"{total_syllabus_done:6.2f}%")
        box_kv("Remaining Coverage     :", f"{remaining:6.2f}%")
        box_kv("Predicted Final Grade  :", predicted)
        
        box_bottom()
        print()
    
    # Display overall chart if subjects exist
    if manual_len(overall_percents) > 0:
        overall_avg = manual_sum(overall_percents) / manual_len(overall_percents)
        
        print("════════════════════════════════════════")
        print("📊 OVERALL PERFORMANCE CHART\n")
        
        overall_chart_lines = build_overall_chart(
            subject_names,
            overall_percents,
            max_bars=len(subject_names)
        )
        
        for ln in overall_chart_lines:
            print(truncate_to_width(ln, BOX_INNER))
        
        print(f"\nOverall Average Across Subjects: {overall_avg:.2f}%")
    
    input("\nPress Enter...")