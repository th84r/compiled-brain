---
description: Health check. Contradictions, stale facts, orphans, dead sources, trial balance. Recommends, changes nothing
---

You are running `/lint`. This operation recommends and changes no knowledge. `/consolidate` is the one that acts.

The one thing it does write is `wiki/status.md`, which is regenerated from frontmatter and holds nothing that is not derived from the pages themselves.

## 1. Run the deterministic checks

```
python3 .claude/scripts/fmquery.py --stale
python3 .claude/scripts/fmquery.py --orphans
python3 .claude/scripts/fmquery.py --balance
python3 .claude/scripts/fmquery.py --dashboard
python3 .claude/scripts/fmquery.py --eval
python3 .claude/scripts/fmquery.py --agree
python3 .claude/scripts/fmquery.py --rotate-log --dry-run
```

A failed assertion in `--eval` outranks everything else in the report. It means a fact the owner relies on has changed or a page has drifted. A failure in `--agree` ranks with it, a key figure missing from its own page or an old value still standing undated on another page. Fix the stale copy by updating it or by dating it, and never by deleting the old value from the table.

An account without a posting in `--balance` comes next, and so does a commit without a posting. A page changed with no journal entry is a fact nobody can trace, so the fix is a late entry saying when and why, naming the commit by its short hash, written from what the page and git history show. Never invent the reason.

## 2. Check what a script cannot

- **Contradictions.** Facts that conflict across pages. Are they dated as superseded, or just stacked?
- **Confident inference.** Pages marked `verified` that actually contain derived conclusions.
- **Missing review dates.** Volatile facts (numbers, dates, statuses, roles) with no `review` field.
- **Dead sources.** `sources:` entries pointing at files that no longer exist.
- **Schema drift.** Status values outside the vocabulary, missing TL;DR lines, missing `hat`.

## 3. Report in priority order

Group findings by severity. Something that could make you confidently wrong in a meeting outranks a missing cross-link.

For each finding give the page, the problem, and the specific fix. Do not apply them.
