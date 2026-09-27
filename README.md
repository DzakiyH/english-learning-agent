# English Learning Agent

A lightweight, personalized English vocabulary acquisition system designed to build retention and fluency through contextual reading.

Instead of rote flashcards or generic chat, this project uses an AI agent to generate reading passages demonstrating words across their distinct real-world meanings, paired with a deterministic spaced repetition engine.

---

## Core Learning Loop

1. **Select**: The engine serves candidate words prioritized by need:  
   `REQUESTED` > `DIFFICULT` > `REVIEW` > `PRACTICING` > `NEW`
2. **Generate**: The AI generates study material following strict rules in `docs/MATERIAL-RULES.md` (pronunciation IPA, verb forms, distinct-usage paragraphs, pattern notes, fixed expressions, and quick-recap tables).
3. **Study & Evaluate**: You review the material and label each word:
   - `done`: sufficiently learned (archived to 30-day maintenance check)
   - `practice again`: re-queued with spaced repetition (1d → 3d → 7d → 14d)
   - `difficult`: prioritized for immediate next review
   - `add <word>`: spot an unfamiliar word in the text and queue it as top priority
   - `remove <word>`: permanently stop practicing
4. **Discover**: At the end of every session, the agent suggests 2–3 notable candidate words found in the generated passages for quick queuing.

---

## Quick Reference

Zero third-party dependencies. Runs entirely on Python 3 standard library (`sqlite3`, `datetime`).

```bash
# Pull the next batch of due words
python vocab.py next --limit 5

# Update learner state after a session
python vocab.py update reluctant done
python vocab.py update subtle "practice again"
python vocab.py update overwhelming difficult

# Add newly discovered words (auto-queued as top priority)
python vocab.py add adorned tear

# Check database stats and scheduled review dates
python vocab.py stats
python vocab.py list
```

---

## Dataset

Pre-seeded with **3,479 curated words** from the **Oxford 3000 & 5000** corpus:
- **B1**: Core intermediate
- **B2**: Upper-intermediate sweet spot
- **C1**: Advanced vocabulary
- *(Elementary A1 and A2 words are excluded)*

To re-seed or update the vocabulary dataset:
```bash
python seed_oxford.py
```

---

## Project Structure

- `vocab.py`: SQLite-backed CLI & spaced repetition storage engine.
- `seed_oxford.py`: One-time parser and seeder for Oxford 3000/5000 dataset.
- `docs/MATERIAL-RULES.md`: Format rules for generated learning material.
- `docs/ROADMAP.md`: Project development roadmap and phase status.
- `docs/STATUS.md`: Living snapshot of current project progress.
- `IDEA.md`: Vision, principles, and technology strategy.
