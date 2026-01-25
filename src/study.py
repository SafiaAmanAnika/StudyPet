# DEV_MODE = True means:
# 1 minute in logic = 1 second in real time (for fast demo/testing)

import time

DEV_MODE = True

MAX_STUDY_MIN = 180     # Upper limit so program doesn't run forever
MAX_BREAK_MIN = 60

# Difficulty choice mapped to (name, coin reward)
DIFFICULTY = {
    "1": ("Easy", 5),
    "2": ("Medium", 10),
    "3": ("Hard", 20),
}


def trim(s):
    """
    Manually removes leading and trailing whitespace.
   
    """
    if s is None:
        return ""

    start = 0
    end = len(s) - 1

    while start <= end and (s[start] in " \t\n\r"):
        start += 1

    while end >= start and (s[end] in " \t\n\r"):
        end -= 1

    if start > end:
        return ""

    return s[start:end + 1]


def is_alpha_space(s):
    """
    Returns True if string contains only letters (A-Z/a-z) and spaces.
    """
    if s is None or s == "":
        return False

    for ch in s:
        if ch != " " and not ("a" <= ch <= "z") and not ("A" <= ch <= "Z"):
            return False
    return True


def get_topic(prompt_text):
    """
    Keeps asking until user enters a valid topic.
    Only letters + spaces allowed.
    """
    while True:
        raw = trim(input(prompt_text))
        if raw != "" and is_alpha_space(raw):
            return raw
        print("Enter topic using letters and spaces only.")


def get_choice(prompt_text, allowed):
    """
    Generic input validator.
    Keeps asking until input matches one of the allowed options.
    """
    while True:
        v = trim(input(prompt_text))
        for a in allowed:
            if v == a:
                return v

        # Manually build allowed options string 
        msg = "Please choose one of: "
        first = True
        for a in allowed:
            if not first:
                msg += ", "
            msg += a
            first = False

        print(msg)


def countdown(seconds, label):
    """
    Displays a live countdown timer in MM:SS format.
    Uses carriage return (\r) to overwrite the same line.
    """
    if seconds <= 0:
        return

    remaining = seconds
    last_line = ""

    while remaining > 0:
        mins = remaining // 60
        secs = remaining % 60

        mins_s = "0" + str(mins) if mins < 10 else str(mins)
        secs_s = "0" + str(secs) if secs < 10 else str(secs)

        line = label + " - time left: " + mins_s + ":" + secs_s
        print(line, end="\r")
        last_line = line

        time.sleep(1)
        remaining -= 1

    # Clear the last countdown line completely
    if last_line != "":
        print(" " * len(last_line), end="\r")

    print(label + " finished.")


def today_date_str():
    """
    Returns today's date in YYYY-MM-DD format without using date.isoformat().
    """
    t = time.localtime()
    year = t.tm_year
    month = t.tm_mon
    day = t.tm_mday

    month_s = "0" + str(month) if month < 10 else str(month)
    day_s = "0" + str(day) if day < 10 else str(day)

    return f"{year}-{month_s}-{day_s}"


def start_session(user_data):
    """
    Runs one full study session.
    Returns updated user_data and a session log dictionary.
    """

    if "user_id" not in user_data:
        raise KeyError("user_data must include 'user_id'")

    if "coins" not in user_data:
        user_data["coins"] = 0
    if "health" not in user_data:
        user_data["health"] = 0

    

    # Ask for topic
    topic = get_topic("Enter study topic (letters and spaces only): ")

    # Difficulty selection
    print("\nSelect difficulty:")
    print("1. Easy\n2. Medium\n3. Hard")
    choice = get_choice("Choose 1/2/3: ", {"1", "2", "3"})
    diff_name, coins_reward = DIFFICULTY[choice]

    # Pomodoro selection
    print("\nSelect Pomodoro mode:")
    print("1. 25 / 5\n2. 50 / 10\n3. Custom\n4. Cancel")
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
        # Custom minutes with validation
        while True:
            s_text = trim(input("Enter study minutes (1–180): "))
            b_text = trim(input("Enter break minutes (0–60): "))

            try:
                s_val = int(s_text)
                b_val = int(b_text)
            except Exception:
                print("Enter valid integers.")
                continue

            if 1 <= s_val <= MAX_STUDY_MIN and 0 <= b_val <= MAX_BREAK_MIN:
                study_minutes = s_val
                break_minutes = b_val
                break

            print("Study: 1–180 minutes, Break: 0–60 minutes.")

    # Convert minutes to seconds depending on DEV_MODE
    study_seconds = study_minutes if DEV_MODE else study_minutes * 60
    break_seconds = break_minutes if DEV_MODE else break_minutes * 60

    # Countdown study

    if DEV_MODE:
        print("\n[DEV MODE] 1 minute = 1 second")

    print("\nStarting study for " + str(study_minutes) + " minute(s)")
    countdown(study_seconds, "Study time")

    # Countdown break
    if break_minutes > 0:
        print("Starting break for " + str(break_minutes) + " minute(s)")
        countdown(break_seconds, "Break time")

    # Update coins and health 
    cur_coins = int(user_data["coins"])
    cur_health = int(user_data["health"])

    cur_coins += coins_reward
    cur_health += 1  

    user_data["coins"] = cur_coins
    user_data["health"] = cur_health

    print("\nWell done! You completed '" + topic + "' (" + diff_name + ").")
    print(f"Coins earned: +{coins_reward} | Total: {cur_coins}")
    print(f"Health +1 | Current: {cur_health}")

    session_log = {
        "user_id": user_data["user_id"],
        "date": today_date_str(),
        "topic": topic,
        "difficulty": diff_name,
        "study_minutes": study_minutes,
        "break_minutes": break_minutes,
        "coins_earned": coins_reward,
        "dev_mode": DEV_MODE
    }

    return user_data, session_log


if __name__ == "__main__":
    demo = {"user_id": "demo_user", "coins": 0, "health": 5}
    updated, log = start_session(demo)
    print("\nUpdated user:", updated)
    print("Session log:", log)
