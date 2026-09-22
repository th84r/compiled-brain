#!/usr/bin/env python3
"""fmquery, structured queries over the wiki.

This is what makes "what is overdue" and "where did we discuss X" queries
rather than judgement calls. It drives /lint, /weekly-review and /eval
deterministically, generates wiki/status.md, and searches the whole library
including the log.

Examples,
  fmquery.py --dashboard                   # regenerate wiki/status.md
  fmquery.py --stale                       # overdue review/expires + old active pages
  fmquery.py --type case --active --sort value --desc
  fmquery.py --type case --hat <hat>
  fmquery.py --orphans                     # pages with no inbound links
  fmquery.py --search "abstract deadline"  # ranked full-text search, pages and log
  fmquery.py --search "slides" --hat <hat> --type case
  fmquery.py --links cases/<case>/overview.md
  fmquery.py --eval                        # deterministic assertions, no model needed
  fmquery.py --rotate-log                  # move old log entries to wiki/log/YYYY-MM.md
  fmquery.py --rotate-log --dry-run

Design notes,
  Search is built in memory on every call and never persisted. A regenerated
  index is the same idea as the generated dashboard, a derived view that
  cannot drift from the source because it does not outlive the call.

Standard library only. Python 3.9+.
"""
import argparse
import collections
import datetime
import math
import os
import re
import sys

# ---------------------------------------------------------------- vocabulary
# Keep these in sync with wiki/workflows/frontmatter-schema.md and with
# .claude/hooks/validate.py. Localise freely, the code does not care what the
# strings are.
STATUS_VALUES = ("active", "waiting", "on_hold", "closed")
CLOSED = {"closed", "on_hold"}
WORK_TYPES = {"case", "project"}
HAT_FIELD = "hat"

# Labels used in the generated dashboard. Localise here.
L = {
    "title": "Status overview (generated)",
    "h1": "Status overview",
    "tldr": "Generated from frontmatter on {date}. NEVER edit this file by hand, "
            "run `python3 .claude/scripts/fmquery.py --dashboard` to refresh it. "
            "Field corrections belong in the individual page's frontmatter.",
    "overdue": "Needs action, overdue",
    "none_overdue": "None. Everything is current.",
    "per_hat": "Active cases and projects per hat",
    "cols": "| Page | Status | Value | Next step | Date | Updated |",
    "reviews": "Review dates in the next 30 days",
    "odd": "Status values outside the schema",
    "none": "None.",
    "review_overdue": "review overdue",
    "expires_overdue": "expires overdue",
    "silent": "active, not updated for {days} days",
    "nad_passed": "next_action_date passed",
}

# Log rotation. Entries whose month is older than KEEP_MONTHS (counting the
# current month as 1) move to wiki/log/YYYY-MM.md. The main log stays a
# rolling recent window, which is what an agent actually reads.
KEEP_MONTHS = 2
LOG_ENTRY = re.compile(r"^## (\d{4}-\d{2}-\d{2})\b", re.M)

# Eval assertions live in a markdown table under this heading.
EVAL_HEADING = re.compile(r"^##+\s*Assertions\s*$", re.M | re.I)

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
WIKI = os.path.join(ROOT, "wiki")
TODAY = datetime.date.today()
TOKEN = re.compile(r"[a-zà-ɏ0-9]{2,}", re.I)


# ------------------------------------------------------------------ parsing
def parse_fm(text):
    """Tolerant frontmatter parser, reads top-level scalar fields.

    Deliberately not a YAML parser. Pages use [[wikilink]] syntax, which is
    not valid YAML, and a strict parser would reject pages that are otherwise
    perfectly good. Tolerance here is a feature.
    """
    fm = {}
    s = text.lstrip()
    if not s.startswith("---"):
        return fm, text
    rest = s[3:]
    end = rest.find("\n---")
    if end == -1:
        return fm, text
    for line in rest[:end].splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s?(.*)$", line)
        if m:
            k, v = m.group(1), m.group(2).strip()
            if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
                v = v[1:-1]
            fm[k] = v
    return fm, rest[end + 4:]


