import os
import time


def read_line_with_timeout(timeout_seconds):
    """Return a full line if user submits within timeout, else None."""
    timeout_seconds = float(timeout_seconds)
    if timeout_seconds <= 0:
        return None

    if os.name != "nt":
        # Fallback for non-Windows without select: no timed input support.
        time.sleep(timeout_seconds)
        return None

    import msvcrt

    end = time.time() + timeout_seconds
    buf = []

    while time.time() < end:
        if not msvcrt.kbhit():
            time.sleep(0.03)
            continue

        ch = msvcrt.getwch()
        if ch in ("\r", "\n"):
            print()
            return "".join(buf)

        if ch == "\x08":
            if buf:
                buf.pop()
                print("\b \b", end="", flush=True)
            continue

        buf.append(ch)
        print(ch, end="", flush=True)

    return None