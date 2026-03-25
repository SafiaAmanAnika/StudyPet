from src import pet
from src.interface.ui import clear_screen, print_fancy_box, menu, pause
from src.core.wallet import log_transaction

NORMAL_FOOD_COST = 50
PREMIUM_FOOD_COST = 75

NORMAL_FOOD_HEALTH = 5
PREMIUM_FOOD_HEALTH = 10
MAX_PET_HEALTH = 20

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
            "❌ Not Enough Coins",
            [
                "You don't have enough coins to buy Normal Food.",
                f"Normal Food costs : {NORMAL_FOOD_COST} coins",
                f"Your coins        : {user_data['coins']}",
            ],
            theme="yellow",
        )
        pause()
        return user_data
    
    user_data = pet.change_coins(user_data, -NORMAL_FOOD_COST)
    user_data["inventory"]["normal_food"] += 1
    user_data = log_transaction(user_data, "Bought Normal Food", NORMAL_FOOD_COST, "debit")

    clear_screen()
    print_fancy_box(
    "✅ Purchase Complete",
    [
        "🍎 Normal Food bought successfully!",
        f"🎒 Normal Food in inventory : {user_data['inventory']['normal_food']}",
        f"💰 Remaining Coins          : {user_data['coins']}",
    ],
    theme="green",
) 
    
    
    pause()
    return user_data


def buy_premium_food(user_data: dict) -> dict:
    if user_data["coins"] < PREMIUM_FOOD_COST:
        clear_screen()
        print_fancy_box(
            "❌ Not Enough Coins",
            [
                "You don't have enough coins to buy Premium Food.",
                f"Premium Food costs : {PREMIUM_FOOD_COST} coins",
                f"Your coins         : {user_data['coins']}",
            ],
            theme="yellow",
        )
        pause()
        return user_data
    
    user_data = pet.change_coins(user_data, -PREMIUM_FOOD_COST)
    user_data["inventory"]["premium_food"] += 1
    user_data = log_transaction(user_data, "Bought Premium Food", PREMIUM_FOOD_COST, "debit")

    clear_screen()
    print_fancy_box(
    "✅ Purchase Complete",
    [
        "🍗 Premium Food bought successfully!",
        f"🎒 Premium Food in inventory : {user_data['inventory']['premium_food']}",
        f"💰 Remaining Coins           : {user_data['coins']}",
    ],
    theme="green",
)
    

    pause()
    return user_data

def feed_pet(user_data: dict) -> dict:
    user_data = pet.ensure_pet_defaults(user_data)

    while True:
        clear_screen()
        normal = user_data["inventory"]["normal_food"]
        premium = user_data["inventory"]["premium_food"]
        print_fancy_box(
            "🍽️  FEED PET",
            [
                f"❤️  Current Health: {user_data.get('health', 10)}/{MAX_PET_HEALTH}",
                f"🍎 Normal Food: {normal} | 🍗 Premium Food: {premium}",
                "",
                "Choose food to boost your pet's health.",
            ],
            theme="green",
        )

        choice = menu([
            "Use Normal Food (+5 health)",
            "Use Premium Food (+10 health)",
            "Cancel",
        ])

        if choice == 1:
            if user_data.get("health", 10) >= MAX_PET_HEALTH:
                clear_screen()
                print_fancy_box(
                    "❤️ Health Already Full",
                    [
                        "Your pet is already at maximum health!",
                        f"Current Health : {user_data.get('health', 10)}/{MAX_PET_HEALTH}",
                        "No food was consumed.",
                         "Complete a session first, then come back to feed! 📚",
                    ],
                    theme="yellow",
                )
                pause()
                continue

            if user_data["inventory"]["normal_food"] <= 0:
                clear_screen()
                print_fancy_box(
                    "⚠️ No Normal Food",
                    ["Inventory is empty.", "Buy food from the Pet Shop."],
                    theme="yellow",
                )
                pause()
                continue

            health_before = int(user_data.get("health", 10))
            user_data["inventory"]["normal_food"] -= 1
            user_data = pet.change_health(user_data, NORMAL_FOOD_HEALTH)
            gained = int(user_data.get("health", 10)) - health_before

            clear_screen()
            lines = ["Used Normal Food.", f"❤️ Health increased by {gained}."]
            if gained < NORMAL_FOOD_HEALTH:
                lines.append("Reached max health cap (20).")
            print_fancy_box("🍽️ Feeding Complete", lines, theme="green")
            break
        

        elif choice == 2:
            if user_data.get("health", 10) >= MAX_PET_HEALTH:
                clear_screen()
                print_fancy_box(
                    "❤️ Health Already Full",
                    [
                        "Your pet is already at maximum health!",
                        f"Current Health : {user_data.get('health', 10)}/{MAX_PET_HEALTH}",
                        "No food was consumed.",
                         "Complete a session first, then come back to feed! 📚",
                    ],
                    theme="yellow",
                )
                pause()
                continue


