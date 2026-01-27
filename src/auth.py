from datetime import date
import re
from src.storage import load_users, save_users

# ---------------- EMAIL VALIDATION ---------------- #

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+-]+@(gmail\.com|iut-dhaka\.edu)$"
)


def ask_email() -> str:
    """Ask until user enters a valid email from allowed domains."""
    while True:
        email = input("Enter email address: ").strip().lower()

        if EMAIL_REGEX.match(email):
            return email

        print("Invalid email.")


# ---------------- INPUT HELPERS ---------------- #

def ask_non_empty(prompt: str) -> str:
    """Ask until user enters a non-empty value."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def ask_goal_hours() -> int:
    """Ask for valid study hours (1–24)."""
    while True:
        try:
            hours = int(input("Enter daily study hours (1–24): "))
            if 1 <= hours <= 24:
                return hours
            print("Please enter a number between 1 and 24.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def ask_pet_theme() -> str:
    """Ask user to choose pet theme using numeric options only."""
    options = {
        "1": "Cat",
        "2": "Dog",
        "3": "Bunny"
    }

    while True:
        print("\nChoose pet theme:")
        print("1. Cat")
        print("2. Dog")
        print("3. Bunny")

        choice = input("Enter choice (1–3): ").strip()

        if choice in options:
            return options[choice]

        print("Invalid choice. Please enter 1, 2, or 3.")


# ---------------- PET LOGIC ---------------- #

def assign_personality(goal_hours: int) -> str:
    """Assign pet personality based on study hours."""
    if goal_hours <= 2:
        return "Lower than average"
    elif goal_hours <= 4:
        return "Average"
    else:
        return "Better than average"


def check_inactivity_penalty(user_data: dict):
    """
    Check if user was inactive for 7+ days.
    If so, reset health and coins.
    """
    last_login_str = user_data.get("last_login")
    if not last_login_str:
        return user_data, None

    try:
        last_login_date = date.fromisoformat(last_login_str)
    except ValueError:
        return user_data, None

    today = date.today()
    days_inactive = (today - last_login_date).days

    if days_inactive >= 7:
        user_data["health"] = 10
        user_data["coins"] = -100
        return user_data, "Inactive for 7+ days: pet died. Reset applied."

    return user_data, None


# ---------------- AUTH ---------------- #

def register():
    users = load_users()

    email = ask_email()
    if email in users:
        print("Email already registered. Please login instead.")
        return None, None

    name = ask_non_empty("Enter name: ")
    goal_hours = ask_goal_hours()
    academic_goal = ask_non_empty("Enter academic goal: ")
    pet_theme = ask_pet_theme()

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

    users[email] = user_data
    save_users(users)

    print("Registration successful.")
    return email, user_data


def login():
    users = load_users()

    email = ask_email()
    if email not in users:
        print("User not found.")
        return None, None

    user_data = users[email]

    user_data, warning = check_inactivity_penalty(user_data)
    if warning:
        print(warning)

    user_data["last_login"] = str(date.today())
    users[email] = user_data
    save_users(users)

    print("Login successful.")
    return email, user_data