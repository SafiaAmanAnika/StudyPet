import json, os
from datetime import date, timedelta
from src.interface.ui import clear_screen, print_fancy_box, menu, pause

# ---------------- PATH + SAFE JSON HELPERS ---------------- #

def _project_root():
    return os.path.dirname(os.path.dirname(__file__))


def _data_path(filename: str) -> str:
    return os.path.join(_project_root(), "data", filename)


def _safe_load_json(path: str, default):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f, indent=2)
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(path, "w") as f:
            json.dump(default, f, indent=2)
        return default


def _safe_save_json(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def today_str():
    return str(date.today())


# ---------------- DATE RANGE (LAST 7 DAYS) ---------------- #

def last_7_dates():
    end = date.today()
    start = end - timedelta(days=6)
    dates = []
    cur = start
    while cur <= end:
        dates.append(str(cur))
        cur += timedelta(days=1)
    return dates, str(start), str(end)


# ---------------- STUDY LOG LOADING ---------------- #

def load_study_logs():
    return _safe_load_json(_data_path("study_log.json"), default=[])


def filter_study_logs_last_7(user_id: str):
    logs = load_study_logs()
    dates, start, end = last_7_dates()
    date_set = set(dates)

    user_logs = []
    for log in logs:
        if not isinstance(log, dict):
            continue
        if log.get("user_id") != user_id:
            continue
        d = log.get("date")
        if d in date_set:
            user_logs.append(log)

    return user_logs, dates, start, end


# ---------------- CORE METRICS ---------------- #

def compute_daily_minutes_and_sessions(user_logs: list, dates: list):
    minutes_by_date = {d: 0 for d in dates}
    sessions_by_date = {d: 0 for d in dates}

    for log in user_logs:
        d = log.get("date")
        if d not in minutes_by_date:
            continue
        mins = log.get("study_minutes", 0)
        sessions_completed = log.get("sessions_completed", 1)
        try:
            mins = int(mins)
        except (TypeError, ValueError):
            mins = 0
        try:
            sessions_completed = int(sessions_completed)
        except (TypeError, ValueError):
            sessions_completed = 1
        minutes_by_date[d] += max(0, mins)
        sessions_by_date[d] += max(1, sessions_completed)

    total_minutes = sum(minutes_by_date.values())
    total_sessions = sum(sessions_by_date.values())
    days_studied = sum(1 for d in dates if minutes_by_date[d] > 0)

    return minutes_by_date, sessions_by_date, total_minutes, total_sessions, days_studied


# ---------------- GOAL ACHIEVEMENT ---------------- #

def compute_goal_rate(minutes_by_date: dict, dates: list, user_data: dict):
    goal_hours = user_data.get("goal_hours", 0)
    try:
        goal_hours = int(goal_hours)
    except (TypeError, ValueError):
        goal_hours = 0

    goal_minutes = max(0, goal_hours * 60)

    if goal_minutes == 0:
        return None, goal_minutes, 0

    met_days = 0
    for d in dates:
        if minutes_by_date.get(d, 0) >= goal_minutes:
            met_days += 1

    goal_rate = met_days / 7
    return goal_rate, goal_minutes, met_days


# ---------------- MOOD TRENDS ---------------- #

def load_mood_log():
    return _safe_load_json(_data_path("mood_log.json"), default={})


def mood_trends_last_7(user_id: str, dates: list):
    db = load_mood_log()
    records = db.get(user_id, [])
    if not isinstance(records, list):
        return None, {}

    mood_by_date = {}
    for r in records:
        if not isinstance(r, dict):
            continue
        d = r.get("date")
        m = r.get("mood")
        if d in dates and isinstance(m, str) and m.strip():
            mood_by_date[d] = m

    dist = {}
    for d in dates:
        m = mood_by_date.get(d)
        if m:
            dist[m] = dist.get(m, 0) + 1

    if not dist:
        return None, {}

    top_mood = max(dist.keys(), key=lambda k: dist[k])
    return top_mood, dist


# ---------------- PRODUCTIVITY SCORE ---------------- #

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def productivity_score(total_minutes: int, days_studied: int, goal_minutes: int, goal_rate):
    if goal_minutes > 0:
        target = goal_minutes * 7
        minutes_ratio = total_minutes / target if target > 0 else 0
    else:
        target = 7 * 60
        minutes_ratio = total_minutes / target if target > 0 else 0

    minutes_score = clamp(minutes_ratio * 40, 0, 40)
    consistency_score = clamp((days_studied / 7) * 30, 0, 30)

    if goal_rate is None:
        goal_score = 0
    else:
        goal_score = clamp(goal_rate * 30, 0, 30)

    total = round(minutes_score + consistency_score + goal_score)
    label = "Low" if total < 40 else "Medium" if total < 70 else "High"

    return total, label, round(minutes_score, 1), round(consistency_score, 1), round(goal_score, 1)


# ---------------- IMPROVEMENT TIPS ---------------- #

def generate_tips(goal_rate, days_studied, total_minutes, top_mood):
    tips = []

    if days_studied <= 2:
        tips.append("✨ Study on at least 4 days next week to build consistency. ✨")
    elif days_studied <= 4:
        tips.append("✨ Try to study at least 5 days a week to strengthen your habit. ✨")

    if total_minutes < 180:
        tips.append("✨ Increase total weekly study time—aim for 30–45 minutes more per day. ✨")
    elif total_minutes < 420:
        tips.append("✨ Great progress—try one extra Pomodoro on 2–3 days to level up. ✨")

    if goal_rate is not None and goal_rate < 0.4:
        tips.append("✨ Break your daily goal into smaller chunks (e.g., 2 short sessions) to meet it more often. ✨")
    elif goal_rate is not None and goal_rate < 0.7:
        tips.append("✨ You’re close to your goal—tighten your routine on 2 more days. ✨")

    if top_mood and "Tired" in top_mood:
        tips.append("✨ Your mood shows fatigue—sleep/rest matters. Try shorter sessions + better breaks. ✨")
    elif top_mood and "Stressed" in top_mood:
        tips.append("✨ Stress is showing—use the recreation/meditation unlocks to reset your mind. ✨")

    while len(tips) < 3:
        tips.append("✨ Keep tracking your mood and sessions—small consistent gains beat big spikes. ✨")

    return tips[:3]


# ---------------- REPORT PRINTING ---------------- #

def print_report(start: str, end: str, dates: list,
                 minutes_by_date: dict, sessions_by_date: dict,
                 total_minutes: int, total_sessions: int, days_studied: int,
                 goal_rate, goal_minutes: int, met_days: int,
                 top_mood, mood_dist: dict,
                 user_data: dict,
                 score: int, score_label: str,
                 minutes_score, consistency_score, goal_score,
                 tips: list):
    summary_lines = [
        f"Range: {start} -> {end}",
        f"Pomodoro sessions completed: {total_sessions}",
        f"Total study minutes: {total_minutes}",
        f"Days studied: {days_studied}/7",
    ]

    if goal_rate is None:
        summary_lines.append("Goal achievement rate: (goal not set)")
    else:
        summary_lines.append(f"Goal achievement rate: {met_days}/7 = {round(goal_rate*100, 1)}%")
        summary_lines.append(f"Daily goal: {goal_minutes} minutes/day")

    print_fancy_box("🗓️ Weekly Performance Report", summary_lines, theme="cyan")

    mood_lines = []
    if top_mood is None:
        mood_lines.append("No mood data recorded this week.")
    else:
        mood_lines.append(f"Top mood: {top_mood}")
        for k in sorted(mood_dist.keys(), key=lambda x: mood_dist[x], reverse=True):
            mood_lines.append(f"{k}: {mood_dist[k]} day(s)")
    print_fancy_box("🌈 Mood Trends", mood_lines, theme="blue")

    breakdown_lines = [
        f"{d}: {minutes_by_date.get(d, 0)} min | {sessions_by_date.get(d, 0)} session(s)"
        for d in dates
    ]
    print_fancy_box("📅 Daily Breakdown (Last 7 Days)", breakdown_lines, theme="yellow")

    health = user_data.get("health", 10)
    coins = user_data.get("coins", 0)
    pet_lines = [
        f"Pet health: {health}",
        f"Coins: {coins}",
    ]
    if isinstance(health, int) and health <= 3:
        pet_lines.append("⚠️ Pet is weak! Feed it soon.")
    print_fancy_box("🐾 Pet Snapshot", pet_lines, theme="magenta")

    score_lines = [
        f"Productivity score: {score}/100 ({score_label})",
        f"Breakdown: minutes {minutes_score}/40, consistency {consistency_score}/30, goal {goal_score}/30",
    ]
    print_fancy_box("📈 Productivity Score", score_lines, theme="green")

    tips_lines = []
    for i, t in enumerate(tips, start=1):
        tips_lines.append(f"{i}. {t}")
    print_fancy_box("💡 3 Tips For Next Week", tips_lines, theme="cyan")


# ---------------- SNAPSHOT SAVING ---------------- #

REPORT_FILE = "weekly_reports.json"


def load_reports_db():
    return _safe_load_json(_data_path(REPORT_FILE), default={})


def save_reports_db(db: dict):
    _safe_save_json(_data_path(REPORT_FILE), db)


def save_snapshot(user_id: str, start: str, end: str,
                  total_sessions: int, total_minutes: int,
                  goal_rate, top_mood, health, score):

    db = load_reports_db()
    if user_id not in db or not isinstance(db[user_id], list):
        db[user_id] = []

    snapshot = {
        "generated_on": today_str(),
        "range_start": start,
        "range_end": end,
        "sessions": total_sessions,
        "total_minutes": total_minutes,
        "goal_rate": goal_rate,
        "top_mood": top_mood,
        "pet_health": health,
        "productivity_score": score
    }

    db[user_id].append(snapshot)
    save_reports_db(db)


# ---------------- CLI ENTRY ---------------- #

menu_label = "Weekly Report 🗓️"


def run(user_id: str, user_data: dict) -> dict:
    user_logs, dates, start, end = filter_study_logs_last_7(user_id)
    minutes_by_date, sessions_by_date, total_minutes, total_sessions, days_studied = \
        compute_daily_minutes_and_sessions(user_logs, dates)

    goal_rate, goal_minutes, met_days = compute_goal_rate(minutes_by_date, dates, user_data)
    top_mood, mood_dist = mood_trends_last_7(user_id, dates)

    score, label, ms, cs, gs = productivity_score(
        total_minutes, days_studied, goal_minutes, goal_rate
    )

    tips = generate_tips(goal_rate, days_studied, total_minutes, top_mood)

    while True:
        clear_screen()
        print_report(
            start, end, dates,
            minutes_by_date, sessions_by_date,
            total_minutes, total_sessions, days_studied,
            goal_rate, goal_minutes, met_days,
            top_mood, mood_dist,
            user_data,
            score, label,
            ms, cs, gs,
            tips
        )

        c = menu(["Save this report snapshot", "Back"])

        if c == 1:
            health = user_data.get("health", 10)
            save_snapshot(
                user_id, start, end,
                total_sessions, total_minutes,
                goal_rate, top_mood,
                health, score
            )
            clear_screen()
            print_fancy_box(
                "✅ Snapshot Saved",
                [f"Weekly snapshot stored for {start} -> {end}."],
                theme="green",
            )
            pause()
        elif c == 0:
            clear_screen()
            return user_data