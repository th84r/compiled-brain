---
title: Frontmatter schema
type: workflow
status: active
confidence: verified
hat: bridging
created: 2026-01-01
updated: 2026-01-01
tags: [schema, frontmatter, convention]
related: [[brain-design.md]]
---

TL;DR. Every main page carries YAML frontmatter. Dates are ISO, always. Enforced by `.claude/hooks/validate.py` on write and read by `.claude/scripts/fmquery.py`.

## Universal fields

| Field | Required | Values |
|---|---|---|
| `title` | yes | free text |
| `type` | yes | `case`, `project`, `person`, `organization`, `reference`, `workflow` |
| `status` | for case and project | `active`, `waiting`, `on_hold`, `closed` |
| `confidence` | recommended | `verified`, `tentative` |
| `hat` | yes on work pages | one of your hats, or `bridging` |
| `created` | yes | YYYY-MM-DD |
| `updated` | yes | YYYY-MM-DD |
| `tags` | recommended | list |
| `related` | optional | list of `[[wikilinks]]` |
| `sources` | recommended | list of paths or URLs |

## Work fields, case and project only

| Field | Purpose |
|---|---|
| `next_action` | what happens next, in one line |
| `next_action_date` | when. A passed date is what the dashboard sorts on |
| `counterpart` | the other party, if there is one. A client, a supplier, a partner, an opponent |
| `value` | what is at stake, if quantifiable |
| `expires` | when an agreement ends |
| `review` | when volatile facts must be re-verified |

## Rules that are easy to get wrong

**Status carries no nuance.** Four values, nothing else. "Active but waiting for their lawyer" is `status: active` with the nuance in `next_action`. Put it in the status field and the dashboard can no longer group across pages, which is the whole reason the field exists.

**Dates are never relative.** "Next month" is not a date. Convert it when you write it.

**`review` belongs on volatile facts only.** A price, a term, a position, a role. Putting a review date on a historical chronology just creates noise that trains you to ignore the linter.

**`confidence: tentative` is not an admission of weakness.** It is what lets a derived conclusion be useful without becoming a false fact. Use it freely.

## Which pages need full frontmatter

Main pages: `overview.md` in any case or project folder, and anything under `reference/`, `themes/` or `workflows/`.

Sub-documents (chronology, preparation, working analysis) do not need it. They are free-form on purpose, because forcing a schema on working notes is how people stop writing working notes.

## TL;DR line

Every page opens with one line summarising the core, so relevance can be triaged before the page is read. This is the single highest-value convention in the schema and the one most often skipped.
