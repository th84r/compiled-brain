# CLAUDE.md, the library's own instructions

This file is read at the start of every session. It is the contract between you and the agent. Edit it to fit your work, because a template that is never adapted is a template that gets ignored.

Everything in `<angle brackets>` is a placeholder. The fastest way to replace all of them is to say "set this up for me", which runs `/onboard`. It interviews you and shapes this file, the hats, the example and the voice rules to your work. See `docs/ONBOARDING.md`.

---

## What this library is

A knowledge base covering <your name>'s work across <domain>, kept current as raw material is posted into it.

**Hats.** You wear several. Each one is a context with its own people, its own deadlines, its own tempo. The library serves all of them from one place, and the `hat` field in frontmatter is what keeps them separable without splitting the library into silos.

- `<hat-one>`, <one line: what this role is>
- `<hat-two>`, <one line>
- `<hat-three>`, <one line>
- `bridging`, topics that touch several hats

Write hat values in lowercase. `wiki/hats/` holds one router page per hat, which is the entry point when you step into that role.

**A note worth keeping.** If some of your hats have someone external who chases you and some do not, say so here explicitly. The ones nobody chases are the ones that fall out of sight first, and they are usually the ones with hard deadlines and no reminder attached. Treat a passed `next_action_date` in that group as more serious than one someone is already chasing.

---

## Session start, fresh context before anything else

Hand-written overviews rot, so at the start of every working session:

1. **Run** `python3 .claude/scripts/fmquery.py --dashboard`. Takes seconds. It regenerates `wiki/status.md` from frontmatter.
2. **Read** `wiki/status.md`. It is the authoritative picture of now: active cases per hat, overdue actions, upcoming reviews. It beats `index.md`, `hats/` and the agent's own memory, all of which can be behind.
3. Then use `index.md` and `hats/` for the semantic question (what is this case about) and agent memory for the personal one (how does this person work).
4. When looking for where something was discussed, run `python3 .claude/scripts/fmquery.py --search "<terms>"` before grepping. It ranks pages and every log entry, archives included, and it is faster than reading.

`status.md` is machine-generated and must NEVER be edited by hand. Field corrections go in the individual page's frontmatter, then the dashboard is regenerated. When a session changes the state of a case, update that page's `updated`, `next_action` and `next_action_date` as part of the change. That is what keeps the dashboard true.

---

## Mental model

**This is bookkeeping.** Raw material (emails, documents, data, meeting notes) is what gets posted. The wiki is the books. `log.md` is the journal, each page is an account, `status.md` is the balance sheet computed from the accounts, `fmquery.py --balance` is the trial balance proving journal and accounts agree, and a fact that changes gets a correcting entry rather than an eraser.

The rule underneath everything is that **you never rub anything out.** When a price, a date, a status or a role changes, the old value stays with its date and the new one is written beside it. That is what lets the library answer "what was true in March" a year later.

**Two zones.**

1. **The working directory** is the active workspace. Raw material lands in `inbox/`, is posted into `wiki/`, artefacts are created in `output/`.
2. **Agent memory** is long-term knowledge about the person: role, preferences, contacts, pitfalls. Maintained automatically across conversations.

The two build on each other. Do not duplicate. Rule of thumb:

- "How this person works", "who is who", "writing style rules" go to agent memory.
- "What do we know about case X", "developments in field Y", "methodology Z" go to the wiki.

---

## Directory structure

```
<project-root>/
├── CLAUDE.md, README.md
├── inbox/            RAW MATERIAL    pending/ -> processed/{YYYY-MM}/ -> archive/
├── wiki/             THE BOOKS
│   ├── index.md      master table of contents, the router, read it first
│   ├── log.md        append-only operations log
│   ├── status.md     GENERATED, never edit by hand
│   ├── hats/         one router index per hat
│   ├── cases/ projects/ people/ orgs/ meetings/ reference/ workflows/ themes/ archive/
├── output/           GENERATED ARTEFACTS
├── data/             STRUCTURED DATASETS the analyses are built on
├── .claude/          commands/, hooks/, scripts/
```

The hat dimension lives in the `hat` field in frontmatter rather than in separate libraries. Every hat is served by the same wiki, the same inbox and the same output folder, so knowledge cross-links across them, which is the whole reason for keeping one library.

---

## Seven operations drive the system

Full steps live in `.claude/commands/`. They run when intent matches, see the table below.

