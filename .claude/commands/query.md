---
description: Search the library, synthesise with citations, save answers worth keeping
---

You are running `/query`.

## 1. Understand the question

Is it about a case, a person, a market, a method, or a decision? That decides where to look first.

## 2. Search both zones

Start with `python3 .claude/scripts/fmquery.py --search "<terms>"`. It ranks every page and every log entry, archives included. Then read the top hits in full. Search your own persistent memory for the personal context. Read `wiki/status.md` if the question touches current state.

Search widely before answering. A confident answer built on the first file you opened is the most common failure mode here.

## 3. Synthesise

Answer the question directly, then support it. Every factual claim carries a source, either a wiki path or an original source file. Distinguish clearly between what a source says and what you concluded.

If the library cannot answer, say so plainly and say what is missing. A gap named is a gap that can be closed.

## 4. Save what has lasting value

If the answer required real synthesis and would be useful again, write it into the wiki as a new page or a new section on an existing one. Mark derived conclusions `confidence: tentative` with a `review` date.

Ephemeral answers stay in the conversation. Do not clutter the library with them.
