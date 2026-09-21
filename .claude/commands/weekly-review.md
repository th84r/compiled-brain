---
description: What needs attention this week, in priority order
---

You are running `/weekly-review`.

## 1. Generate, do not recall

```
python3 .claude/scripts/fmquery.py --dashboard
python3 .claude/scripts/fmquery.py --stale
```

Read `wiki/status.md`. Never build this review from memory of what was happening last week.

## 2. Group by what actually forces action

- **Overdue.** A passed `next_action_date` or `review`. Say how many days.
- **This week.** Deadlines, meetings, dates falling within seven days.
- **Drifting.** Active cases untouched for more than 90 days. These are the expensive ones, because nothing external is reminding anyone.
- **Waiting on others.** Things that are blocked, and how long they have been blocked.

## 3. Weight by who is chasing

Work where someone else is waiting on you pushes on its own. Work where nobody is chasing moves only when the owner pushes, so it falls out of sight first. Treat a passed date in that group as more serious than one on work that chases itself.

## 4. Recommend

Name the three things that matter most this week and say why. A list of twenty items is a list nobody acts on.
