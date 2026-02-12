menu_label = "Quiz & Prediction 🧠"
QUIZ_FILE = "data/quiz_marks.json"

import json

# ---------------- File handling ----------------
def write_json(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
    except:
        print("Error writing file:", path)

def read_json(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
            if type(data) != dict:
                data = {}
            return data
    except:
        return {}

# ---------------- Helpers ----------------
def strip(s):
    start = 0
    end = len(s) - 1
    while start <= end and s[start] == " ":
        start += 1
    while end >= start and s[end] == " ":
        end -= 1
    return s[start:end+1]

def round_num(x):
    return int(x * 10) / 10

# ---------------- Input helpers ----------------
def ask_non_empty_letters(prompt):
    while True:
        v = strip(input(prompt))
        if v == "":
            print("Cannot be empty.")
            continue

        has_letter = False
        valid = True
        for i in range(len(v)):
            ch = v[i]
            if ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'):
                has_letter = True
            elif ch == " " or ('0' <= ch <= '9'):
                pass
            else:
                valid = False
                break

        if not has_letter:
            print("Must contain at least one letter.")
            continue
        if not valid:
            print("Only letters, numbers and spaces allowed.")
            continue
        return v

def ask_int(prompt, min_v=None, max_v=None):
    while True:
        v = strip(input(prompt))
        n = 0
        try:
            n = int(v)
        except:
            print("Enter a valid integer.")
            continue
        if min_v is not None and n < min_v:
            print("Must be >=", min_v)
            continue
        if max_v is not None and n > max_v:
            print("Must be <=", max_v)
            continue
        return n

def ask_percent(prompt):
    return ask_int(prompt, 0, 100)

def ask_date(prompt):
    while True:
        d = strip(input(prompt))
        if d == "":
            print("Using empty date")
            return ""

        # manual split
        parts = []
        temp = ""
        for i in range(len(d)):
            if d[i] == "-":
                n = 0
                for _ in parts: n += 1
                parts_new = [0] * (n + 1)
                for j in range(n): parts_new[j] = parts[j]
                parts_new[n] = temp
                parts = parts_new
                temp = ""
            else:
                temp = temp + d[i]
        n = 0
        for _ in parts: n += 1
        parts_new = [0] * (n + 1)
        for j in range(n): parts_new[j] = parts[j]
        parts_new[n] = temp
        parts = parts_new

        if len(parts) != 3:
            print("Invalid date, format YYYY-MM-DD")
            continue

        try:
            y = int(parts[0])
            m = int(parts[1])
            day = int(parts[2])
            
            if m < 1 or m > 12:
                print("Invalid month. Must be 1-12.")
                continue

            # Days in month
            if m == 2:
                # leap year check
                is_leap = False
                if y % 4 == 0:
                    if y % 100 != 0 or y % 400 == 0:
                        is_leap = True
                max_day = 29 if is_leap else 28
            elif m in [1,3,5,7,8,10,12]:
                max_day = 31
            else:
                max_day = 30

            if day < 1 or day > max_day:
                print(f"Invalid day for month {m}. Must be 1-{max_day}.")
                continue

            return d
        except:
            print("Invalid date, format YYYY-MM-DD")


# ---------------- Quiz helpers ----------------
def get_user_quizzes(db, user_id):
    found = False
    for key in db:
        if key == user_id:
            found = True
            break
    if not found:
        db[user_id] = {"quizzes": []}
    if "quizzes" not in db[user_id]:
        db[user_id]["quizzes"] = []
    return db[user_id]["quizzes"]

def quiz_percent(q):
    try:
        return int(q["score"]) / int(q["max_score"]) * 100
    except:
        return 0.0

# ---------------- Add quiz ----------------
def add_quiz(user_id):
    db = read_json(QUIZ_FILE)
    quizzes = get_user_quizzes(db, user_id)

    print("\n=== Add Quiz Marks ===")
    title = ask_non_empty_letters("Quiz title: ")
    topic = ask_non_empty_letters("Topic: ")
    max_score = ask_int("Max marks: ", 1)
    score = ask_int("Your marks: ", 0, max_score)
    coverage = ask_percent("Syllabus covered % (0-100): ")
    d = ask_date("Date (YYYY-MM-DD, blank=today): ")

    record = {"date": d, "title": title, "topic": topic, "score": score,
              "max_score": max_score, "coverage_percent": coverage}

    # manual append
    n = 0
    for _ in quizzes: n += 1
    new_quizzes = [0] * (n + 1)
    for i in range(n):
        new_quizzes[i] = quizzes[i]
    new_quizzes[n] = record
    quizzes = new_quizzes

    db[user_id]["quizzes"] = quizzes
    write_json(QUIZ_FILE, db)
    pct = round_num(score / max_score * 100)
    print("✅ Saved:", title, "-", score, "/", max_score, "(", pct, "% )")

# ---------------- Trend ----------------
def detect_trend(last_quizzes):
    n = 0
    for _ in last_quizzes: n += 1
    if n < 2: return "need at least 2 quizzes"

    changes = []
    for i in range(1, n):
        prev = quiz_percent(last_quizzes[i-1])
        curr = quiz_percent(last_quizzes[i])
        ch = 0
        if curr > prev: ch = 1
        elif curr < prev: ch = -1

        # manual append
        clen = 0
        for _ in changes: clen += 1
        new_changes = [0] * (clen + 1)
        for j in range(clen): new_changes[j] = changes[j]
        new_changes[clen] = ch
        changes = new_changes

    # evaluate trend
    all_up = True; all_down = True; all_stable = True
    clen = 0
    for _ in changes: clen += 1
    for i in range(clen):
        c = changes[i]
        if c != 1: all_up = False
        if c != -1: all_down = False
        if c != 0: all_stable = False

    if all_up: return "⬆️ Improving"
    elif all_down: return "⬇️ Declining"
    elif all_stable: return "↔️ Stable"
    else: return "↔️ Stable"

# ---------------- View history ----------------
def view_history(user_id, last_n=5):
    db = read_json(QUIZ_FILE)
    quizzes = get_user_quizzes(db, user_id)
    n = 0
    for _ in quizzes: n += 1
    if n == 0:
        print("⚠️ No quizzes yet.")
        return

    # manual sort by date (bubble sort)
    for i in range(n):
        for j in range(0, n-i-1):
            if quizzes[j]["date"] > quizzes[j+1]["date"]:
                temp = quizzes[j]; quizzes[j] = quizzes[j+1]; quizzes[j+1] = temp

    # collect subjects manually
    subjects = []
    for i in range(n):
        topic = quizzes[i]["topic"]
        found = False
        for j in range(len(subjects)):
            if subjects[j] == topic: found = True
        if not found:
            subjects_len = 0
            for _ in subjects: subjects_len += 1
            new_subjects = [0] * (subjects_len + 1)
            for k in range(subjects_len): new_subjects[k] = subjects[k]
            new_subjects[subjects_len] = topic
            subjects = new_subjects

    # show each subject
    overall_quizzes = []
    subjects_len = 0
    for _ in subjects: subjects_len += 1
    for si in range(subjects_len):
        sub = subjects[si]
        print("\n=== History:", sub, "===")
        sub_quizzes = []
        for i in range(n):
            if quizzes[i]["topic"] == sub:
                sub_len = 0
                for _ in sub_quizzes: sub_len += 1
                new_sub = [0] * (sub_len + 1)
                for k in range(sub_len): new_sub[k] = sub_quizzes[k]
                new_sub[sub_len] = quizzes[i]
                sub_quizzes = new_sub
                overall_len = 0
                for _ in overall_quizzes: overall_len += 1
                new_overall = [0] * (overall_len + 1)
                for k in range(overall_len): new_overall[k] = overall_quizzes[k]
                new_overall[overall_len] = quizzes[i]
                overall_quizzes = new_overall

        # print sub quizzes
        sub_len = 0
        for _ in sub_quizzes: sub_len += 1
        for i in range(sub_len):
            q = sub_quizzes[i]
            pct = round_num(quiz_percent(q))
            cov = q["coverage_percent"]
            print("-", q["date"], "|", q["title"], "|", q["score"], "/", q["max_score"], "(", pct, "% ) | Coverage:", cov)

        sub_recent_len = sub_len if sub_len < last_n else last_n
        recent = [0] * sub_recent_len
        for i in range(sub_recent_len):
            recent[i] = sub_quizzes[sub_len - sub_recent_len + i]
        print("Trend (last", sub_recent_len, "quizzes):", detect_trend(recent))

# ---------------- Coverage remaining ----------------
def show_coverage(user_id):
    db = read_json(QUIZ_FILE)
    quizzes = get_user_quizzes(db, user_id)
    n = 0
    for _ in quizzes: n += 1
    if n == 0:
        print("⚠️ No quizzes yet.")
        return

    # collect subjects
    subjects = []
    for i in range(n):
        topic = quizzes[i]["topic"]
        found = False
        for j in range(len(subjects)):
            if subjects[j] == topic: found = True
        if not found:
            subjects_len = 0
            for _ in subjects: subjects_len += 1
            new_subjects = [0] * (subjects_len + 1)
            for k in range(subjects_len): new_subjects[k] = subjects[k]
            new_subjects[subjects_len] = topic
            subjects = new_subjects

    print("\n=== Coverage per subject ===")
    subjects_len = 0
    for _ in subjects: subjects_len += 1
    for si in range(subjects_len):
        sub = subjects[si]
        total_covered = 0
        for i in range(n):
            if quizzes[i]["topic"] == sub and "coverage_percent" in quizzes[i]:
                total_covered += quizzes[i]["coverage_percent"]
        if total_covered > 100: total_covered = 100
        remaining = 100 - total_covered
        if total_covered == 0:
            print("-", sub, ": coverage unknown")
        else:
            print("-", sub, ":", total_covered, "% covered |", remaining, "% remaining")

# ---------------- Performance prediction ----------------
def predict_performance(user_id):
    db = read_json(QUIZ_FILE)
    quizzes = get_user_quizzes(db, user_id)
    n = 0
    for _ in quizzes: n += 1
    if n == 0:
        print("⚠️ Add at least 1 quiz first.")
        return

    # collect subjects
    subjects = []
    for i in range(n):
        topic = quizzes[i]["topic"]
        found = False
        for j in range(len(subjects)):
            if subjects[j] == topic: found = True
        if not found:
            subjects_len = 0
            for _ in subjects: subjects_len += 1
            new_subjects = [0] * (subjects_len + 1)
            for k in range(subjects_len): new_subjects[k] = subjects[k]
            new_subjects[subjects_len] = topic
            subjects = new_subjects

    print("\n=== Performance Prediction ===")
    subjects_len = 0
    for _ in subjects: subjects_len += 1
    for si in range(subjects_len):
        sub = subjects[si]
        sub_quizzes = []
        for i in range(n):
            if quizzes[i]["topic"] == sub:
                sub_len = 0
                for _ in sub_quizzes: sub_len += 1
                new_sub = [0] * (sub_len + 1)
                for k in range(sub_len): new_sub[k] = sub_quizzes[k]
                new_sub[sub_len] = quizzes[i]
                sub_quizzes = new_sub

        sub_len = 0
        for _ in sub_quizzes: sub_len += 1
        total_covered = 0
        total_score = 0
        for i in range(sub_len):
            total_covered += sub_quizzes[i]["coverage_percent"]
            total_score += quiz_percent(sub_quizzes[i])
        if total_covered > 100: total_covered = 100
        remaining = 100 - total_covered
        if sub_len > 0:
            avg = total_score / sub_len
        else:
            avg = 0

        predicted = avg - remaining * 0.05
        if predicted < 0: predicted = 0
        if predicted > 100: predicted = 100
        low = predicted - 5
        if low < 0: low = 0
        high = predicted + 5
        if high > 100: high = 100

        print("\n--- Subject:", sub, "---")
        print("Based on", sub_len, "quiz(es), average =", round_num(avg), "%")
        print("Coverage remaining:", remaining, "%")
        print("📈 Predicted score range:", round_num(low), "% –", round_num(high), "%")

# ---------------- CLI ----------------
def run(user_id, user_data):
    while True:
        print("\n=== Quiz & Prediction ===")
        print("1. Add quiz")
        print("2. View history")
        print("3. Coverage remaining")
        print("4. Predict performance")
        print("5. Back")
        choice = strip(input("Choose: "))
        if choice == "1":
            add_quiz(user_id)
        elif choice == "2":
            view_history(user_id)
        elif choice == "3":
            show_coverage(user_id)
        elif choice == "4":
            predict_performance(user_id)
        elif choice == "5":
            return user_data
        else:
            print("❌ Invalid choice")


