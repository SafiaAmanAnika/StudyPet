<div align="center">

<pre>
███████╗████████╗██╗   ██╗██████╗ ██╗   ██╗██████╗ ███████╗████████╗ 
██╔════╝╚══██╔══╝██║   ██║██╔══██╗╚██╗ ██╔╝██╔══██╗██╔════╝╚══██╔══╝ 
███████╗   ██║   ██║   ██║██║  ██║ ╚████╔╝ ██████╔╝█████╗     ██║    
╚════██║   ██║   ██║   ██║██║  ██║  ╚██╔╝  ██╔═══╝ ██╔══╝     ██║    
███████║   ██║   ╚██████╔╝██████╔╝   ██║   ██║     ███████╗   ██║    
╚══════╝   ╚═╝    ╚═════╝ ╚═════╝    ╚═╝   ╚═╝     ╚══════╝   ╚═╝    
</pre>

# STUDYPET

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/Type-CLI%20Application-FFA6CA?style=flat-square)](#)
[![Platform](https://img.shields.io/badge/Platform-Cross--Platform-FF9913?style=flat-square)](#)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)](#)

<br>

<i>✨ Meet StudyPet, a cozy Python-based command-line companion designed to upgrade your study routine. Built with Python, it seamlessly blends a Pomodoro planner, pet progression, wellbeing tracking, and performance analytics into one habit-building tool. ✨</i>

<br>

<a href="#installation">⚙️ Installation</a>  🔷
<a href="#system_workflow">🔁 System Workflow</a>  🔷
<a href="#core_features">✨ Core Features</a>  🔷
<a href="#architecture">🏗️ Architecture</a>  🔷
<a href="#breakdown">📚 Module & Storage Breakdown</a>

</div>

---

<a name="installation"></a>
## ⚙️ Installation

### Prerequisites

| Requirement | Version | Link |
|--------------|---------|------|
| Python | 3.10 or higher | [Download](https://www.python.org/downloads/) |

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/zenken24/StudyPet.git
cd StudyPet/code

# 2. Run the app
python3 main.py
```

> All runtime data is created automatically under `data/` on first use — no separate setup step or database is required.

<details>
<summary><b>Developer mode</b></summary>

<br>

### Compile Check

Quickly verify the whole codebase compiles without running it:

```bash
python3 -m compileall main.py src
```

### Timer Testing Shortcut

For fast iteration on Pomodoro sessions during development:

- Edit `DEV_MODE` in `src/study/study.py`.
- `True` — treats minutes as seconds, so sessions complete almost instantly.
- `False` — uses real session durations (default for normal use).

<br>

</details>

---

<a name="system_workflow"></a>
## 🔁 System Workflow

```
1. Register or log in to StudyPet via secure, masked password input
2. Generate or review your study plan
3. Pick a subject and start a focused study session
4. Earn coins and feed your pet to make it happy
5. Check mood, energy, and burnout signals
6. Review progress and make reflections
```

---
 
<a name="core_features"></a>
## ✨ Core Features
 
<details>
<summary><b>Study + Focus</b> — Pomodoro sessions tied to planned subjects</summary>

<br>

- Pomodoro presets (25/5, 50/10) plus a fully custom timing mode.
- Difficulty-based reward and pet-health impact — harder sessions earn more coins.
- Start a quick standalone session on the fly, or seed one directly from your pre-scheduled study planner.
- Every completed session is logged with topic, difficulty, and duration for analytics and weekly reporting.

<br>

</details>

<details>
<summary><b>Study Planner → Pomodoro Integration</b> — planner and timer working as one flow</summary>

<br>

- Choose a subject straight from the generated plan.
- Optionally adopt the planner's suggested difficulty.
- Optionally reuse the planner's timing for study and break length.
- Session logs capture topic, difficulty, study minutes, and break minutes for later analytics.

<br>

</details>

<details>
<summary><b>Pet Progression</b> — coins, feeding, shop, evolution</summary>
  
<br>

- Choice of pet theme: **Cat, Dog, or Bunny**.
- Coins are earned through study sessions and spent through the **Pet Shop**, looping back into feeding and inventory.
- Pet health reacts to study consistency and difficulty.
- Pet abilities unlock and the pet **evolves** based on sustained activity patterns rather than a single action.
  
<br>

</details>

<details>
<summary><b>Wellbeing + Recovery</b> — mood, burnout, and recreation</summary>

<br>

- Mood check-ins logged over time, separate from the study log.
- **Tired-streak detection** flags when a student has been overworking.
- Burnout handling steps in once workload thresholds are crossed.
- Recreation prompts are triggered automatically after sustained heavy study load.

<br>

</details>
<details>
<summary><b>Tracking + Reporting</b> — quizzes, analytics, weekly reports</summary>

<br>

- Quiz performance tracker with goals and trend tracking.
- Analytics dashboard with heatmap-style insight into study patterns.
- **Weekly report** snapshots summarizing the week's study activity.
- Reflection journal for end-of-session or end-of-day notes, feeding into an achievement flow.

<br>

</details>

<details>
<summary><b>UI / UX</b> — themes, animation, and universal commands</summary>

<br>

- Animated intro splash on launch.
- **Theme Studio** — switchable color themes and animation styles.
- Universal commands available at any prompt:
  - `:back` / `:b` — step back without losing progress
  - `:exit` / `:q` — exit cleanly from anywhere

<br>

</details>
<details>
<summary><b>Settings Studio</b> — account management and presentation controls</summary>

<br>

- Change name, email, or password.
- Change pet (theme) and study goals.
- **Theme Studio** — Pastel Pink 🎀, Ocean Breeze 🌊, Sunset Glow 🌇, plus animation style controls.
- Account deletion, gated behind password confirmation.

<br>

</details>

---

<a name="architecture"></a>
## 🏗️ Architecture

StudyPet organizes its logic by **domain** rather than by technical layer — study, pet, wellbeing, and system concerns each live in their own package, with shared low-level helpers kept in `custom/`. This keeps the planner, Pomodoro timer, pet logic, and analytics independent of one another while still able to share data through `storage.py`.

<pre>
  
┌─────────────────────────────────────────────────────────┐
│                 Interface (CLI Layer)                   │
│               src/interface/ui.py · menus               │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────┐
│                     Domain Modules                       │
│   study/     -> Sessions, Planners, Quizzes & Reports    │
│   pet/       -> Engine, Animation, and Evolution         │
│   wellbeing/ -> Mood analysis & Overwork constraints     │
│   core/      -> Analytics matrix, Shop & Wallets         │
└───────────────────────────┬──────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────┐
│                 System Services Layer                     │
│         auth.py · navigation.py · storage.py              │
└───────────────────────────┬───────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────┐
│                    Data Layer (JSON)                      │
│      Flat-file databases auto-synchronized on write       │
└───────────────────────────────────────────────────────────┘

</pre>

<details>
<summary><b>View full project structure</b></summary>

<br>

```
code/
├── .gitignore
├── main.py
├── data/                          # created at runtime
│   ├── users.json
│   ├── study_log.json
│   ├── study_log.json.backup
│   ├── mood_log.json
│   ├── quiz_marks.json
│   ├── study_planner.json
│   └── weekly_reports.json
└── src/
    ├── __init__.py
    ├── core/
    │   ├── analytics.py
    │   ├── shop.py
    │   └── wallet.py
    ├── custom/
    │   ├── custom_hash.py
    │   ├── custom_input.py
    │   ├── custom_random.py
    │   ├── custom_text.py
    │   └── custom_validation.py
    ├── interface/
    │   └── ui.py
    ├── pet/
    │   ├── animation.py
    │   ├── evolution.py
    │   └── pet.py
    ├── study/
    │   ├── reflection.py
    │   ├── study.py
    │   ├── user_reflection.py
    │   ├── weekly_report.py
    │   ├── quiz/
    │   │   ├── quiz.py
    │   │   ├── quiz_analytics.py
    │   │   ├── quiz_charts.py
    │   │   ├── quiz_config_helpers.py
    │   │   ├── quiz_dashboard.py
    │   │   ├── quiz_file_io.py
    │   │   ├── quiz_goal.py
    │   │   ├── quiz_goal_helpers.py
    │   │   ├── quiz_syllabus.py
    │   │   ├── quiz_text_helpers.py
    │   │   ├── quiz_trend.py
    │   │   ├── quiz_ui_boxes.py
    │   │   ├── quiz_ui_input.py
    │   │   └── quiz_ui_marks.py
    │   └── study_planner/
    │       ├── study_planner.py
    │       ├── study_planner_config_helpers.py
    │       ├── study_planner_file_io.py
    │       ├── study_planner_plan.py
    │       ├── study_planner_profile.py
    │       ├── study_planner_progress.py
    │       ├── study_planner_recovery.py
    │       ├── study_planner_text_helpers.py
    │       ├── study_planner_ui_boxes.py
    │       ├── study_planner_ui_input.py
    │       └── study_planner_ui_subjects.py
    ├── system/
    │   ├── auth.py
    │   ├── navigation.py
    │   └── storage.py
    └── wellbeing/
        ├── wellbeing.py
        └── recreation.py
```

</details>

---

<a name="breakdown"></a>
## 📚 Module & Storage Breakdown

StudyPet is built almost entirely on the Python standard library, with a set of hand-rolled utility modules covering input handling, hashing, randomness, and text formatting rather than pulling in third-party dependencies.


<details>
<summary><b>Standard Library Usage</b></summary>
<br>

| API | Where it is used |
|-----|-------------------|
| `json` | All persistence — users, study logs, mood logs, quiz marks, planner data, weekly reports |
| `time` / `datetime` | Pomodoro timers, demo-mode timing, weekly report windows |
| `random` (via `custom_random.py`) | Random subject/task assignment in the Study Planner |
| `os` / `sys` | Terminal control and file path handling |

<br>
</details>

<details>
<summary><b>System Services (<code>src/system/</code>)</b></summary>
<br>

| Module | What it does |
|--------|---------------|
| `auth.py` | Account creation, login, and credential verification. |
| `navigation.py` | Menu routing and the universal `:back` / `:exit` command handling. |
| `storage.py` | Reads and writes the JSON data files under `data/`. |

<br>
</details>

<details>
<summary><b>Custom Utilities (<code>src/custom/</code>)</b></summary>
<br>

| Module | What it does |
|--------|---------------|
| `custom_hash.py` | Hashing helper used for credential storage, keeping plain-text passwords off disk. |
| `custom_input.py` | Wraps and validates raw terminal input across menus and forms. |
| `custom_random.py` | Custom randomization logic, including the random task/subject assignment used by the planner. |
| `custom_text.py` | Text formatting and rendering helpers shared across CLI screens. |
| `custom_validation.py` | Centralized input validation rules (emails, passwords, numeric ranges, etc.). |

<br>
</details>

<details>
<summary><b>Core Services (<code>src/core/</code>)</b></summary>
<br>

| Module | What it does |
|--------|---------------|
| `analytics.py` | Builds the analytics dashboard and heatmap-style study insights. |
| `shop.py` | Drives the Pet Shop — browsing, purchasing, and inventory effects. |
| `wallet.py` | Tracks coin balance, earning, and spending across the system. |

<br>
</details>

<details>
<summary><b>Data Storage (<code>data/</code>)</b></summary>
<br>

| File | Contents |
|------|----------|
| `users.json` | Account records — password(hashed), profile info, pet choice |
| `study_log.json` | Full Pomodoro session history — topic, difficulty, study/break minutes, timestamps |
| `mood_log.json` | Mood check-in entries over time |
| `quiz_marks.json` | Quiz performance records and goals |
| `study_planner.json` | Generated study plans, subjects, and planner progress |
| `weekly_reports.json` | Snapshot summaries generated each week from the study log |

<br>
</details>

---

<div align="center">

<br>

<b><a href="https://github.com/zenken24/StudyPet">✨ GitHub Repository — github.com/zenken24/StudyPet ✨</a></b>

<br>

</div>
