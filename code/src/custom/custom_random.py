import time

# Lightweight linear congruential generator (LCG).
# Good enough for simple game/UX randomness in this project.
_MODULUS = 2 ** 31
_MULTIPLIER = 1103515245
_INCREMENT = 12345
_state = int(time.time_ns() % _MODULUS)


def seed(value):
    global _state
    try:
        _state = int(value) % _MODULUS
    except (TypeError, ValueError):
        _state = int(time.time_ns() % _MODULUS)


def _next_int():
    global _state
    _state = (_MULTIPLIER * _state + _INCREMENT) % _MODULUS
    return _state


def randint(a, b):
    """Return random integer N such that a <= N <= b."""
    a = int(a)
    b = int(b)
    if a > b:
        a, b = b, a

    span = (b - a) + 1
    return a + (_next_int() % span)


def choice(seq):
    """Return a random element from a non-empty sequence."""
    if seq is None or len(seq) == 0:
        raise IndexError("Cannot choose from an empty sequence")
    idx = randint(0, len(seq) - 1)
    return seq[idx]
