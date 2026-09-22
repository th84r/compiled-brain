---
description: Learn the owner's work and shape the library to it. Run first, re-run when a role is added
---

You are running `/onboard`. The template you are sitting in was generalised from one person's work, and a template that is never adapted is a template that gets ignored. Your job is to learn this person's work well enough to adapt it for them, then do the adapting, then show them what changed.

Two rules for the whole run.

**Ask, then act.** Do the interview first, in one pass, and only then edit files. Do not edit after each answer, it produces a library shaped by whatever was said last.

**Write in their language.** If they answer in Norwegian, the hats, the quality filter and the example case are written in Norwegian. The scripts do not care, and the library should read like theirs.

If `wiki/reference/profile.md` already exists, this is a re-run. Read it first, ask only what has changed, and keep everything else.

---

## Part 1, the interview

Ask these in order. Keep it conversational, one or two questions per message, and accept short answers. Every question maps to something specific that gets written, which is why none of them are optional.

### 1. The work

"In two or three sentences, what do you do and who do you do it for?"

Maps to: the opening paragraph of `CLAUDE.md`, and the tone of everything else.

### 2. The hats

"Which distinct roles or contexts do you work in? A hat is a context with its own people, its own deadlines and its own tempo. One line each. If you only have one, say so."

Then: "Which of these have someone external who chases you, and which move only when you push?"

Maps to: the hats list in `CLAUDE.md`, one router page per hat in `wiki/hats/`, and the weighting rule in `/weekly-review` about work nobody is chasing.

### 3. The unit of work

"What is the thing you work on? A case, a matter, a client, a project, a patient, a study, a deal, a ticket, a paper. What do you call it, and what does one look like from the day it starts to the day it ends?"

Maps to: what `wiki/cases/` is called in their library, the `type` vocabulary, and the shape of the example.

### 4. The page

"When you open a page about one of those, what do you need to see? Here is the default: what the situation is, who is involved and what each of them needs, what matters about it, what has happened so far, what happens next, what you do not know yet, and where it all came from. Rename, remove or add."

Maps to: the section template in `/new-case`, and the example page.

### 5. What comes in

"What lands on you in a week? Email, documents, data files, meeting notes, messages, recordings. Which formats, from whom, roughly how much."

Maps to: the ingest conventions and the naming pattern in `CLAUDE.md`.

### 6. What belongs

"What kind of information is worth keeping for years, and what is noise you would never want cluttering the library? Give me two or three examples of each."

Maps to: the quality filter in `CLAUDE.md`. This is the section that most decides whether the library stays useful, so push for concrete examples.

### 7. What must not leave

"Is there anything that must never appear in something that leaves your organisation? Names of tools, suppliers, sources, methods. And who is the reader who would attack how a document was made rather than what it says?"

Maps to: the confidentiality note in `CLAUDE.md`, and the reason paragraph in `wiki/workflows/voice.md`.

### 8. How they write

"What language is the library in? And how do you write when it is you writing, as opposed to a form letter? If you can paste two or three emails you have actually sent, that is the best calibration there is."

Maps to: `wiki/workflows/voice.md`, the "How you actually sound" section, and any banned phrases.

### 9. What must be right

"Name three to five facts from your current work that you would be embarrassed to get wrong in front of someone. A number, a date, a name, a term."

Maps to: the first assertions in `wiki/reference/eval-set.md`, so `fmquery.py --eval` has something real to check from day one.

---

## Part 2, apply

Now edit, in this order. Each step names the file and what changes.

1. **`wiki/reference/profile.md`.** Write the interview answers in full, with frontmatter (`type: reference`, `hat: bridging`, today's date). This is the durable record of the setup and what a re-run reads first.

2. **`CLAUDE.md`.** Replace every `<placeholder>`. Rewrite the opening paragraph from answer 1. Write the hats list from answer 2, and add the note about which ones nobody chases. Rewrite the quality filter from answer 6 with their examples. Add a confidentiality paragraph from answer 7 if there was anything. Set the ingest naming pattern from answer 5. Adjust the intent table so the examples use their words for the unit of work.

3. **`wiki/hats/`.** One router page per hat, using the template in `wiki/hats/README.md`. Delete `example-hat.md`, and replace its line under Hats in `wiki/index.md` with one line per real hat.

4. **`.claude/commands/new-case.md`.** Replace the section template with the sections from answer 4, in their words. If they call the unit of work something other than a case, say so at the top of the command and note that the folder is still `wiki/cases/`, renaming it is possible but touches the scripts.

5. **The example.** Delete `wiki/cases/example-talk/`, and any line in `wiki/index.md` that points at it. Write one fictional page in their domain, using the sections from step 4, with invented names and invented numbers. It exists so the dashboard renders something and so the shape is visible. Say in its TL;DR that it is fictional and should be deleted.

6. **`wiki/workflows/voice.md`.** Rewrite "How you actually sound" from answer 8. If they pasted emails, describe the traits you actually see in them, openings, hedges, asides, length, how they end. Rewrite the "Why this exists" reason from answer 7. Add banned phrases if any came up. If the language is not English, note that the shipped patterns in `voice.py` are English and that the mechanics still apply.

7. **`wiki/reference/eval-set.md`.** Replace the example assertions with real ones from answer 9. Each needs a page that exists, so create or point to the right page. Replace the example question too.

8. **`wiki/index.md`** and **`wiki/log.md`.** Update the index for the new hats. Replace the template log entries with one entry, dated today, `## YYYY-MM-DD onboard | Library set up for <name>`, listing what was configured.

9. **Run and verify.**
   ```
   python3 .claude/scripts/fmquery.py --dashboard
   python3 .claude/scripts/fmquery.py --eval
   python3 .claude/scripts/selftest.py
   ```
   All three must pass. If `--eval` fails, the assertion or the page is wrong, fix it now rather than leaving a failing check on day one.

10. **Commit.** `git add -A && git commit -m "onboard: library set up for <name>"`.

---

## Part 3, report

Tell them, briefly:

- Which files changed and what each now says, in one line per file.
- The three things they should read and correct if wrong: the hats list, the quality filter, and the voice section. Those are judgement calls you made from an interview, and they should be checked.
- That the example page is fictional and how to delete it.
- That `/onboard` can be re-run when a role is added or something changes, and it will read `profile.md` and ask only about the difference.

Do not summarise the architecture. They cloned the repository, they have the README.