- **`/ingest`**, take new material from `inbox/pending/`, filter for quality, reconcile against existing facts (contradictions get resolved rather than stacked), update wiki and index and log, archive the source file.
- **`/query`**, search wiki plus relevant memory, synthesise with citations, save answers with lasting value as a new or extended page.
- **`/lint`**, health check. Contradictions, stale facts (`expires` / `review`), orphan pages, dead sources. Recommends, changes nothing.
- **`/consolidate`**, the linter's acting sibling. Cleans additively (TL;DR, review dates, cross-links, bi-temporal dating, tentative synthesis), proposes the reductive in `wiki/open-questions.md`.
- **`/gap-scan`**, find knowledge gaps in active cases, write them to the work queue, close the web-answerable ones directly.
- **`/eval`**, measure the library against the golden set in `wiki/reference/eval-set.md`. The deterministic half, `fmquery.py --eval`, asserts field values with no model and can run in CI. The other half needs a model and is scored cold.
- **`/distill-skill`**, distil a procedure that worked into `wiki/workflows/skills-index.md` or a reusable command.

The self-reinforcing loop (`/loop`, driver in `.claude/loop.md`) runs the operations semi-autonomously down a priority ladder. Additive work is executed, reductive work is proposed, everything is committed to local git. Architecture in `wiki/workflows/self-improvement.md`. `/loop` is Claude Code's built-in command and reads `.claude/loop.md`. With another agent, give it that file as the prompt.

**Before building anything:** check `wiki/workflows/skills-index.md` (procedures that worked) and `wiki/reference/deliverables.md` (finished analyses and documents). Reuse and extend rather than reinvent.

### Quality filter, what belongs in the wiki

Adapt this section to your work. It is the main defence against a library that fills with noise.

**Belongs.**

- Decisions, and the reasoning behind them
- What happened in a meeting, and what each person there wanted
- Any figure you will be asked about again
- Developments in your field that change what is true
- A finding or a method with value beyond the case it came from
- Who people are and what they decide

**Does not belong.**

- Ordinary correspondence with no substance in it
- Raw material nobody has read yet
- Live correspondence still in flow, which stays in `inbox/processed` until it has concluded
- Anything already held in agent memory

---

## Frontmatter conventions

Every wiki page carries YAML frontmatter. Dates are always ISO (YYYY-MM-DD), never relative.

```yaml
---
title: Case title or subject
type: case | project | person | organization | reference | workflow
status: active | waiting | on_hold | closed
confidence: verified | tentative     # how much may be asserted
hat: <hat-one> | <hat-two> | bridging
parties: who else is involved, if anyone
value: economic value if relevant
created: YYYY-MM-DD
updated: YYYY-MM-DD
expires: YYYY-MM-DD                  # if it has an end date
review: YYYY-MM-DD                   # when volatile facts must be re-verified
next_action: what happens next
next_action_date: YYYY-MM-DD
tags: [topic1, topic2]
related: ["[[other-pages]]"]      # always quoted, or YAML and Obsidian see no links
sources: [inbox/processed/2026-04/x.pdf]
---
```

**TL;DR line.** Every page opens with one line summarising the core, so relevance can be triaged before reading the whole page.

**Facts that change get invalidated rather than overwritten.** When a number, a date, a status or a role changes, mark the old one as superseded with a date instead of deleting it. For example, "capacity 40 (to 2026), then 48 (from 2027, source X)". That way you can still answer "what was it before the change". Put a `review` date on volatile, frequently-read facts so the linter can flag them before they become confidently wrong.

Full schema per type in `wiki/workflows/frontmatter-schema.md`. Enforced by `.claude/hooks/validate.py` on write and by `.claude/scripts/fmquery.py` for queries.

---

## The log

`wiki/log.md` is append-only and is the audit trail. It answers "when did we learn this". It also grows without bound, so `fmquery.py --rotate-log` moves entries older than two months into `wiki/log/YYYY-MM.md`, whole and in order. Run it monthly, and search covers the archives so nothing becomes unfindable.

**The journal and the accounts must balance.** Every change to a page is a posting, so it needs a log entry that names the page, by path, folder or file name. `fmquery.py --balance` is the trial balance. It lists pages changed inside the journal's window that no entry mentions, and entries that name a page which no longer exists. Pages older than the first entry in `log.md` are the opening balance and are not checked. The balance is what the name of this system refers to. Each fact is written twice, once by date in the journal and once by subject on its page, and the two are held against each other.

