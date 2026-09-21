#!/usr/bin/env python3
"""selftest, proves the machinery works on this checkout.

Run it after cloning and after any change to the scripts. Every check is
something that has actually broken once. Exit 1 on the first failure so a
CI job can use it as-is.

    python3 .claude/scripts/selftest.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
FMQ = os.path.join(HERE, "fmquery.py")
VOICE = os.path.join(HERE, "voice.py")
HOOK = os.path.join(ROOT, ".claude", "hooks", "validate.py")
PY = sys.executable
fails = 0


def check(name, ok, detail=""):
    global fails
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail and not ok else ""))
    if not ok:
        fails += 1


def run(args, stdin=None):
    r = subprocess.run([PY] + args, input=stdin, capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout + r.stderr


print(f"selftest in {ROOT}")

rc, out = run([FMQ, "--dashboard"])
check("dashboard generates", rc == 0 and os.path.isfile(os.path.join(ROOT, "wiki", "status.md")), out[-200:])

for flag in (["--stale"], ["--orphans"], ["--type", "case"], ["--active"],
             ["--sort", "updated", "--desc"], ["--review-before", "today"]):
    rc, out = run([FMQ] + flag)
    check("fmquery " + " ".join(flag), rc == 0 and out.startswith("#"), out[:120])

rc, out = run([FMQ, "--search", "export clause"])
check("search returns ranked hits", rc == 0 and "# search" in out and "cases/" in out, out[:200])

rc, out = run([FMQ, "--links", "cases/example-renewal/overview.md"])
check("links resolves a page", rc == 0 and "inbound" in out and "outbound" in out, out[:200])

rc, out = run([FMQ, "--eval"])
check("eval runs assertions", "# eval" in out and " passed" in out, out[:200])
check("eval assertions all pass", rc == 0, out[:300])

rc, out = run([FMQ, "--rotate-log", "--dry-run"])
check("rotate-log dry run", rc == 0 and "rotate-log" in out, out[:200])

tmp = tempfile.mkdtemp()
bad = os.path.join(tmp, "wiki", "cases", "x", "overview.md")
os.makedirs(os.path.dirname(bad))
open(bad, "w").write("---\ntitle: T\ntype: case\nstatus: bogus\n---\nx")
rc, out = run([HOOK], json.dumps({"tool_input": {"file_path": bad, "content": "x"}}))
check("hook rejects status outside schema", rc == 2 and "outside the schema" in out, out[:200])
rc, out = run([HOOK], json.dumps({"tool_input": {"file_path": bad, "content": "a — b"}}))
check("hook rejects em dash", rc == 2 and "em dash" in out, out[:200])
rc, out = run([HOOK], json.dumps({"tool_input": {"file_path": "/tmp/not-wiki.txt", "content": "—"}}))
check("hook ignores files outside wiki/output", rc == 0)
shutil.rmtree(tmp)

v = os.path.join(tempfile.mkdtemp(), "v.txt")
open(v, "w").write("It is not about speed, it is about trust. Moreover, we delve into it. "
                   "This is a renewal, not a new deal.\n")
rc, out = run([VOICE, v])
check("voice catches antithesis", "antithesis" in out, out[:200])
check("voice catches connector and filler", "connector" in out and "filler" in out, out[:200])
open(v, "w").write("The meeting is on Tuesday. Bring the benchmark and the two draft clauses.\n")
rc, out = run([VOICE, v])
check("voice passes clean prose", "CLEAN" in out, out[:200])

for f in ("CLAUDE.md", "README.md", "docs/ARCHITECTURE.md", ".claude/settings.json",
          "wiki/index.md", "wiki/log.md", "wiki/reference/eval-set.md"):
    check(f"file present {f}", os.path.isfile(os.path.join(ROOT, f)))
try:
    json.load(open(os.path.join(ROOT, ".claude", "settings.json")))
    check("settings.json is valid JSON", True)
except Exception as e:
    check("settings.json is valid JSON", False, str(e))

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
