import math
import os
import random
import struct
import wave

try:
    import pygame
except ImportError:
    pygame = None


SAMPLE_RATE = 22050
DEFAULTS = {
    "music_enabled": True,
    "music_volume": 0.35,
    "ambience_enabled": False,
    "ambience_type": "rain",
    "ambience_volume": 0.30,
}

AMBIENCE_LABELS = {
    "rain": "Rain",
    "ocean": "Ocean Waves",
    "fire": "Fire Crackling",
    "none": "None",
}

_ASSET_DIR = "data/soundscape"
_LOFI_FILE = "lofi_loop.wav"
_AMBIENCE_FILES = {
    "rain": "rain_loop.wav",
    "ocean": "ocean_loop.wav",
    "fire": "fire_loop.wav",
}

_READY = False
_SOUND_CACHE = {}
_CURRENT_AMBIENCE = None


def _project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _soundscape_dir():
    return os.path.join(_project_root(), _ASSET_DIR)


def _sound_path(file_name):
    return os.path.join(_soundscape_dir(), file_name)


def _clamp(value, low, high):
    return max(low, min(high, value))


def _to_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _to_bool(value, default):
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


def ensure_user_sound_defaults(user_data):
    user_data["music_enabled"] = _to_bool(user_data.get("music_enabled"), DEFAULTS["music_enabled"])
    user_data["ambience_enabled"] = _to_bool(user_data.get("ambience_enabled"), DEFAULTS["ambience_enabled"])

    music_volume = _to_float(user_data.get("music_volume"), DEFAULTS["music_volume"])
    ambience_volume = _to_float(user_data.get("ambience_volume"), DEFAULTS["ambience_volume"])
    user_data["music_volume"] = _clamp(music_volume, 0.0, 1.0)
    user_data["ambience_volume"] = _clamp(ambience_volume, 0.0, 1.0)

    ambience_type = str(user_data.get("ambience_type", DEFAULTS["ambience_type"]) or DEFAULTS["ambience_type"]).lower()
    if ambience_type not in AMBIENCE_LABELS:
        ambience_type = DEFAULTS["ambience_type"]
    user_data["ambience_type"] = ambience_type

    return user_data


def ambience_keys():
    return ["rain", "ocean", "fire", "none"]


def get_ambience_display_name(kind):
    return AMBIENCE_LABELS.get(str(kind).lower(), AMBIENCE_LABELS["none"])


def _write_wave(path, duration_seconds, sample_func):
    total = max(1, int(SAMPLE_RATE * duration_seconds))
    frames = bytearray()

    for i in range(total):
        t = i / SAMPLE_RATE
        sample = _clamp(sample_func(i, t), -1.0, 1.0)
        value = int(sample * 32767)
        frames.extend(struct.pack("<h", value))

    with wave.open(path, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(bytes(frames))


def _render_lofi(path):
    chords = [
        (261.63, 311.13, 392.00),
        (220.00, 261.63, 329.63),
        (246.94, 293.66, 369.99),
        (196.00, 246.94, 329.63),
    ]

    def sample(_, t):
        chord_len = 2.0
        chord_idx = int(t / chord_len) % len(chords)
        chord = chords[chord_idx]

        chord_mix = 0.0
        for freq in chord:
            chord_mix += math.sin(2.0 * math.pi * freq * t)
        chord_mix /= float(len(chord))

        bass = math.sin(2.0 * math.pi * (chord[0] / 2.0) * t)

        beat = max(0.0, math.sin(2.0 * math.pi * 1.5 * t)) ** 6
        kick = beat * math.sin(2.0 * math.pi * 55.0 * t)

        wobble = 0.5 + 0.5 * math.sin(2.0 * math.pi * 0.10 * t)
        sample_value = (0.42 * chord_mix * wobble) + (0.24 * bass) + (0.20 * kick)
        return sample_value

    _write_wave(path, duration_seconds=16.0, sample_func=sample)


def _render_rain(path):
    rng = random.Random(11)
    state = {"lp": 0.0}

    def sample(_, t):
        white = rng.uniform(-1.0, 1.0)
        state["lp"] = (state["lp"] * 0.975) + (white * 0.025)
        rumble = math.sin(2.0 * math.pi * 120.0 * t + (0.4 * math.sin(2.0 * math.pi * 0.08 * t)))
        return (0.33 * state["lp"]) + (0.04 * rumble)

    _write_wave(path, duration_seconds=10.0, sample_func=sample)


def _render_ocean(path):
    rng = random.Random(27)
    state = {"foam": 0.0}

    def sample(_, t):
        white = rng.uniform(-1.0, 1.0)
        state["foam"] = (state["foam"] * 0.992) + (white * 0.008)

        swell = 0.5 + 0.5 * math.sin(2.0 * math.pi * 0.06 * t)
        undertow = math.sin(2.0 * math.pi * 60.0 * t + (0.6 * swell))
        wash = state["foam"] * (0.4 + 0.6 * swell)
        return (0.20 * undertow) + (0.28 * wash)

    _write_wave(path, duration_seconds=12.0, sample_func=sample)


def _render_fire(path):
    rng = random.Random(58)
    state = {"rumble": 0.0}

    def sample(_, t):
        white = rng.uniform(-1.0, 1.0)
        state["rumble"] = (state["rumble"] * 0.985) + (white * 0.015)
        crackle = white - state["rumble"]

        pop = 0.0
        if rng.random() < 0.0018:
            pop = rng.uniform(-1.0, 1.0)

        low = math.sin(2.0 * math.pi * 42.0 * t)
        return (0.20 * state["rumble"]) + (0.23 * crackle) + (0.25 * pop) + (0.06 * low)

    _write_wave(path, duration_seconds=10.0, sample_func=sample)


def _ensure_generated_assets():
    os.makedirs(_soundscape_dir(), exist_ok=True)

    lofi_path = _sound_path(_LOFI_FILE)
    if not os.path.exists(lofi_path):
        _render_lofi(lofi_path)

    rain_path = _sound_path(_AMBIENCE_FILES["rain"])
    if not os.path.exists(rain_path):
        _render_rain(rain_path)

    ocean_path = _sound_path(_AMBIENCE_FILES["ocean"])
    if not os.path.exists(ocean_path):
        _render_ocean(ocean_path)

    fire_path = _sound_path(_AMBIENCE_FILES["fire"])
    if not os.path.exists(fire_path):
        _render_fire(fire_path)


def _ensure_ready():
    global _READY

    if _READY:
        return True

    if pygame is None:
        return False

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=1024)

        # Keep enough channels for UI SFX, pet sounds, and ambience loop simultaneously.
        current_channels = pygame.mixer.get_num_channels()
        if current_channels < 8:
            pygame.mixer.set_num_channels(8)

        _ensure_generated_assets()
        _READY = True
        return True
    except Exception:
        return False


