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

Without Claude Code, run it by hand on the pages you changed, or on everything
staged for a commit (exit 1 when a rule is broken):

    python3 .claude/hooks/validate.py wiki/cases/acme/overview.md
    python3 .claude/hooks/validate.py --staged

By hand the whole file is checked for em dashes, since there is no "newly
written" part to tell apart.
"""
import json
import os
import re
import subprocess
import sys

# Paths are judged relative to the library root, so a clone that happens to sit
# under a folder called wiki/ or reference/ is not mistaken for a wiki page.
ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


def rel_path(fp):
    """'/wiki/...' style path relative to the library root.

    A file outside the root (a scratch library in a test, say) is judged from
    the wiki/ or output/ folder nearest to it."""
    ap = os.path.abspath(fp).replace("\\", "/")
    r = os.path.relpath(ap, ROOT).replace("\\", "/")
    if not r.startswith(".."):
        return "/" + r
    i = max(ap.rfind("/wiki/"), ap.rfind("/output/"))
    return ap[i:] if i >= 0 else ""


def check(fp, new_text):
    """The rule violations for one file. new_text is what was just written."""
    if not fp.endswith(".md"):
        return []
    norm = rel_path(fp)
    if not (norm.startswith("/wiki/") or norm.startswith("/output/")):
        return []

    issues = []
    for ch, label in BANNED_CHARS.items():
        if ch in new_text:
            issues.append(f"New content contains {label}. "
                          "Use a comma, a full stop, or rewrite.")

    base = os.path.basename(norm)
    is_main = (base == "overview.md") or any(d in norm for d in MAIN_DIRS)
    if (norm.startswith("/wiki/") and is_main
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

    # Wikilinks in frontmatter must be quoted, related: ["[[a]]", "[[b]]"].
    # Unquoted, YAML reads them as lists inside lists and Obsidian sees no links.
    if norm.startswith("/wiki/") and os.path.isfile(fp):
        t = open(fp, encoding="utf-8", errors="ignore").read().lstrip()
        if t.startswith("---"):
            e = t.find("\n---", 3)
            for line in (t[3:e] if e != -1 else "").splitlines():
                if re.match(r"^[A-Za-z_][A-Za-z0-9_]*:\s*\[\[", line):
                    issues.append("Frontmatter has unquoted wikilinks (" + line.split(":")[0]
                                  + "). Write them as [\"[[a]]\", \"[[b]]\"] so YAML and Obsidian read them as links.")
                    break

    return issues


def main():
    """Hook mode. Claude Code sends the write as JSON on stdin."""
    data = json.loads(sys.stdin.read())
    ti = data.get("tool_input", {}) or {}
    fp = ti.get("file_path") or ti.get("path") or ""
    issues = check(fp, ti.get("content") or ti.get("new_string") or "")
    if issues:
        sys.stderr.write("Wiki validation (" + os.path.basename(fp) + "):\n- "
                         + "\n- ".join(issues) + "\n")
        return 2
    return 0


def cli(args):
    """By hand or from a git pre-commit hook. Checks whole files."""
    if args == ["--staged"]:
        out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                             capture_output=True, text=True, cwd=ROOT).stdout
        args = [os.path.join(ROOT, f) for f in out.split() if f.endswith(".md")]
    bad = 0
    for fp in args:
        if not os.path.isfile(fp):
            print(f"{fp}: no such file")
            bad += 1
            continue
        text = open(fp, encoding="utf-8", errors="ignore").read()
        issues = check(fp, text)
        if issues:
            bad += 1
            print(f"{fp}:\n- " + "\n- ".join(issues))
    print("ok" if not bad else f"{bad} file(s) break the rules")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(cli(sys.argv[1:]))
    try:
        sys.exit(main())
    except Exception:
        # Fail open. A broken hook must never block a session.
        sys.exit(0)
