# Pacioli

Double-entry bookkeeping for what you know. Raw material in, dated and sourced knowledge out, nothing ever erased.

Built for people who do professional work across several roles at once and need one library that serves all of them.

---

## Why bookkeeping

Merchants in Florence and Genoa were keeping their books this way by around 1300, and Luca Pacioli wrote the method down in 1494. Their problem was how to keep a record that many people depend on, where the facts change over time and someone has to be able to reconstruct what was true on any given date.

The answer has held for seven centuries. **You never rub anything out. You post a correction.**

That single rule is what this repository implements for knowledge, and the correspondence is closer than an analogy.

The project is named after Luca Pacioli, a Franciscan friar who taught mathematics. He wrote the first printed description of the method, in his *Summa* of 1494, and Leonardo da Vinci drew the illustrations for a later book of his, *De divina proportione*.

| Bookkeeping | Here |
|---|---|
| The journal, chronological and append-only | `wiki/log.md` |
| One account per thing | One page per case, project or person |
| Posting an entry | `/ingest`, where new material is reconciled against old |
| The balance sheet, computed and never written | `wiki/status.md` |
| The trial balance, proving both sides agree | `fmquery.py --balance` |
| A correcting entry, because you never rub out | Supersede with a date rather than overwrite |
| A reference and a date on every entry | A source and a date on every fact |
| The auditor | `fmquery.py --eval`, assertions with no model involved |

## Why double

In double-entry bookkeeping every transaction is written twice, and the two sides must agree. That agreement is the proof that nothing went missing.

Here every fact is written twice too. Once by date in the journal, `wiki/log.md`, saying when it arrived and why. Once by subject on its page, where it is reconciled against what was already known. `fmquery.py --balance` holds the two against each other. A page whose `updated` date falls inside the journal's window and that no journal entry names, or a journal entry naming a page that is gone, shows up as out of balance.

Anything that leaves the library, in a report, a decision or another person's AI, has to show where each fact came from and when. The journal is that trail, and the balance is how you know the trail is complete.

## How material gets in

Raw material is what gets posted. Emails, meeting notes, reports, datasets, drafts. The language model is the clerk that posts it. The wiki is the books. Things reach the wiki only after they have been read, filtered, reconciled against what you already knew, and written down with a date.

The structural pattern comes from Andrej Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) sketch. What this repository adds is the bookkeeping discipline that keeps it honest once it is more than a weekend project: a schema, a validation hook, a generated dashboard, an append-only journal, and the rule that facts get invalidated rather than overwritten.

## Why most second brains rot

Four failure modes, and what this does about each.

**Hand-written overviews go stale.** Someone writes a "current status" page, it is accurate for a week, and then it quietly lies for a year. Here the status page is generated from frontmatter on every run and cannot be edited by hand. If it is wrong, the underlying page is wrong, and you fix it there.

**Contradictions stack.** New information gets appended below old information and both sit there, equally confident. Here the ingest step reconciles explicitly: add, update, or supersede. A superseded fact keeps its date so you can still answer "what was it before the change".

**Inference hardens into fact.** The model writes a reasonable conclusion, and six months later it reads like something you verified. Here anything derived carries `confidence: tentative` and a `review` date, and the linter surfaces it when the date passes.

**Everything looks equally important.** A library with no sense of what is urgent is a library you stop opening. Here work pages carry `next_action` and `next_action_date`, and the dashboard sorts by what is overdue.

## What is in the box

```
CLAUDE.md                  The library's own instructions. Read first, edit to fit you.
AGENTS.md                  Points any other coding agent to CLAUDE.md
wiki/                      The books
  index.md                 Table of contents and router
  log.md                   Append-only operations log
  status.md                GENERATED. Never edit by hand.
  hats/                    One index per role you wear
  cases/ projects/ people/ orgs/ meetings/ reference/ workflows/ themes/ archive/
inbox/                     Raw material: pending -> processed once posted, or archive if it fails the quality filter
output/                    Generated artefacts (reports, analyses, decks)
data/                      Structured datasets the analyses are built on
.claude/
  commands/                Seven operations as slash commands
  hooks/validate.py        Schema enforcement on every write
  scripts/fmquery.py       Query, search, eval, balance, dashboard, log rotation
  scripts/selftest.py      Proves the machinery works on this checkout
  scripts/voice.py         Style enforcement before anything ships
  loop.md                  The semi-autonomous improvement loop
docs/ARCHITECTURE.md       Why it is built this way
docs/ONBOARDING.md         How /onboard shapes the template to your work
docs/MEMORY-ZONE.md        The second zone, which lives outside the repo
```

## Kept on your own machine

The library is a folder of plain files on your own computer. Git keeps its full history in the same folder and sends nothing anywhere by itself. There is no server or account, and no service holds your knowledge, so it keeps working if a vendor changes its terms or retires a model.

Your books never go to GitHub. The setup below cuts the link back to this template, so a stray `git push` has nowhere to go. For an off-site copy, back up the folder, or push to a private remote you control and trust with everything in it.

