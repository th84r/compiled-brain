#!/usr/bin/env python3
"""selftest, proves the machinery works on this checkout.

Run it after cloning and after any change to the scripts. Every check is
something that has actually broken once. Exit 1 on the first failure so a
CI job can use it as-is.

    python3 .claude/scripts/selftest.py
"""
import datetime
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

# The trial balance must catch a page changed with no journal entry. A
# throwaway account is posted without a log line, checked, and removed.
rc, out = run([FMQ, "--balance"])
check("balance runs", rc in (0, 1) and out.startswith("# Trial balance"), out[:200])
probe_dir = os.path.join(ROOT, "wiki", "cases", "zz-selftest-probe")
os.makedirs(probe_dir, exist_ok=True)
try:
    with open(os.path.join(probe_dir, "overview.md"), "w", encoding="utf-8") as f:
        f.write("---\ntitle: probe\ntype: case\nstatus: active\nhat: bridging\n"
                f"created: {datetime.date.today()}\nupdated: {datetime.date.today()}\n---\n\nTL;DR. probe\n")
    rc, out = run([FMQ, "--balance"])
    check("balance flags an unposted page", rc == 1 and "zz-selftest-probe" in out, out[:300])
finally:
    shutil.rmtree(probe_dir, ignore_errors=True)

# The JSON contract with the Mac app. Every report parses, carries the
# contract number, and the balance keeps its exit code in JSON mode.
def as_json(args):
    rc, out = run([FMQ] + args + ["--json"])
    try:
        return rc, json.loads(out.strip().splitlines()[-1])
    except Exception:
        return rc, {"_raw": out[:200]}


rc, d = as_json(["--contract"])
check("json contract number", d.get("contract") == 1 and "changes" in d.get("features", []), str(d)[:200])
rc, d = as_json(["--balance"])
check("json balance", "balanced" in d and rc == (0 if d.get("balanced") else 1), str(d)[:200])
rc, d = as_json(["--eval"])
check("json eval", "passed" in d and "failures" in d, str(d)[:200])
rc, d = as_json(["--stale"])
check("json stale", isinstance(d.get("stale"), list), str(d)[:200])
rc, d = as_json(["--hats"])
check("json hats have display names", isinstance(d.get("hats"), list)
      and all("title" in h and "own" in h for h in d["hats"]), str(d)[:200])
rc, d = as_json(["--type", "case"])
check("json page list", isinstance(d.get("pages"), list), str(d)[:200])
if os.path.isdir(os.path.join(ROOT, ".git")):
    rc, d = as_json(["--changes", "HEAD"])
    check("json changes for the last commit", rc == 0 and "pages" in d and "journal" in d, str(d)[:200])
    rc, d = as_json(["--changes", "no-such-commit"])
    check("json changes reports a bad commit", rc == 2 and "error" in d, str(d)[:200])

# The ledger, every commit balancing on its own. Played out on a throwaway
# git copy: a silent change must be caught, a late entry naming the commit
# must clear it, and a commit that posts its own entry must pass.
def _git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          cwd=cwd, capture_output=True, text=True)


