---
description: Measure the library against a golden set of questions, track the pass rate
---

You are running `/eval`.

## 1. Read the golden set

`wiki/reference/eval-set.md` holds questions the library should be able to answer, each with the expected answer and its source.

If the file is thin, the first useful thing you can do is grow it. Every time the library fails to answer something it should have, that question belongs here.

## 2. Answer cold

Answer each question using only the library, as if you had no memory of this conversation. Do not lean on reasoning a previous iteration wrote. Judge the page as it stands.

This is the hardest part and the reason the operation exists. A model grading its own earlier work grades generously.

## 3. Score

For each question: pass, partial, or fail. A partial is an answer that is correct but missing the source, or correct but stale.

## 4. Record and fix

Append the date and the pass rate to `wiki/reference/eval-set.md` so the trend is visible. For every failure, write a fix note naming the page that should have held the answer.

Fix at most five pages, then stop and report.