def as_list(v):
    """A frontmatter value that may be a scalar or a [a, b] list."""
    v = str(v or "").strip()
    if v.startswith("[") and v.endswith("]"):
        return [x.strip().strip("\"'") for x in v[1:-1].split(",") if x.strip()]
    return [v] if v else []


def hats(fm):
    return [h.lower() for h in as_list(fm.get(HAT_FIELD))] or ["?"]


def parse_date(v):
    if not v:
        return None
    try:
        return datetime.date.fromisoformat(str(v)[:10])
    except Exception:
        return None


def resolve_date(s):
    if not s:
        return None
    return TODAY if s.lower() == "today" else parse_date(s)


def load_pages():
    pages = []
    for root, _, files in os.walk(WIKI):
        r = root.replace("\\", "/")
        if "/assets" in r or "/wiki/log" in r:
            continue
        for fn in files:
            if not fn.endswith(".md") or fn in ("index.md", "log.md", "status.md"):
                continue
            p = os.path.join(root, fn)
            try:
                txt = open(p, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            fm, body = parse_fm(txt)
            fm["_path"] = os.path.relpath(p, WIKI).replace("\\", "/")
            fm["_body"] = body
            pages.append(fm)
    return pages


def is_active(fm):
    s = str(fm.get("status", "")).lower().strip()
    first = re.split(r"[ ,(]", s)[0] if s else ""
    return first not in CLOSED


# ------------------------------------------------------------------ staleness
def stale_reasons(fm):
    r = []
    rev, exp, upd = (parse_date(fm.get(k)) for k in ("review", "expires", "updated"))
    if rev and rev < TODAY:
        r.append(f"{L['review_overdue']} {rev}")
    if exp and exp < TODAY:
        r.append(f"{L['expires_overdue']} {exp}")
    # Silence and a passed next_action only apply to work pages. An entity
    # card may sit still for a year without that meaning anything.
    if str(fm.get("type", "")).lower() in WORK_TYPES:
        if is_active(fm) and upd and (TODAY - upd).days > 90:
            r.append(L["silent"].format(days=(TODAY - upd).days))
        nad = parse_date(fm.get("next_action_date"))
        if is_active(fm) and nad and nad < TODAY:
            r.append(f"{L['nad_passed']} {nad}")
    return r


# --------------------------------------------------------------------- links
LINK_RX = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]|\]\(([^)#\s]+\.md)(?:#[^)]*)?\)")


def outbound(fm):
    """Targets a page links to, as normalised wiki-relative paths or stems."""
    out = set()
    base = os.path.dirname(fm["_path"])
    for m in LINK_RX.finditer(fm.get("_body", "") + " " + str(fm.get("related", ""))):
        t = (m.group(1) or m.group(2) or "").strip()
        if not t or t.startswith(("http://", "https://")):
            continue
        # A relative target is normalised whichever syntax it came in, so
        # [[../../workflows/x.md]] and ](../../workflows/x.md) resolve alike.
        # Normalising only the markdown form made backlinks asymmetric.
        if m.group(2) or "/" in t:
            t = os.path.normpath(os.path.join(base, t)).replace("\\", "/")
        out.add(t)
        out.add(os.path.splitext(t)[0])
    return out


def links_for(pages, target):
    target = target.replace("\\", "/")
    stem = os.path.splitext(os.path.basename(target))[0]
    folder = target.split("/")[0]
    me = next((p for p in pages if p["_path"] == target), None)
    inbound = []
    for p in pages:
        if p["_path"] == target:
            continue
        o = outbound(p)
        if (target in o or stem in o or any(x.endswith("/" + stem) for x in o)
                or any(x.rstrip("/") == folder for x in o)):
            inbound.append(p["_path"])
    return me, sorted(inbound), sorted(outbound(me)) if me else []


def find_orphans(pages, include_archive=False):
    """Pages nothing links to.

    Builds ONE set of link targets and looks up in it. An earlier version
    concatenated every page body into a single string and ran four substring
    searches per page, which on 4,261 pages and 65 MB came to roughly a
    trillion character comparisons and never finished.

    Every index.md counts as a link source, not just the root one. load_pages
    skips index.md, so they are read here. A folder index such as
    wiki/people/index.md is exactly the catalogue that makes its pages
    reachable, and without it 110 person cards looked like orphans.

    wiki/archive/ is skipped by default. An archived page with no inbound
    links is parked on purpose rather than lost.
    """
    targets = set()
    sources = [fm.get("_body", "") + " " + str(fm.get("related", "")) for fm in pages]
    idx = ""
    for root, _, files in os.walk(WIKI):
        for fn in files:
            if fn == "index.md":
                try:
                    txt = open(os.path.join(root, fn), encoding="utf-8", errors="ignore").read()
                except Exception:
                    continue
                sources.append(txt)
                idx += "\n" + txt
    for text in sources:
        for m in LINK_RX.finditer(text):
            t = (m.group(1) or m.group(2) or "").strip()
            if not t or t.startswith(("http://", "https://")):
                continue
            t = t.replace("\\", "/").lstrip("./")
            targets.add(t)
            targets.add(os.path.splitext(os.path.basename(t))[0])
            if "/" in t:
                targets.add(t.split("/")[0])
    # Only specific sub-paths count as coverage, such as "cases/acme-review".
    # A bare top-level "cases/" does not cover everything inside it, otherwise
    # every page is automatically linked and the check always returns zero.
    for m in re.finditer(r"([a-z0-9_-]+/[a-z0-9_/-]+)", idx):
        targets.add(m.group(1).rstrip("/"))

    out = []
    for fm in pages:
        path = fm["_path"]
        if not include_archive and path.startswith("archive/"):
            continue
        stem = os.path.splitext(os.path.basename(path))[0]
        no_ext = os.path.splitext(path)[0]
        folder = os.path.dirname(path)
        if (stem in targets or path in targets or no_ext in targets
                or (folder.count("/") >= 1 and folder in targets)):
            continue
        out.append(fm)
    return out


# -------------------------------------------------------------------- search
def log_entries():
    """Each ## entry of the log, current window and archives, as a document."""
    docs = []
    files = [os.path.join(WIKI, "log.md")]
    ld = os.path.join(WIKI, "log")
    if os.path.isdir(ld):
        files += sorted(os.path.join(ld, f) for f in os.listdir(ld) if f.endswith(".md"))
    for f in files:
        if not os.path.isfile(f):
            continue
        txt = open(f, encoding="utf-8", errors="ignore").read()
        rel = os.path.relpath(f, WIKI).replace("\\", "/")
        starts = [m.start() for m in LOG_ENTRY.finditer(txt)] + [len(txt)]
        for a, b in zip(starts, starts[1:]):
            chunk = txt[a:b].strip()
            head = chunk.splitlines()[0][3:].strip() if chunk else ""
            docs.append({"_path": f"{rel} :: {head[:70]}", "title": head,
                         "_body": chunk, "type": "log", HAT_FIELD: "log"})
    return docs


def tokens(s):
    return TOKEN.findall(s.lower())


def bm25_search(docs, query, k=10, k1=1.5, b=0.75):
    """Plain BM25 over title, frontmatter and body. Built in memory per call."""
    q = tokens(query)
    if not q:
        return []
    fields = []
    for d in docs:
        meta = " ".join(str(v) for kk, v in d.items() if not kk.startswith("_"))
        fields.append(tokens((str(d.get("title", "")) + " ") * 3 + meta + " " + d.get("_body", "")))
    N = len(fields)
    avgdl = (sum(len(f) for f in fields) / N) if N else 1
    df = collections.Counter()
    for f in fields:
        for t in set(f):
            df[t] += 1
    scores = []
    for d, f in zip(docs, fields):
        tf = collections.Counter(f)
        s = 0.0
        for t in q:
            if t not in tf:
                continue
            idf = math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5))
            s += idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(f) / avgdl))
        if s > 0:
            scores.append((s, d))
    scores.sort(key=lambda x: -x[0])
    return scores[:k]


