# yandex-practicum-solver

Skill + scripts to auto-complete the Yandex Practicum «Андроид-разработчик» course (`ap-android-st`) via API: theory, quizzes, Kotlin code tasks, and the final project/review workflow.

## Contents

- `SKILL.md` — the skill: full workflow, what to ask the user, API endpoints, git rules.
- `FOR_CLASSMATES.md` — короткая инструкция для студентов: что установить и какие данные дать агенту.
- `scripts/` — full automation toolset from the reference run (paths auto-resolve via `PRACTICUM_COOKIES`):
  - `run_all.py` — mass lesson runner (checkin → quiz/action blocks → solve).
  - `ws_only.py`, `submit_tasks.py`, `submit_par.py`, `submit_batch.py`, `submit2-4.py` — WebSocket jrunner task checkers (sequential / batched / retries).
  - `solve_tasks.py` — task dispatcher reading `pending_tasks.json` + `solutions.json`.
  - `qc.py`, `qc2.py` — quiz_coding block checkers.
  - `getlogs.py` — dump jrunner LOG frames verbatim for a task.
  - `verify.py` — sweep all lessons and report unsolved.
  - `practicum_helpers.py` — cookie loading for Playwright.
- `answers/` — `solutions.json` (accepted solutions to all 17 WS tasks), `task_details.json` (task descriptions/panes), `NOTES.md` (per-task preprocessor gotchas), `inventory.json` (course map), `pending_tasks.json` (the 29 code items list).
- `docs/` — review submission checklist + Yandex.Disk/Docs upload guide.
- `requirements.txt` — Python deps.

## Setup

```bash
pip install playwright requests
playwright install chromium
export PRACTICUM_COOKIES=/path/to/practicum_cookies.txt   # Netscape cookie export
```

Never commit the cookies file (`.gitignore` already covers it).