def _ambience_channel():
    if pygame is None:
        return None
    try:
        return pygame.mixer.Channel(2)
    except Exception:
        return None


def _load_sound(path):
    if path in _SOUND_CACHE:
        return _SOUND_CACHE[path]

    try:
        sound = pygame.mixer.Sound(path)
        _SOUND_CACHE[path] = sound
        return sound
    except Exception:
        return None


def _play_lofi(volume):
    if pygame is None:
        return

    path = _sound_path(_LOFI_FILE)
    try:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(_clamp(volume, 0.0, 1.0))
    except Exception:
        return


def _stop_lofi():
    if pygame is None:
        return
    try:
        pygame.mixer.music.stop()
    except Exception:
        return


def _play_ambience(kind, volume):
    global _CURRENT_AMBIENCE

    if pygame is None:
        return

    if kind not in _AMBIENCE_FILES:
        _stop_ambience()
        return

    channel = _ambience_channel()
    if channel is None:
        return

    path = _sound_path(_AMBIENCE_FILES[kind])
    sound = _load_sound(path)
    if sound is None:
        return

    try:
        if _CURRENT_AMBIENCE != kind or not channel.get_busy():
            channel.play(sound, loops=-1)
            _CURRENT_AMBIENCE = kind
        channel.set_volume(_clamp(volume, 0.0, 1.0))
    except Exception:
        return


def _stop_ambience():
    global _CURRENT_AMBIENCE

    channel = _ambience_channel()
    if channel is not None:
        try:
            channel.stop()
        except Exception:
            pass

    _CURRENT_AMBIENCE = None


def apply_user_soundscape(user_data):
    ensure_user_sound_defaults(user_data)

    if not _ensure_ready():
        return False

    if user_data.get("music_enabled", DEFAULTS["music_enabled"]):
        _play_lofi(user_data.get("music_volume", DEFAULTS["music_volume"]))
    else:
        _stop_lofi()

    ambience_enabled = user_data.get("ambience_enabled", DEFAULTS["ambience_enabled"])
    ambience_type = str(user_data.get("ambience_type", DEFAULTS["ambience_type"]) or "none").lower()
    ambience_volume = user_data.get("ambience_volume", DEFAULTS["ambience_volume"])

    if ambience_enabled and ambience_type in _AMBIENCE_FILES:
        _play_ambience(ambience_type, ambience_volume)
    else:
        _stop_ambience()

    return True


def stop_soundscape():
    _stop_lofi()
    _stop_ambience()


def soundscape_available():
    return pygame is not None
