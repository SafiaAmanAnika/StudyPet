# ============================================================================
# quiz_analytics.py — re-exports all analytics functions
# quiz.py only needs to import from here
# ============================================================================

from src.study.quiz.quiz_syllabus import (
    syllabus_coverage_tracker,
    calc_institute_syllabus,
    calc_personal_syllabus,
)
from src.study.quiz.quiz_trend import (
    result_overview_and_advisor,
    determine_trend_label,
)
from src.study.quiz.quiz_dashboard import view_dashboard
from src.study.quiz.quiz_goal import set_goal