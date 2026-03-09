from src import pet
from src.ui import clear_screen, print_fancy_box

NORMAL_FOOD_COST = 50
PREMIUM_FOOD_COST = 75

NORMAL_FOOD_HEALTH = 3
PREMIUM_FOOD_HEALTH = 5


def open_shop(user_data: dict) -> dict:
    user_data = pet.ensure_pet_defaults(user_data)

    while True:
        print_fancy_box(
            "🛒 PET SHOP",
            [
                f"💰 Current Coins: {user_data['coins']}",
                "",
                "[1] Buy Normal Food  (50 coins)",
                "[2] Buy Premium Food (75 coins)",
                "[0] Back",
            ],
            theme="cyan",
        )

        choice = input("Choose your option: ").strip()

        if choice == "1":
            user_data = buy_normal_food(user_data)
        elif choice == "2":
            user_data = buy_premium_food(user_data)
        elif choice == "0":
            return user_data
        else:
            clear_screen()
            print("❌ Invalid option. Please try again.")
            print()


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

    print("🍎 Normal Food added to inventory!")
    print(f"💰 Current Coins: {user_data['coins']}")
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

    print("🍗 Premium Food added to inventory!")
    print(f"💰 Current Coins: {user_data['coins']}")
    return user_data


def feed_pet(user_data: dict) -> dict:
    user_data = pet.ensure_pet_defaults(user_data)

    while True:
        normal = user_data["inventory"]["normal_food"]
        premium = user_data["inventory"]["premium_food"]
        print_fancy_box(
            "🍽️ FEED PET",
            [
                f"🍎 Normal Food: {normal} | 🍗 Premium Food: {premium}",
                "",
                "[1] Use Normal Food  (+3 health)",
                "[2] Use Premium Food (+5 health)",
                "[0] Cancel",
            ],
            theme="green",
        )

        choice = input("Choose your option: ").strip()

        if choice == "1":
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

            print("\n🍽️ Feeding pet...")
            print("❤️ Health increased by 3")
            break

        elif choice == "2":
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

            print("\n🍽️ Feeding pet...")
            print("❤️ Health increased by 5")
            break

        elif choice == "0":
            return user_data

        else:
            clear_screen()
            print("❌ Invalid option. Please try again.")
            print()

    pet.show_status(user_data)
    return user_data
