---
description: The linter's acting sibling. Does the additive cleanup, proposes the reductive
---

You are running `/consolidate`.

## The rule that governs everything here

**Additive changes you make. Reductive changes you propose.**

Additive: new review dates, missing cross-links, missing TL;DR lines, gap notes, tentative-marked synthesis, bi-temporal dating of facts that changed, updates to the skills index.

Reductive: merging pages, archiving, deleting, overwriting facts. These go to `wiki/open-questions.md` under "Proposals waiting for a human". Do not touch them yourself.

## Budget

At most five pages changed per run. Hit the ceiling and you stop and report. This is what prevents a runaway rewrite.

## Steps

1. Run `/lint` first and work from its findings.
2. Do the additive fixes, one commit per change.
3. Write the reductive proposals to `wiki/open-questions.md` with enough context that a human can decide without re-reading everything.
4. Report what you changed and what is waiting.

## Preserve

Numbers, names, dates and legal wording are copied exactly. Compression targets redundancy and prose, never facts. Recall over precision.
