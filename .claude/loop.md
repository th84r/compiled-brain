# The self-reinforcing loop

You are running the loop. The goal is to make the library cleverer, cleaner and better at answering questions over time, while the owner works. Self-paced. Pick the interval yourself, short when there is active work, long (up to an hour) when it is quiet.

## Ground rules, semi-autonomous

- **Additive improvements you make yourself.** New `review` dates on volatile facts, missing cross-links, missing TL;DR lines, gap notes, tentative-marked synthesis, updates to the skills index. Anything that only adds.
- **Reductive changes you only propose.** Merging pages, archiving, deleting, overwriting facts. Write them to `wiki/open-questions.md` under "Proposals waiting for a human". Do not touch them.
- **Never act externally.** No email, no contact with third parties, nothing that commits the owner.

## Guardrails, never skip these

1. **Judge is not author.** When you run `/eval` or assess quality, do it cold, without leaning on the reasoning a previous iteration wrote. Judge the page as it stands.
2. **Edit budget.** At most five pages changed per iteration. Hit the ceiling and you stop and summarise. This is what prevents a runaway rewrite at three in the morning.
3. **Inference expires.** Anything you derive rather than read directly from a source is marked `confidence: tentative` with a `review` date. A conclusion must never harden into a fact.
4. **One commit per change.** After each additive change run `git add -A && git commit -m "loop: what"`. That way everything can be rolled back. Deletions and merges are proposals and are not committed by you.
5. **Preserve numbers, names, dates and legal wording exactly.** Compression targets redundancy and prose, never facts. Recall over precision.

## Priority ladder, take the highest rung that has work

Each iteration, pick ONE task from the top of the ladder that has something to do. Do it, commit the additive parts, and end the iteration.

1. **New raw material.** Anything in `inbox/pending/`? Run the `/ingest` logic on one file.
2. **Stale facts.** Run `fmquery.py --stale`. Volatile facts with no `review` date? Set them (additive). Passed dates on internal facts become proposals. Web-verifiable ones (market data, law) get verified with a targeted lookup and updated with the source.
3. **Contradictions.** Find facts that conflict across the library. Are they dated as superseded, or just stacked? Additive dating you fix. A real conflict about what is true becomes a proposal.
4. **Knowledge gaps.** Run the `/gap-scan` logic on one active case. Write what the page cannot answer to `wiki/open-questions.md`. Close the web-answerable ones.
5. **Cross-links and orphans.** Run `fmquery.py --orphans`. Link orphan pages in where they belong.
6. **Synthesis.** Has an entity gained five or more new facts since last time? Write a tentative-marked `## Synthesis` section with the higher-order pattern, linked to the source facts.
7. **Capability.** Did a new procedure get used and work? Run the `/distill-skill` logic.
8. **Eval.** More than a week since the last `/eval`? Run the golden set, log the trend, open fix notes on pages that answered wrong.

## When nothing has work

If none of rungs 1 to 8 has anything to do, say so briefly, set a long interval, and continue. The loop should be cheap when the library is healthy.

## Reporting

Keep it to one line between iterations. Save the fuller summary for when you are asked, or when you have just closed something substantial.
