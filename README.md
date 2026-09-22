# doubleentry

Double-entry bookkeeping for what you know. Raw material in, dated and sourced knowledge out, nothing ever erased.

Built for people who do professional work across several roles at once and need one library that serves all of them.

---

## Why bookkeeping

Accounting solved this problem in 1494. How do you keep a record that many people depend on, where the facts change over time, and where someone has to be able to reconstruct what was true on any given date.

The answer has not improved in five centuries. **You never rub anything out. You post a correction.**

That single rule is what this repository implements for knowledge, and the correspondence is closer than an analogy.

| Bookkeeping | Here |
|---|---|
| The journal, chronological and append-only | `wiki/log.md` |
| One account per thing | One page per case, project or person |
| Posting an entry | `/ingest`, where new material is reconciled against old |
| The trial balance, computed and never written | `wiki/status.md` |
| A correcting entry, because you never rub out | Supersede with a date rather than overwrite |
| A reference and a date on every entry | A source and a date on every fact |
| The auditor | `fmquery.py --eval`, assertions with no model involved |

## How material gets in

Raw material is what gets posted. Emails, meeting notes, reports, datasets, drafts. The language model is the clerk that posts it. The wiki is the books. The wiki is never where you dump things. It is where things end up after they have been read, filtered, reconciled against what you already knew, and written down with a date on them.

The structural pattern comes from Andrej Karpathy's LLM-wiki sketch. What this repository adds is the bookkeeping discipline that keeps it honest once it is more than a weekend project: a schema, a validation hook, a generated dashboard, an append-only journal, and the rule that facts get invalidated rather than overwritten.

## Why most second brains rot

Four failure modes, and what this does about each.

**Hand-written overviews go stale.** Someone writes a "current status" page, it is accurate for a week, and then it quietly lies for a year. Here the status page is generated from frontmatter on every run and cannot be edited by hand. If it is wrong, the underlying page is wrong, and you fix it there.

**Contradictions stack.** New information gets appended below old information and both sit there, equally confident. Here the ingest step reconciles explicitly: add, update, or supersede. A superseded fact keeps its date so you can still answer "what was it before the change".

**Inference hardens into fact.** The model writes a reasonable conclusion, and six months later it reads like something you verified. Here anything derived carries `confidence: tentative` and a `review` date, and the linter surfaces it when the date passes.

**Everything looks equally important.** A library with no sense of what is urgent is a library you stop opening. Here work pages carry `next_action` and `next_action_date`, and the dashboard sorts by what is overdue.

## What is in the box

```
CLAUDE.md                  The brain's own instructions. Read first, edit to fit you.
wiki/                      The books
  index.md                 Table of contents and router
  log.md                   Append-only operations log
  status.md                GENERATED. Never edit by hand.
  hats/                    One index per role you wear
  cases/ projects/ people/ orgs/ meetings/ reference/ workflows/ themes/ archive/
inbox/                     Raw material: pending -> processed -> archive
output/                    Generated artefacts (reports, analyses, decks)
data/                      Structured datasets the analyses are built on
.claude/
  commands/                Seven operations as slash commands
  hooks/validate.py        Schema enforcement on every write
  scripts/fmquery.py       Query, search, eval, dashboard, log rotation
  scripts/selftest.py      Proves the machinery works on this checkout
  scripts/voice.py         Style enforcement before anything ships
  loop.md                  The semi-autonomous improvement loop
docs/ARCHITECTURE.md       Why it is built this way
docs/ONBOARDING.md         How /onboard shapes the template to your work
docs/MEMORY-ZONE.md        The second zone, which lives outside the repo
```

## Quickstart

```bash
git clone https://github.com/th84r/doubleentry.git my-books
cd my-books
python3 .claude/scripts/selftest.py              # every check should say ok
python3 .claude/scripts/fmquery.py --dashboard   # writes wiki/status.md
python3 .claude/scripts/fmquery.py --search "abstract"
```

Then say **"set this up for me"**. The agent runs `/onboard`, interviews you about your work in nine questions, and shapes the library to it: the roles, the quality filter, the page template, the example, the voice rules and the first fact checks. Details in [docs/ONBOARDING.md](docs/ONBOARDING.md).

If you would rather do it by hand, open `CLAUDE.md` and do three things.

