---
title: Skills index, procedures that worked
type: workflow
status: active
confidence: verified
hat: bridging
created: 2026-01-01
updated: 2026-01-01
tags: [skills, procedures, reuse]
related: ["[[self-improvement.md]]"]
---

TL;DR. Procedures that worked, written down so they are not rediscovered. Check here before building anything. Added by `/distill-skill`.

## How an entry is written

The task in one line, the exact commands and paths, the traps that cost time the first time, and how to tell it worked. Credentials are named by location, never by value.

Known limitations belong in the entry. A procedure with an honest list of what it does not handle is worth more than one that claims to be general.

## Entries

### Example, regenerate the dashboard

`python3 .claude/scripts/fmquery.py --dashboard`

Writes `wiki/status.md` from frontmatter. Run it at the start of every session and after any change to a page's status, next action or dates.

Trap. If a page shows up under "status values outside the schema", the page is using a status the dashboard cannot group. Fix the page rather than the script.

### Example, check a document before it ships

`python3 .claude/scripts/voice.py path/to/file.docx`

Reads `.md`, `.txt` and `.docx`. Quoted passages are excluded, because a verbatim quote is the source's language.

Trap. Bold lead-ins inside a .docx can still be flagged as setup-and-punchline, because a .docx paragraph break reaches the checker as a single line break. That is a false positive in a structured note. Judge those manually rather than rewriting around the checker.
