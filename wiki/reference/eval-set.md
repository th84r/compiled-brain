---
title: Eval set, the golden questions
type: reference
status: active
confidence: verified
hat: bridging
created: 2026-01-01
updated: 2026-01-01
tags: [eval, quality, testing]
---

TL;DR. Questions the library should be able to answer correctly and with a source. `/eval` runs them cold and records the pass rate below.

## How to use this

Add a question every time the library fails to answer something it should have. That failure is the most valuable signal you get, and it is free.

A good question has one right answer, a source, and would actually be asked. Avoid questions that only test whether a page exists.

## Two kinds of check

**Assertions** are deterministic. A page, a field, an expected value. `fmquery.py --eval` runs them with no model involved, so they can run in CI and they catch a silently changed fact the moment it changes. Use them for the numbers and terms you would be embarrassed to get wrong.

**Questions** need a model to answer. `/eval` runs them cold and scores the answers. Use them for the things that require reading and synthesis.

## Assertions

Columns are page (wiki-relative path), field (a frontmatter key, or `body` for the page text) and expected. An expected value starting with `~` matches as a case-insensitive substring, anything else must match exactly.

| page | field | expected |
|---|---|---|
| cases/example-talk/overview.md | status | active |
| cases/example-talk/overview.md | hat | example-hat |
| cases/example-talk/overview.md | body | ~abstract |
| workflows/frontmatter-schema.md | type | workflow |

## Key figures

The figures that are copied to more than one page, a price, a count, a deadline, and so are the first to go stale on one of them. Columns are key, value (as it is written on the page), page (where the figure lives), was (earlier values, separated by `;`) and also called (other names for it, separated by `,`). `fmquery.py --agree` fails when the value is missing from its page, or when another page still states an earlier value near the figure's name without dating it. A year, a date, a strikethrough or a word such as until, was or previously counts as dating it. When a figure changes, write the new value here and move the old one to was, the same way a page keeps the old fact with a date.

| key | value | page | was | also called |
|---|---|---|---|---|
| Expected audience | about 120 | cases/example-talk/overview.md | about 80 | audience |

## Questions

| # | Question | Expected answer | Source page |
|---|---|---|---|
| 1 | When is the abstract due, and who wants it? | 15 February, the programme committee | cases/example-talk/overview.md |
| 2 | _(replace with your own)_ | | |

## Pass rate over time

| Date | Passed | Partial | Failed | Notes |
|---|---|---|---|---|
| | | | | |
