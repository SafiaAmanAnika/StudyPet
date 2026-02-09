from src import pet
from src.ui import clear_screen

def open_shop(user_data: dict) -> dict:
    user_data = pet.ensure_pet_defaults(user_data)

    while True:
        print("╔═══════════════════════════════╗")
        print("║           PET SHOP            ║")
        print("╚═══════════════════════════════╝")
        print("[1] Buy Food")
        print("[2] Feed Pet")
        print("[0] Back")

        choice = input("Choose your option: ").strip()
        clear_screen()

        if choice == "1":
            user_data = buy_food(user_data)
        elif choice == "2":
            user_data = feed_pet(user_data)
        elif choice == "0":
            return user_data
        else:
            print("❌ Invalid option.")

NORMAL_FOOD_COST = 50
PREMIUM_FOOD_COST = 75

NORMAL_FOOD_HEALTH = 3
PREMIUM_FOOD_HEALTH = 5


def buy_food(user_data: dict) -> dict:
    user_data = pet.ensure_pet_defaults(user_data)

    print("╔═══════════════════════════════╗")
    print("║           PET SHOP            ║")
    print("╚═══════════════════════════════╝")
    print("[1] Buy Normal Food  (50 coins)")
    print("[2] Buy Premium Food (75 coins)")
    print("[0] Back")

    choice = input("Choose your option: ").strip()
    clear_screen()

    if choice == "1":
        if user_data["coins"] < NORMAL_FOOD_COST:
            print("❌ Not enough coins!")
            print(f"💰 Current Coins: {user_data['coins']}")
            return user_data

        user_data = pet.change_coins(user_data, -NORMAL_FOOD_COST)
        user_data["inventory"]["normal_food"] += 1

        print("🍎 Normal Food added to inventory!")
        print("💰 Coins spent: 50")
        print(f"💰 Current Coins: {user_data['coins']}")

    elif choice == "2":
        if user_data["coins"] < PREMIUM_FOOD_COST:
            print("❌ Not enough coins!")
            print(f"💰 Current Coins: {user_data['coins']}")
            return user_data

        user_data = pet.change_coins(user_data, -PREMIUM_FOOD_COST)
        user_data["inventory"]["premium_food"] += 1

        print("🍗 Premium Food added to inventory!")
        print("💰 Coins spent: 75")
        print(f"💰 Current Coins: {user_data['coins']}")

    elif choice == "0":
        return user_data

    else:
        print("❌ Invalid option.")

    return user_data


def feed_pet(user_data: dict) -> dict:
    user_data = pet.ensure_pet_defaults(user_data)

    print("╔═══════════════════════════════╗")
    print("║           FEED PET            ║")
    print("╚═══════════════════════════════╝")
    print("[1] Use Normal Food  (+3 health)")
    print("[2] Use Premium Food (+5 health)")
    print("[0] Cancel")

    choice = input("Choose your option: ").strip()

    if choice == "1":
        if user_data["inventory"]["normal_food"] <= 0:
            print("❌ No Normal Food available!")
            print("🛒 Buy food from the Pet Shop.")
            return user_data

        user_data["inventory"]["normal_food"] -= 1
        user_data = pet.change_health(user_data, NORMAL_FOOD_HEALTH)

        print("\n🍽️ Feeding pet...")
        print("❤️ Health increased by 3")
        print(f"❤️ Current Health: {user_data['health']}")

    elif choice == "2":
        if user_data["inventory"]["premium_food"] <= 0:
            print("❌ No Premium Food available!")
            print("🛒 Buy food from the Pet Shop.")
            return user_data

        user_data["inventory"]["premium_food"] -= 1
        user_data = pet.change_health(user_data, PREMIUM_FOOD_HEALTH)

        print("\n🍽️ Feeding pet...")
        print("❤️ Health increased by 5")
        print(f"❤️ Current Health: {user_data['health']}")

    elif choice == "0":
        return user_data

    else:
        print("❌ Invalid option.")

    pet.show_status(user_data)
    return user_data