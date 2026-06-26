from src.interface.ui import print_fancy_box
from datetime import datetime

def _today_str():
    today = datetime.now().date()
    return today.strftime("%Y-%m-%d")

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

def show_wallet(user_data: dict) -> None:
    transactions = user_data.get("wallet_transactions", [])

    if not transactions:
        print_fancy_box(
            "💰 WALLET - BANK STATEMENT",
            ["No transactions yet.", "Start studying or visit the shop!"],
            theme="cyan",
        )
        return
    
     # Column widths
    W_DATE  = 12
    W_DESC  = 28
    W_CR    = 8
    W_DB    = 8
    W_BAL   = 8
    SEP     = " | "

    def row(date, desc, credit, debit, balance):
        date_col  = date[:W_DATE].ljust(W_DATE)
        desc_col  = desc[:W_DESC].ljust(W_DESC)
        cr_col    = str(credit).rjust(W_CR)
        db_col    = str(debit).rjust(W_DB)
        bal_col   = str(balance).rjust(W_BAL)
        return date_col + SEP + desc_col + SEP + cr_col + SEP + db_col + SEP + bal_col

    header = row("Date", "Description", "Credit", "Debit", "Balance")
    divider = "-" * len(header)

    lines = [header, divider]

    for tx in transactions:
        lines.append(row(
            tx.get("date", ""),
            tx.get("description", ""),
            tx.get("credit", 0) or "",
            tx.get("debit", 0) or "",
            tx.get("balance", 0),
        ))

    lines.append(divider)
    lines.append(row("", "Current Balance", "", "", user_data.get("coins", 0)))

    print_fancy_box("💰 WALLET - BANK STATEMENT", lines, theme="cyan")