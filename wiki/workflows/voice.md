---
title: Voice, how we write and how machine prose is spotted
type: workflow
status: active
confidence: verified
hat: bridging
created: 2026-01-01
updated: 2026-01-01
tags: [writing, style, quality]
---

TL;DR. Everything written in your name must sound like you and must not read as machine output. This page is the rule, `.claude/scripts/voice.py` is the enforcement. Replace the contents with your own calibration.

## Why this exists at all

Two reasons, and the second is the one people miss.

The obvious one is quality. Machine prose is recognisable and it reads as unconsidered.

The less obvious one is credibility. If a document that leaves your organisation reads as generated, anyone with a reason to doubt it will attack how it was made rather than what it says. That is a cheap attack and it works, because it moves the argument away from your evidence. Whatever your policy on using models, the writing should not be the thing that raises the question.

## Mechanics

No em dashes. No sentence opening with a conjunction. Colons inside sentences are an opt-in house rule, see the calibration note below. Write accented and non-ASCII characters directly rather than transliterating.

## The patterns that give machine prose away

1. **The antithesis.** "It is not X, it is Y", "not just X, but Y", "X, not Y". The most reliable tell there is. State the positive claim and let the contrast follow from the substance.
2. **Setup and punchline.** A long sentence followed by a short stab that restates it. Real writing does not land a point per paragraph.
3. **The aphorism.** The quotable closing line. One per document can be earned. Several is a generator performing.
4. **The rule of three.** Three parallel items of matching rhythm, where the third is often a synonym of the second. Write two, or four uneven ones.
5. **The didactic opening.** "Note that", "It is worth noting", "Keep in mind". You are writing to colleagues rather than teaching them.
6. **Announcing instead of saying.** "Here are three things", "Let me walk you through". Say the thing.
7. **Overexplicit connectors.** "Moreover", "Furthermore", "Ultimately", "That said". Real prose skips a step and trusts the reader.
8. **Glossy filler.** "Fascinating", "in today's fast-paced", "navigating the complexities", "a rich tapestry", "delve into". Praise is concrete or absent.
9. **Metaphor as load-bearing architecture.** Leverage, framework, flywheel, north star. One metaphor at a time, never a system of them.
10. **Flawless evenness.** Identical paragraph lengths, identical sentence lengths, no loose ends. The absence of noise is itself a tell. Real writing has hedges, an aside, and one knotty sentence.
11. **The fronted clause.** "What makes this important is", "The thing we agreed on is". Put the subject first.

## How you actually sound

Replace this section with your own calibration, drawn from your own sent mail. The traits worth naming are the ones that must be present for a text to be yours.

Useful things to capture: how you open (a reaction, a question, mid-thought), your hedges and particles, whether you use parenthetical asides, whether you ask the reader questions inside the text, and how you end.

## Calibrating the checker

Two things the script gets wrong often enough to say out loud.

**A factual enumeration is not a rule of three.** "Cases, projects and people" names three folders. The rule targets three parallel items chosen for rhythm, where the third restates the second. Judge these by hand.

**This page flags itself.** It quotes the banned phrases as examples, so the checker matches them. Any page that documents the rules will do the same.

**A bold lead-in is not a punchline.** A short sentence opening a paragraph is a sub-heading. The script skips paragraph-initial sentences, and it still misses some in .docx. Judge those by hand too.

**The colon rule is opt-in.** A colon introducing a list is ordinary English, so `voice.py` enforces it only under `--strict`. Turn it on if you hold the stricter view, which is that a colon lets a sentence avoid deciding its own shape.

## Banned phrases

Add your own below. A bullet wrapped in slashes is read as a regular expression, anything else as a literal phrase. `voice.py` picks these up automatically.

- /\bsynerg\w*/
- delve into

## The check

Before anything ships, three passes. Read it aloud, and rewrite whatever cannot be said. Run `python3 .claude/scripts/voice.py <file>`. Then ask whether you would have bothered to write that sentence, and if not, cut it.

One pattern can be coincidence. Three in the same text is a verdict.
