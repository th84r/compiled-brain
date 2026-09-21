# CLAUDE.md, the brain's own instructions

This file is read at the start of every session. It is the contract between you and the agent. Edit it to fit your work, because a template that is never adapted is a template that gets ignored.

Everything in `<angle brackets>` is a placeholder. The fastest way to replace all of them is to say "set this up for me", which runs `/onboard`. It interviews you and shapes this file, the hats, the example and the voice rules to your work. See `docs/ONBOARDING.md`.

---

## What this library is

A self-developing knowledge base covering <your name>'s work across <domain>. It grows sharper over time as raw material is fed in and compiled into structured knowledge.

**Hats.** You wear several. Each one is a context with its own people, deadlines and tempo. The library serves all of them from one place, and the `hat` field in frontmatter is what keeps them separable without splitting the library into silos.

- `<hat-one>`, <one line: what this role is>
- `<hat-two>`, <one line>
- `<hat-three>`, <one line>
- `bridging`, topics that touch several hats

Write hat values in lowercase. `wiki/hats/` holds one router page per hat, which is the entry point when you step into that role.

**A note worth keeping.** If some of your hats have someone external who chases you and some do not, say so here explicitly. The ones nobody chases are the ones that fall out of sight first, and they are usually the ones with hard deadlines and no reminder attached. Treat a passed `next_action_date` in that group as more serious than one someone is already chasing.

---

## Session start, fresh context before anything else

Hand-written overviews rot. So at the start of every working session:

1. **Run** `python3 .claude/scripts/fmquery.py --dashboard`. Takes seconds. It regenerates `wiki/status.md` from frontmatter.
2. **Read** `wiki/status.md`. It is the authoritative picture of now: active cases per hat, overdue actions, upcoming reviews. It beats `index.md`, `hats/` and the agent's own memory, all of which can be behind.
3. Then use `index.md` and `hats/` for the semantic question (what is this case about) and agent memory for the personal one (how does this person work).
4. When looking for where something was discussed, run `python3 .claude/scripts/fmquery.py --search "<terms>"` before grepping. It ranks pages and every log entry, archives included, and it is faster than reading.

`status.md` is machine-generated and must NEVER be edited by hand. Field corrections go in the individual page's frontmatter, then the dashboard is regenerated. When a session changes the state of a case, update that page's `updated`, `next_action` and `next_action_date` as part of the change. That is what keeps the dashboard true.

---

## Mental model

**The model is a compiler.** Raw material (emails, documents, data, meeting notes) is source code. The wiki is compiled output. It grows organically as new material is embedded and cross-linked.

**Two zones.**

1. **The working directory** is the active workspace. Raw material lands in `inbox/`, is compiled into `wiki/`, artefacts are created in `output/`.
2. **Agent memory** is long-term knowledge about the person: role, preferences, contacts, pitfalls. Maintained automatically across conversations.

The two build on each other. Do not duplicate. Rule of thumb:

- "How this person works", "who is who", "writing style rules" go to agent memory.
- "What do we know about case X", "developments in market Y", "methodology Z" go to the wiki.

---

## Directory structure

```
<project-root>/
├── CLAUDE.md, README.md
├── inbox/            RAW MATERIAL    pending/ -> processed/{YYYY-MM}/ -> archive/
├── wiki/             COMPILED KNOWLEDGE
│   ├── index.md      master table of contents, the router, read it first
│   ├── log.md        append-only operations log
│   ├── status.md     GENERATED, never edit by hand
│   ├── hats/         one router index per hat
│   ├── cases/ projects/ people/ orgs/ meetings/ reference/ workflows/ themes/ archive/
├── output/           GENERATED ARTEFACTS
├── data/             STRUCTURED DATASETS the analyses are built on
├── .claude/          commands/, hooks/, scripts/
```

The hat dimension lives in the `hat` field in frontmatter rather than in separate libraries. The same wiki, inbox and output serve every hat, so knowledge cross-links across them. That is the point.

---

## Seven operations drive the system

Full steps live in `.claude/commands/`. They run when intent matches, see the table below.

- **`/ingest`**, take new material from `inbox/pending/`, filter for quality, reconcile against existing facts (contradictions get resolved rather than stacked), update wiki and index and log, archive the source file.
- **`/query`**, search wiki plus relevant memory, synthesise with citations, save answers with lasting value as a new or extended page.
- **`/lint`**, health check. Contradictions, stale facts (`expires` / `review`), orphan pages, dead sources. Recommends, changes nothing.
- **`/consolidate`**, the linter's acting sibling. Cleans additively (TL;DR, review dates, cross-links, bi-temporal dating, tentative synthesis), proposes the reductive in `wiki/open-questions.md`.
- **`/gap-scan`**, find knowledge gaps in active cases, write them to the work queue, close the web-answerable ones directly.
- **`/eval`**, measure the library against the golden set in `wiki/reference/eval-set.md`. The deterministic half, `fmquery.py --eval`, asserts field values with no model and belongs in CI. The other half needs a model and is scored cold.
- **`/distill-skill`**, distil a procedure that worked into `wiki/workflows/skills-index.md` or a reusable command.

