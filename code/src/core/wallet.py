from src.interface.ui import print_fancy_box
import time


def _today_str():
    t = time.localtime()
    return f"{t.tm_year}-{t.tm_mon:02}-{t.tm_mday:02}"

def log_transaction(user_data: dict, description: str, amount: int, tx_type: str) -> dict:
    # tx_type: "credit" or "debit"
    if "wallet_transactions" not in user_data:
        user_data["wallet_transactions"] = []

    balance = int(user_data.get("coins", 0))

    entry = {
        "date": _today_str(),
        "description": description,
        "credit": amount if tx_type == "credit" else 0,
        "debit": amount if tx_type == "debit" else 0,
        "balance": balance,
    }

    user_data["wallet_transactions"].append(entry)
    return user_data

