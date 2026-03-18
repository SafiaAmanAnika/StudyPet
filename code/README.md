# StudyPet 🐾

StudyPet is a cozy, gamified command-line study companion built with Python.
It blends planner-driven Pomodoro flow, pet progression, wellbeing tracking, and performance analytics into one daily routine.

## At A Glance

| Area | What you get |
|---|---|
| Focus | Pomodoro sessions (25/5, 50/10, custom) |
| Planning | Study Planner subjects flow into session start |
| Motivation | Coins, pet health, feeding, shop, pet evolution |
| Wellbeing | Mood logs, tired streak handling, burnout checks |
| Insights | Analytics heatmaps, quiz tracking, weekly reports |
| Experience | Animated intro, themes, animation styles |

## Daily Gameplay Loop

1. Generate or review your study plan.
2. Pick a subject and launch a focused study session.
3. Earn rewards and manage your pet.
4. Check mood, energy, and burnout signals.
5. Review progress and reflections.

## Planner → Pomodoro Integration

Study sessions can now start directly from planner output:

- Choose subject from generated plan entries.
- Optionally adopt planner difficulty.
- Optionally use planner timing for study/break.
- Session logs store topic, difficulty, study minutes, and break minutes.

This makes Study Planner and Pomodoro feel like one continuous flow instead of two separate tools.

## Feature Highlights

### Study + Focus

- Pomodoro presets and custom mode.
- Difficulty-based reward and health impact.

### Pet Progression

- Pet themes: Cat, Dog, Bunny.
- Coins and inventory loop through shop + feeding.
- Pet abilities and evolution checks based on activity patterns.

### Wellbeing + Recovery

- Mood check-ins with logs.
- Tired streak detection and burnout handling.
- Recreation triggers after workload thresholds.

### Tracking + Reporting

- Quiz performance tracker.
- Analytics dashboard and heatmap-style insights.
- Weekly report snapshots.
- Reflection and achievement flow.

### UI/UX

- Animated intro splash.
- Theme Studio (color themes + animation style).
- Universal commands at prompts:
  - `:back` / `:b`
  - `:exit` / `:q`

## Dashboard Menu (Post Login)

1. Start Study Session
2. Feed Pet
3. Pet Shop
4. View Pet Status
5. View User Status
6. Mood Check-in
7. Study Performance Tracker
8. Analytics
9. Weekly Report
10. Study Planner
11. Reflection Journal
12. Settings
0. Logout

## Settings Studio

- Change name, email, password.
- Change pet and goals.
- Theme Studio:
  - Pastel Pink 🎀
  - Ocean Breeze 🌊
  - Sunset Glow 🌇
  - animation style controls
- Account deletion with password confirmation.

## Quick Start

### Requirements

- Python 3.10+

Run from this folder (`code/`):

```bash
python3 main.py
```

## Canonical Data Layout

All runtime data is centralized in `data/`:

- `data/users.json`
- `data/study_log.json`
- `data/study_log.json.backup`
- `data/mood_log.json`
- `data/quiz_marks.json`
- `data/study_planner.json`
- `data/weekly_reports.json`

## Architecture (Current)

```text
code/
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
    __init__.py
    interface/
      __init__.py
      ui.py
    core/
      __init__.py
      analytics.py
      shop.py
    pet/
      __init__.py

        study_planner_profile.py
        study_planner_progress.py
        study_planner_recovery.py
        study_planner_ui_input.py
    system/
      __init__.py
      auth.py
      navigation.py
      storage.py
    wellbeing/
      __init__.py
      wellbeing.py
      recreation.py
```

## Developer Notes

Compile-check quickly:

```bash
python3 -m compileall main.py src
```

Timer testing shortcut:

- Edit `DEV_MODE` in `src/study/study.py`.
- `True` treats minutes as seconds for fast iteration.
- `False` uses real session durations.

## Closing

StudyPet is built to make consistency feel rewarding: focused sessions, visible growth, and a companion that evolves with your effort. ✨
