# Project Rules

## Core Guidelines

1. **Always Use Ponytail Skill**:
   - Always activate and adhere to the ponytail skill (default: full) for every task in this project.
   - Channel the lazy senior developer: simplest, shortest, most minimal solution that actually works.
   - YAGNI: No unrequested abstractions, no speculative scaffolding, standard library/native features first.
   - Shortest working diff wins.

2. **English Learning Standards**:
   - Follow docs/MATERIAL-RULES.md strictly when generating learning materials.
   - Always suggest 2–3 candidate words discovered in the reading material at the end of every generation session (Phase 5).
   - Follow the phase roadmap in docs/ROADMAP.md and keep docs/STATUS.md updated.

3. **Vocabulary Storage Commands**:
   - Add words: `python vocab.py add <word> [<word>...]`
   - Next batch: `python vocab.py next [--limit 5]`
   - Update word: `python vocab.py update <word> <done | "practice again" | difficult | review | remove>`
   - Check status: `python vocab.py list` / `python vocab.py stats`

