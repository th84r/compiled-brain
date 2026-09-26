---
description: Get a new library working in a couple of minutes, three questions and the first documents. /shape does the full interview later
---

You are running `/onboard`. The goal is that the owner sees the library do something useful with their own material within a few minutes. The full interview that shapes the library to their work is `/shape`, and it is offered afterwards, once they have seen why it is worth ten minutes.

Four rules for the whole run.

**Three questions, then act.** Ask the three questions below, then edit. Nothing else is asked now.

**Write in their language.** If they answer in French, the hats and the profile are written in French, and so is every answer from now on.

**Keep the books at home.** Before the first question, run `git remote -v`. If a remote still points to the public template, remove it with `git remote remove origin` and tell the owner why, so their own material can never be pushed there by mistake. Leave any other remote alone and mention it.

**Plain words.** Assume they may be new to terminals and agents. Explain any file or term the first time it comes up.

If `wiki/reference/profile.md` already exists, the library is set up. Say so in one line and offer `/shape` or a first ingest instead.

**Answers given in an app.** If `.claude/onboarding-answers.md` exists, the owner has already answered somewhere else, for example in Pacioli for Mac. Read the answers from it and ask only what is missing. The app that wrote the file removes it afterwards, so leave it where it is. If every answer is there, go straight to Part 2.

**Start with a one-line welcome.** "Three short questions, then we put your first documents in and you can ask about them."

---

## Part 1, three questions

### 1. The work

"In two or three sentences, what do you do and who do you do it for?"

Maps to: the opening paragraph of `CLAUDE.md`.

### 2. The hats

"Which distinct roles or contexts do you work in? A hat is a context with its own people, its own deadlines and its own tempo. One line each. If you only have one, say so. Which of them move only when you push, with nobody outside chasing you?"

Maps to: the hats list in `CLAUDE.md`, one router page per hat in `wiki/hats/`, and `own_hats` in the profile.

### 3. The language

"Which language should the library be kept in?"

Maps to: every page and answer from now on.

---

## Part 2, apply

1. **`wiki/reference/profile.md`.** The three answers, with frontmatter (`title`, `type: reference`, `hat: bridging`, `created` and `updated` today) and `own_hats: [...]` with the keys of the hats nobody outside chases, `owner:` with the owner's name and `language:` with the library's language named in English, such as Danish. Leave out `shaped:`, which `/shape` sets.
2. **`CLAUDE.md`.** Rewrite the opening paragraph from answer 1 and the hats list from answer 2. Leave every other `<placeholder>` for `/shape`.
3. **`wiki/hats/`.** One router page per hat, using the template in `wiki/hats/README.md`, with a short `name:` that is the hat's name as the owner says it, since that is what the app shows. Delete `example-hat.md`, and replace its line in `wiki/index.md` with one line per real hat. Move the example case to one of the real hats by changing its `hat:` field, and say in its TL;DR that it is fictional.
4. **The template's own pages in the owner's language.** When the library is kept in another language than English, give the pages the template brings, the eval set, the page template, the voice page, open questions and the frontmatter schema, a `title:` and a TL;DR line in that language. Keep their paths and their tables as they are. An owner should never meet an English page title in their own books.
5. **`wiki/log.md`.** Replace the template log entries with one entry, dated today, `## YYYY-MM-DD onboard | Library set up for <name> (initials)`, naming by path every page you created, changed or removed. That entry is the opening balance.
6. **Run and verify.**
   ```
   python3 .claude/scripts/fmquery.py --dashboard
   python3 .claude/scripts/fmquery.py --balance
   python3 .claude/scripts/selftest.py
   ```
   If `--balance` lists a page, add it to the onboard entry.
7. **Commit.** Stage what you changed with `git add` and the paths, then `git commit -m "onboard | Library set up for <name>"`. If git does not know who they are, which happens on a machine where git has never been set up, ask for the name and email they want on their own history and set them for this library only with `git config user.name "<name>"` and `git config user.email "<email>"`, then commit again. Their books stay on their machine, so any address will do.

---

## Part 3, the first documents

This is the moment they decide whether to keep using it, so do it with them now.

1. Ask for three to five recent documents from one piece of current work. They can drag them into `inbox/pending/` or into this window.
2. Take them in with `/ingest`.
3. Ask them to put one question about that work in plain words, and answer it with its sources.
4. Then, in three lines, tell them what they can simply say from now on ("take this in", "what do we know about ...", "open a case for ...", "weekly status"), and offer `/shape`, "Nine questions that fit the library to how you work, about ten minutes, whenever you like."

Do not summarise the architecture.