if shutil.which("git"):
    ltmp = tempfile.mkdtemp()
    try:
        for d in ("wiki", ".claude"):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(ltmp, d),
                            ignore=shutil.ignore_patterns("__pycache__"))
        _git(ltmp, "init", "-q")
        _git(ltmp, "add", "-A")
        _git(ltmp, "commit", "-qm", "root")
        lf = os.path.join(ltmp, ".claude", "scripts", "fmquery.py")
        subprocess.run([PY, lf, "--open-ledger"], capture_output=True, cwd=ltmp)
        _git(ltmp, "add", "-A")
        _git(ltmp, "commit", "-qm", "open ledger")
        page = next((os.path.join(r, f) for r, _, fs in os.walk(os.path.join(ltmp, "wiki", "cases"))
                     for f in fs if f == "overview.md"), None)
        if page:
            rel = os.path.relpath(page, os.path.join(ltmp, "wiki"))
            open(page, "a", encoding="utf-8").write("\nA silent line.\n")
            _git(ltmp, "commit", "-qam", "silent")
            sha = _git(ltmp, "rev-parse", "--short=7", "HEAD").stdout.strip()
            r = subprocess.run([PY, lf, "--balance", "--json"], capture_output=True, text=True, cwd=ltmp)
            d = json.loads(r.stdout.strip().splitlines()[-1])
            check("ledger catches a silent commit", r.returncode == 1
                  and any(rel in c["pages"] for c in d.get("unposted_commits", [])), r.stdout[:300])
            open(os.path.join(ltmp, "wiki", "log.md"), "a", encoding="utf-8").write(
                f"\n## {datetime.date.today()} correction | Late entry\n\nA line was added in {sha} without an entry.\n")
            _git(ltmp, "commit", "-qam", "late entry")
            r = subprocess.run([PY, lf, "--balance"], capture_output=True, text=True, cwd=ltmp)
            check("a late entry naming the commit clears it", r.returncode == 0, r.stdout[-300:])
            open(page, "a", encoding="utf-8").write("\nA posted line.\n")
            open(os.path.join(ltmp, "wiki", "log.md"), "a", encoding="utf-8").write(
                f"\n## {datetime.date.today()} update | Posted\n\n{rel} got a line.\n")
            _git(ltmp, "commit", "-qam", "update | posted")
            r = subprocess.run([PY, lf, "--balance"], capture_output=True, text=True, cwd=ltmp)
            check("a commit that posts its own entry balances", r.returncode == 0, r.stdout[-300:])

        # Key figures. A stale undated copy fails, a dated one passes.
        figs = subprocess.run([PY, lf, "--agree", "--json"], capture_output=True, text=True, cwd=ltmp)
        fd = json.loads(figs.stdout.strip().splitlines()[-1])
        check("agree runs", "figures" in fd, figs.stdout[:200])
        rows = []
        sys.path.insert(0, os.path.dirname(lf))
        if fd.get("figures"):
            import importlib.util as _ilu
            _spec = _ilu.spec_from_file_location("fmq_copy", lf)
            _m = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_m)
            rows = [r_ for r_ in _m.key_figures() if r_["was"]]
        if rows:
            f0 = rows[0]
            probe = os.path.join(ltmp, "wiki", "zz-agree-probe.md")
            open(probe, "w", encoding="utf-8").write(
                f"---\ntitle: probe\ntype: reference\n---\n\nThe {f0['names'][0]} is {f0['was'][0]} today.\n")
            r = subprocess.run([PY, lf, "--agree"], capture_output=True, text=True, cwd=ltmp)
            check("agree catches a stale copy", r.returncode == 1 and "zz-agree-probe" in r.stdout, r.stdout[:300])
            open(probe, "w", encoding="utf-8").write(
                f"---\ntitle: probe\ntype: reference\n---\n\nThe {f0['names'][0]} was {f0['was'][0]} until 2025.\n")
            r = subprocess.run([PY, lf, "--agree"], capture_output=True, text=True, cwd=ltmp)
            check("agree accepts a dated old value", r.returncode == 0, r.stdout[:300])
    finally:
        shutil.rmtree(ltmp, ignore_errors=True)

# Status words in all four languages. A Norwegian closed case and a Swedish
# waiting one must be read as such, and a made-up word must not.
sys.path.insert(0, HERE)
from vocabulary import canonical_status  # noqa: E402
for word, want in (("avsluttet", "closed"), ("väntar", "waiting"), ("i bero", "on_hold"),
                   ("afventer (svar fra X)", "waiting"), ("Aktiv", "active"), ("forhandling", "")):
    check(f"status word {word!r}", canonical_status(word) == want, canonical_status(word))

# The permissions the library ships with. Writing the wiki and running its
# own scripts is allowed, reaching the network from the shell and pushing
# are not, and the agent may not widen its own permissions.
try:
    perm = json.load(open(os.path.join(ROOT, ".claude", "settings.json"))).get("permissions", {})
except Exception:
    perm = {}
allow, deny = perm.get("allow", []), perm.get("deny", [])
check("permissions allow writing the wiki", "Edit(wiki/**)" in allow)
# Claude Code reads only Edit(path) rules for files, and they cover every tool that writes one.
# A Write(path) rule is ignored with a warning at every start, so none may ship.
check("file rules are Edit rules only", not any(r.startswith("Write(") for r in allow + deny))
check("permissions allow the library's scripts by name", "Bash(python3 .claude/scripts/fmquery.py *)" in allow
      and not any(r.startswith("Bash(python3 .claude/scripts/*") for r in allow))
check("permissions allow no shell command that can write where it likes",
      not any(r.split("(")[0] == "Bash" and r[5:].split(" ")[0].rstrip("*)") in ("find", "sort", "echo", "cat", "mv", "tee", "cp")
              for r in allow))
check("the agent may not change .claude", "Edit(.claude/**)" in deny)
check("permissions deny the network from the shell", "Bash(curl *)" in deny and "Bash(wget *)" in deny)
check("permissions deny push and self-editing", any(x.startswith("Bash(git push") for x in deny)
      and "Edit(.claude/settings.json)" in deny)

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
check("rotate-log dry run", rc == 0 and "# rotate-log" in out, out[:200])

