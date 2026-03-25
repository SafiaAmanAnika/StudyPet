from src.interface.ui import print_fancy_box
import time


def _today_str():
    t = time.localtime()
    return f"{t.tm_year}-{t.tm_mon:02}-{t.tm_mday:02}"
