EVOLUTION_LEVELS = [
    (1, "Baby 🐣"),
    (5, "Teen 📚"),
    (10, "Master Scholar 🧙‍♂️")
]


def get_pet_stage(level: int) -> str:
    stage = "Baby 🐣"

    for lvl, name in EVOLUTION_LEVELS:
        if level >= lvl:
            stage = name

    return stage

def check_pet_evolution(user_data: dict, streak_days: int):
    from src.pet import ensure_pet_defaults
    
    user_data = ensure_pet_defaults(user_data)

    level = user_data["level"]
    hours = user_data["total_study_hours"]

    new_level = level

    if hours >= 30:
        new_level = 10
    elif hours >= 10:
        new_level = 5

    if streak_days >= 7:
        new_level += 1

    evolved = new_level > level

    if evolved:
        user_data["level"] = new_level

    return user_data, evolved