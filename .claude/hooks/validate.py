#!/usr/bin/env python3
"""PostToolUse hook. Validates wiki markdown on every Write and Edit.

Conventions that depend on discipline stop working in month three. This is
the machine that keeps the schema true.

High precision, few false positives, and it fails open. A broken hook must
never block a working session, so any unexpected exception exits 0.

Exit 2 plus a message on stderr when a rule is broken, which is what lets the
agent see the problem and fix it in the same turn.

Two deliberate design choices:

- The em dash check runs only on NEWLY WRITTEN text (content / new_string),
  so old em dashes already sitting in a file are not re-flagged on every
  future edit of that file.
- Frontmatter requirements apply only to main pages (overview.md plus
  anything under reference/, themes/, workflows/), not to chronology,
  preparation or working sub-documents, which are free-form on purpose.

Wire it up in .claude/settings.json under hooks.PostToolUse.
"""
import json
import os
import re
import sys

MAIN_DIRS = ("/reference/", "/themes/", "/workflows/")

# Keep in sync with .claude/scripts/fmquery.py and the schema page.
# Nuance belongs in 'next_action', not in the status field, otherwise the
# dashboard cannot group across pages.
STATUS_VALUES = ("active", "waiting", "on_hold", "closed")

# Characters that should never appear in newly written prose.
BANNED_CHARS = {
    "—": "em dash (—)",
    "―": "horizontal bar (―)",
}


def main():
    data = json.loads(sys.stdin.read())
    ti = data.get("tool_input", {}) or {}
    fp = ti.get("file_path") or ti.get("path") or ""
    if not fp.endswith(".md"):
        return 0
    norm = fp.replace("\\", "/")
    if not ("/wiki/" in norm or "/output/" in norm):
        return 0

    issues = []

    new_text = ti.get("content") or ti.get("new_string") or ""
    for ch, label in BANNED_CHARS.items():
        if ch in new_text:
            issues.append(f"New content contains {label}. "
                          "Use a comma, a full stop, or rewrite.")

    base = os.path.basename(norm)
    is_main = (base == "overview.md") or any(d in norm for d in MAIN_DIRS)
    if ("/wiki/" in norm and is_main
            and base not in ("index.md", "log.md", "status.md")
            and "/assets/" not in norm):
        if os.path.isfile(fp):
            text = open(fp, encoding="utf-8", errors="ignore").read()
            if not text.lstrip().startswith("---"):
                issues.append("Main page has no frontmatter (must start with ---). "
                              "See wiki/workflows/frontmatter-schema.md")
            else:
                fm = {}
                s = text.lstrip()[3:]
                end = s.find("\n---")
                if end != -1:
                    for line in s[:end].splitlines():
                        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s?(.*)$", line)
                        if m:
                            fm[m.group(1)] = m.group(2).strip()
                if not fm.get("title"):
                    issues.append("Frontmatter is missing 'title'.")
                if not fm.get("type"):
                    issues.append("Frontmatter is missing 'type'.")
                if fm.get("type") in ("case", "project"):
                    st = str(fm.get("status", "")).strip().lower()
                    if not st:
                        issues.append(f"Type '{fm.get('type')}' is missing 'status'.")
                    elif st not in STATUS_VALUES:
                        issues.append(
                            f"Status '{fm.get('status')}' is outside the schema. "
                            f"Use one of {', '.join(STATUS_VALUES)} and put the "
                            "nuance in 'next_action'.")

    if issues:
        sys.stderr.write("Wiki validation (" + base + "):\n- "
                         + "\n- ".join(issues) + "\n")
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Fail open. A broken hook must never block a session.
        sys.exit(0)