**Entry headers name who posted.** `## YYYY-MM-DD operation | title (initials)`. In a library with one owner the initials are optional. With several people they are what makes the journal answer "who changed this", which is the first question anyone asks about a surprising fact.

## Memory lifecycle

Wiki pages are in one of three states. **active** (current, shown in the index, updated), **waiting / on_hold** (parked, can be revived), **closed** (read-only, moved to `wiki/archive/` at the next lint). `status` is updated when a case closes. Content is never deleted, only archived. Auditability over tidiness.

## Several people, one library

The library works for a team as well as for one person, with three rules.

- **The wiki is shared and agent memory is personal.** Each person's agent keeps its own memory of how that person works. What the team knows goes in the wiki, where everyone's agent reads it. Anything that two people's memories both hold probably belongs in the wiki.
- **Who may delete applies to people too.** Additive changes anyone can make. Reducing changes, meaning merges, deletions and moves to the archive, go to `wiki/open-questions.md` for the page's owner to decide. The owner of a case is whoever `next_action` points at.
- **Keep the library in git and commit often.** Git records who changed what, and the journal records why. Together they are the audit trail. Two people editing the same page is resolved like any merge conflict, and the losing version is superseded with a date rather than lost.

## Cadence

| When | What | Who, in a team |
|---|---|---|
| Daily | `/ingest` whatever arrived | Whoever received it |
| Weekly | `/weekly-review`, `/lint`, `fmquery.py --balance` | One named person, rotating |
| Monthly | `/consolidate`, `fmquery.py --rotate-log`, archive closed cases | The same person |
| Quarterly | Read `open-questions.md` and `eval-set.md` and decide what the library should know that it does not | Everyone, together |

The weekly slot matters most. It is the one that keeps `status.md` true, and it is the one that slips first.

---

## Writing style

Applies to everything the agent generates. Replace this section with your own rules and mirror them in `wiki/workflows/voice.md`, which is the file `scripts/voice.py` enforces.

The shipped defaults:

- **No contrast constructions** of the type "X, not Y" or "it is not X, it is Y". A classic machine tell. State the positive claim and let the contrast follow from the substance.
- **No em dashes.** Use a comma, a full stop, or rewrite.
- **No colons inside sentences**, if you hold that view. Colons belong in headings, frontmatter and tables. This one is opt-in, `voice.py --strict` checks it and the plain run does not, because a colon introducing a list is ordinary English.
- **Concrete before abstract.** Numbers, names, dates before generalisations.

Run `python3 .claude/scripts/voice.py <file>` before anything ships.

---

## Ingest conventions

Naming in `inbox/pending/`: `YYYYMMDD-source-topic-short.ext`, for example `20260428-mail-committee-invitation.eml`. After ingest the file is kept in `inbox/processed/YYYY-MM/`.

---

## Intent recognition, use the operations proactively

You will rarely type slash commands. You say what you want and the agent recognises the workflow.

| When you say something like | Run this |
|---|---|
| "set this up for me", "adapt this to my work", "I have a new role" | `/onboard` |
| "there is something in the inbox", "take this in", "read this" | `/ingest` |
| "what do we know about X", "find out", "where are we with Z" | `/query` |
| "weekly status", "what is happening this week", "prioritise" | `/weekly-review` |
| "clean up", "check for errors", "find contradictions" | `/lint` |
| "strengthen the library", "run the loop", "keep optimising" | `/loop` or `/consolidate` |
| "what are we missing on X", "where are we thin" | `/gap-scan` |
| "does the library work", "is it answering correctly" | `/eval` |
| "new case X", "open a case for" | `/new-case` |
| "build an analysis", "make a deck" | build directly, save in `output/` |

When ambiguous, pick the most likely workflow and confirm briefly before continuing. Prefer action over long clarification. For compound input ("check X AND draft Y AND update the wiki"), chain several workflows in order.

## When you recognise intent, act

If a request surfaces something that belongs in the wiki, post it too, without asking permission for each step.

**Exceptions where you confirm first:**

- Deletions or moves that reduce information
- External actions (sending mail, pushing to a remote, contacting a third party)
- Decisions that commit the user to someone else (figures, promises, drafts sent as final)

---

## What this file is

This file sets the rules for a knowledge library kept by a working professional. When in doubt, ask first and post afterwards.
