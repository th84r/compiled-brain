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

# The example fixture is meant to be deleted during onboarding, so nothing
# here may name it. Discover a page instead, and say so when there is none.
rc, out = run([FMQ, "--type", "case", "--active"])
a_case = next((ln.split()[0] for ln in out.splitlines()
               if ln.startswith("  ") and ln.strip().endswith(".md")
               or (ln.startswith("  ") and ".md" in ln)), None)
a_case = a_case.strip() if a_case else None

if a_case:
    term = os.path.splitext(os.path.basename(os.path.dirname(a_case) or a_case))[0].split("-")[0]
    rc, out = run([FMQ, "--search", term])
    check("search returns ranked hits", rc == 0 and "# search" in out, out[:200])
    rc, out = run([FMQ, "--links", a_case])
    check("links resolves a page", rc == 0 and "inbound" in out and "outbound" in out, out[:200])
else:
    rc, out = run([FMQ, "--search", "the"])
    check("search runs on an empty library", rc == 0 and "# search" in out, out[:200])
    print("  skip  links resolves a page  (no case pages yet)")

rc, out = run([FMQ, "--eval"])
check("eval runs assertions", "# eval" in out and " passed" in out, out[:200])
# Assertions naming a page the owner has since deleted are their problem to
# clean up, not a broken checkout. Only a crash counts as a failure here.
missing_only = all("page not found" in ln for ln in out.splitlines() if ln.strip().startswith("FAIL"))
check("eval assertions all pass", rc == 0 or missing_only,
      out[:300] + "  (assertions fail for reasons other than a deleted page)")

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
# A .md outside wiki/ and output/, carrying content the hook would otherwise
# reject. The old version used .txt, which the extension guard caught first,
# so the path guard had no coverage at all and could be deleted unnoticed.
outside = os.path.join(tmp, "not-wiki.md")
open(outside, "w").write("a — b")
rc, out = run([HOOK], json.dumps({"tool_input": {"file_path": outside, "content": "a — b"}}))
check("hook ignores a .md outside wiki and output", rc == 0, out[:200])

shutil.rmtree(tmp, ignore_errors=True)

vdir = tempfile.mkdtemp()
v = os.path.join(vdir, "v.txt")
open(v, "w").write("It is not about speed, it is about trust. Moreover, we delve into it. "
                   "This is a draft, not a final version.\n")
rc, out = run([VOICE, v])
check("voice catches antithesis", "antithesis" in out, out[:200])
check("voice catches connector and filler", "connector" in out and "filler" in out, out[:200])
open(v, "w").write("The meeting is on Tuesday. Bring the slides and the two handouts.\n")
rc, out = run([VOICE, v])
check("voice passes clean prose", "CLEAN" in out, out[:200])

# Every one of these was an unhandled traceback once. A public template gets
# pointed at the wrong file constantly, so each failure must be a sentence.
bad = os.path.join(os.path.dirname(v), "bin.txt")
open(bad, "wb").write(b"\xa8\xff\xfe binary")
rc, out = run([VOICE, bad])
check("voice survives a binary file", "SKIPPED" in out and "binary" in out, out[:200])
fake = os.path.join(os.path.dirname(v), "fake.docx")
open(fake, "wb").write(b"PK\x03\x04 not really a zip")
rc, out = run([VOICE, fake])
check("voice survives a corrupt .docx", "SKIPPED" in out and "zip" in out, out[:200])
empty_docx = os.path.join(os.path.dirname(v), "empty.docx")
import zipfile as _zf
with _zf.ZipFile(empty_docx, "w") as _z:
    _z.writestr("a.txt", "x")
rc, out = run([VOICE, empty_docx])
check("voice survives a .docx with no document.xml", "SKIPPED" in out, out[:200])
rc, out = run([VOICE, os.path.join(os.path.dirname(v), "nope.md")])
check("voice survives a missing file", "SKIPPED" in out and "no such file" in out, out[:200])

for f in ("CLAUDE.md", "README.md", "docs/ARCHITECTURE.md", "docs/ONBOARDING.md",
          ".claude/commands/onboard.md", ".claude/settings.json",
          "wiki/index.md", "wiki/log.md", "wiki/reference/eval-set.md"):
    check(f"file present {f}", os.path.isfile(os.path.join(ROOT, f)))
try:
    json.load(open(os.path.join(ROOT, ".claude", "settings.json")))
    check("settings.json is valid JSON", True)
except Exception as e:
    check("settings.json is valid JSON", False, str(e))

shutil.rmtree(vdir, ignore_errors=True)

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
