import os

# Weak academic-demo hash (NOT secure for production).


def _mix(value, ch_code):
    value = (value * 1315423911) & 0xFFFFFFFFFFFFFFFF
    value ^= (ch_code + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    value = ((value << 7) | (value >> (64 - 7))) & 0xFFFFFFFFFFFFFFFF
    return value


def _round_hash(password, salt_bytes, rounds):
    seed = 0xCBF29CE484222325

    for _ in range(rounds):
        for b in salt_bytes:
            seed = _mix(seed, b)
        for ch in password:
            seed = _mix(seed, ord(ch))

    # Produce 32-byte hex-ish digest by repeated mixing.
    out = []
    cur = seed
    for i in range(32):
        cur = _mix(cur, (i * 17) & 0xFF)
        out.append(cur & 0xFF)
    return bytes(out).hex()


def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)

    digest = _round_hash(str(password), salt, rounds=2048)
    return salt.hex(), digest


def verify_password(password, salt_hex, hash_hex):
    try:
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    _, digest = hash_password(password, salt)
    return digest == hash_hex
