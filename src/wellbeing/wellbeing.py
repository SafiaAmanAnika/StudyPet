import json, os 
from datetime import date, timedelta
from src.ui import print_fancy_box

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MOOD_FILE = os.path.join(DATA_DIR, "mood_log.json")
STUDY_LOG_FILE = os.path.join(DATA_DIR, "study_log.json")

def today_str():
    return str(date.today())

def load_mood_db():
    #if mood log doesn't exist, create it with empty dict 
    os.makedirs(DATA_DIR, exist_ok = True)

    if not os.path.exists(MOOD_FILE):
        with open(MOOD_FILE, "w") as f:
            json.dump({}, f)
        return {}
    
    #opening mood log, if it's corrupted, reset to empty dict
    try: 
        with open(MOOD_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else: 
                return {}
    except json.JSONDecodeError:
        with open(MOOD_FILE, "w") as f:
            json.dump({}, f)
        return {}
    except (FileNotFoundError, Exception):
        return {}
    
    
def save_mood_db(db):
    os.makedirs(DATA_DIR, exist_ok = True)
    with open(MOOD_FILE, "w") as f:
        if isinstance(db, dict):
            json.dump(db, f, indent = 2)
        else:
            json.dump({}, f, indent = 2)

#loading and saving study logs

def load_study_logs():
    os.makedirs(DATA_DIR, exist_ok = True)

    if not os.path.exists(STUDY_LOG_FILE):
        with open(STUDY_LOG_FILE, "w") as f:
            json.dump([], f)
        return []

    try: 
        with open(STUDY_LOG_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else: 
                return []
    except json.JSONDecodeError:
        with open(STUDY_LOG_FILE, "w") as f:
            json.dump([], f)
        return []
    except (FileNotFoundError, Exception):
        return []
    

#mood logging

menu_label = "Wellbeing and Recreation 🌼"

def log_mood(user_id: str, mood: str):
    db = load_mood_db()
    today = today_str()

    #if user dont exist/ user doesnt have a list of mood entries, create empty list
    if user_id not in db or not isinstance(db[user_id], list):
        db[user_id] = []

    for entry in db[user_id]:
        if isinstance(entry, dict) and entry.get("date") == today:
            entry["mood"] = mood
            save_mood_db(db)
            return 
        
    db[user_id].append({"date": today, "mood": mood, "penalty_applied" : False})
    save_mood_db(db)

#tired streak penalty 

def tired_streak_days(user_id: str) -> int:
    db = load_mood_db()
    records = db.get(user_id, []) 
    if not isinstance(records, list) or len(records) == 0: 
        return 0 
    
    #mapping each date w mood
    record_map = {}
    for r in records: 
        if isinstance(r, dict) and "date" in r: 
            record_map[r.get("date")] = r.get("mood")
    
    streak = 0 
    cur = date.today()

    #counting the tired days from the present day to the day when it shows not tired 
    while True: 
        d = str(cur)
        #print(f"Checking date: {d}, Mood: {record_map.get(d)}") 
        #if the user was tired today, continue the streak 
        if record_map.get(d) == "Tired 😞":
            streak += 1     
        else: 
            #if the user wasnt tired, reset the streak 
            break 
        
        #go to the prev day 
        cur -= timedelta(days = 1) #subtracting 1 day from current date 

    #print(f"Tired streak for user {user_id}: {streak}")
    return streak 

def apply_tired_penalty(user_id: str, user_data: dict):
    db = load_mood_db()
    user_records = db.get(user_id, [])
    if not isinstance(user_records, list):
        user_records = []
        db[user_id] = user_records

    today = today_str()

    #prevent multiple penalties in the same day 
    for r in user_records: 
        if isinstance(r, dict) and r.get("date") == today and r.get("penalty_applied"):
            return user_data, None
    
    if tired_streak_days(user_id) >= 3: 
        user_data["health"] = max(0, user_data.get("health", 10) - 2)

        #penalty marked on today's record, create penalty if missing
        
        found_today = False
        for r in user_records: 
            if isinstance(r, dict) and r.get("date") == today: 
                r["penalty_applied"] = True
                found_today = True
                break 

        if not found_today:
            user_records.append(
                {
                    "date" : today,
                    "mood" : user_data.get("mood_today", ""),
                    "penalty_applied" : True
                }
            )

            save_mood_db(db)
            return user_data, "😷 You’ve been tired for 3 days straight. Pet health -2. Please rest! Take a chill pill~"
    
    return user_data, None 

# if user studies for more than 5 hours / tired for more than 3 days
def detect_burnout(user_id, user_data):
    total_minutes = int(user_data.get("total_study_hours", 0) * 60)
    if total_minutes > 300: 
        print_fancy_box(
            "⚠️ Burnout Detected",
            ["You have studied for more than 5 hours.", "Please rest before continuing."],
            theme="yellow",
        )
        return True
    
    if tired_streak_days(user_id) >= 3:
        print_fancy_box(
            "⚠️ Burnout Detected",
            ["You have been tired for multiple days.", "Please rest before continuing."],
            theme="yellow",
        )
        return True
    
    return False

def handle_burnout(user_id, user_data):
    if detect_burnout(user_id, user_data):
        today = today_str()

        # Prevent repeated burnout penalties in a single day.
        if user_data.get("last_burnout_penalty_date") == today:
            print_fancy_box(
                "Burnout Already Handled",
                ["A burnout penalty was already applied today.", "Please take a break before studying again."],
                theme="yellow",
            )
            return True

        user_data["health"] = max(0, user_data.get("health", 10) - 2)
        user_data["last_burnout_penalty_date"] = today
        print_fancy_box(
            "Rest Required 💤",
            ["Your pet insists you take a rest.", "Burnout penalty applied (-2 health)."],
            theme="magenta",
        )
        return True
    return False 

# energy will decrease 0.5 times per minute 
def update_energy(user_data, study_minutes):
    try:
        energy = float(user_data.get('energy', 100))
    except (TypeError, ValueError):
        energy = 100.0

    try:
        minutes = float(study_minutes)
    except (TypeError, ValueError):
        minutes = 0.0

    energy_spent = minutes * 0.5
    user_data['energy'] = max(0.0, round(energy - energy_spent, 1))
    if user_data['energy'] <= 0: 
        print_fancy_box(
            "⚠️ Energy Depleted",
            ["Please take a break and restore your energy."],
            theme="yellow",
        )
    return user_data

def restore_energy(user_data):
    try:
        energy = float(user_data.get('energy', 0))
    except (TypeError, ValueError):
        energy = 0.0

    user_data['energy'] = min(100.0, round(energy + 20, 1))
    print_fancy_box(
        "🔋 Energy Restored",
        [f"Current energy: {user_data['energy']}"],
        theme="green",
    )
    return user_data