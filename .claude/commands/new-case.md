---
description: Open a new case with correct structure from the start
---

You are running `/new-case`.

## 1. Establish the basics

Title, which hat, who else is involved, what matters about it, and the deadline if there is one. Ask for whatever is missing rather than guessing, because the frontmatter written now will drive the dashboard for the life of the case.

## 2. Check it does not already exist

Search `wiki/cases/` and the archive. A revived case is better than a duplicate.

## 3. Create the structure

`wiki/cases/<short-name>/overview.md` with full frontmatter, a TL;DR line, and these sections:

```
## Situation            what this is, in a paragraph
## Who is involved      each person and what they need, with sources
## What matters         figures, consequences, what changes with the outcome
## Chronology           dated, append-only
## Next steps           what happens, who does it, by when
## Open questions       what we do not know yet
## Sources
```

These are the defaults. `/onboard` replaces them with the sections the owner actually needs, in their words. If that has been run, use what it wrote here rather than the list above.

Sub-documents (chronology, preparation, analysis) go in the same folder and do not need full frontmatter.

## 4. Wire it in

Add it to `wiki/index.md` and to the relevant `wiki/hats/` router. Cross-link from any related case. Add one entry to `wiki/log.md`, headed `## YYYY-MM-DD new-case | title (initials)`, that names the new page and every page you linked it from, otherwise it shows up as out of balance in `fmquery.py --balance`. Run the dashboard.

## 5. Run a gap scan

A new case is mostly gaps. Naming them on day one is cheaper than discovering them the day before a meeting.