The agent is the only part that reaches outside. It reads the pages a task needs and sends them to whichever model it runs on. Choose that model the way you would choose anyone else who reads your files, and for sensitive material, run the library with a model you host yourself. The scripts that check the books run locally and never call a model.

## Not tied to one tool

The books are plain Markdown with YAML frontmatter. Any editor opens them, any agent can read them, and they will still open in twenty years. The checks are plain Python with no dependencies and no model involved, so `fmquery.py`, `validate.py`, `voice.py` and `selftest.py` give the same answer whichever AI you use, or none.

The operations in `.claude/commands/` are written for Claude Code, but each one is an ordinary Markdown file of instructions. They ask a lot of the agent. It has to read and edit many files, run Python, reconcile new material against what is already known, and follow a procedure over many steps without losing its place. Any agentic model with that level of capability can run the library, from Anthropic, from another provider or on your own hardware. A weaker model can still run the checks and answer from the books, and it will make more mistakes when it posts. `AGENTS.md` points agents that look for that file name to `CLAUDE.md`.

The whole repository opens as an Obsidian vault as it is. Links in page bodies and in `related:` show up as backlinks and in the graph, so Obsidian can be the place you read and browse while the agent does the posting. Frontmatter wikilinks must be quoted for that to work, and the hook enforces it.

What you would lose by switching agent is the automatic hook on every write. Run `validate.py` by hand or in a git pre-commit hook instead, and nothing else changes.

## Quickstart

```bash
git clone https://github.com/th84r/pacioli.git my-books
cd my-books
git remote remove origin                         # your books stay on this machine
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

Plus `/onboard` to shape the library to your work, `/new-case`, `/weekly-review`, and a semi-autonomous `/loop` that runs the ladder on its own. `/loop` is Claude Code's built-in command and reads `.claude/loop.md`. With another agent, give it that file as the prompt.

## The rules that matter

Five constraints carry most of the value.

**Additive runs, reductive proposes.** The loop may add review dates, cross-links, TL;DR lines and tentative synthesis on its own. Merging pages, archiving, deleting and overwriting facts are written to `wiki/open-questions.md` for a human. Content is moved to the archive and kept.

**A generated dashboard beats a written one.** `fmquery.py --dashboard` regenerates `wiki/status.md` in seconds. Start every session with it.

**Facts get invalidated rather than overwritten.** Keep the old value with a date next to the new one. This is the correcting entry, and it is the rule the whole thing rests on.

**Inference expires.** Anything derived is `tentative` with a `review` date.

**Edit budget.** The loop changes at most five pages per iteration, then stops and reports. This is what prevents a runaway rewrite of your library.

## Two zones

The wiki holds knowledge about the work: chronologies, domain knowledge, methodology, project history. Your agent's own persistent memory holds knowledge about you: how you work, who people are, your writing rules, one-line case summaries.

Keep them apart and cross-reference. Duplicating between them is how they drift. The shape of the memory zone is in [docs/MEMORY-ZONE.md](docs/MEMORY-ZONE.md).

## Enforcement

Three machine checks, because conventions that depend on discipline stop working in month three.

`hooks/validate.py` runs after every write to `wiki/` and reports a page that has no `title`, no `type`, or a `status` outside the schema. It runs on the main pages, meaning any `overview.md` and anything under `reference/`, `themes/` or `workflows/`, so working sub-documents stay free-form. It fires after the write and reports the problem, so the agent can fix the page in the same turn.

`scripts/fmquery.py` drives the linter and the weekly review deterministically, so "what is overdue" is a query rather than a judgement call. It also searches the whole library including the log (`--search`, BM25, built in memory per call), runs deterministic fact assertions with no model involved (`--eval`), shows what links to what (`--links`), and keeps the log readable by archiving old months (`--rotate-log`).

`scripts/voice.py` scans anything before it leaves the building, against the rules you set in `wiki/workflows/voice.md`. The shipped default catches em dashes, sentences opening with a conjunction, and ten of the eleven sentence patterns listed in `wiki/workflows/voice.md`. The third, the closing aphorism, has no detector because telling a good last line from a generated one needs a reader. A stricter mode adds mid-sentence colons for those who ban them.

## Requirements

Python 3.9 or later, standard library only. An agent that reads `CLAUDE.md` and can run shell commands. Built and used daily with [Claude Code](https://claude.com/claude-code). Any agentic model capable enough to follow the procedures can run it, see [Not tied to one tool](#not-tied-to-one-tool).

Git is assumed. Every change is a commit, which is what makes the semi-autonomous loop safe to run.

## Status

This is the generalised skeleton of a system in daily production use across several roles. The content has been removed and the architecture kept.

Issues and pull requests welcome, particularly on the schema and on the voice rules, which are the two parts most likely to need reshaping for a different kind of work.

## Licence

MIT. See [LICENSE](LICENSE).
