# Roadmap

> Phase-by-phase development plan. Update as phases complete.
> Current status of each phase lives in `docs/STATUS.md`.

## Phase 0 — Project Definition ✅

Goals, learning loop, vocabulary states, user actions, initial behavior all
defined (see `IDEA.md`). Exit criteria met: project behavior describable
without ambiguity.

## Phase 1 — Hermes Local Prototype (in progress)

- [x] Install Hermes Agent locally
- [x] Configure an initial LLM provider (OpenRouter)
- [x] Configure API credentials securely
- [x] Verify Hermes communicates with the selected model
- [x] Validate material generation format with real trial sessions
      (format spec now in `docs/MATERIAL-RULES.md`)
- [x] Create the English-learning skill encoding the material rules
- [ ] Verify memory/persistence behavior across sessions

Exit criteria: a complete basic learning session can be performed locally.

## Phase 2 — Manual Vocabulary Prototype

Test whether the learning method is actually useful before building infrastructure.

- [ ] Manually provide a small vocabulary list
- [ ] Generate content for each word per `docs/MATERIAL-RULES.md`
- [ ] Support multiple usages/topics
- [ ] Allow user to request additional paragraphs (`more`)
- [ ] Allow user to mark words: done / practice again / difficult / add / remove
- [ ] Verify the agent remembers these decisions across sessions

Example session:
```text
Today's words: reluctant, subtle, overwhelming, emphasize, retrieve
Generate today's learning material.
reluctant → done | subtle → practice again | overwhelming → difficult | consequence → add
```

Exit criteria: the workflow feels useful enough to continue developing.

## Phase 3 — Vocabulary Database (Implemented)

Move vocabulary state from conversational memory into persistent structured storage.

- [x] Select database technology (SQLite stdlib)
- [x] Design vocabulary schema (word, status, times_practiced, last_practiced, notes)
- [x] Store vocabulary items and user learning state (`vocab.db`)
- [x] Implement CRUD operations via minimal CLI (`vocab.py`)
- [x] Pass automated verification tests (`python vocab.py test`)

Conceptual model:
```text
Vocabulary
    ├── Word metadata (definition, part_of_speech, frequency_rank, ...)
    └── User learning state (status, difficulty, history, review info)
```

Vocabulary states: NEW, PRACTICING, REVIEW, LEARNED, DIFFICULT.

Exit criteria: restarting Hermes does not lose vocabulary progress.

## Phase 4 — Automated Vocabulary Selection (Completed)

- [x] Obtain a reliable English frequency dataset (Oxford 3000 & 5000)
- [x] Import vocabulary; implement basic frequency filtering (B1, B2, C1; skipped A1/A2)
- [x] Exclude known words; prioritize difficult & requested words
- [x] Avoid recently practiced words (`last_practiced` sorting)
- [x] Generate daily vocabulary sets with manual override allowed (`vocab.py next`)

Initial priority order: requested words > difficult/review > new frequent > other eligible.

Exit criteria met: `python vocab.py next` returns prioritized, filtered vocabulary sets.

## Phase 5 — Vocabulary Discovery (Completed)

- [x] Identify candidate vocabulary in generated content (`docs/MATERIAL-RULES.md`)
- [x] Let user select words to add (`add <word>`)
- [x] Mark them user-discovered (`REQUESTED`), prioritize at top of queue, prevent duplicates

Exit criteria met: words discovered in reading (`adorned`, `tear`) automatically queued as top priority for next practice.

## Phase 6 — Improved Learning Algorithm (Completed)

- [x] Spaced repetition scheduling based on learner action & practice count
- [x] Intervals: `PRACTICING` (1d → 3d → 7d → 14d), `DIFFICULT` (immediate), `LEARNED` (30d), `REQUESTED` (immediate)
- [x] `vocab.py next` automatically filters for words due for review (`due_only`), with `--all` override available
- [x] Unit tests passing for spaced repetition logic (`python vocab.py test`)

Exit criteria met: practiced words follow review intervals; daily practice only pulls due words and new words.

## Phase 7 — Better Learning Exercises

Expand beyond passive reading gradually: fill-in-the-blank, multiple choice,
sentence creation/rewriting, explaining in English, personal sentences,
English↔Indonesian translation, context selection, short writing exercises.

## Phase 8 — Voice and Pronunciation

Speech recording → speech-to-text → comparison with intended sentence →
pronunciation feedback → track recurring problems. Postponed until the
text-based system is proven useful.

## Phase 9 — VPS Deployment (target: Maritime)

Run continuously without the user's PC powered on. Tasks: sizing, install,
persistent storage, secrets, networking, backups, scheduled tasks,
restart persistence, external access, resource/cost monitoring.

## Phase 10 — Optimization and Personalization

Level estimation, automatic difficulty estimation, personalized topics/
length/complexity, progress reports, weekly summaries, weak-word reports,
retention tracking, adaptive exercise selection, curriculum generation.
