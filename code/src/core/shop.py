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

       

