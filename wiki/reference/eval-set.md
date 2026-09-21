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

**Assertions** are deterministic. A page, a field, an expected value. `fmquery.py --eval` runs them with no model involved, so they belong in CI and they catch a silently changed fact the moment it changes. Use them for the numbers and terms you would be embarrassed to get wrong.

**Questions** need a model to answer. `/eval` runs them cold and scores the answers. Use them for the things that require reading and synthesis.

## Assertions

Columns are page (wiki-relative path), field (a frontmatter key, or `body` for the page text) and expected. An expected value starting with `~` matches as a case-insensitive substring, anything else must match exactly.

| page | field | expected |
|---|---|---|
| cases/example-renewal/overview.md | status | active |
| cases/example-renewal/overview.md | counterpart | Northwind Software |
| cases/example-renewal/overview.md | body | ~export clause |
| workflows/frontmatter-schema.md | type | workflow |

## Questions

| # | Question | Expected answer | Source page |
|---|---|---|---|
| 1 | What does Northwind want and what do we want instead? | A three-year term at a held price; we want annual terms plus a data-export clause | cases/example-renewal/overview.md |
| 2 | _(replace with your own)_ | | |

## Pass rate over time

| Date | Passed | Partial | Failed | Notes |
|---|---|---|---|---|
| | | | | |
