menu_label = "Quiz & Prediction 🧠"
QUIZ_FILE = "data/quiz_marks.json"

import json

# ---------------- File Handling ----------------
def write_json(path, data):
    try:
        with open(path, "w") as f:
            f.write(json.dumps(data, indent=4))
    except Exception as e:
        print("Error writing file:", e)

def read_json(path):
    try:
        with open(path, "r") as f:
            content = f.read()
        data = json.loads(content)
        if type(data) != dict:
            print("⚠️ Invalid JSON format, resetting file")
            return {}
        return data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print("⚠️ JSON decode error:", e)
        return {}

# ---------------- Manual Utilities ----------------
def manual_len(lst):
    count = 0
    for _ in lst: count += 1
    return count

def manual_append(lst, item):
    n = manual_len(lst)
    new_lst = [0] * (n + 1)
    for i in range(n):
        new_lst[i] = lst[i]
    new_lst[n] = item
    return new_lst

def strip(s):
    whitespace = " \t\n\r"
    start = 0
    end = len(s) - 1
    while start <= end and s[start] in whitespace: start += 1
    while end >= start and s[end] in whitespace: end -= 1
    return s[start:end+1]

def round_num(x):
    return int(x * 10) / 10

# ---------------- Input Helpers ----------------
def ask_non_empty_letters(prompt):
    while True:
        v = strip(input(prompt))
        if v == "": print("Cannot be empty."); continue
        has_letter = False
        valid = True
        for ch in v:
            if ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'): has_letter = True
            elif ch == " " or ('0' <= ch <= '9'): pass
            else: valid = False; break
        if not has_letter: print("Must contain at least one letter."); continue
        if not valid: print("Only letters, numbers and spaces allowed."); continue
        return v

def ask_int(prompt, min_v=None, max_v=None):
    while True:
        v = strip(input(prompt))
        try: n = int(v)
        except: print("Enter a valid integer."); continue
        if min_v is not None and n < min_v: print("Must be >=", min_v); continue
        if max_v is not None and n > max_v: print("Must be <=", max_v); continue
        return n

def ask_percent(prompt):
    return ask_int(prompt, 0, 100)

def ask_date(prompt):
    while True:
        d = strip(input(prompt))
        if d == "": print("Date cannot be empty."); continue

        parts = []
        temp = ""
        for ch in d:
            if ch == "-":
                parts = manual_append(parts, temp)
                temp = ""
            else:
                temp += ch
        parts = manual_append(parts, temp)
        if manual_len(parts) != 3:
            print("Invalid format. Use YYYY-MM-DD"); continue
        try: y = int(parts[0]); m = int(parts[1]); day = int(parts[2])
        except: print("Invalid numbers in date."); continue
        if m < 1 or m > 12: print("Invalid month."); continue
        if m == 2: is_leap = (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)); max_day = 29 if is_leap else 28
        elif m in [1,3,5,7,8,10,12]: max_day = 31
        else: max_day = 30
        if day < 1 or day > max_day: print("Invalid day for month."); continue
        return d

# ---------------- Quiz Helpers ----------------
def get_user_quizzes(db, user_id):
    if user_id not in db: db[user_id] = {"quizzes":[]}
    if "quizzes" not in db[user_id]: db[user_id]["quizzes"] = []
    return db[user_id]["quizzes"]

def quiz_percent(q):
    try: return int(q["score"]) / int(q["max_score"]) * 100
    except: return 0.0

# ---------------- Add Quiz ----------------
def add_quiz(user_id):
    db = read_json(QUIZ_FILE)
    quizzes = get_user_quizzes(db, user_id)

    print("\n=== Add Quiz Marks ===")
    title = ask_non_empty_letters("Quiz title: ")
    topic = ask_non_empty_letters("Topic: ")
    max_score = ask_int("Max marks: ", 1)
    score = ask_int("Your marks: ", 0, max_score)
    coverage = ask_percent("Syllabus covered % (0-100): ")
    d = ask_date("Date (YYYY-MM-DD): ")

    record = {"date":d, "title":title, "topic":topic, "score":score,
              "max_score":max_score, "coverage_percent":coverage}

    quizzes = manual_append(quizzes, record)
    db[user_id]["quizzes"] = quizzes
    write_json(QUIZ_FILE, db)
    pct = round_num(score / max_score * 100)
    print("✅ Saved:", title, "-", score, "/", max_score, "(", pct, "% )")

# ---------------- Trend & Sparkline ----------------
def detect_trend(quizzes, overall=False):
    """
    Determine trend: Improving ⬆️, Declining ⬇️, Stable ↔️
    Minor fluctuations <=5% are ignored for stability.
    """
    n = manual_len(quizzes)
    if n < 2: return "Need at least 2 quizzes"
    
    ups = downs = 0
    threshold = 5  # Only changes >5% count
    
    for i in range(1, n):
        prev = quiz_percent(quizzes[i-1]) if not overall else quizzes[i-1]["score"]
        curr = quiz_percent(quizzes[i]) if not overall else quizzes[i]["score"]
        diff = curr - prev
        if diff > threshold: ups += 1
        elif diff < -threshold: downs += 1

    if ups > downs and ups >= n//2: return "⬆️ Improving"
    elif downs > ups and downs >= n//2: return "⬇️ Declining"
    else: return "↔️ Stable"

def sparkline(values):
    bars = "▁▂▃▄▅▆▇█"; n = manual_len(values)
    if n==0: return ""
    min_val = max_val = values[0]
    for i in range(n):
        if values[i]<min_val: min_val=values[i]
        if values[i]>max_val: max_val=values[i]
    line=""
    for i in range(n):
        if max_val==min_val: index = len(bars)//2
        else: index = int((values[i]-min_val)/(max_val-min_val)*(len(bars)-1))
        line += bars[index]
    return line

