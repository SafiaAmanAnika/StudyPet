# StudyPet 🐾

StudyPet is a gamified command-line study companion built with Python.
It blends focused study sessions, virtual pet care, wellbeing tracking, and progress analytics into one daily routine.

## Why StudyPet

StudyPet is designed around a simple loop:

1. Study in Pomodoro-style sessions.
2. Earn coins and maintain your pet's health/energy.
3. Track mood, burnout risk, and consistency.
4. Reflect on progress and improve next-day planning.

The result is a CLI app that feels playful while still being useful for real study habits.

## Feature Highlights

- Study sessions with difficulty-based rewards and health impact.
- Virtual pet system with feeding, shop items, and pet evolution.
- Pet abilities (Cat, Dog, Bunny) that modify post-session outcomes.
- Wellbeing check-ins, tired-streak penalties, burnout handling, and energy recovery.
- Recreation unlocks (meditation and mini-game) after sustained effort.
- Quiz performance tracking and analytics views.
- Weekly report generation and stored snapshots.
- Study planner modules for profile, plan, progress, and recovery.
- Reflection journal with achievement tracking.
- Theme Studio with runtime UI themes.
- Global navigation shortcuts available across prompts.

## Dashboard Menu

After login, the dashboard includes:

1. Start Study Session
2. Feed Pet
3. Pet Shop
4. View Pet Status
5. View User Status
6. Mood Check-in
7. Study Performance Tracker (Quiz)
8. Analytics
9. Weekly Report
10. Study Planner
11. Reflection Journal
12. Theme Studio
0. Logout

## Theme Studio 🎨

Open from dashboard option `12`.

Available profiles:
- `Pastel Pink 🎀`
- `Ocean Breeze 🌊`
- `Sunset Glow 🌇`

Theme choice is stored per user as `ui_theme` in `data/users.json`.

## Universal Commands

You can use these from most prompts:

- `:back` or `:b` to go back to the previous/main flow.
- `:exit` or `:q` to close the app safely.

## Quick Start

Requirements:
- Python 3.10+

Run:

```bash
python3 main.py
```

No external dependency install is required for core functionality.

## Data Storage

StudyPet uses JSON files in `data/`:

- `data/users.json`: account data, pet stats, streaks, theme, and profile fields.
- `data/study_log.json`: per-session logs (topic, duration, rewards, mood).
- `data/mood_log.json`: mood check-in history.
- `data/quiz_marks.json`: quiz scores/attempt history.
- `data/study_planner.json`: planner profile, goals, and progress.
- `data/weekly_reports.json`: generated weekly snapshots.

## Project Layout

```text
StudyPet/
  main.py
  README.md
  data/
    users.json
    study_log.json
    mood_log.json
    quiz_marks.json
    study_planner.json
    weekly_reports.json
  src/
    _init_.py
    analytics.py
    animation.py
    auth.py
    evolution.py
    navigation.py
    pet.py
    quiz.py
    quiz_analytics.py
    quiz_charts.py
    quiz_config_helpers.py
    quiz_ui_input.py
    recreation.py
    reflection.py
    shop.py
    storage.py
    study.py
    study_planner.py
    study_planner_config_helpers.py
    study_planner_plan.py
    study_planner_profile.py
    study_planner_progress.py
    study_planner_recovery.py
    study_planner_ui_input.py
    ui.py
    user_reflection.py
    weekly_report.py
    wellbeing.py
```

## Developer Notes

Quick syntax check:

```bash
python3 -m compileall main.py src
```

Fast testing mode for timers:
- Toggle `DEV_MODE` in `src/study.py`.
- `True` treats minutes as seconds for rapid testing.
- `False` uses real session durations.

## Closing Note

StudyPet is built to make consistency feel rewarding.
Small daily sessions, visible progress, and a growing pet companion are the core experience. ✨
