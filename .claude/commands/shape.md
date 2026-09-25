---
description: Shape the library to the owner's work with a nine-question interview. Run after /onboard, re-run when a role is added
---

You are running `/shape`. `/onboard` got the library working in a couple of minutes with three questions. This is the second step, offered once the owner has seen the library answer something real. The template was generalised from one person's work, and a template that is never adapted is a template that gets ignored. Your job is to learn this person's work well enough to adapt it for them, then do the adapting, then show them what changed.

Three rules for the whole run.

**Ask, then act.** Do the interview first, in one pass, and only then edit files. Do not edit after each answer, it produces a library shaped by whatever was said last.

**Write in their language.** If they answer in French, the hats, the quality filter and the example case are written in French. The scripts do not care, and the library should read like theirs.

**Keep the books at home.** Before the interview, run `git remote -v`. If a remote still points to the public template, remove it with `git remote remove origin` and tell the owner why, so their own material can never be pushed there by mistake. Leave any other remote alone and mention it.

Read `wiki/reference/profile.md` first. `/onboard` has already asked about the work, the hats and the language, so confirm those in one line each ("You said ... is that still right?") and ask only the rest. If the profile has `shaped:` with a date, this is a re-run, ask only what has changed and keep everything else.

**Answers given in an app.** If `.claude/onboarding-answers.md` exists, the owner has already answered the nine questions somewhere else, for example in Pacioli for Mac. Read the answers from it, skip the welcome and the questions it answers, and ask only what is missing. An answer marked `(skipped)` keeps the template's default for that part, and the report says so. The app that wrote the file removes it afterwards, so leave it where it is.

**Start with a short welcome.** Before the first question, tell them in plain words what is about to happen. Something like: "I will ask you nine short questions about your work, it takes about ten minutes. Short answers are fine, and you can say skip and come back to it later. Then I shape the library to fit, check that everything works, and show you how to use it." Assume they may be new to terminals and agents, avoid jargon, and explain any file or term the first time it comes up.

**Show progress.** Number the questions as you go, "Question 3 of 9", so they always know how far they are.

---

## Part 1, the interview

Ask these in order. Keep it conversational, one or two questions per message, and accept short answers. Every question maps to something specific that gets written, which is why none of them are optional.

### 1. The work

"In two or three sentences, what do you do and who do you do it for?"

Maps to: the opening paragraph of `CLAUDE.md`, and the tone of everything else.

### 2. The hats

"Which distinct roles or contexts do you work in? A hat is a context with its own people, its own deadlines and its own tempo. One line each. If you only have one, say so."

Then: "Which of these have someone external who chases you, and which move only when you push?"

Maps to: the hats list in `CLAUDE.md`, one router page per hat in `wiki/hats/`, and the note in `CLAUDE.md` on which hats nobody chases, which `/weekly-review` uses to weight overdue work.

### 3. The unit of work

"What is the thing you work on? A case, a matter, a client, a project, a patient, a study, a deal, a ticket, a paper. What do you call it, and what does one look like from the day it starts to the day it ends?"

Maps to: what `wiki/cases/` is called in their library, the `type` vocabulary, and the shape of the example.

### 4. The page

"When you open a page about one of those, what do you need to see? Here is the default: what the situation is, who is involved and what each of them needs, what matters about it, what has happened so far, what happens next, what you do not know yet, and where it all came from. Rename, remove or add."

Maps to: `wiki/workflows/page-template.md`, which `/new-case` follows, and the example page.

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

1. **`wiki/reference/profile.md`.** Add the interview answers in full under the ones `/onboard` wrote, and set `shaped: <today>` in the frontmatter, which is how the app and a re-run know the interview has been done. Keep `own_hats: [...]` current from answer 2. This is the durable record of the setup and what a re-run reads first.

2. **`CLAUDE.md`.** Replace every `<placeholder>`. Rewrite the opening paragraph from answer 1. Write the hats list from answer 2, and add the note about which ones nobody chases. Rewrite the quality filter from answer 6 with their examples. Add a confidentiality paragraph from answer 7 if there was anything. Set the ingest naming pattern from answer 5. Adjust the intent table so the examples use their words for the unit of work.

3. **`wiki/hats/`.** One router page per hat, using the template in `wiki/hats/README.md`. Delete `example-hat.md`, and replace its line under Hats in `wiki/index.md` with one line per real hat.

4. **`wiki/workflows/page-template.md`.** Replace the sections with those from answer 4, in their words, and say what the unit of work is called from answer 3. If they call it something other than a case, note that the folder is still `wiki/cases/`, renaming it is possible but touches the scripts.

5. **The example.** Delete `wiki/cases/example-talk/`, and any line in `wiki/index.md` that points at it. Write one fictional page in their domain, using the sections from step 4, with invented names and invented numbers. It exists so the dashboard renders something and so the shape is visible. Say in its TL;DR that it is fictional and should be deleted. Give it no `next_action_date`, so it never shows as overdue on the owner's first day.

6. **`wiki/workflows/voice.md`.** Rewrite "How you actually sound" from answer 8. If they pasted emails, describe the traits you actually see in them, openings, hedges, asides, length, how they end. Rewrite the "Why this exists" reason from answer 7. Add banned phrases if any came up. If the language is not English, note that the shipped patterns in `voice.py` are English and that the mechanics still apply.

7. **`wiki/reference/eval-set.md`.** Replace the example assertions with real ones from answer 9. Each needs a page that exists, so create or point to the right page. Replace the example question too.

8. **`wiki/index.md`** and **`wiki/log.md`.** Update the index for the new hats. Append one entry, dated today, `## YYYY-MM-DD shape | Library shaped to <name>'s work (initials)`, listing what was configured and naming by path every page you created, changed or removed, in the same commit as those pages. `fmquery.py --balance` checks it in step 9. If several people will share the library, ask who they are and write the cadence table in `CLAUDE.md` with their names.

9. **Run and verify.**
   ```
   python3 .claude/scripts/fmquery.py --dashboard
   python3 .claude/scripts/fmquery.py --eval
   python3 .claude/scripts/fmquery.py --balance
   python3 .claude/scripts/selftest.py
   ```
   All four must pass. If `--eval` fails, the assertion or the page is wrong, fix it now rather than leaving a failing check on day one. If `--balance` lists a page, add it to the onboard log entry.

10. **Commit.** `git add -A && git commit -m "shape | Library shaped to <name>'s work"`. If git says it does not know who they are, which happens on a machine where git has never been set up, ask for the name and email they want on their own history and set them for this library only with `git config user.name "<name>"` and `git config user.email "<email>"`, then commit again. Their books stay on their machine, so any address will do.

---

## Part 3, report

Keep this short and friendly, it is the moment they decide whether to keep using it. Tell them, briefly:

- Which files changed and what each now says, in one line per file.
- The three things they should read and correct if wrong: the hats list, the quality filter, and the voice section. Those are judgement calls you made from an interview, and they should be checked.
- That the example page is fictional and how to delete it.
- That `/shape` can be re-run when a role is added or something changes, and it will read `profile.md` and ask only about the difference.
- How to use it from now on, as a short list of things they can simply say:
  - "take this in", after putting files in `inbox/pending/`
  - "what do we know about ...", to ask the library
  - "open a case for ...", when a new piece of work starts
  - "weekly status", for what is due and what has gone quiet
  They never need to type the commands, plain words are enough.
- What to do next. If `inbox/pending/` is empty and nothing has been taken in yet, suggest three to five recent documents from one piece of current work and say "take this in".

Do not summarise the architecture. They cloned the repository, they have the README.
