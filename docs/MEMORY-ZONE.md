# The memory zone

The wiki is one of two zones. This document describes the other one, because the template cannot ship it. Agent memory lives outside the repository, in the agent's own persistent store, and it is about the person rather than the work.

## What goes there

- Who the person is. Role, responsibilities, working style.
- Feedback. Corrections and confirmed approaches, each with the reason behind it.
- Contacts. Who is who, one line each, with the file in `wiki/people/` for the detail.
- Standing rules. Which email account for which context, what needs sign-off, what must never leave the building.
- One-line summaries of live cases, as a fast index into the wiki.

## What does not

Chronologies, domain knowledge, methodology, data findings, anything with a source. That is wiki material. The test is simple: could a colleague use this fact? If yes, it belongs in the wiki. If it only makes sense as a note about how this particular person works, it belongs in memory.

## The shape that works

One file per fact, each with a short frontmatter, and one index file that lists them. The index is what gets loaded into every session, so it holds one line per memory and never the content.

```markdown
---
name: feedback-no-outbound-without-signoff
description: Never send outbound correspondence without the owner's explicit sign-off
type: feedback
---

Drafts yes, sending never. Applies to email, messages, and anything else
that reaches a third party.

**Why:** an unreviewed message commits the owner to a position they may
not hold.

**How to apply:** produce the draft, put it on the clipboard or in a file,
and stop.
```

Four types have proved enough. `user` for who the person is. `feedback` for guidance on how to work, both corrections and confirmations, always with the reason. `project` for ongoing work, goals or constraints that the code and history do not show. `reference` for pointers to external resources.

## The rule that keeps the zones apart

Before saving to memory, check whether the wiki already records it. Before saving to the wiki, check whether it is really about the person. When a fact could go either way, it goes to the wiki with a one-line pointer in memory.

Duplicating between the zones is how they drift. A figure recorded in both places will be updated in one and not the other, and six months later the two disagree.

## If your agent has no persistent memory

Keep a `memory/` folder in the repository with the same structure, gitignored if it holds anything private. The two-zone discipline matters more than where the second zone physically lives.
