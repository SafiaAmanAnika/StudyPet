def clear_screen():
    print("\033[2J\033[3J\033[H", end="")

def pause():
    try:
        input("\nPress the Enter button to continue!")
    except KeyboardInterrupt:
        print("\nExiting pause.")


def menu(options):
    while True:
        for i, option in enumerate(options[:-1], start=1):
            print(f"[{i}] {option}")
        print(f"[0] {options[-1]}")  # last option = 0

        choice = input("Choose your option: ").strip()

        if choice.isdigit():
            choice = int(choice)
            if choice == 0:
                return 0
            elif 1 <= choice < len(options):
                return choice

        clear_screen()
        print("❌ Invalid choice. Please try again.")
        print()


def print_kv(label, value):
    print(f"{label:<15}: {value}")
    

def show_user_summary(user_data):
    name = user_data.get("name", "User")
    health = user_data.get("health", 10)
    coins = user_data.get("coins", 5)
    pet_theme = user_data.get("pet_theme", "Unknown")
    goal_hours = user_data.get("goal_hours", "?")
    academic_goal = user_data.get("academic_goal", "")
    pet_personality = user_data.get("pet_personality", "Neutral")
    mood = user_data.get("mood_today", "")

    width = 73

    if mood:
        print("║ " + f"Mood Today    : {mood}".ljust(width - 2) + "║")

    if health <= 3:
        print("║ " + "⚠️ Warning: Your pet is very weak! Feed it soon.".ljust(width - 1) + "║")
        print("║" + " " * width + "║")

    print("║" + " " * width + "║")

    print("║ " + f"Name          : {name}".ljust(width - 1) + "║")
    print("║ " + f"Pet           : {pet_theme}".ljust(width - 1) + "║")
    print("║ " + f"Personality   : {pet_personality}".ljust(width - 3) + "║")
    print("║ " + f"Health        : {health}".ljust(width - 1) + "║")
    print("║ " + f"Coins         : {coins}".ljust(width - 1) + "║")
    print("║ " + f"Daily Goal    : {goal_hours} hours".ljust(width - 1) + "║")

    if academic_goal:
        print("║ " + f"Academic Goal : {academic_goal}".ljust(width - 1) + "║")

    print("╚" + "═" * width + "╝")


def show_user_stats(user_id, user_data):
    width = 73

    print("╔═════════════════════════════════════════════════════════════════════════╗")
    print("║                         🐱 USER STATISTICS 🐱                           ║")
    print("╠═════════════════════════════════════════════════════════════════════════╣")
    print(f"║ 🐱 Email        : {user_id.ljust(54)}║")
    print(f"║ 🐱 Nickname     : {user_data.get('name', 'User').ljust(54)}║")
    print(f"║ 🐱 Goal Hours   : {str(user_data.get('goal_hours', '?')).ljust(54)}║")
    print(f"║ 🐱 Academic Goal: {user_data.get('academic_goal', '').ljust(54)}║")
    print(f"║ 🐱 Pet Theme    : {user_data.get('pet_theme', 'Unknown').ljust(54)}║")
    print(f"║ 🐱 Personality  : {user_data.get('pet_personality', 'Neutral').ljust(53)}║")
    print(f"║ 🐱 Health       : {str(user_data.get('health', 10)).ljust(54)}║")
    print(f"║ 🐱 Coins        : {str(user_data.get('coins', 5)).ljust(54)}║")
    print(f"║ 🐱 Last Login   : {user_data.get('last_login', '').ljust(54)}║")
    print(f"║ 🐱 Mood Today   : {user_data.get('mood_today', '').ljust(53)}║")
    print("╚═════════════════════════════════════════════════════════════════════════╝")
    

def choose_mood(menu_func): 
    moods = ["Happy 😊", "Neutral 😐", "Tired 😞", "Stressed 😫", "Motivated 🥳", "Skip"]
    print("╔═════════════════════════════════════════════════════════════════════════╗")
    print("║                     How are you feeling today, dear?                    ║")
    print("╚═════════════════════════════════════════════════════════════════════════╝")
    choice = menu_func(moods)

    return moods[choice -1]

# ---------------- ANALYTICS UI ---------------- #

def analytics_menu():
    print("╔═════════════════════════════════════════════════════════════════════════╗")
    print("║                         📈 STUDY ANALYTICS 📈                           ║")
    print("╚═════════════════════════════════════════════════════════════════════════╝")

    options = [
        "View last 7 days",
        "View last 28 days",
        "View last 56 days",
        "Back"
    ]

    return menu(options)