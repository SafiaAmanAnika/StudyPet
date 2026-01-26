
# Shop and feeding system

from src import pet

NORMAL_FOOD_COST = 50
NORMAL_FOOD_HEALTH = 3

PREMIUM_FOOD_COST = 75
PREMIUM_FOOD_HEALTH = 5


def feed_pet(user_data: dict) -> dict:
    
    #Allows user to feed pet.
    
    user_data = pet.ensure_pet_defaults(user_data)

    print("\n--- FEED PET MENU ---")
    print("1. Normal Food   (50 coins, +3 health)")
    print("2. Premium Food (75 coins, +5 health)")
    print("3. Cancel")

    choice = input("Choose an option: ").strip()

    if choice == "1":
        if user_data["coins"] < NORMAL_FOOD_COST:
            print("❌ Not enough coins to buy Normal Food.")
            return user_data

        user_data = pet.change_coins(user_data, -NORMAL_FOOD_COST)
        user_data = pet.change_health(user_data, NORMAL_FOOD_HEALTH)

        print("✅ Pet fed with Normal Food!")
        print("Health +3 | Coins -50")

    elif choice == "2":
        if user_data["coins"] < PREMIUM_FOOD_COST:
            print("❌ Not enough coins to buy Premium Food.")
            return user_data

        user_data = pet.change_coins(user_data, -PREMIUM_FOOD_COST)
        user_data = pet.change_health(user_data, PREMIUM_FOOD_HEALTH)

        print("🌟 Pet enjoyed Premium Food!")
        print("Health +5 | Coins -75")

    elif choice == "3":
        print("Returning to previous menu...")

    else:
        print("❌ Invalid choice.")

    return user_data


def open_shop(user_data: dict) -> dict:
    
    #Shop wrapper menu.
    
    user_data = pet.ensure_pet_defaults(user_data)

    while True:
        print("\n========== PET SHOP ==========")
        print("1. Feed your pet")
        print("2. View pet status")
        print("3. Exit shop")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            user_data = feed_pet(user_data)

        elif choice == "2":
            pet.show_status(user_data)

        elif choice == "3":
            print("Leaving shop...")
            break

        else:
            print("❌ Invalid option.")

    return user_data
