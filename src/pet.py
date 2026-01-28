# Pet-related logic: status, health, coins, warnings

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

    return user_data


def get_pet_ascii(health: int) -> str:
    if health >= 10:
        return (
            "   /\\_/\\\n"
            "  ( ^_^ )\n"
            "   > ^ <\n"
            "✨😸 Your pet is energetic and happy!"
        )
    elif health >=8:
        return (
            "   /\\_/\\\n"
            "  ( -_- )\n"
            "   > ^ <\n"
            "😺 Your pet is doing okay."
        )
    elif health >= 5 and health > 3:
        return (
            "   /\\_/\\\n"
            "  ( T_T )\n"
            "   > ^ <\n"
            "😿 Your pet looks hungry..."
        )
    else:
        return (
            "   /\\_/\\\n"
            "  ( x_x )\n"
            "   > ^ <\n"
            "🙀 Pet is in critical condition!"
        )


def show_status(user_data: dict) -> None:
    user_data = ensure_pet_defaults(user_data)

    print("\n=========== PET STATUS ===========")
    print(f"Health : {user_data['health']}")
    print(f"Coins  : {user_data['coins']}")
    print("---------------------------------")
    print("Inventory:")
    print(f"🍎 Normal Food  : {user_data['inventory']['normal_food']}")
    print(f"🍗 Premium Food: {user_data['inventory']['premium_food']}")
    print("---------------------------------")
    print(get_pet_ascii(user_data["health"]))

    warning = health_warning(user_data)
    if warning:
        print("\n" + warning)

    print("=================================\n")


def change_health(user_data: dict, delta: int) -> dict:
    user_data = ensure_pet_defaults(user_data)

    user_data["health"] += delta

    if user_data["health"] > 20:
        user_data["health"] = 20

    if user_data["health"] < 0:
        user_data["health"] = 0

    return user_data


def change_coins(user_data: dict, delta: int) -> dict:
    user_data = ensure_pet_defaults(user_data)

    user_data["coins"] += delta

    if user_data["coins"] < -100:
        user_data["coins"] = -100

    return user_data


def health_warning(user_data: dict):
    health = user_data["health"]

    if health <= 3:
        return "⚠️ CRITICAL WARNING: Feed your pet immediately!"
    elif health < 10:
        return "😿 Your pet is hungry."
    return None