---
title: Page template, the sections of a page about one piece of work
type: workflow
status: active
confidence: verified
hat: bridging
created: 2026-01-10
updated: 2026-01-10
tags: [template, new-case, shape]
---

TL;DR. The sections every page about one piece of work gets. `/new-case` uses them, and `/shape` rewrites them in the owner's own words.

The unit of work here is called a **case**. Its pages live in `wiki/cases/`.

## Sections

```
## Situation            what this is, in a paragraph
## Who is involved      each person and what they need, with sources
## What matters         figures, consequences, what changes with the outcome
## Chronology           dated, append-only
## Next steps           what happens, who does it, by when
## Open questions       what we do not know yet
## Sources
```

Sub-documents, a chronology, a preparation or an analysis, go in the same folder and do not need full frontmatter.

## Why this is a page and not part of the command

The owner's words belong in the wiki, where they can be read, changed and posted like any other page. The commands in `.claude/commands/` stay as the template ships them, and Claude Code does not let an unattended run change them.
