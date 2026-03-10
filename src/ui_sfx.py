import math
import os
import struct
import wave

try:
    import pygame
except ImportError:
    pygame = None


SAMPLE_RATE = 22050
SFX_VOLUME = 0.28

_READY = False
_CACHE = {}


def _project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sfx_dir():
    return os.path.join(_project_root(), "data", "ui_sfx")


def _sound_paths():
    base = _sfx_dir()
    return {
        "click": os.path.join(base, "cute_click.wav"),
        "back": os.path.join(base, "cute_back.wav"),
        "error": os.path.join(base, "cute_error.wav"),
    }


def _enabled():
    return os.environ.get("STUDYPET_UI_SFX", "1").strip().lower() not in {"0", "false", "off", "no"}


def _envelope(i, total):
    attack = max(1, int(0.01 * SAMPLE_RATE))
    release = max(1, int(0.03 * SAMPLE_RATE))

    attack_gain = min(1.0, i / attack)
    release_gain = min(1.0, (total - i) / release)
    return max(0.0, min(attack_gain, release_gain))


def _render_note(freq, duration, volume):
    frames = bytearray()
    total = max(1, int(SAMPLE_RATE * duration))

    for i in range(total):
        t = i / SAMPLE_RATE
        env = _envelope(i, total)

        base = math.sin(2.0 * math.pi * freq * t)
        sparkle = 0.35 * math.sin(2.0 * math.pi * freq * 2.0 * t)
        sample = (base + sparkle) / 1.35

        value = int(32767 * volume * env * sample)
        frames.extend(struct.pack("<h", value))

    return frames


def _write_sound(path, notes):
    frames = bytearray()
    for freq, duration, volume in notes:
        frames.extend(_render_note(freq, duration, volume))

    with wave.open(path, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(bytes(frames))


def _ensure_generated_files():
    os.makedirs(_sfx_dir(), exist_ok=True)
    paths = _sound_paths()

    if not os.path.exists(paths["click"]):
        _write_sound(
            paths["click"],
            [
                (990.0, 0.05, 0.90),
                (1320.0, 0.07, 0.80),
            ],
        )

    if not os.path.exists(paths["back"]):
        _write_sound(
            paths["back"],
            [
                (880.0, 0.05, 0.75),
                (660.0, 0.08, 0.70),
            ],
        )

    if not os.path.exists(paths["error"]):
        _write_sound(
            paths["error"],
            [
                (370.0, 0.06, 0.75),
                (300.0, 0.09, 0.72),
            ],
        )


def _ensure_ready():
    global _READY

    if _READY:
        return True

    if not _enabled() or pygame is None:
        return False

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
        _ensure_generated_files()
        _READY = True
        return True
    except Exception:
        return False


def _load_sound(name):
    if name in _CACHE:
        return _CACHE[name]

    try:
        path = _sound_paths()[name]
        sound = pygame.mixer.Sound(path)
        sound.set_volume(SFX_VOLUME)
        _CACHE[name] = sound
        return sound
    except Exception:
        return None


def _play(name):
    if not _ensure_ready():
        return

    sound = _load_sound(name)
    if sound is not None:
        try:
            sound.play()
        except Exception:
            return


def play_ui_click():
    _play("click")


def play_ui_back():
    _play("back")


def play_ui_error():
    _play("error")
