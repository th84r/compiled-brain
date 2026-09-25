# Onboarding

The template was generalised from one person's work, and every generalisation leaves a shape behind. The section names, the quality filter, the example and the intent table all carry assumptions about what a working day looks like. Editing those by hand is the step people skip, and a template with the wrong shape gets quietly abandoned around week three.

Setting up happens in two steps, so the library is useful before it is perfect.

**`/onboard`, a couple of minutes.** Say "set this up for me". It asks three things, what you do, which hats you wear and which of them nobody chases, and which language the library is kept in. It writes the profile, the hats and the first journal entry, then takes in your first three to five documents with you and answers a question about them with its sources.

**`/shape`, about ten minutes, whenever you like.** Say "shape this to my work". It confirms the three answers and asks the rest.

## What /shape does

It interviews you. Nine questions, one pass, short answers are fine, and the three `/onboard` asked are only confirmed. Each question maps to a specific file, which is why none of them are optional.

| It asks about | It writes |
|---|---|
| What you do and for whom | The opening of `CLAUDE.md` |
| Your roles, and which ones nobody chases | The hats list, one router page per hat, and a note on which ones nobody chases |
| Your unit of work and what you call it | The `type` vocabulary and the example |
| What a page about one should show | The sections in `wiki/workflows/page-template.md`, which `/new-case` follows |
| What lands on you in a week | Ingest conventions and naming |
| What is worth keeping and what is noise | The quality filter, with your examples |
| What must never leave, and who would attack a document's origin | The confidentiality note and the reason in `voice.md` |
| Your language and how you write | The voice calibration, ideally from emails you have sent |
| Facts you would be embarrassed to get wrong | The first real assertions in `eval-set.md` |

Then it edits, sets `shaped:` in the profile, runs the dashboard, the eval and the selftest, commits, and tells you which three things to check because they were judgement calls: the hats, the quality filter, and the voice section.

## What it does not do

It does not rename `wiki/cases/`. If you call your unit of work something else, the command notes it and the folder stays, because the scripts point at it. Renaming is a five-minute job if you want it.

It does not touch the scripts. The machinery is the same for a lawyer, a researcher and a product manager. What differs is the schema vocabulary and the words on the pages, and that is what the onboarding changes.

## Re-running it

`/shape` reads `wiki/reference/profile.md`, the record of your first answers, and asks only about what has changed. Adding a role, changing what counts as noise, or recalibrating the voice after a year of drift are all re-runs.

## If you would rather do it by hand

Open `CLAUDE.md`, replace everything in angle brackets, rewrite the quality filter, and set your voice in `wiki/workflows/voice.md`. Delete the example case. That is the same result, done manually.