# A real rotation on a copy. Every entry is dated five years back first, so
# log.md is left with its header only, which once broke both the dry run and
# the opening balance. The balance must read the same before and after.
rtmp = tempfile.mkdtemp()
try:
    shutil.copytree(os.path.join(ROOT, "wiki"), os.path.join(rtmp, "wiki"))
    os.makedirs(os.path.join(rtmp, ".claude", "scripts"))
    shutil.copy(FMQ, os.path.join(rtmp, ".claude", "scripts", "fmquery.py"))
    shutil.copy(os.path.join(HERE, "vocabulary.py"), os.path.join(rtmp, ".claude", "scripts", "vocabulary.py"))
    rfmq = os.path.join(rtmp, ".claude", "scripts", "fmquery.py")
    rlog = os.path.join(rtmp, "wiki", "log.md")
    import re as _re
    txt = open(rlog, encoding="utf-8").read()
    txt = _re.sub(r"^## (\d{4})", lambda m: f"## {int(m.group(1)) - 5}", txt, flags=_re.M)
    open(rlog, "w", encoding="utf-8").write(txt)

    def rrun(args):
        r = subprocess.run([PY, rfmq] + args, capture_output=True, text=True, cwd=rtmp)
        return r.returncode, r.stdout + r.stderr

    def summary(out):
        return out.splitlines()[0] if out else ""

    rc_b, out_b = rrun(["--balance"])
    rc, out = rrun(["--rotate-log"])
    emptied = not _re.search(r"^## \d{4}-\d{2}-\d{2}", open(rlog, encoding="utf-8").read(), _re.M)
    check("rotate-log empties log.md on a copy", rc == 0 and emptied, out[:200])
    rc, out = rrun(["--rotate-log", "--dry-run"])
    check("rotate-log dry run after full rotation", rc == 0 and "# rotate-log" in out, out[:200])
    rc_a, out_a = rrun(["--balance"])
    check("balance unchanged by rotation", rc_a == rc_b and summary(out_a) == summary(out_b),
          f"before: {summary(out_b)}  after: {summary(out_a)}")
finally:
    shutil.rmtree(rtmp, ignore_errors=True)

tmp = tempfile.mkdtemp()
bad = os.path.join(tmp, "wiki", "cases", "x", "overview.md")
os.makedirs(os.path.dirname(bad))
open(bad, "w").write("---\ntitle: T\ntype: case\nstatus: bogus\n---\nx")
rc, out = run([HOOK], json.dumps({"tool_input": {"file_path": bad, "content": "x"}}))
check("hook rejects status outside schema", rc == 2 and "outside the schema" in out, out[:200])
rc, out = run([HOOK], json.dumps({"tool_input": {"file_path": bad, "content": "a — b"}}))
check("hook rejects em dash", rc == 2 and "em dash" in out, out[:200])
# Unquoted wikilinks in frontmatter parse as nested lists, and Obsidian
# then shows no links at all. The hook must reject them.
qdir = os.path.join(tmp, "wiki", "cases", "q")
os.makedirs(qdir, exist_ok=True)
qpage = os.path.join(qdir, "overview.md")
open(qpage, "w").write("---\ntitle: q\ntype: case\nstatus: active\nrelated: [[a.md]]\n---\n\nTL;DR. q\n")
rc, out = run([HOOK], json.dumps({"tool_input": {"file_path": qpage, "content": "q"}}))
check("hook rejects unquoted frontmatter wikilinks", rc == 2 and "unquoted" in out, out[:200])
open(qpage, "w").write("---\ntitle: q\ntype: case\nstatus: active\nrelated: [\"[[a.md]]\"]\n---\n\nTL;DR. q\n")
rc, out = run([HOOK], json.dumps({"tool_input": {"file_path": qpage, "content": "q"}}))
check("hook accepts quoted frontmatter wikilinks", rc == 0, out[:200])

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
open(v, "w").write("The content is stripped, the architecture is not.\n")
rc, out = run([VOICE, v])
check("voice catches a trailing 'the Y is not'", "antithesis" in out, out[:200])
open(v, "w").write("The wiki is never a dumping ground. It is where things end up.\n")
rc, out = run([VOICE, v])
check("voice catches 'is never X. It is Y'", "antithesis" in out, out[:200])
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
          ".claude/commands/onboard.md", ".claude/commands/shape.md",
          ".claude/scripts/vocabulary.py", ".claude/settings.json",
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
