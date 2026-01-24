# Pet-related logic: status, health, coins, warnings


def ensure_pet_defaults(user_data: dict) -> dict:
    if "health" not in user_data:
        user_data["health"] = 10

    if "coins" not in user_data:
        user_data["coins"] = 0

    if "pet_theme" not in user_data:
        user_data["pet_theme"] = "Default"

    if "pet_personality" not in user_data:
        user_data["pet_personality"] = "Neutral"

    return user_data


def get_pet_ascii(health: int) -> str:
    """
    Returns ASCII art based on pet health.
    """

    if health >= 15:
        return (
            "   /\\_/\\\n"
            "  ( o.o )  \n"
            "   > ^ <   \n"
            "Pet is energetic and happy!"
        )

    if health >= 10:
        return (
            "   /\\_/\\\n"
            "  ( -.- )  \n"
            "   > ^ <   \n"
            "Pet is doing okay."
        )

    if health >= 4:
        return (
            "   /\\_/\\\n"
            "  ( T.T )  \n"
            "   > ^ <   \n"
            "Pet looks hungry..."
        )

    return (
        "   /\\_/\\\n"
        "  ( x.x )  \n"
        "   > ^ <   \n"
        "Pet is in critical condition!"
    )


def show_status(user_data: dict) -> None:
    user_data = ensure_pet_defaults(user_data)

    print("\n================ PET STATUS ================")
    print(f"Pet Theme       : {user_data['pet_theme']}")
    print(f"Pet Personality : {user_data['pet_personality']}")
    print(f"Health          : {user_data['health']}")
    print(f"Coins           : {user_data['coins']}")
    print("-------------------------------------------")

    ascii_pet = get_pet_ascii(user_data["health"])
    print(ascii_pet)

    warning = health_warning(user_data)
    if warning is not None:
        print("\n" + warning)

    print("===========================================\n")


def change_health(
    user_data: dict,
    delta: int,
    min_health: int = 0,
    max_health: int = 20
) -> dict:
    user_data = ensure_pet_defaults(user_data)

    current_health = user_data["health"]
    new_health = current_health + delta

    if new_health > max_health:
        new_health = max_health

    if new_health < min_health:
        new_health = min_health

    user_data["health"] = new_health
    return user_data


def change_coins(
    user_data: dict,
    delta: int,
    min_coins: int = -100
) -> dict:
    user_data = ensure_pet_defaults(user_data)

    current_coins = user_data["coins"]
    new_coins = current_coins + delta

    if new_coins < min_coins:
        new_coins = min_coins

    user_data["coins"] = new_coins
    return user_data


def health_warning(user_data: dict):
    user_data = ensure_pet_defaults(user_data)

    health = user_data["health"]

    if health <= 3:
        return "⚠ CRITICAL WARNING: Your pet may die soon!"

    if health < 10:
        return "🐾 Your pet is hungry. Please feed it."

    return None
