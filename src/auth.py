from datetime import date
from storage import load_users, save_users

def ask_student_id() -> str:
    """Ask for a numeric student ID."""
    while True:
        user_id = input("Enter Student ID: ").strip()
        if user_id.isdigit():
            return user_id
        print("Student ID must be numeric.")


def ask_non_empty(prompt: str) -> str:
    """Ask until user enters a non-empty value."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def ask_goal_hours() -> int:
    """Ask for valid study hours (0–24)."""
    while True:
        try:
            hours = int(input("Enter daily study hours (0–24): "))
            if 0 <= hours <= 24:
                return hours
            print("Please enter a number between 0 and 24.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def assign_personality(goal_hours: int) -> str:
    """Assign pet personality based on study hours."""
    if goal_hours <= 2:
        return "Lazy"
    elif goal_hours <= 4:
        return "Mediocre"
    else:
        return "Serious"


def register():
    users = load_users()

    user_id = ask_student_id()
    if user_id in users:
        print("User already exists. Please login instead.")
        return None, None

    name = ask_non_empty("Enter name: ")
    goal_hours = ask_goal_hours()
    academic_goal = ask_non_empty("Enter academic goal: ")
    pet_theme = ask_non_empty("Choose pet theme (Cat, Dog, Bear): ")

    personality = assign_personality(goal_hours)

    user_data = {
        "name": name,
        "goal_hours": goal_hours,
        "academic_goal": academic_goal,
        "pet_theme": pet_theme,
        "pet_personality": personality,
        "health": 10,
        "coins": 5,
        "last_login": str(date.today()),
        "mood_today": ""
    }

    users[user_id] = user_data
    save_users(users)

    print("Registration successful.")
    return user_id, user_data


def login():
    users = load_users()

    user_id = ask_student_id()
    if user_id not in users:
        print("User not found.")
        return None, None

    user_data = users[user_id]

    user_data["last_login"] = str(date.today())
    users[user_id] = user_data
    save_users(users)

    print("Login successful.")
    return user_id, user_data