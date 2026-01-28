def clear_line(): 
    print("-" * 40)

def title(text): 
    clear_line()
    print(text)
    clear_line()

def clear_screen():
    print("\033[2J\033[3J\033[H", end="")

def pause():
    try:
        input("\nPress the Enter button to continue!")
    except KeyboardInterrupt:
        print("\nExiting pause.")

def menu(prompt, options):
    if not options:
        print("No options available.")
        return None

    while True: 
        print("\n" + prompt)
        for i, option in enumerate(options, start=1):
            print(f"{i}. {option}")
        choice = input("Choose your option: ").strip()

        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(options):
                return choice
            
        print("Invalid choice provided. Please try again.")

def show_user_summary(user_data):
    name = user_data.get("name", "User")
    health = user_data.get("health", 10)
    if health <= 3: 
        print("\n⚠️ Warning: Your pet is very weak! Feed it soon.")
    coins = user_data.get("coins", 5)
    if coins < 0: 
        print("\n⚠️ Penalty active: negative coins due to inactivity.")
    pet_theme = user_data.get("pet_theme", "Unknown")
    goal_hours = user_data.get("goal_hours", "?")
    academic_goal = user_data.get("academic_goal", "")
    pet_personality = user_data.get("pet_personality", "Neutral")
    mood = user_data.get("mood_today", "")
    if mood: 
        print(f"Mood Today: {mood}")

    print(f"Name: {name}")
    print(f"Pet: {pet_theme} | Personality: {pet_personality}")
    print(f"Health: {health}   Coins: {coins}")
    print(f"Daily Goal: {goal_hours} hours")
    if academic_goal: 
        print(f"Academic Goal: {academic_goal}")


def print_kv(label, value):
    print(f"{label:<15}: {value}")

def show_user_stats(user_id, user_data):
    title_text = f"User Stats - {user_data.get('name', 'User')}"
    clear_line()
    print(title_text)
    clear_line()

    print_kv("🐱 Email", user_id)
    print_kv("🐱 Nickname", user_data.get("name", "User"))
    print_kv("🐱 Goal Hours", user_data.get("goal_hours", "?"))
    print_kv("🐱 Academic Goal", user_data.get("academic_goal", ""))
    print_kv("🐱 Pet Theme", user_data.get("pet_theme", "Unknown"))
    print_kv("🐱 Personality", user_data.get("pet_personality", "Neutral"))
    print_kv("🐱 Health", user_data.get("health", 10))
    print_kv("🐱 Coins", user_data.get("coins", 5))
    print_kv("🐱 Last Login", user_data.get("last_login", ""))
    print_kv("🐱 Mood Today", user_data.get("mood_today", ""))
    

def choose_mood(menu_func): 
    moods = ["Happy 😊", "Neutral 😐", "Tired 😞", "Stressed 😫", "Motivated 🥳", "Skip"]
    choice = menu_func("How are you feeling today, dear?", moods)
    return moods[choice -1]