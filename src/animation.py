import time, os

animation_indexes = {}

PETS_FRAMES = {

    "Cat": {

        "Baby": {

            "Happy": [
                " /\\_/\\   ♪\n( ^.^ )\n >  ^  <",
                " /\\_/\\   ♪\n( ^o^ )\n >  ^  <",
                " /\\_/\\   ♪\n( ^.^ )\n >  o  <",
            ],

            "Neutral": [
                " /\\_/\\\n( -.- )\n >  ^  <",
                " /\\_/\\\n( -_- )\n >  ^  <",
                " /\\_/\\\n( -.- )\n >  _  <",
            ],

            "Tired": [
                " /\\_/\\  zZ\n( -.- )\n >  ^  <",
                " /\\_/\\  zZ\n( -_- )\n >  ^  <",
                " /\\_/\\  zZ\n( -.- )\n >  _  <",
            ],

            "Stressed": [
                " /\\_/\\  !!!\n( o.O )\n >  ^  <",
                " /\\_/\\  !!!\n( O.o )\n >  ^  <",
                " /\\_/\\  !!!\n( o.O )\n >  _  <",
            ],

            "Motivated": [
                " /\\_/\\  🔥\n( >.< )\n >  ^  <",
                " /\\_/\\  🔥\n( >o< )\n >  ^  <",
                " /\\_/\\  🔥\n( >.< )\n >  o  <",
            ]
        },

        "Teen": {

            "Happy": [
                " /\\_/\\  📚\n( ^.^ )\n >  ^  <",
                " /\\_/\\  📚\n( ^o^ )\n >  ^  <",
                " /\\_/\\  📚\n( ^.^ )\n >  o  <",
            ],

            "Neutral": [
                " /\\_/\\  📚\n( -.- )\n >  ^  <",
                " /\\_/\\  📚\n( -_- )\n >  ^  <",
                " /\\_/\\  📚\n( -.- )\n >  _  <",
            ],

            "Tired": [
                " /\\_/\\  📚 zZ\n( -.- )\n >  ^  <",
                " /\\_/\\  📚 zZ\n( -_- )\n >  ^  <",
                " /\\_/\\  📚 zZ\n( -.- )\n >  _  <",
            ],

            "Stressed": [
                " /\\_/\\  📚 !!!\n( o.O )\n >  ^  <",
                " /\\_/\\  📚 !!!\n( O.o )\n >  ^  <",
                " /\\_/\\  📚 !!!\n( o.O )\n >  _  <",
            ],

            "Motivated": [
                " /\\_/\\  📚 🔥\n( >.< )\n >  ^  <",
                " /\\_/\\  📚 🔥\n( >o< )\n >  ^  <",
                " /\\_/\\  📚 🔥\n( >.< )\n >  o  <",
            ]
        },

        "Scholar": {

            "Happy": [
                " /\\_/\\  🎓\n( ^.^ )\n >  ^  <",
                " /\\_/\\  🎓\n( ^o^ )\n >  ^  <",
                " /\\_/\\  🎓\n( ^.^ )\n >  o  <",
            ],

            "Neutral": [
                " /\\_/\\  🎓\n( -.- )\n >  ^  <",
                " /\\_/\\  🎓\n( -_- )\n >  ^  <",
                " /\\_/\\  🎓\n( -.- )\n >  _  <",
            ],

            "Tired": [
                " /\\_/\\  🎓 zZ\n( -.- )\n >  ^  <",
                " /\\_/\\  🎓 zZ\n( -_- )\n >  ^  <",
                " /\\_/\\  🎓 zZ\n( -.- )\n >  _  <",
            ],

            "Stressed": [
                " /\\_/\\  🎓 !!!\n( o.O )\n >  ^  <",
                " /\\_/\\  🎓 !!!\n( O.o )\n >  ^  <",
                " /\\_/\\  🎓 !!!\n( o.O )\n >  _  <",
            ],

            "Motivated": [
                " /\\_/\\  🎓 🔥\n( >.< )\n >  ^  <",
                " /\\_/\\  🎓 🔥\n( >o< )\n >  ^  <",
                " /\\_/\\  🎓 🔥\n( >.< )\n >  o  <",
            ]
        }
    },

# ---------------------------------------------------

    "Dog": {

        "Baby": {

            "Happy": [
                "  /^^^\\  ♪\n / ^ ^ \\\n V\\ v /V",
                "  /^^^\\  ♪\n / o o \\\n V\\ ^ /V",
                "  /^^^\\  ♪\n / ^ ^ \\\n V\\ o /V",
            ],

            "Neutral": [
                " /^^^\\\n / - - \\ \n V\\ ^ /V", 
                " /^^^\\\n / -.- \\ \n V\\ ^ /V", 
                " /^^^\\\n / - - \\ \n V\\ _ /V",
            ],

            "Tired": [
                "  /^^^\\  zZ\n / - - \\\n V\\ ^ /V",
                "  /^^^\\  zZ\n / -.- \\\n V\\ ^ /V",
                "  /^^^\\  zZ\n / - - \\ \n V\\ _ /V",
            ],

            "Stressed": [
                "  /^^^\\  !!!\n / o.O \\\n V\\ ^ /V",
                "  /^^^\\  !!!\n / O.o \\\n V\\ ^ /V",
                "  /^^^\\  !!!\n / o.O \\\n V\\ _ /V",
            ],

            "Motivated": [
                "  /^^^\\  🔥\n / >.< \\\n V\\ ^ /V",
                "  /^^^\\  🔥\n / >o< \\\n V\\ ^ /V",
                "  /^^^\\  🔥\n / >.< \\\n V\\ _ /V",
            ]
        },

        "Teen": {

            "Happy": [
                "  /^^^\\  📚\n / ^ ^ \\\n V\\ v /V",
                "  /^^^\\  📚\n / o o \\\n V\\ ^ /V",
                "  /^^^\\  📚\n / ^ ^ \\\n V\\ o /V",
            ],

            "Neutral": [
                "  /^^^\\  📚\n / - - \\\n V\\ ^ /V",
                "  /^^^\\  📚\n / -.- \\\n V\\ ^ /V",
                "  /^^^\\  📚\n / - - \\\n V\\ _ /V",
            ],

            "Tired": [
                "  /^^^\\  📚 zZ\n / - - \\\n V\\ ^ /V",
                "  /^^^\\  📚 zZ\n / -.- \\\n V\\ ^ /V",
                "  /^^^\\  📚 zZ\n / - - \\\n V\\ _ /V",
            ],

            "Stressed": [
                "  /^^^\\  📚 !!!\n / o.O \\\n V\\ ^ /V",
                "  /^^^\\  📚 !!!\n / O.o \\\n V\\ ^ /V",
                "  /^^^\\  📚 !!!\n / o.O \\\n V\\ _ /V",
            ],

            "Motivated": [
                "  /^^^\\  📚 🔥\n / >.< \\\n V\\ ^ /V",
                "  /^^^\\  📚 🔥\n / >o< \\\n V\\ ^ /V",
                "  /^^^\\  📚 🔥\n / >.< \\\n V\\ _ /V",
            ]
        },

        "Scholar": {

            "Happy": [
                "  /^^^\\  🎓\n / ^ ^ \\\n V\\ v /V",
                "  /^^^\\  🎓\n / o o \\\n V\\ ^ /V",
                "  /^^^\\  🎓\n / ^ ^ \\\n V\\ o /V",
            ],

            "Neutral": [
                "  /^^^\\  🎓\n / - - \\\n V\\ ^ /V",
                "  /^^^\\  🎓\n / -.- \\\n V\\ ^ /V",
                "  /^^^\\  🎓\n / - - \\\n V\\ _ /V",
            ],

            "Tired": [
                "  /^^^\\  🎓 zZ\n / - - \\\n V\\ ^ /V",
                "  /^^^\\  🎓 zZ\n / -.- \\\n V\\ ^ /V",
                "  /^^^\\  🎓 zZ\n / - - \\\n V\\ _ /V",
            ],

            "Stressed": [
                "  /^^^\\  🎓 !!!\n / o.O \\\n V\\ ^ /V",
                "  /^^^\\  🎓 !!!\n / O.o \\\n V\\ ^ /V",
                "  /^^^\\  🎓 !!!\n / o.O \\\n V\\ _ /V",
            ],

            "Motivated": [
                "  /^^^\\  🎓 🔥\n / >.< \\\n V\\ ^ /V",
                "  /^^^\\  🎓 🔥\n / >o< \\\n V\\ ^ /V",
                "  /^^^\\  🎓 🔥\n / >.< \\\n V\\ _ /V",
            ]
        }
    },

# ---------------------------------------------------

    "Bunny": {

        "Baby": {

            "Happy": [
                "  (\\_/)  ♪\n ( ^.^ )\n o(   )o",
                "  (\\_/)  ♪\n ( ^o^ )\n o(   )o",
                "  (\\_/)  ♪\n ( ^.^ )\n o(   )o",
            ],

            "Neutral": [
                "  (\\_/)\n ( -.- )\n o(   )o",
                "  (\\_/)\n ( -_- )\n o(   )o",
                "  (\\_/)\n ( -.- )\n o(   )o",
            ],

            "Tired": [
                "  (\\_/)  zZ\n ( -.- )\n o(   )o",
                "  (\\_/)  zZ\n ( -_- )\n o(   )o",
                "  (\\_/)  zZ\n ( -.- )\n o(   )o",
            ],

            "Stressed": [
                "  (\\_/)  !!!\n ( o.O )\n o(   )o",
                "  (\\_/)  !!!\n ( O.o )\n o(   )o",
                "  (\\_/)  !!!\n ( o.O )\n o(   )o",
            ],

            "Motivated": [
                "  (\\_/)  🔥\n ( >.< )\n o(   )o",
                "  (\\_/)  🔥\n ( >o< )\n o(   )o",
                "  (\\_/)  🔥\n ( >.< )\n o(   )o",
            ]
        },

        "Teen": {

            "Happy": [
                "  (\\_/)  📚\n ( ^.^ )\n o(   )o",
                "  (\\_/)  📚\n ( ^o^ )\n o(   )o",
                "  (\\_/)  📚\n ( ^.^ )\n o(   )o",
            ],

            "Neutral": [
                "  (\\_/)  📚\n ( -.- )\n o(   )o",
                "  (\\_/)  📚\n ( -_- )\n o(   )o",
                "  (\\_/)  📚\n ( -.- )\n o(   )o",
            ],

            "Tired": [
                "  (\\_/)  📚 zZ\n ( -.- )\n o(   )o",
                "  (\\_/)  📚 zZ\n ( -_- )\n o(   )o",
                "  (\\_/)  📚 zZ\n ( -.- )\n o(   )o",
            ],

            "Stressed": [
                "  (\\_/)  📚 !!!\n ( o.O )\n o(   )o",
                "  (\\_/)  📚 !!!\n ( O.o )\n o(   )o",
                "  (\\_/)  📚 !!!\n ( o.O )\n o(   )o",
            ],

            "Motivated": [
                "  (\\_/)  📚 🔥\n ( >.< )\n o(   )o",
                "  (\\_/)  📚 🔥\n ( >o< )\n o(   )o",
                "  (\\_/)  📚 🔥\n ( >.< )\n o(   )o",
            ]
        },

        "Scholar": {

            "Happy": [
                "  (\\_/)  🎓\n ( ^.^ )\n o(   )o",
                "  (\\_/)  🎓\n ( ^o^ )\n o(   )o",
                "  (\\_/)  🎓\n ( ^.^ )\n o(   )o",
            ],

            "Neutral": [
                "  (\\_/)  🎓\n ( -.- )\n o(   )o",
                "  (\\_/)  🎓\n ( -_- )\n o(   )o",
                "  (\\_/)  🎓\n ( -.- )\n o(   )o",
            ],

            "Tired": [
                "  (\\_/)  🎓 zZ\n ( -.- )\n o(   )o",
                "  (\\_/)  🎓 zZ\n ( -_- )\n o(   )o",
                "  (\\_/)  🎓 zZ\n ( -.- )\n o(   )o",
            ],

            "Stressed": [
                "  (\\_/)  🎓 !!!\n ( o.O )\n o(   )o",
                "  (\\_/)  🎓 !!!\n ( O.o )\n o(   )o",
                "  (\\_/)  🎓 !!!\n ( o.O )\n o(   )o",
            ],

            "Motivated": [
                "  (\\_/)  🎓 🔥\n ( >.< )\n o(   )o",
                "  (\\_/)  🎓 🔥\n ( >o< )\n o(   )o",
                "  (\\_/)  🎓 🔥\n ( >.< )\n o(   )o",
            ]
        }
    }
}