def snippet(body, query, width=150):
    q = [t for t in tokens(query) if len(t) > 2]
    low = body.lower()
    pos = min((low.find(t) for t in q if low.find(t) >= 0), default=0)
    a = max(0, pos - width // 3)
    s = re.sub(r"\s+", " ", body[a:a + width]).strip()
    return ("…" if a else "") + s + ("…" if a + width < len(body) else "")


# ---------------------------------------------------------------------- eval
def run_eval():
    """Deterministic assertions from wiki/reference/eval-set.md.

    Table under '## Assertions' with columns  page | field | expected.
    field is a frontmatter key, or 'body' for the page text.
    expected matches exactly, or as a substring when prefixed with ~.
    No model is involved, so this can run in CI and catches schema drift
    and silently changed facts the moment they happen.
    """
    p = os.path.join(WIKI, "reference", "eval-set.md")
    if not os.path.isfile(p):
        print("no eval-set.md")
        return 0
    txt = open(p, encoding="utf-8").read()
    m = EVAL_HEADING.search(txt)
    if not m:
        print("no '## Assertions' section in eval-set.md")
        return 0
    block = txt[m.end():]
    nxt = re.search(r"^##\s", block, re.M)
    block = block[:nxt.start()] if nxt else block
    rows = []
    for line in block.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or set(cells[0]) <= set("-: ") or cells[0].lower() == "page":
            continue
        rows.append(cells[:3])
    pages = {pg["_path"]: pg for pg in load_pages()}
    passed = failed = 0
    for page, field, expected in rows:
        pg = pages.get(page)
        if pg is None:
            print(f"  FAIL  {page}  (page not found)")
            failed += 1
            continue
        actual = pg.get("_body", "") if field == "body" else str(pg.get(field, ""))
        ok = (expected[1:].lower() in actual.lower()) if expected.startswith("~") \
            else (actual.strip() == expected)
        if ok:
            passed += 1
        else:
            got = actual.strip()[:60].replace("\n", " ")
            print(f"  FAIL  {page} :: {field}  expected {expected!r}, got {got!r}")
            failed += 1
    print(f"# eval  {passed} passed, {failed} failed, {len(rows)} assertions  [{TODAY}]")
    return 1 if failed else 0


# ------------------------------------------------------------- log rotation
def rotate_log(dry_run=False):
    """Move log entries older than KEEP_MONTHS into wiki/log/YYYY-MM.md.

    Append-only is preserved: nothing is deleted, entries are moved whole and
    in the order they appeared. The header above the first entry stays in
    log.md. Line counts are verified before anything is written.
    """
    lp = os.path.join(WIKI, "log.md")
    if not os.path.isfile(lp):
        print("no log.md")
        return
    txt = open(lp, encoding="utf-8").read()
    starts = [m.start() for m in LOG_ENTRY.finditer(txt)]
    if not starts:
        print("log.md has no dated entries")
        return
    header = txt[:starts[0]]
    bounds = starts + [len(txt)]
    entries = [txt[a:b] for a, b in zip(bounds, bounds[1:])]

    y, mth = TODAY.year, TODAY.month
    keep = set()
    for i in range(KEEP_MONTHS):
        keep.add(f"{y:04d}-{mth:02d}")
        mth -= 1
        if mth == 0:
            mth, y = 12, y - 1

    stay, move = [], collections.defaultdict(list)
    for e in entries:
        ym = e[3:10]
        (stay if ym in keep else move[ym]).append(e)

    orig_lines = txt.count("\n")
    new_main = header + "".join(stay)
    moved_lines = sum(e.count("\n") for es in move.values() for e in es)
    # A plain assert disappears under python3 -O, and this is the one
    # operation in the repo that rewrites an append-only file. It raises.
    if new_main.count("\n") + moved_lines != orig_lines:
        raise SystemExit("rotate-log aborted, line count does not reconcile. "
                         "Nothing was written.")

    print(f"# rotate-log  keep {sorted(keep)}  stay {len(stay)}  "
          f"move {sum(len(v) for v in move.values())} across {len(move)} months"
          + ("  [dry run]" if dry_run else ""))
    for ym in sorted(move):
        print(f"  {ym}  {len(move[ym])} entries -> wiki/log/{ym}.md")
    if dry_run or not move:
        return
    ld = os.path.join(WIKI, "log")
    os.makedirs(ld, exist_ok=True)
    for ym, es in move.items():
        ap = os.path.join(ld, f"{ym}.md")
        new = not os.path.isfile(ap)
        with open(ap, "a", encoding="utf-8") as f:
            if new:
                f.write(f"# Log archive {ym}\n\nMoved from log.md by fmquery.py --rotate-log. "
                        "Append-only, order preserved.\n\n")
            f.write("".join(es))
    with open(lp, "w", encoding="utf-8") as f:
        f.write(new_main)
    print("  done, nothing deleted")


# ----------------------------------------------------------------- dashboard
def build_dashboard(pages):
    work = [p for p in pages if str(p.get("type", "")).lower() in WORK_TYPES]
    active = [p for p in work if is_active(p)]

    def nad(p):
        return parse_date(p.get("next_action_date")) or datetime.date.max

    o = ["---", f"title: {L['title']}", "type: reference", "status: active",
         "confidence: verified", f"{HAT_FIELD}: bridging",
         f"updated: {TODAY.isoformat()}", "tags: [status, dashboard, generated]",
         "---", "", f"# {L['h1']}", "", L["tldr"].format(date=TODAY.isoformat()), ""]

    overdue = [(p, stale_reasons(p)) for p in active]
    overdue = [(p, r) for p, r in overdue if r]
    o += [f"## {L['overdue']} ({len(overdue)})", ""]
    o += [f"- **{str(p.get('title', p['_path']))[:60]}** ({p['_path']}), {'; '.join(r)}"
          for p, r in sorted(overdue, key=lambda x: nad(x[0]))] or [f"- {L['none_overdue']}"]
    o.append("")

    o += [f"## {L['per_hat']}", ""]
    for h in sorted({h for p in active for h in hats(p)}):
        grp = sorted([p for p in active if h in hats(p)], key=nad)
        o += [f"### {h}", "", L["cols"], "|---|---|---|---|---|---|"]
        for p in grp:
            o.append(f"| [{str(p.get('title', p['_path']))[:40]}]({p['_path']}) "
                     f"| {str(p.get('status', ''))[:20]} | {str(p.get('value', ''))[:18]} "
                     f"| {str(p.get('next_action', ''))[:70]} "
                     f"| {p.get('next_action_date', '')} | {p.get('updated', '')} |")
        o.append("")

    soon = TODAY + datetime.timedelta(days=30)
    up = [p for p in pages if parse_date(p.get("review"))
          and TODAY <= parse_date(p.get("review")) <= soon]
    o += [f"## {L['reviews']} ({len(up)})", ""]
    o += [f"- {p.get('review')}, {p.get('title', p['_path'])} ({p['_path']})"
          for p in sorted(up, key=lambda x: parse_date(x.get("review")))] or [f"- {L['none']}"]
    o.append("")

    odd = [p for p in work if str(p.get("status", "")).lower().strip() not in set(STATUS_VALUES)]
    o += [f"## {L['odd']} ({len(odd)})", ""]
    o += [f"- {p['_path']}, `{p.get('status', '')}`" for p in sorted(odd, key=lambda x: x["_path"])] \
        or [f"- {L['none']}"]
    o.append("")

    os.makedirs(WIKI, exist_ok=True)
    out = os.path.join(WIKI, "status.md")
    open(out, "w", encoding="utf-8").write("\n".join(o) + "\n")
    print(f"Wrote {out}  (active: {len(active)}, overdue: {len(overdue)}, schema deviations: {len(odd)})")


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--type"); ap.add_argument("--status"); ap.add_argument("--hat")
    ap.add_argument("--active", action="store_true")
    ap.add_argument("--stale", action="store_true")
    ap.add_argument("--orphans", action="store_true")
    ap.add_argument("--include-archive", action="store_true",
                    help="include wiki/archive in --orphans")
    ap.add_argument("--dashboard", action="store_true", help="regenerate wiki/status.md")
    ap.add_argument("--search", metavar="QUERY", help="ranked full-text search, pages and log")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--links", metavar="PAGE", help="inbound and outbound links for a page")
    ap.add_argument("--eval", action="store_true", help="run deterministic assertions")
    ap.add_argument("--rotate-log", action="store_true", help="archive old log entries by month")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--review-before"); ap.add_argument("--expires-before"); ap.add_argument("--updated-before")
    ap.add_argument("--sort"); ap.add_argument("--desc", action="store_true")
    a = ap.parse_args()

    if a.dashboard:
        return build_dashboard(load_pages())
    if a.eval:
        return sys.exit(run_eval())
    if a.rotate_log:
        return rotate_log(a.dry_run)

    pages = load_pages()

    if a.links:
        me, inb, outb = links_for(pages, a.links)
        if me is None:
            print(f"not found: {a.links}")
            return
        print(f"# {a.links}\n  inbound ({len(inb)})")
        for x in inb:
            print(f"    <- {x}")
        print(f"  outbound ({len(outb)})")
        for x in outb:
            print(f"    -> {x}")
        return

    if a.orphans:
        rows = find_orphans(pages, a.include_archive)
        print(f"# Orphan pages ({len(rows)})")
        for fm in sorted(rows, key=lambda x: x["_path"]):
            print(f"  {fm['_path']}  [{fm.get('type','?')}/{fm.get('status','?')}]")
        return

    rows = pages + (log_entries() if a.search else [])
    if a.type:
        rows = [p for p in rows if str(p.get("type", "")).lower() == a.type.lower()]
    if a.status:
        rows = [p for p in rows if str(p.get("status", "")).lower() == a.status.lower()]
    if a.hat:
        rows = [p for p in rows if a.hat.lower() in hats(p)]
    if a.active:
        rows = [p for p in rows if is_active(p)]
    for field, bound in (("review", resolve_date(a.review_before)),
                         ("expires", resolve_date(a.expires_before)),
                         ("updated", resolve_date(a.updated_before))):
        if bound:
            rows = [p for p in rows if parse_date(p.get(field)) and parse_date(p.get(field)) < bound]

    if a.search:
        hits = bm25_search(rows, a.search, k=a.limit)
        print(f"# search {a.search!r}, {len(hits)} of {len(rows)} documents")
        for s, d in hits:
            print(f"  {s:5.2f}  {d['_path']}")
            print(f"         {snippet(d.get('_body',''), a.search)}")
        return

    if a.stale:
        out = [(p, stale_reasons(p)) for p in rows]
        out = [(p, r) for p, r in out if r]
        print(f"# Stale / overdue ({len(out)})  [date {TODAY}]")
        for p, r in sorted(out, key=lambda x: x[0]["_path"]):
            print(f"  {p['_path']}  [{p.get('status','?')}]  -> {'; '.join(r)}")
        return

    if a.sort:
        def key(p):
            v = p.get(a.sort)
            d = parse_date(v)
            if d:
                return (0, d.toordinal())
            try:
                return (1, float(re.sub(r"[^0-9.]", "", str(v)) or 0))
            except Exception:
                return (2, str(v))
        rows = sorted(rows, key=key, reverse=a.desc)

    print(f"# {len(rows)} pages")
    for p in rows:
        bits = [f"[{p.get('type','?')}/{p.get('status','-')}]"]
        for k, lab in (("value", ""), ("updated", "upd "), ("next_action_date", "next ")):
            if p.get(k):
                bits.append(lab + str(p[k]))
        print(f"  {p['_path']:<48} {str(p.get('title',''))[:40]:<40} {' '.join(bits)}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # happens when output is piped through | head. Exit quietly.
        try:
            sys.stdout.close()
        except Exception:
            pass
        os._exit(0)
