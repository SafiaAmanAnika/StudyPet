import time
import random
from datetime import datetime, timedelta

# ---------------- UTILITY ---------------- #
def today_str():
    t = time.localtime()
    return f"{t.tm_year}-{t.tm_mon:02}-{t.tm_mday:02}"

def input_study_date():
    date_str = input("Enter study date (YYYY-MM-DD) or leave empty for today:\n> ").strip()
    if date_str == "":
        return today_str()
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except:
        print("Invalid date format. Using today.")
        return today_str()
    

def input_study_hours():
    while True:
        hours_str = input("How many hours did you study today? (1-24)\n> ").strip()
        try:
            hours = float(hours_str)
            if 0 < hours <= 24:
                return hours
            else:
                print("Please enter a valid number between 1 and 24.")
        except:
            print("Please enter a valid number between 1 and 24.")