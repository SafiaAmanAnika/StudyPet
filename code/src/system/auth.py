from datetime import date
from getpass import getpass
from src.interface.ui import clear_screen, print_fancy_box, pause
from .storage import load_users, save_users
from src.custom.custom_validation import is_valid_email
from src.custom.custom_hash import hash_password as custom_hash_password, verify_password as custom_verify_password

# ---------------- EMAIL VALIDATION ---------------- #

class _EmailRegexProxy:
    def fullmatch(self, value):
        return is_valid_email(value)


EMAIL_REGEX = _EmailRegexProxy()

# ---------------- PASSWORD HELPERS ---------------- #

def masked_input(prompt: str) -> str:
    # Prefer hidden input; some terminals may not support getpass reliably.
    try:
        return getpass(prompt).strip()
    except Exception:
        return input(prompt).strip()


def is_valid_password(password: str) -> bool:
    """Check password rules."""
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True


def hash_password(password: str, salt: bytes = None):
    """Hash password using project custom hash (academic demo only)."""
    return custom_hash_password(password, salt)


def verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    """Verify password against stored custom hash."""
    return custom_verify_password(password, salt_hex, hash_hex)




def ask_password() -> str:
    """Ask until user enters a valid password."""
    while True:
        password = masked_input(
            "🔒 Create password (Min 8 characters, 1 capital letter and 1 number): "
        )

        if is_valid_password(password):
            return password

        print(
            "❌ Password must be at least 8 characters long, "
            "contain 1 capital letter and 1 number."
        )

# ---------------- EMAIL INPUT ---------------- #

def ask_email() -> str:
    """Ask until user enters a valid email."""
    while True:
        email = input("📧 Enter email address          : ").strip().lower()
        if EMAIL_REGEX.fullmatch(email):
            return email
        
        print("❌ Invalid email. Please try again.")
        print()

# ---------------- INPUT HELPERS ---------------- #

def ask_non_empty(prompt: str) -> str:
    """Ask until user enters a non-empty value."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("⚠️ This field cannot be empty.")

                 
def ask_goal_hours() -> int:
    """Ask for valid study hours (1–24)."""
    while True:
        try:
            hours = int(input("📘 Enter daily study hours (1-24): "))
            if 1 <= hours <= 24:
                return hours
            print("❌ Invalid input. Please enter a number between 1 and 24.")
            print()
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            print()

# ---------------- PET SELECTION ---------------- #

def ask_pet_theme() -> str:
    """Ask user to choose pet theme using numeric options only."""
    options = {
        "1": "Cat",
        "2": "Dog",
        "3": "Bunny"
    }

    while True:
        print_fancy_box(
            "PET THEME",
            [
                "[1] Cat 😸",
                "[2] Dog 🐶",
                "[3] Bunny 🐰",
            ],
            theme="yellow",
        )

        choice = input("Choose a pet theme (1–3): ").strip()
        if choice in options:
            return options[choice]

        clear_screen()
        print("❌ Invalid choice. Please enter 1, 2, or 3")
        print()

# ---------------- PET LOGIC ---------------- #

def assign_personality(goal_hours: int) -> str:
    """Assign pet personality based on study hours."""
    if goal_hours <= 2:
        return "Sleepy but curious, learning one step at a time🤔💭"
    elif goal_hours <= 4:
        return "Calm, steady, and building consistency🤗😌"
    else:
        return "Focused, intense, and hungry for knowledge🤓📚"


def check_inactivity_penalty(user_data: dict) -> bool:
    """Check inactivity penalty. Return True if penalty was applied."""
    last_login_str = user_data.get("last_login")
    if not last_login_str:
        return False

    try:
        last_login_date = date.fromisoformat(last_login_str)
    except ValueError:
        return False

    today = date.today()
    days_inactive = (today - last_login_date).days

    if days_inactive >= 7:
        user_data["health"] = 10
        user_data["coins"] = -100
        return True

    return False

# ---------------- AUTH ---------------- #

def register():
    users = load_users()

    email = ask_email()
    if email in users:
        clear_screen()
        print_fancy_box(
            "⚠️ Registration Blocked",
            ["Email already registered.", "Please login instead."],
            theme="yellow",
        )
        pause()
        return None, None

    name = ask_non_empty("👤 Enter nickname               : ")
    password = ask_password()
    salt, password_hash = hash_password(password)
    
    # Registration keeps these as defaults; users can change later in settings.
    goal_hours = 2
    academic_goal = ""
    pet_theme = "Cat"
    personality = assign_personality(goal_hours)

    user_data = {
        "name": name,
        "password_salt": salt,
        "password_hash": password_hash,
        "goal_hours": goal_hours,
        "academic_goal": academic_goal,
        "pet_theme": pet_theme,
        "pet_personality": personality,
        "health": 10,
        "energy": 100,
        "coins": 5,
        "study_streak": 0,
        "total_study_hours": 0,
        "total_study_minutes": 0,
        "last_study_date": "",
        "inventory": {
            "normal_food": 0,
            "premium_food": 0
        },
        "last_login": str(date.today()),
        "mood_today": "",
        "ui_theme": "pastel_pink",
        "animation_style": "sparkly",
        "music_enabled": True,
        "music_volume": 0.35,
        "ambience_enabled": False,
        "ambience_type": "rain",
        "ambience_volume": 0.30,
    }


    users[email] = user_data
    save_users(users)

    print("✅ Registration successful!")
    print(" ")
    return email, user_data


def login():
    users = load_users()

    email = ask_email()
    if email not in users:
        clear_screen()
        print_fancy_box(
            "⚠️ User Not Found",
            ["Please register first and try login again."],
            theme="yellow",
        )
        return None, None

    user_data = users[email]

    while True:
        password = masked_input("🔑 Enter password               : ")
        if verify_password(
            password,
            user_data["password_salt"],
            user_data["password_hash"]
        ):
            break
        print("❌ Incorrect password. Please try again.")

    penalized = check_inactivity_penalty(user_data)

    if penalized:
        save_users(users)
        clear_screen()
        print_fancy_box(
            "⚠️ Inactivity Penalty",
            [
                "Inactive for 7+ days.",
                "Pet died 💀⚰️",
                "Negative coins applied.",
            ],
            theme="magenta",
        )
        input("\nPress Enter to continue...")

    user_data["last_login"] = str(date.today())
    users[email] = user_data
    save_users(users)

    clear_screen()
    print_fancy_box("✅ Login Successful", ["Welcome back to StudyPet!"], theme="green")
    
    return email, user_data