The self-reinforcing loop (`/loop`, driver in `.claude/loop.md`) runs the operations semi-autonomously down a priority ladder. Additive work is executed, reductive work is proposed, everything is committed to local git. Architecture in `wiki/workflows/self-improvement.md`.

**Before building anything:** check `wiki/workflows/skills-index.md` (procedures that worked) and `wiki/reference/output-artefakter.md` (finished analyses and documents). Reuse and extend rather than reinvent.

### Quality filter, what belongs in the wiki

Adapt this section to your work. It is the main defence against a library that fills with noise.

**Belongs:** decisions and the reasoning behind them, outcomes of meetings and what the people involved want, figures and terms you will be asked about again, developments in your field that change what is true, findings and methods with value beyond the case they came from, people's roles.

**Does not belong:** ordinary correspondence without substance, raw material without analysis, active correspondence still in flow (keep as `inbox/processed` until settled), anything already in agent memory.

---

## Frontmatter conventions

Every wiki page carries YAML frontmatter. Dates are always ISO (YYYY-MM-DD), never relative.

```yaml
---
title: Case title or subject
type: case | project | person | reference | workflow
status: active | waiting | on_hold | closed
confidence: verified | tentative     # how much may be asserted
hat: <hat-one> | <hat-two> | bridging
counterpart: the other party, if there is one
value: economic value if relevant
created: YYYY-MM-DD
updated: YYYY-MM-DD
expires: YYYY-MM-DD                  # if an agreement has an end date
review: YYYY-MM-DD                   # when volatile facts must be re-verified
next_action: what happens next
next_action_date: YYYY-MM-DD
tags: [topic1, topic2]
related: [[other-pages]]
sources: [inbox/processed/2026-04/x.pdf]
---
```

**TL;DR line.** Every page opens with one line summarising the core, so relevance can be triaged before reading the whole page.

**Facts that change get invalidated rather than overwritten.** When a price, term, position or role changes, mark the old one as superseded with a date instead of deleting it. For example, "12.25m/year (to 2026), then 13.0m/year (from 2027, source X)". That way you can still answer "what was it before the change". Put a `review` date on volatile, frequently-read facts so the linter can flag them before they become confidently wrong.

Full schema per type in `wiki/workflows/frontmatter-schema.md`. Enforced by `.claude/hooks/validate.py` on write and by `.claude/scripts/fmquery.py` for queries.

---

## The log

`wiki/log.md` is append-only and is the audit trail. It answers "when did we learn this". It also grows without bound, so `fmquery.py --rotate-log` moves entries older than two months into `wiki/log/YYYY-MM.md`, whole and in order. Run it monthly. Search covers the archives, so nothing becomes unfindable.

## Memory lifecycle

Wiki pages are in one of three states. **active** (current, shown in the index, updated), **waiting / on_hold** (parked, can be revived), **closed** (read-only, moved to `wiki/archive/` at the next lint). `status` is updated when a case closes. Content is never deleted, only archived. Auditability over tidiness.

---

## Writing style

Applies to everything the agent generates. Replace this section with your own rules and mirror them in `wiki/workflows/voice.md`, which is the file `scripts/voice.py` enforces.

The shipped defaults:

- **No contrast constructions** of the type "X, not Y" or "it is not X, it is Y". A classic machine tell. State the positive claim and let the contrast follow from the substance.
- **No em dashes.** Use a comma, a full stop, or rewrite.
- **No colons inside sentences.** Colons belong in headings, frontmatter and tables.
- **Concrete before abstract.** Numbers, names, dates before generalisations.

Run `python3 .claude/scripts/voice.py <file>` before anything ships.

---

## Ingest conventions

Naming in `inbox/pending/`: `YYYYMMDD-source-topic-short.ext`, for example `20260428-mail-northwind-proposal.eml`. After ingest the file is kept in `inbox/processed/YYYY-MM/`.

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

If a request surfaces something that belongs in the wiki, compile it too, without asking permission for each step.

**Exceptions where you confirm first:**

- Deletions or moves that reduce information
- External actions (sending mail, pushing to a remote, contacting a third party)
- Decisions that commit the user to someone else (prices, draft agreements)

---

## What this file is not

This is not a code CLAUDE.md and this is not a software project. It is a living knowledge library for a working professional. When in doubt, ask first and compile afterwards.
