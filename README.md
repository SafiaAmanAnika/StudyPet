# StudyPet 🐾✨

StudyPet is a CLI study companion that mixes productivity, wellbeing, and gamification.
You study, your pet grows, and your progress becomes visible through streaks, reports, and achievements.

## ✨ What Makes It Fun

- Pomodoro-based study sessions with pet animations.
- Virtual pet care loop with health, energy, coins, feeding, and evolution.
- Pet abilities based on theme (Cat, Dog, Bunny).
- Mood check-ins, burnout detection, and tired-streak penalties.
- Recreation unlocks (meditation + mini-game) after enough study effort.
- Quiz performance tracker with analytics-style views.
- Weekly report generation with productivity scoring.
- Study planner suite for profile, plan generation, progress, and recovery.
- Reflection journal + achievement badges to keep motivation high.

## 🧩 Core Features

- Authentication and persistence:
	- Register/login users.
	- Saves user state in `data/users.json`.
- Study engine:
	- Difficulty-aware rewards and health effects.
	- Pomodoro presets or custom study/break lengths.
	- Session logs saved to `data/study_log.json`.
- Pet system:
	- Shop and feeding mechanics.
	- Evolution based on study consistency/hours.
	- Theme abilities applied after sessions.
- Wellbeing system:
	- Mood logging in `data/mood_log.json`.
	- Tired streak penalties.
	- Burnout handling with daily guard.
	- Energy decrease/recovery flow.
- Analytics and reports:
	- Study heatmap-style analytics.
	- Weekly performance reports + snapshots in `data/weekly_reports.json`.
- Reflection and achievements:
	- Reflection journal entries.
	- Streak badges and periodic surprise rewards.

## 🖥️ Dashboard Options

After login, users can access:

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
0. Logout

## 📁 Project Structure

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
		auth.py
		storage.py
		ui.py
		study.py
		pet.py
		shop.py
		evolution.py
		wellbeing.py
		recreation.py
		animation.py
		quiz.py
		quiz_analytics.py
		quiz_charts.py
		quiz_config_helpers.py
		quiz_ui_input.py
		analytics.py
		weekly_report.py
		study_planner.py
		study_planner_*.py
		user_reflection.py
```

## 🚀 Quick Start

1. Make sure Python 3.10+ is installed.
2. Open the project root.
3. Run:

```bash
python3 main.py
```

No external packages are required for the core CLI experience.

## 💾 Data & Persistence

- All runtime data is JSON-based under `data/`.
- If files are missing, modules create them automatically.
- This makes local testing easy and keeps state between runs.

## 🛠️ Dev Notes

- Fast syntax check:

```bash
python3 -m compileall main.py src
```

- Study countdown speed is controlled by `DEV_MODE` in `src/study.py`.
	- `True`: treats minutes like seconds for quick testing.
	- `False`: runs real-time study durations.

## 🌟 Final Vibe

StudyPet is built to feel encouraging, playful, and personal.
Small daily wins, a growing pet companion, and visible progress loops are the heart of the project.