# ---------------- Group by subject ----------------
def group_by_subject(quizzes):
    subject_map = {}
    for q in quizzes:
        topic = q["topic"]
        if topic not in subject_map: subject_map[topic] = []
        subject_map[topic] = manual_append(subject_map[topic], q)
    return subject_map

# ---------------- Dashboard ----------------
def view_dashboard(user_id, last_n=5):
    db = read_json(QUIZ_FILE)
    quizzes = get_user_quizzes(db, user_id)
    if manual_len(quizzes) == 0:
        print("⚠️ No quizzes yet."); return

    # Sort by date
    n_quiz = manual_len(quizzes)
    for i in range(n_quiz-1):
        for j in range(i+1, n_quiz):
            if quizzes[i]["date"] > quizzes[j]["date"]:
                temp = quizzes[i]; quizzes[i] = quizzes[j]; quizzes[j] = temp

    subjects=[]
    for q in quizzes:
        topic = q["topic"]; found=False
        for s in subjects:
            if s == topic: found=True
        if not found: subjects = manual_append(subjects, topic)

    overall_scores=[]
    print("\n=== Dashboard ===")
    for sub in subjects:
        sub_quizzes=[]
        for q in quizzes:
            if q["topic"]==sub: sub_quizzes = manual_append(sub_quizzes,q)

        sub_scores=[]; sub_coverage=0
        for q in sub_quizzes:
            s = round_num(quiz_percent(q))
            sub_scores = manual_append(sub_scores,s)
            overall_scores = manual_append(overall_scores,{"score":s})
            sub_coverage += q["coverage_percent"]
        if sub_coverage>100: sub_coverage=100

        total_score=0
        for s in sub_scores: total_score += s
        avg_score = total_score / manual_len(sub_scores)

        recent_len = last_n if last_n < manual_len(sub_scores) else manual_len(sub_scores)
        recent_scores=[]
        for i in range(manual_len(sub_scores)-recent_len, manual_len(sub_scores)):
            recent_scores = manual_append(recent_scores, sub_scores[i])

        print("\n--- Subject:", sub, "---")
        print("Average Score:", round_num(avg_score), "%")
        print("Coverage:", sub_coverage, "%")
        print("Recent Scores:", end=" ")
        for sc in recent_scores: print(sc, end="  ")
        print("\nLine:  ", sparkline(recent_scores))
        print("Trend (last", recent_len, "):", detect_trend(sub_quizzes))

    # Overall trend
    overall_scores_list = []
    for o in overall_scores:
        overall_scores_list = manual_append(overall_scores_list, o["score"])

    overall_avg = 0
    for sc in overall_scores_list: overall_avg += sc
    overall_avg = overall_avg / manual_len(overall_scores_list) if manual_len(overall_scores_list)>0 else 0

    print("\n=== Overall ===")
    print("Average Score:", round_num(overall_avg), "%")
    print("Scores:", end=" ")
    for sc in overall_scores_list: print(sc, end="  ")
    print("\nLine:  ", sparkline(overall_scores_list))
    print("Trend:", detect_trend([{"score":s,"max_score":100} for s in overall_scores_list], overall=True))

# ---------------- Predict Performance ----------------
def predict_performance(user_id):
    db = read_json(QUIZ_FILE)
    quizzes = get_user_quizzes(db, user_id)
    if manual_len(quizzes)==0: print("⚠️ Add at least 1 quiz first."); return
    subject_map = group_by_subject(quizzes)
    print("\n=== Performance Prediction ===")
    for subject in subject_map:
        sub = subject_map[subject]
        total = 0
        for q in sub: total += quiz_percent(q)
        avg = total/manual_len(sub)
        total_coverage = 0
        for q in sub: total_coverage += q["coverage_percent"]
        if total_coverage>100: total_coverage=100
        remaining = 100 - total_coverage
        predicted = avg - remaining*0.05
        if predicted<0: predicted=0
        if predicted>100: predicted=100
        low = predicted-5; high = predicted+5
        if low<0: low=0
        if high>100: high=100
        print("\n---", subject, "---")
        print("Average:", round_num(avg), "%")
        print("Coverage remaining:", remaining, "%")
        print("Predicted score range:", round_num(low), "% -", round_num(high), "%")

# ---------------- Coverage ----------------
def show_coverage(user_id):
    db = read_json(QUIZ_FILE)
    quizzes = get_user_quizzes(db, user_id)
    if manual_len(quizzes)==0: print("⚠️ No quizzes yet."); return
    subject_map = group_by_subject(quizzes)
    print("\n=== Coverage per subject ===")
    for subject in subject_map:
        total=0
        for q in subject_map[subject]: total+=q["coverage_percent"]
        if total>100: total=100
        print("-", subject, ":", total, "% covered |", 100-total, "% remaining")

# ---------------- CLI ----------------
def run(user_id, user_data):
    while True:
        print("\n=== Quiz & Prediction ===")
        print("1. Add quiz")
        print("2. View dashboard")
        print("3. Coverage remaining")
        print("4. Predict performance")
        print("0. Exit")

        choice = strip(input("Choose: "))
        if choice=="1": add_quiz(user_id)
        elif choice=="2": view_dashboard(user_id)
        elif choice=="3": show_coverage(user_id)
        elif choice=="4": predict_performance(user_id)
        elif choice=="0": print("👋 Exiting Quiz Module..."); return user_data
        else: print("❌ Invalid choice")

