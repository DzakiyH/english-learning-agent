# Material Generation Rules

> How learning material must be generated. This file is the single source of
> truth for content format. Any agent/session generating material MUST follow
> it exactly. When the user refines the format, update this file first.

## Header block (per word)

Every word entry starts with a header containing:

1. **Pronunciation** — IPA transcription plus a plain-sound approximation
   (e.g. `/beər/ — sounds like "bair" (rhymes with hair, care)`).
2. **Verb forms** (if the word is a verb) — ALL forms listed:
   base → past → past participle, plus -ing form and 3rd person.
   Example: `bear → bore → borne | -ing: bearing | 3rd person: bears`

## Paragraphs

- One paragraph per DISTINCT meaning/use of the word. Paragraph count is NOT
  fixed — it grows with however many meanings the word actually has.
- Each paragraph must use the word in a DIFFERENT way (different meaning,
  grammatical pattern, or register) if such different ways exist.
  - Priority: different USAGE > different TOPIC. Two paragraphs may share a
    topic as long as each uses the word differently.
- If a word is a verb, use its various FORMS (past, participle, etc.)
  naturally inside paragraphs. Prefer fitting multiple forms into one
  paragraph; split into separate paragraphs only if combining would hurt
  comprehension.
- Include the noun sense of a word too, when it exists (e.g. bear the animal).
- After each paragraph: an italic note showing the usage pattern, register,
  common collocations, or a trap to watch for.

## Required quality bar (all paragraphs)

- Use the target word naturally, correct grammar.
- Meaning must be understandable from context alone.
- Realistic situations; vocabulary appropriate to the learner's level.
- Enough repetition of the target word to reinforce it, but no unnatural repetition.
- AVOID: unnecessarily complex sentences, excessive advanced vocabulary,
  dictionary-like sentences, repetitive structures, many unrelated hard words.

## Closing blocks (per word)

End every word entry with:

1. **Fixed expressions** — common idioms/phrases containing the word,
   each with a short meaning and example where useful.
2. **Quick recap table** — one row per form/sense with a model sentence.

## Learner feedback commands (reserved)

The learner responds per word with:
- `done` — sufficiently learned
- `practice again` — wants more exposure
- `difficult` — struggling; prioritize it
- `add <word>` — add a new discovered word to future sessions
- `more <word>` / `more` — generate additional material for that word
- `remove <word>` — stop intentionally practicing it

## End-of-Session Candidate Discovery (Phase 5)

At the end of every material generation response (after all target words are presented), the agent MUST scan the generated text and list 2–3 notable non-target candidate words that appeared naturally in the paragraphs:

Format:
```markdown
### 💡 Candidate Words Discovered in This Session
- **[word]** (IPA) — short definition (*from [target word] paragraph [N]*)
- **[word]** (IPA) — short definition (*from [target word] paragraph [N]*)
*(Reply `add <word>` to queue any of these for your next session)*
```
