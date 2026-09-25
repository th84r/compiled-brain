---
description: Open a new case with correct structure from the start
---

You are running `/new-case`.

## 1. Establish the basics

Title, which hat, who else is involved, what matters about it, and the deadline if there is one. Ask for whatever is missing rather than guessing, because the frontmatter written now will drive the dashboard for the life of the case.

## 2. Check it does not already exist

Search `wiki/cases/` and the archive. A revived case is better than a duplicate.

## 3. Create the structure

`wiki/cases/<short-name>/overview.md` with full frontmatter, a TL;DR line, and the sections in `wiki/workflows/page-template.md`, in the order and words it gives. `/shape` writes them there in the owner's own words. The same page says what the unit of work is called here.

## 4. Wire it in

Add it to `wiki/index.md` and to the relevant `wiki/hats/` router. Cross-link from any related case. Add one entry to `wiki/log.md`, headed `## YYYY-MM-DD new-case | title (initials)`, that names the new page and every page you linked it from, otherwise it shows up as out of balance in `fmquery.py --balance`. Run the dashboard.

## 5. Run a gap scan

A new case is mostly gaps. Naming them on day one is cheaper than discovering them the day before a meeting.
