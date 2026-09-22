# Architecture

Why this is built the way it is. Read this if you are deciding whether the structure is worth adopting, or if you want to change it without breaking what makes it work.

---

## The problem it solves

A professional working across several roles accumulates knowledge faster than they can organise it. The obvious responses all fail in a predictable way.

A folder of notes fails because nothing connects and nothing is current. A wiki fails because maintaining it is a second job. Handing everything to a model with a long context fails because the model has no memory between sessions and no way to tell what it verified from what it guessed.

What works is keeping the library the way a bookkeeper keeps the books. Every entry dated and referenced, nothing rubbed out, the summary computed from the entries rather than written, and a small amount of machinery enforcing those rules so they do not depend on discipline.

## The bookkeeping model

Raw material is what gets posted. The wiki is the books.

The metaphor is double-entry bookkeeping rather than a compiler, and the difference matters. **A compiler has no memory.** It translates what is in front of it and does not care what it translated last time. The most distinctive discipline here is the opposite. New material is held against what is already recorded, and a fact that has changed keeps its old value with a date.

Bookkeeping is the only human system that solved exactly this, a record many people depend on where the facts change and someone must be able to reconstruct any past state. The answer since 1494 has been the same. You never rub anything out, you post a correction.

This has a consequence people usually miss. **You do not edit an account to record something new. You post an entry.** The new thing goes in `inbox/`, and the posting step reads it, decides which accounts it touches, reconciles it against what is already recorded, and writes it in with a date and a reference. The discipline lives in the posting rather than in the person.

It has a second consequence. **A trial balance is recomputed, never kept.** Anything derived from the accounts can be struck again from the accounts whenever they change. This is why `status.md` is generated rather than written. It is the part of the library most likely to be wrong, so it is the part that never gets written by hand.

## The four failure modes and their counters

### Hand-written overviews rot

Someone writes a status page. It is accurate for a week. Then it quietly lies for a year, and worse, people keep reading it.

**Counter.** `fmquery.py --dashboard` regenerates `wiki/status.md` from frontmatter in seconds. The file carries a warning that it must never be hand-edited. Corrections go in the underlying page, which is the only place they can be true.

The deeper point is that the dashboard is a **query result**, so "what is overdue" stops being a judgement call and becomes a fact about the data. That is what makes it trustworthy enough to start a session with.

### Contradictions stack

New information is appended below old information and both sit there with equal confidence. Six months later nobody knows which is current.

**Counter.** Step 5 of `/ingest` forces an explicit decision for every fact that touches something existing: add, update, or supersede. A superseded fact keeps its date and stays on the page.

That last part matters more than it looks. Keeping the old value is what lets you answer "what was it before the change", which is often the question that decides what happens next.

### Inference hardens into fact

A model writes a reasonable conclusion. Nothing marks it as a conclusion. Six months later it reads like something that was verified.

**Counter.** `confidence: tentative` plus a `review` date on anything derived. The linter surfaces it when the date passes. The loop is explicitly told that a conclusion must never harden into a fact.

This is the invariant most likely to be quietly dropped when someone adapts the template, and it is the one that causes the most damage when it goes.

### Everything looks equally important

A library with no sense of urgency is a library you stop opening.

**Counter.** `next_action` and `next_action_date` on work pages, and a dashboard that sorts by what is overdue. Plus a deliberate weighting rule: work where nobody external is chasing you falls out of sight first, so a passed date there is treated as more serious rather than less.

## Why two zones

The wiki holds knowledge about the work. The agent's own persistent memory holds knowledge about the person.

They are separated because they have different lifecycles and different readers. Case knowledge is long-lived, needs sources, and is the kind of thing a colleague could read. Personal knowledge is about preferences and working style, is short, and is useless to anyone else.

Mixing them produces a library where you cannot find the facts because they are buried in habits, and habits that go stale because they are buried in facts.

The rule for deciding is simple. "How does this person work", "who is this person", "what are the writing rules" go to memory. "What do we know about X" goes to the wiki. Cross-reference, never duplicate.

## Why hats rather than separate libraries

A `hat` field rather than one repository per role.

Separate libraries look tidier and are worse. The value in a cross-role library is exactly the connections that cross roles: the person who appears in two pieces of work, the reference data that informs three cases, the method developed in one context that applies in another. Split the library and those connections stop existing.

The `hat` field gives you the separation where you need it, which is filtering and routing, without giving up the cross-links.

## Why additive runs and reductive proposes

The loop can improve the library while you work. The question is what it may do unsupervised.

The split is by reversibility. Adding a review date, a cross-link or a TL;DR is cheap to undo and cheap to be wrong about. Merging two pages, archiving something, or overwriting a fact destroys information, and the loop cannot know what you were going to need.

The edit budget of five pages per iteration exists for the same reason. A loop that can change fifty pages in one run is a loop that can quietly corrupt your library while you sleep, and git is only a good recovery mechanism if you notice in time.

## Why machine enforcement

Conventions that depend on discipline stop working in month three. This is the single most reliable observation about knowledge systems.

Three checks, each at the point where the convention is most likely to break.

`hooks/validate.py` runs on write, which is when a schema violation is cheapest to fix. It fails open, because a broken hook that blocks a session is worse than the violation it was catching.

`scripts/fmquery.py` makes staleness a query. Nobody has to remember to check. The same script runs the deterministic half of the eval, `--eval`, which asserts specific field values on specific pages with no model involved. That catches a silently changed fact, or a schema that drifted, the moment it happens, and it runs in CI.

The log is append-only and grows without bound, which makes it a poor retrieval target after a few thousand lines. `--rotate-log` moves entries older than two months into `wiki/log/YYYY-MM.md`, whole and in order, nothing deleted. The main log stays a rolling window an agent can actually read, and search covers the archives too.

`scripts/voice.py` runs before anything ships. Style rules are the ones people most reliably believe they are following while not following them, which is exactly the situation a script handles better than a read-through.

## What is deliberately not here

**No database.** Flat markdown files in git. You can read them without the tooling, diff them, and recover them. A database would make queries faster and the library less durable, and durability is worth more.

**No persisted search index.** Search exists, `fmquery.py --search`, ranked with BM25 over pages and every log entry. It is built in memory on each call and thrown away. That is the same idea as the generated dashboard: a derived view cannot drift from the source if it never outlives the call. Embeddings would be the next step at a scale where lexical search stops finding things, and the rule would be the same, regenerate rather than maintain.

**No automated deletion.** Ever. Content is archived, never removed. Auditability over tidiness.

**No sync service.** Git is the sync. If you need it on two machines, push it somewhere private.

## Adapting it

`/onboard` handles the changing. It interviews the owner and rewrites the parts below. This section says what they are and why, for anyone doing it by hand or checking what the onboarding did.

Three things almost always need changing, and one thing almost never should.

**Change the hats.** They are specific to your work and the template's are placeholders.

**Change the quality filter.** What belongs in your library is specific to your field. This is the section that most determines whether the library stays useful or fills with noise.

**Change the voice rules.** `wiki/workflows/voice.md` and the patterns in `voice.py` are calibrated for one person's writing. Yours will differ.

**Do not change the confidence discipline.** `tentative` plus a `review` date on anything derived is what keeps the library honest. It is the easiest invariant to drop and the most expensive to lose.
