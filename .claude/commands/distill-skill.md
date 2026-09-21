---
description: Turn a procedure that worked into something reusable
---

You are running `/distill-skill`.

## When to run this

Something non-obvious just worked. A data pipeline, a document build, an access route, a query that took three attempts to get right. The knowledge is currently in a conversation that will be gone tomorrow.

## What to capture

Not the narrative. The procedure.

- What the task was, in one line
- The exact commands, paths, parameters and credentials location (never the credential itself)
- The traps. What failed first and why, because that is usually the expensive part
- How to tell it worked

## Where it goes

- **A short procedure** goes to `wiki/workflows/skills-index.md` as a new entry.
- **A procedure you will run repeatedly** becomes a new file in `.claude/commands/`.
- **A script** goes to `.claude/scripts/` with a docstring that explains why it exists rather than only what it does.

## Known limitations belong in the entry

A procedure with an honest list of what it does not handle is worth more than one that claims to be general. Write the limitations down while you still remember them.
