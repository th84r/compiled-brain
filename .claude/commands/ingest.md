---
description: Read new raw material from inbox/pending, post it to the wiki, archive the source
---

You are running `/ingest`. Follow these steps exactly.

## 1. Scan the inbox

List everything in `inbox/pending/`. If it is empty, say so and stop.

For each file identify the type and format, the date (from the filename if possible, otherwise metadata or content), the source, and the main subject.

## 2. Read

Open and read what matters. For large binaries (parquet, xlsx) peek at the metadata first with DuckDB or pandas rather than loading the whole thing. For `.eml` extract sender, recipients, date, subject and body.

## 3. Quality filter

Judge each file against the filter in `CLAUDE.md`. If it does not pass, move it to `inbox/archive/` and skip steps 4 to 6 for that file.

Getting this step wrong is the main way a library fills with noise. When a file is borderline, ask rather than guess.

## 4. Identify entities

Which cases, projects, people or reference topics does this touch? Check `wiki/cases/` and `wiki/projects/` before creating anything new.

## 5. Reconcile against what you already know

This is the step that separates a library from a pile. Before writing, compare the new material against what is already there. For every fact that touches something existing (a number, a date, a status, a role), decide:

- **ADD**, a new non-conflicting fact. Write it in.
- **UPDATE**, the same fact with a newer or more precise value. Update it and set `updated`.
- **SUPERSEDE**, the fact has changed over time. Keep the old one marked superseded with its date, add the new one with source and date.

Never stack two contradicting facts on top of each other without marking which one is current. Put a `review` date on volatile, frequently-read facts.

## 6. Update the wiki

Update existing pages according to step 5. Create new pages with correct frontmatter, a TL;DR line and a `confidence` value. Cross-reference with `[[other-pages]]`. Update `wiki/index.md` if pages were added or status changed.

## 7. Log and archive

Add one entry to `wiki/log.md`, headed `## YYYY-MM-DD ingest | title (initials)`, that names every page you created or changed. An unnamed page will show up as out of balance in `fmquery.py --balance`. Move the files from `inbox/pending/` to `inbox/processed/YYYY-MM/`, creating the month folder if needed. Say which files were routed to archive and why.

## 8. Report

Number of files handled, which pages were created or updated, and anything that needs a human decision (contradictions, missing context, choices you could not make).

## If in doubt

Stop and ask. Parking material is better than embedding the wrong structure. Wrong content is harder to remove than missing content is to add.
