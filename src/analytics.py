import json
import os
from datetime import date, datetime, timedelta
from src.ui import analytics_menu, clear_screen



# Safe File Handling


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

# ← Add this helper to fix import errors
def _safe_save_json(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def today_str():
    return str(date.today())

# =========================
# Load + Filter Logs
# =========================

def load_study_logs():
    path = _data_path("study_log.json")
    return _safe_load_json(path, default=[])

def filter_user_logs(all_logs: list, user_id: str) -> list:
    return [
        log for log in all_logs
        if isinstance(log, dict) and log.get("user_id") == user_id
    ]

# =========================
# Build Daily Maps
# =========================

def build_daily_maps(user_logs: list):
    minutes_by_date = {}
    sessions_by_date = {}

    for log in user_logs:
        d = log.get("date")
        mins = log.get("study_minutes", 0)

        if not isinstance(d, str):
            continue

        try:
            datetime.fromisoformat(d)
        except Exception:
            continue

        try:
            mins = int(mins)
        except Exception:
            mins = 0

        minutes_by_date[d] = minutes_by_date.get(d, 0) + max(0, mins)
        sessions_by_date[d] = sessions_by_date.get(d, 0) + 1

    return minutes_by_date, sessions_by_date

# Intensity Mapping


def intensity_char(total_minutes: int) -> str:
    if total_minutes <= 0:
        return "·"
    if total_minutes <= 24:
        return "░"
    if total_minutes <= 49:
        return "▒"
    if total_minutes <= 99:
        return "▓"
    return "█"


# Date Range Builder


def date_range_list(days: int):
    end = date.today()
    start = end - timedelta(days=days - 1)

    out = []
    cur = start
    while cur <= end:
        out.append(str(cur))
        cur += timedelta(days=1)
    return out

# =========================
# Heatmap Grid
# =========================

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def build_heatmap_grid(date_list: list, minutes_by_date: dict):
    grid = [["·" for _ in range(len(date_list))] for _ in range(7)]

    for col, dstr in enumerate(date_list):
        try:
            d = date.fromisoformat(dstr)
        except Exception:
            continue

        row = d.weekday()
        mins = minutes_by_date.get(dstr, 0)
        grid[row][col] = intensity_char(mins)

    return grid

def print_heatmap(date_list: list, grid: list):
    print("\n===== STUDY HEATMAP =====")
    print("Legend: ·=0  ░=1-24  ▒=25-49  ▓=50-99  █=100+ minutes")
    print(f"Range : {date_list[0]}  to  {date_list[-1]}\n")

    for r in range(7):
        row_label = f"{WEEKDAYS[r]:>3} "
        row_cells = "".join(grid[r])
        print(row_label + row_cells)

    print("==========================\n")


# Stats Computation


def sum_last_n(days: int, minutes_by_date: dict, sessions_by_date: dict):
    dates = date_range_list(days)
    total_mins = sum(int(minutes_by_date.get(d, 0)) for d in dates)
    total_sessions = sum(int(sessions_by_date.get(d, 0)) for d in dates)
    return total_mins, total_sessions

def current_streak(minutes_by_date: dict):
    streak = 0
    cur = date.today()

    while True:
        dstr = str(cur)
        if minutes_by_date.get(dstr, 0) > 0:
            streak += 1
            cur -= timedelta(days=1)
        else:
            break

    return streak

def longest_streak_in_range(date_list: list, minutes_by_date: dict):
    best = 0
    run = 0

    for dstr in date_list:
        if minutes_by_date.get(dstr, 0) > 0:
            run += 1
            best = max(best, run)
        else:
            run = 0

    return best

def best_day_in_range(date_list: list, minutes_by_date: dict):
    best_date = None
    best_mins = 0

    for dstr in date_list:
        mins = int(minutes_by_date.get(dstr, 0))
        if mins > best_mins:
            best_mins = mins
            best_date = dstr

    return best_date, best_mins

def print_stats(date_list, minutes_by_date, sessions_by_date):
    total7_mins, total7_sessions = sum_last_n(7, minutes_by_date, sessions_by_date)
    cur_streak = current_streak(minutes_by_date)
    longest = longest_streak_in_range(date_list, minutes_by_date)
    bdate, bmins = best_day_in_range(date_list, minutes_by_date)

    print("===== STATS =====")
    print(f"Last 7 days total minutes : {total7_mins}")
    print(f"Last 7 days sessions      : {total7_sessions}")
    print(f"Current streak (days)     : {cur_streak}")
    print(f"Longest streak in range   : {longest}")

    if bdate:
        print(f"Best day in range         : {bdate} ({bmins} mins)")
    else:
        print("Best day in range         : No study data")

    print("=================\n")


# Required Interface


menu_label = "Study Analytics 📈"

def run(user_id: str, user_data: dict) -> dict:
    while True:
        clear_screen()
        choice = analytics_menu()

        if choice == 0:
            return user_data

        if choice not in {1, 2, 3}:
            continue

        days = 7 if choice == 1 else 28 if choice == 2 else 56

        all_logs = load_study_logs()
        user_logs = filter_user_logs(all_logs, user_id)
        minutes_by_date, sessions_by_date = build_daily_maps(user_logs)

        dates = date_range_list(days)
        grid = build_heatmap_grid(dates, minutes_by_date)

        clear_screen()
        print_heatmap(dates, grid)
        print_stats(dates, minutes_by_date, sessions_by_date)

        input("Press Enter to return to Analytics menu...")