def get_pet_stage(level):
    if level >= 10:
        return "Scholar"
    elif level >= 5:
        return "Teen"
    else:
        return "Baby"


def get_animation_frame(pet_theme, mood, level):

    stage = get_pet_stage(level)

    pet_data = PETS_FRAMES.get(pet_theme, {})
    stage_data = pet_data.get(stage, {})

    frames = stage_data.get(mood)

    if not frames:
        frames = stage_data.get("Neutral", [])

    if not frames:
        return "🐾 Pet is waiting..."

    key = (pet_theme, stage, mood)
    index = animation_indexes.get(key, 0)
    frame = frames[index]
    animation_indexes[key] = (index + 1) % len(frames)
    return frame


EVOLUTION_ANIMATIONS = {

    "Cat": [
        " /\\_/\\\n( o.o )\n > ^ <",
        " /\\_/\\  ✨\n( o.o )\n > ^ <",
        " /\\_/\\  🎓\n( ^.^ )\n > ^ <"
    ],

    "Dog": [
        "  /^^^\\\n / o o \\\n V\\ ^ /V",
        "  /^^^\\  ✨\n / o o \\\n V\\ ^ /V",
        "  /^^^\\  🎓\n / ^ ^ \\\n V\\ v /V"
    ],

    "Bunny": [
        "  (\\_/)\n ( o.o )\n o(   )o",
        "  (\\_/)  ✨\n ( o.o )\n o(   )o",
        "  (\\_/)  🎓\n ( ^.^ )\n o(   )o"
    ]
}


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def play_evolution_animation(pet_theme):

    frames = EVOLUTION_ANIMATIONS.get(pet_theme)

    if not frames:
        return

    for frame in frames:
        clear()
        print("╔══════════════════════════════════════╗")
        print("║         ✨ PET EVOLUTION ✨          ║")
        print("╚══════════════════════════════════════╝")
        print()
        print(frame)
        time.sleep(0.6)

    print("\nYour pet has evolved! 🐾📚")
    time.sleep(1)


def animate_pet(pet_theme, mood, level, seconds):

    start = time.time()

    while time.time() - start < seconds:

        clear()

        frame = get_animation_frame(pet_theme, mood, level)

        print("╔══════════════════════════════════════╗")
        print("║           Study in Progress          ║")
        print("╚══════════════════════════════════════╝")
        print()
        print(frame)

        time.sleep(0.6)