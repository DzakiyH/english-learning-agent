# Project Status

> Living snapshot of where the project is. Update at the end of every work session.
> Last updated: 2026-09-27

## Current Phase

Phases 0–6 completed. Vocabulary engine fully functional with persistent storage, Oxford 3000/5000 dataset, in-session candidate discovery, and spaced repetition review scheduling.

## What Works (validated by real trial sessions)

- Material generation format is CONFIRMED GOOD by the user (3 trial rounds). Rules locked in `docs/MATERIAL-RULES.md`.
- Persistent vocabulary storage (`vocab.py` + SQLite `vocab.db`):
  - Zero external dependencies (Python stdlib `sqlite3`, `datetime`).
  - Priority queue: `REQUESTED` > `DIFFICULT` > `REVIEW` > `PRACTICING` > `NEW`.
  - Spaced repetition algorithm (Phase 6): Leitner/SM-2 intervals (`PRACTICING`: 1d → 3d → 7d → 14d; `DIFFICULT`: immediate; `LEARNED`: 30d; `REQUESTED`: immediate).
  - All automated tests passing (`python vocab.py test`).
- Seeded Oxford 3000 & 5000 dataset (Phase 4):
  - 3,479 unique words (B1, B2, C1).
- In-session candidate discovery (Phase 5):
  - End-of-session candidate words extracted from generated text.
  - Adding a word (`add <word>`) automatically queues it as `REQUESTED` with top priority for the next session.
- Telegram Bot interface (`bot.py`):
  - Powered by Google Gemini (`gemini-flash-lite`).
  - Supports natural language intent parsing (evaluations, study requests, adding words) and slash commands (`/today`, `/stats`, `/list`, `/add`).
  - Safe multi-message chunking for mobile reading.
  - Optional `ALLOWED_USER_ID` security gate.

## User Preferences Learned

- End goal is NOT a desktop app — whatever makes English learning easiest/best;
  possibly pure agent-driven engine. Architecture stays flexible.
- Paragraphs: multiple per word, driven by distinct usages, not a fixed count.
- Usage variation across paragraphs takes priority over topic variation.
- Wants pronunciation guidance (learning IPA gradually).
- Wants pattern notes, fixed expressions, and quick-recap tables always included.
- Oxford 3000/5000 chosen as the core vocabulary source (B1–C1).
- Google Gemini via Google AI Studio chosen as primary LLM.

## Next Step

Deploy `bot.py` to Maritime using GitHub repo connection.
