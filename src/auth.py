from datetime import date
from src.ui import clear_screen
from src.storage import load_users, save_users
import re, os, hashlib, sys

# ---------------- EMAIL VALIDATION ---------------- #

EMAIL_REGEX = re.compile(
    r"^[a-z0-9](?:[a-z0-9._%+-]{0,62}[a-z0-9])?"
    r"@[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z]{2,})+$"
)

# ---------------- PASSWORD HELPERS ---------------- #

def masked_input(prompt: str) -> str:
    print(prompt, end="", flush=True)
    password = ""

    if os.name == "nt":  # Windows
        import msvcrt
        while True:
            ch = msvcrt.getch()
            if ch in {b"\r", b"\n"}:
                print()
                break
            elif ch == b"\x08":  # backspace
                if password:
                    password = password[:-1]
                    print("\b \b", end="", flush=True)
            else:
                password += ch.decode("utf-8", errors="ignore")
                print("*", end="", flush=True)
    else:  # Linux / macOS
        try:
            import tty
            import termios
        except ImportError:
                raise RuntimeError("This password input method is only supported on Unix systems.")


        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\n", "\r"):
                    print()
                    break
                elif ch == "\x7f":  # backspace
                    if password:
                        password = password[:-1]
                        print("\b \b", end="", flush=True)
                else:
                    password += ch
                    print("*", end="", flush=True)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return password.strip()


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
    """Hash password with salt using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)

    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        100_000
    )

    return salt.hex(), pwd_hash.hex()


def verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    """Verify password against stored hash."""
    salt = bytes.fromhex(salt_hex)
    _, new_hash = hash_password(password, salt)
    return new_hash == hash_hex


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
        email = input("Enter email address: ").strip().lower()
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
            hours = int(input("Enter daily study hours: "))
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
        print("╔═══════════════════════════════╗")
        print("║           PET THEME           ║")
        print("╚═══════════════════════════════╝")
        print("[1] Cat😸")
        print("[2] Dog🐶")
        print("[3] Bunny🐰")

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
        print("╔═══════════════════════════════════════════════════════╗")
        print("║  ⚠️  Email already registered. Please login instead!   ║")
        print("╚═══════════════════════════════════════════════════════╝")
        return None, None

    name = ask_non_empty("Enter nickname     : ")
    password = ask_password()
    salt, password_hash = hash_password(password)

    goal_hours = ask_goal_hours()
    academic_goal = ask_non_empty("Enter academic goal: ")
    clear_screen()
    pet_theme = ask_pet_theme()
    clear_screen()
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
        "coins": 5,
        "inventory": {
            "normal_food": 0,
            "premium_food": 0
        },
        "last_login": str(date.today()),
        "mood_today": ""
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
        print("╔══════════════════════════════════════════════════╗")
        print("║   ⚠️  User not found. Please register instead!    ║")
        print("╚══════════════════════════════════════════════════╝")
        return None, None

    user_data = users[email]

    while True:
        password = masked_input("🔑 Enter password  : ")
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
        print("╔══════════════════════════════════════════════════╗")
        print("║          ⚠️   Inactive for 7+ days                ║")
        print("║                  Pet died💀⚰️                     ║")
        print("║          Negative coins due to inactivity        ║")
        print("╚══════════════════════════════════════════════════╝")
        input("\nPress Enter to continue...")

    user_data["last_login"] = str(date.today())
    users[email] = user_data
    save_users(users)

    clear_screen()
    print("✅ Login successful!")
    print()
    
    return email, user_data