1. Replace the **hats** with your own roles. A hat is a context you work in, and the `hat` field in frontmatter is what lets one library serve all of them without splitting into silos.
2. Adjust the **quality filter** section. What belongs in your library is specific to your work, and getting this wrong is the main way a library fills with noise.
3. Set your **voice rules** in `wiki/workflows/voice.md`. This is the file `voice.py` enforces.

Drop a file into `inbox/pending/` and say "take this in". The agent will run `/ingest`.

## The seven operations

Each is a slash command in `.claude/commands/`. You rarely type them. You describe what you want and the agent recognises which one applies, using the intent table in `CLAUDE.md`.

| Command | What it does |
|---|---|
| `/ingest` | Read new material, filter it, reconcile against existing facts, write it in, archive the source |
| `/query` | Search, synthesise with citations, save answers that have lasting value |
| `/lint` | Health check. Contradictions, stale facts, orphans, dead sources. Recommends, changes nothing |
| `/consolidate` | The linter's acting sibling. Does the additive cleanup, proposes the reductive |
| `/gap-scan` | Find what an active case cannot answer, write it to the work queue, close what the web can close |
| `/eval` | Measure the library against a golden set of questions, track the pass rate |
| `/distill-skill` | Turn a procedure that worked into a reusable command |

Plus `/onboard` to shape the library to your work, `/new-case`, `/weekly-review`, and a semi-autonomous `/loop` that runs the ladder on its own.

## The rules that actually matter

Five constraints carry most of the value. The folder layout carries very little of it.

**Additive runs, reductive proposes.** The loop may add review dates, cross-links, TL;DR lines and tentative synthesis on its own. Merging pages, archiving, deleting and overwriting facts are written to `wiki/open-questions.md` for a human. Content is archived, never deleted.

**A generated dashboard beats a written one.** `fmquery.py --dashboard` regenerates `wiki/status.md` in seconds. Start every session with it.

**Facts get invalidated rather than overwritten.** Keep the old value with a date next to the new one. This is the correcting entry, and it is the rule the whole thing rests on.

**Inference expires.** Anything derived is `tentative` with a `review` date.

**Edit budget.** The loop changes at most five pages per iteration, then stops and reports. This is what prevents a runaway rewrite of your library at three in the morning.

## Two zones

The wiki holds knowledge about the work: chronologies, domain knowledge, methodology, project history. Your agent's own persistent memory holds knowledge about you: how you work, who people are, your writing rules, one-line case summaries.

Keep them apart and cross-reference. Duplicating between them is how they drift. The shape of the memory zone is in [docs/MEMORY-ZONE.md](docs/MEMORY-ZONE.md).

## Enforcement

Three machine checks, because conventions that depend on discipline stop working in month three.

`hooks/validate.py` runs after every write to `wiki/` and reports a page that has no `title`, no `type`, or a `status` outside the schema. It runs on the main pages, meaning any `overview.md` and anything under `reference/`, `themes/` or `workflows/`, so working sub-documents stay free-form. It fires after the write rather than before, so it reports rather than blocks, which is what lets the agent fix the page in the same turn.

`scripts/fmquery.py` drives the linter and the weekly review deterministically, so "what is overdue" is a query rather than a judgement call. It also searches the whole library including the log (`--search`, BM25, built in memory per call), runs deterministic fact assertions with no model involved (`--eval`), shows what links to what (`--links`), and keeps the log readable by archiving old months (`--rotate-log`).

`scripts/voice.py` scans anything before it leaves the building, against the rules you set in `wiki/workflows/voice.md`. The shipped default catches em dashes, sentences opening with a conjunction, and ten of the eleven sentence patterns listed in `wiki/workflows/voice.md`. The eleventh, the earned closing aphorism, has no detector because telling a good last line from a generated one needs a reader. A stricter mode adds mid-sentence colons for those who ban them.

## Requirements

Python 3.9 or later, standard library only. An agent that reads `CLAUDE.md` and can run shell commands. Built and used daily with [Claude Code](https://claude.com/claude-code), and the structure carries to any agent that reads a project instruction file.

Git is assumed. Every change is a commit, which is what makes the semi-autonomous loop safe to run.

## Status

This is the generalised skeleton of a system in daily production use across several roles. The content is stripped, the architecture is not.

Issues and pull requests welcome, particularly on the schema and on the voice rules, which are the two parts most likely to need reshaping for a different kind of work.

## Licence

MIT. See [LICENSE](LICENSE).

<!-- guard verified 2026-09-22 -->
