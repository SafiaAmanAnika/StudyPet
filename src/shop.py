from src import pet
from src.ui import clear_screen, print_fancy_box, menu

NORMAL_FOOD_COST = 50
PREMIUM_FOOD_COST = 75

NORMAL_FOOD_HEALTH = 3
PREMIUM_FOOD_HEALTH = 5


def open_shop(user_data: dict) -> dict:
    user_data = pet.ensure_pet_defaults(user_data)

    while True:
        clear_screen()
        print_fancy_box(
            "🛒 PET SHOP",
            [
                f"💰 Current Coins: {user_data['coins']}",
                "",
                "Stock up food to keep your pet healthy.",
            ],
            theme="cyan",
        )

        choice = menu([
            "Buy Normal Food (50 coins)",
            "Buy Premium Food (75 coins)",
            "Back",
        ])

        if choice == 1:
            user_data = buy_normal_food(user_data)
        elif choice == 2:
            user_data = buy_premium_food(user_data)
        elif choice == 0:
            return user_data


def buy_normal_food(user_data: dict) -> dict:
    if user_data["coins"] < NORMAL_FOOD_COST:
        clear_screen()
        print_fancy_box(
            "❌ Purchase Failed",
            ["Not enough coins.", f"💰 Current Coins: {user_data['coins']}"],
            theme="yellow",
        )
        return user_data

    user_data = pet.change_coins(user_data, -NORMAL_FOOD_COST)
    user_data["inventory"]["normal_food"] += 1

    clear_screen()
    print_fancy_box(
        "✅ Purchase Complete",
        [
            "🍎 Normal Food added to inventory.",
            f"💰 Current Coins: {user_data['coins']}",
        ],
        theme="green",
    )
    return user_data


def buy_premium_food(user_data: dict) -> dict:
    if user_data["coins"] < PREMIUM_FOOD_COST:
        clear_screen()
        print_fancy_box(
            "❌ Purchase Failed",
            ["Not enough coins.", f"💰 Current Coins: {user_data['coins']}"],
            theme="yellow",
        )
        return user_data

    user_data = pet.change_coins(user_data, -PREMIUM_FOOD_COST)
    user_data["inventory"]["premium_food"] += 1

    clear_screen()
    print_fancy_box(
        "✅ Purchase Complete",
        [
            "🍗 Premium Food added to inventory.",
            f"💰 Current Coins: {user_data['coins']}",
        ],
        theme="green",
    )
    return user_data


def feed_pet(user_data: dict) -> dict:
    user_data = pet.ensure_pet_defaults(user_data)

    while True:
        clear_screen()
        normal = user_data["inventory"]["normal_food"]
        premium = user_data["inventory"]["premium_food"]
        print_fancy_box(
            "🍽️ FEED PET",
            [
                f"🍎 Normal Food: {normal} | 🍗 Premium Food: {premium}",
                "",
                "Choose food to boost your pet's health.",
            ],
            theme="green",
        )

        choice = menu([
            "Use Normal Food (+3 health)",
            "Use Premium Food (+5 health)",
            "Cancel",
        ])

        if choice == 1:
            if user_data["inventory"]["normal_food"] <= 0:
                clear_screen()
                print_fancy_box(
                    "⚠️ No Normal Food",
                    ["Inventory is empty.", "Buy food from the Pet Shop."],
                    theme="yellow",
                )
                continue

            user_data["inventory"]["normal_food"] -= 1
            user_data = pet.change_health(user_data, NORMAL_FOOD_HEALTH)

            clear_screen()
            print_fancy_box(
                "🍽️ Feeding Complete",
                ["Used Normal Food.", "❤️ Health increased by 3."],
                theme="green",
            )
            break

        elif choice == 2:
            if user_data["inventory"]["premium_food"] <= 0:
                clear_screen()
                print_fancy_box(
                    "⚠️ No Premium Food",
                    ["Inventory is empty.", "Buy food from the Pet Shop."],
                    theme="yellow",
                )
                continue

            user_data["inventory"]["premium_food"] -= 1
            user_data = pet.change_health(user_data, PREMIUM_FOOD_HEALTH)

            clear_screen()
            print_fancy_box(
                "🍽️ Feeding Complete",
                ["Used Premium Food.", "❤️ Health increased by 5."],
                theme="green",
            )
            break

        elif choice == 0:
            return user_data

    pet.show_status(user_data)
    return user_data
