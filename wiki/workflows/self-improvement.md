---
title: The self-reinforcing loop
type: workflow
status: active
confidence: verified
hat: bridging
created: 2026-01-01
updated: 2026-01-01
tags: [loop, automation, quality]
related: ["[[design.md]]", "[[skills-index.md]]"]
---

TL;DR. The loop runs the operations down a priority ladder while you work. Additive changes it makes, reductive changes it proposes. Driver in `.claude/loop.md`.

## What it is for

A library decays unless something maintains it. The loop does the maintenance nobody does by hand.

## The ladder

Each iteration takes the highest rung that has work, does one task, commits, and stops.

1. New raw material in the inbox
2. Stale facts (`--stale`)
3. Contradictions
4. Knowledge gaps on one active case
5. Cross-links and orphans (`--orphans`)
6. Synthesis where an entity has gained five or more facts
7. Capability, distil a procedure that worked
8. Eval against the golden set

## The five guardrails

**Judge is not author.** Quality assessment is done cold, without leaning on the reasoning a previous iteration wrote. A model grading its own earlier work grades generously.

**Five pages per iteration.** A loop that can change fifty pages in one run can quietly corrupt the library while you sleep.

**Inference expires.** Everything derived is `tentative` with a `review` date.

**One commit per change.** Git is the undo button, and it only works if the commits are granular.

**Numbers, names, dates and legal wording are copied exactly.** Compression targets redundancy and prose, never facts. Recall over precision. This is the guardrail that protects the content while the others protect the structure.

## When it goes wrong

The failure mode to watch for is a loop that is busy rather than useful: adding cross-links nobody needed, writing synthesis sections on pages with nothing to synthesise. If every iteration reports work but the library is not getting better, the ladder is being climbed too eagerly. The correct behaviour when nothing has real work is to say so and go quiet.
