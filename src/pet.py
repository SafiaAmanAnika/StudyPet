from src.evolution import get_pet_stage

def ensure_pet_defaults(user_data: dict) -> dict:
    if "health" not in user_data:
        user_data["health"] = 10

    if "coins" not in user_data:
        user_data["coins"] = 5

    if "inventory" not in user_data:
        user_data["inventory"] = {
            "normal_food": 0,
            "premium_food": 0
        }

    if "pet_theme" not in user_data:
        user_data["pet_theme"] = "Default"

    if "pet_personality" not in user_data:
        user_data["pet_personality"] = "Neutral"

    if "level" not in user_data:
        user_data["level"] = 1

    if "total_study_hours" not in user_data:
        user_data["total_study_hours"] = 0

    return user_data


def get_health_state(health: int) -> str:
    if health <= 3:
        return "critical"
    elif health < 10:
        return "hungry"
    elif health < 15:
        return "okay"
    return "happy"


def get_pet_ascii(health: int) -> str:
    state = get_health_state(health)

    if state == "happy":
        return (
            "   /\\_/\\\n"
            "  ( ^_^ )\n"
            "   > ^ <\n"
            "✨😸 Your pet is energetic and happy!"
        )
    elif state == "okay":
        return (
            "   /\\_/\\\n"
            "  ( -_- )\n"
            "   > ^ <\n"
            "😺 Your pet is doing okay."
        )
    elif state == "hungry":
        return (
            "   /\\_/\\\n"
            "  ( T_T )\n"
            "   > ^ <\n"
            "😿 Your pet looks hungry..."
        )
    else:  # critical
        return (
            "   /\\_/\\\n"
            "  ( x_x )\n"
            "   > ^ <\n"
            "🙀 Pet is in critical condition!"
        )


def show_status(user_data: dict) -> None:
    user_data = ensure_pet_defaults(user_data)

    print("╔══════════════════════════════════════════╗")
    print("║            🐱 PET STATUS 🐱              ║")
    print("╚══════════════════════════════════════════╝")

    print(f"Health : {user_data['health']}")
    print(f"Coins  : {user_data['coins']}")
    print(f"Level  : {user_data['level']} ({get_pet_stage(user_data['level'])})")
    print("════════════════════════════════════════════")

    print("Inventory:")
    print(f"🍎 Normal Food : {user_data['inventory']['normal_food']}")
    print(f"🍗 Premium Food: {user_data['inventory']['premium_food']}")
    print("════════════════════════════════════════════")

    print(get_pet_ascii(user_data["health"]))
    print("════════════════════════════════════════════\n")


def change_health(user_data: dict, delta: int) -> dict:
    user_data = ensure_pet_defaults(user_data)

    user_data["health"] += delta

    if user_data["health"] > 20:
        user_data["health"] = 20
    elif user_data["health"] < 0:
        user_data["health"] = 0

    return user_data


def change_coins(user_data: dict, delta: int) -> dict:
    user_data = ensure_pet_defaults(user_data)

    user_data["coins"] += delta

    if user_data["coins"] < -100:
        user_data["coins"] = -100

    return user_data

# applying pet abilities based on pet theme

# dog -> +10% more coins on long sessions like an hour
# cat ->  study streak >= 5, more coins
# bunny -> increases health by 1 
def apply_pet_abilities(user_data):
    pet = user_data.get('pet_theme', 'Cat');
    study_minutes = user_data.get('total_study_minutes', 0)

    if pet == 'Dog':
        if study_minutes >= 60:
            coins_earned = user_data.get('coins', 0) * 1.1
            user_data['coins'] = int(coins_earned)
            print("Your doggo gives you extra coins 🪙")

    elif pet == 'Bunny':
        user_data['health'] = user_data.get('health', 0) + 1
        print("Your bunnyyy gives you extra health 🏥")

    elif pet == 'Cat':
        streak = user_data.get('study_streak', 0)
        if streak >= 5: 
            user_data['coins'] += 50
            print("Your catto gives you extra coins 🪙")

                                          