# DEV_MODE = True treats 1 minute as 1 second for quick testing.

import time

# Set True for quick demo (1 minute == 1 second). Set False for real minutes.
DEV_MODE = True

DIFFICULTY = {
    "1": ("Easy", 5),
    "2": ("Medium", 10),
    "3": ("Hard", 20),
}


def trim(s):
    """Remove leading and trailing spaces, tabs, newlines ."""
    if s is None:
        return ""
    start = 0
    end = len(s) - 1
    while start <= end and (s[start] == " " or s[start] == "\t" or s[start] == "\n" or s[start] == "\r"):
        start = start + 1
    while end >= start and (s[end] == " " or s[end] == "\t" or s[end] == "\n" or s[end] == "\r"):
        end = end - 1
    if start > end:
        return ""
    return s[start:end + 1]


def is_alpha_space(s):
    """Return True if s has only letters (A-Z/a-z) and spaces."""
    if s is None or s == "":
        return False
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == " ":
            i = i + 1
            continue
        if "a" <= ch <= "z":
            i = i + 1
            continue
        if "A" <= ch <= "Z":
            i = i + 1
            continue
        return False
    return True


def get_topic(prompt_text):
    """Ask until user gives a topic with letters and spaces only."""
    while True:
        raw = input(prompt_text)
        raw = trim(raw)
        if raw != "" and is_alpha_space(raw):
            return raw
        print("Enter topic using letters and spaces only. Example: Data Structures")


def get_choice(prompt_text, allowed):
    """Ask until user enters one of the allowed choices (strings)."""
    while True:
        v = input(prompt_text)
        v = trim(v)
        for a in allowed:
            if v == a:
                return v
        # show allowed choices
        out = ""
        first = True
        for a in allowed:
            if first:
                out = a
                first = False
            else:
                out = out + ", " + a
        print("Please choose one of: " + out)


def countdown(seconds, label):
    """Simple MM:SS countdown; clears previous line using exact length."""
    if seconds <= 0:
        return
    remaining = seconds
    last_line = ""
    while remaining > 0:
        mins = remaining // 60
        secs = remaining - (mins * 60)
        if mins < 10:
            mins_s = "0" + str(mins)
        else:
            mins_s = str(mins)
        if secs < 10:
            secs_s = "0" + str(secs)
        else:
            secs_s = str(secs)

        line = label + " - time left: " + mins_s + ":" + secs_s
        # print and overwrite previous line
        print(line, end="\r")
        last_line = line

        # sleep 1 second per tick
        time.sleep(1)
        remaining = remaining - 1

    # clear previous printed line using its exact length
    if last_line != "":
        clear = ""
        i = 0
        while i < len(last_line):
            clear = clear + " "
            i = i + 1
        print(clear, end="\r")

    # final message on its own line
    print(label + " finished.")


def today_date_str():
    """
    Return today's date as "YYYY-MM-DD" without using date.isoformat().
    Uses only basic operations and simple zero-pad logic.
    """
    t = time.localtime()
    year = t.tm_year
    month = t.tm_mon
    day = t.tm_mday

    if month < 10:
        month_s = "0" + str(month)
    else:
        month_s = str(month)

    if day < 10:
        day_s = "0" + str(day)
    else:
        day_s = str(day)

    return str(year) + "-" + month_s + "-" + day_s


def start_session(user_data):
    """
    Start interactive study session.
    Returns (updated_user_data, session_log) or (user_data, None) if cancelled.
    """
    if "user_id" not in user_data:
        raise KeyError("user_data must include 'user_id'")

    if "coins" not in user_data:
        user_data["coins"] = 0
    if "health" not in user_data:
        user_data["health"] = 0

    # Topic: only letters and spaces allowed
    topic = get_topic("Enter study topic (letters and spaces only): ")

    # Difficulty
    print("")
    print("Select difficulty:")
    print("1. Easy")
    print("2. Medium")
    print("3. Hard")
    choice = get_choice("Choose 1/2/3: ", {"1", "2", "3"})
    diff_name, coins_reward = DIFFICULTY[choice]

    # Pomodoro selection
    print("")
    print("Select Pomodoro mode:")
    print("1. 25 / 5")
    print("2. 50 / 10")
    print("3. Custom")
    print("4. Cancel")
    pm = get_choice("Choose 1/2/3/4: ", {"1", "2", "3", "4"})

    if pm == "4":
        print("Cancelled. No session started.")
        return user_data, None

    if pm == "1":
        study_minutes = 25
        break_minutes = 5
    elif pm == "2":
        study_minutes = 50
        break_minutes = 10
    else:
        while True:
            s_text = input("Enter study minutes (positive integer): ")
            s_text = trim(s_text)
            b_text = input("Enter break minutes (0 or positive integer): ")
            b_text = trim(b_text)
            ok = True
            try:
                s_val = int(s_text)
            except Exception:
                ok = False
            try:
                b_val = int(b_text)
            except Exception:
                ok = False
            if ok:
                if s_val > 0 and b_val >= 0:
                    study_minutes = s_val
                    break_minutes = b_val
                    break
            print("Enter valid integers: study > 0, break >= 0.")

    # convert minutes to seconds depending on DEV_MODE
    if DEV_MODE:
        study_seconds = study_minutes
        break_seconds = break_minutes
    else:
        study_seconds = study_minutes * 60
        break_seconds = break_minutes * 60

    print("")
    print("Starting study for " + str(study_minutes) + " minute(s)")
    countdown(study_seconds, "Study time")

    if break_minutes > 0:
        print("Starting break for " + str(break_minutes) + " minute(s).")
        countdown(break_seconds, "Break time")

    # Update user_data
    try:
        cur_coins = int(user_data["coins"])
    except Exception:
        cur_coins = 0
    try:
        cur_health = int(user_data["health"])
    except Exception:
        cur_health = 0

    cur_coins = cur_coins + coins_reward
    cur_health = cur_health + 1

    user_data["coins"] = cur_coins
    user_data["health"] = cur_health

    print("")
    print("Well done! You completed '" + topic + "' (" + diff_name + ").")
    print("Coins earned: +" + str(coins_reward) + "  - Total: " + str(user_data["coins"]))
    print("Health +1  - Current: " + str(user_data["health"]))

    session_log = {
        "user_id": user_data["user_id"],
        "date": today_date_str(),
        "topic": topic,
        "difficulty": diff_name,
        "study_minutes": study_minutes,
        "coins_earned": coins_reward
    }

    return user_data, session_log


if __name__ == "__main__":
    demo = {"user_id": "demo_user", "coins": 0, "health": 5}
    updated, log = start_session(demo)
    print("")
    print("Updated user:", updated)
    print("Session log:", log)