---
title: Why the library is built this way
type: workflow
status: active
confidence: verified
hat: bridging
created: 2026-01-01
updated: 2026-01-01
tags: [design, architecture, method]
related: ["[[frontmatter-schema.md]]", "[[self-improvement.md]]"]
---

TL;DR. The library is kept like a set of books. Raw material is posted, each page is an account, the log is the journal, the dashboard is a balance sheet computed from the accounts, `--balance` proves journal and accounts agree, and nothing is ever rubbed out. Four things keep it honest, a generated dashboard, explicit reconciliation of contradictions, expiring inference, and machine-enforced schema. Full reasoning in `docs/ARCHITECTURE.md`.

## The five invariants

Everything else is adjustable. These are not.

1. **The dashboard is generated, never written.** A hand-written status page is accurate for a week and then lies.
2. **Facts are invalidated rather than overwritten.** The old value stays with its date, so "what was it last time" remains answerable.
3. **Inference expires.** Anything derived carries `confidence: tentative` and a `review` date.
4. **Additive runs, reductive proposes.** Split by reversibility. The loop may add, a human decides what gets removed.
5. **Content is archived, never deleted.** Auditability over tidiness.

## The two zones

The wiki holds knowledge about the work. Agent memory holds knowledge about the person. Separate lifecycles, separate readers, cross-referenced and never duplicated.

## What to change when you adapt this

The hats, the quality filter in `CLAUDE.md`, and the voice rules. Leave invariant 3 alone, it is the easiest to drop and the most expensive to lose.
