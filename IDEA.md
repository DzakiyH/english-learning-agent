# English Learning AI Agent — Vision & Principles

> **Primary Goal:** Build a personal English vocabulary-learning agent that
> progressively adapts to the user's vocabulary, learning difficulties, and preferences.
>
> This document covers WHAT and WHY. For HOW/WHEN see `docs/ROADMAP.md`,
> for content format rules see `docs/MATERIAL-RULES.md`, for current state
> see `docs/STATUS.md`.

---

# 1. Vision

A personal AI-powered English learning agent whose primary purpose is to help
the user **acquire, understand, remember, and eventually use English vocabulary naturally**.

Not a generic chatbot or tutor, but:

> **Personalized vocabulary acquisition system with an AI agent as its interface,
> learning assistant, and content generator.**

The system progressively learns which words the user: already knows, is
learning, struggles with, wants reviewed, discovers naturally while studying,
and should encounter again in future exercises.

The end goal is NOT tied to any particular app form (desktop/web/etc). It is
whatever makes English learning easiest and best for the user — possibly a
pure agent-driven engine with no separate app at all.

# 2. Core Learning Philosophy

## 2.1 Start Small

First version = one simple loop:

```text
Select vocabulary → Generate learning material → User studies
→ User evaluates → Update vocabulary state → Select next session's vocabulary
```

Every future feature is added only after the basic loop is tested and useful.

## 2.2 The User Remains in Control

Explicit user commands the system must respect:
"I know this word" / "I still need practice" / "I don't understand" /
"use this again tomorrow" / "add this word" / "more examples" / "stop practicing this word".

## 2.3 Prioritize Natural English

Generated material must have natural usage, correct grammar, appropriate
difficulty, real-world contexts, and must NOT pile on unrelated advanced words.

## 2.4 Personal Vocabulary Over Generic Vocabulary

Word importance comes from English frequency AND personal history: known or
not, encounter count, difficulty marks, recency of practice, explicit requests,
natural appearances in material, past failures.

# 3. Initial Scope

Focus: **vocabulary acquisition through generated reading material.**

Supported in v1:
- selecting a small number of target words,
- generating multiple paragraphs per word covering distinct USAGES
  (see `docs/MATERIAL-RULES.md` for the exact format),
- marking words done / practice-again / difficult / remove,
- discovering & adding new words from generated material,
- vocabulary state influencing the next session.

NOT needed initially: speech recognition, pronunciation scoring, advanced
spaced repetition, dashboards, mobile/web apps, large databases, analytics,
automatic curriculum, multi-user support.

Single-user personal project.

# 4. High-Level Architecture (eventual)

```text
User Interface (Telegram / Web / CLI / Hermes chat ...)
        ↓
Hermes Agent (conversation, memory, skills, tools)
        ↓                          ↓
LLM Provider            Learning Engine
(OpenRouter/OpenAI/     (vocabulary state, progress,
 swappable)              selection, history)
                                 ↓
                             Database
```

This is eventual architecture; the first prototype is far simpler.
Key split (never violate): **agent/LLM handles conversation & generation;
the Learning Engine owns deterministic logic, records, selection,
persistence. Do not put critical persistent learning logic inside prompts.**

# 5. Technology Strategy

- **Agent framework:** Hermes Agent. Don't rebuild unless proven unsuitable.
- **LLM provider:** usage-based billing preferred (OpenRouter/OpenAI/etc).
  Never permanently commit to one provider; keep models swappable per task
  (cheap model for routine paragraphs, capable model for hard explanations).
- **Cost:** first-class concern from day one. Spending must be measurable and
  controllable. Eventually answer "what did today/month cost me?".
- **Hosting:** local PC first; VPS (Maritime) only after the prototype works.
  Target: inexpensive, persistent storage, scheduled tasks, secure keys.

# 6. Vocabulary System

Central data. Each item eventually carries word metadata (definition, part of
speech, frequency rank/source) plus user learning state (status, difficulty,
timestamps, times seen/practiced, notes).

Vocabulary states: `NEW`, `PRACTICING`, `REVIEW`, `LEARNED`, `DIFFICULT`.
User actions: `DONE`, `PRACTICE AGAIN`, `DIFFICULT`, `ADD`, `MORE`, `REMOVE`.

- A LEARNED word does not disappear — it may appear naturally in content.
  Distinguish *intentionally practicing* vs *naturally encountering*.
- Preferred source: frequency-based list (research & document source before
  adopting). Alphabetical dictionary order is optional, never primary.
- Selection starts simple and deterministic (requested > difficult/review >
  new frequent > other); complex scoring only later, driven by observed data.
- Spaced repetition: not in v1; leave architectural room.

# 7. Learning Memory vs Conversational Memory

Conversational memory = continuing the current interaction.
Learning memory = persistent structured facts (status, counts, dates) that
must survive restarts in structured storage — never only in prompts/chat.

# 8. Development Rules

1. Start with the smallest useful implementation.
2. No infrastructure before validating the learning experience.
3. Simple deterministic logic over unnecessary AI complexity.
4. Keep LLM providers interchangeable.
5. Keep learning data separate from conversational memory.
6. Don't blindly trust LLM vocabulary recommendations.
7. Use reliable external vocabulary/frequency sources.
8. Measure LLM cost from the beginning.
9. No features just because they're technically interesting.
10. Every major feature must contribute to actual learning.
11. Test personally before expanding.
12. Single-user until there's a reason not to be.
13. Always use the Ponytail skill (simplest working solution, YAGNI, standard library first).

# 9. Success Criteria

Not "Hermes runs" or "paragraphs get generated". Success is:

> **Does using the system measurably help the user learn and retain English vocabulary?**

Evaluate: recognition, understanding across contexts, recall after days,
natural use, enjoyment, adaptation to weaknesses, skipping already-known words.

# 10. Guiding Principle

> Start as a simple AI-powered vocabulary exercise and gradually turn it into
> a personalized learning system based on actual usage.

Build small. Use it. Observe. Improve. The ultimate goal is a system that
**actually makes the user's English better.**
