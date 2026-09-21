#!/usr/bin/env python3
"""voice, scans text for the patterns that mark machine-written prose.

Run it on anything before it ships.

    python3 .claude/scripts/voice.py draft.md
    python3 .claude/scripts/voice.py report.docx notes.txt
    python3 .claude/scripts/voice.py mail.txt --mail
    python3 .claude/scripts/voice.py draft.md --strict   # also bans mid-sentence colons

Reads .md, .txt and .docx. Quoted passages are counted separately, because a
verbatim quote is the source's language and not yours.

Why a script and not a read-through: documents get rebuilt every time a
number changes, and a read-through only covers the version that was on disk
that day. The rules live here so they can be run again after every rebuild.

Extend it by adding lines to wiki/workflows/voice.md under the heading
"## Banned phrases", one phrase or /regex/ per bullet. That file is the
human-readable statement of the same rules.

Standard library only. Python 3.9+.
"""
import os
import re
import statistics
import sys
import zipfile

W = r"[A-Za-zÀ-ɏ]"  # a letter, including accented and Nordic

VOICE_FILE = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "wiki", "workflows", "voice.md"))


# --------------------------------------------------------------------- input
def read_any(path):
    if path.endswith(".docx"):
        with zipfile.ZipFile(path) as z:
            x = z.read("word/document.xml").decode("utf-8")
        x = re.sub(r"</w:p>", "\n", x)
        return re.sub(r"[ \t]+", " ", re.sub(r"<[^>]+>", "", x))
    return open(path, encoding="utf-8").read()


def strip_noise(t):
    """Remove what is not prose.

    Verbatim quotations are the source's language and not yours. Code blocks,
    frontmatter and table rows are structure, and the colon rule does not
    apply to them. Skipping these is what keeps the checker precise enough
    that people leave it switched on.
    """
    # YAML frontmatter at the top of the file
    t = re.sub(r"\A---\n.*?\n---\n", "\n", t, flags=re.S)
    # fenced and inline code
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = re.sub(r"`[^`\n]*`", " ", t)
    # markdown table rows and horizontal rules
    t = re.sub(r"^\s*\|.*$", " ", t, flags=re.M)
    # block quotes
    t = re.sub(r"^\s*>.*$", " ", t, flags=re.M)
    # quoted speech
    for pat in (r"«[^»]{0,800}»", r'"[^"]{0,800}"', r"\u201c[^\u201d]{0,800}\u201d"):
        t = re.sub(pat, " ", t)
    return t


def sentences(t):
    t = re.sub(r"\s+", " ", t)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]


# ------------------------------------------------------------------ mechanics
MECHANICS = [
    ("em dash", r"[—―]"),
    # A sentence that opens with a conjunction is a spoken habit in some
    # languages and a tell in written prose. Opt-out by deleting the line.
    ("conjunction opener", r"(?:^|[.!?] )(?:And|But|So) [a-zA-Z]"),
]

# Opt-in via --strict. A colon introducing a list is ordinary English, so
# this is a house rule rather than a machine tell. Some writers ban it
# because it is a crutch that lets a sentence avoid deciding its own shape.
# Turn it on if that is your view.
STRICT = [
    ("mid-sentence colon", rf"{W}: {W}"),
]

# ------------------------------------------------------- sentence-level tells
# Each entry is (label, regex). Keep them high precision. A checker that
# cries wolf is a checker people switch off.
PATTERNS = [
    # 1. The antithesis. The single most reliable machine tell.
    ("1 antithesis",
     rf"(?:\bit(?:'s| is)(?: not| n't)\s+{W}[^,.]{{1,50}}, it(?:'s| is)\b"
     rf"|\bnot (?:just |merely |simply |only )?{W}[^,.]{{1,50}}, but\b"
     rf"|, not {W}[^,.]{{1,40}}[.,])"),

    # 5. The didactic imperative as an opening.
    ("5 didactic opening",
     r"(?:^|\. )(?:Note that|Remember that|Keep in mind|Bear in mind|"
     r"It(?:'s| is) worth noting|It(?:'s| is) important to (?:note|remember))\b"),

    # 6. Announcing the thing instead of saying it.
    ("6 meta-announcement",
     r"(?:^|\. |\n)(?:Here(?:'s| are| is) (?:three|two|four|the)|Let me|"
     r"I(?:'ll| will) (?:walk you|break this|explain)|"
     r"(?:Three|Two|Four|Five) (?:things|points|reasons|takeaways)\b"
     r"[^.]{0,30}(?:to note|worth|are|is))"),

    # 7. Connectors that do the reader's work for them.
    ("7 overexplicit connector",
     r"(?:^|\. )(?:Moreover|Furthermore|Additionally|In conclusion|"
     r"Ultimately|That said|Importantly|Crucially|Notably)\b"),

    # 8. Flattery and glossy filler.
    ("8 flattery / filler",
     r"(?:great question|fascinating|truly remarkable|deeply impressive|"
     r"in today(?:'s)? (?:fast-paced|rapidly)|ever-(?:evolving|changing)|"
     r"navigat\w+ the complexit|a rich tapestry|the \w+ landscape\b|"
     r"\bdelve into\b|\brealm of\b)"),

    # 11. The fronted clause. Makes the reader wait for the point.
    ("11 fronted clause",
     rf"(?:^|\. )(?:What|The (?:thing|reason|point|question)) {W}[^,.]{{2,60}}, "
     rf"(?:is|was|are|were)\b"),
]

METAPHOR = (r"\b(?:leverage|leveraging|framework|lever|levers|surface area|"
            r"north star|flywheel|unlock|unlocking|double down|"
            r"move the needle)\b")


# ------------------------------------------------------------- user extension
def load_extra():
    """Extra banned phrases from wiki/workflows/voice.md.

    Looks for a '## Banned phrases' heading and reads the bullets under it.
    A bullet wrapped in slashes is treated as a regex, anything else as a
    literal phrase.
    """
    out = []
    if not os.path.isfile(VOICE_FILE):
        return out
    txt = open(VOICE_FILE, encoding="utf-8").read()
    m = re.search(r"^##+\s*Banned phrases\s*$(.*?)(?=^##\s|\Z)",
                  txt, re.M | re.S | re.I)
    if not m:
        return out
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith(("-", "*")):
            continue
        item = line[1:].strip().strip("`")
        if not item:
            continue
        if len(item) > 2 and item.startswith("/") and item.endswith("/"):
            out.append(("custom regex", item[1:-1]))
        else:
            out.append(("custom phrase", re.escape(item)))
    return out


# ------------------------------------------------------------------- scanning
def scan(path, mail=False, strict=False):
    raw = read_any(path)
    t = strip_noise(raw)
    found = []

    rules = MECHANICS + PATTERNS + load_extra() + (STRICT if strict else [])
    for label, pat in rules:
        for m in re.finditer(pat, t, re.M | re.I):
            found.append((label, m.group(0).strip()[:90]))

    ss = sentences(t)
    lengths = [len(s.split()) for s in ss]

    # 2. Setup and punchline. A short stab right after a long sentence.
    # The first sentence of a paragraph is skipped, because a short opener is
    # a sub-heading and not a punchline.
    para_starts = set()
    n = 0
    for block in t.split("\n"):
        for j, _ in enumerate(sentences(block)):
            if j == 0:
                para_starts.add(n)
            n += 1
    for i in range(1, len(ss)):
        if i in para_starts:
            continue
        if lengths[i] <= 6 and lengths[i - 1] >= 18:
            found.append(("2 setup/punchline", ss[i][:90]))

    # 4. The rule of three. Three parallel items of near-identical length,
    # where research shows the third is often a synonym of the second.
    for m in re.finditer(rf"\b({W}{{4,14}}), ({W}{{4,14}}),? and ({W}{{4,14}})\b", t):
        a, b, c = (len(g) for g in m.groups())
        if max(a, b, c) - min(a, b, c) <= 4:
            found.append(("4 rule of three", m.group(0)[:90]))

    # 9. Business metaphor as load-bearing architecture.
    met = re.findall(METAPHOR, t, re.I)
    if len(met) > max(3, len(t.split()) // 250):
        found.append(("9 metaphor overdose",
                      f"{len(met)} hits, {sorted(set(x.lower() for x in met))}"))

    # 10. Flawless evenness. Real prose has hedges, asides and one knotty
    # sentence. The absence of noise is itself a tell.
    if len(lengths) > 12 and statistics.pstdev(lengths) < 5.0:
        found.append(("10 too even",
                      f"sentence-length spread {statistics.pstdev(lengths):.1f} words"))

    if mail:
        if re.search(r"^\s*(?:#|\d+\.|[-*•])\s", raw, re.M):
            found.append(("mail form", "heading or list in an email"))
        if "**" in raw:
            found.append(("mail form", "bold text in an email"))

    return found, len(raw.split()), lengths


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    mail = "--mail" in sys.argv
    strict = "--strict" in sys.argv
    worst = 0
    for path in args:
        found, words, lengths = scan(path, mail, strict)
        print(f"\n{os.path.basename(path)}  {words} words, {len(lengths)} sentences")
        if lengths:
            print(f"  sentence length {min(lengths)} to {max(lengths)}, "
                  f"spread {statistics.pstdev(lengths):.1f}")
        if not found:
            print("  CLEAN")
        else:
            for label, s in found:
                print(f"  {label:24} {s}")
            print(f"  {len(found)} findings")
            worst = max(worst, len(found))
    # Three patterns in one text is a verdict, one can be coincidence.
    sys.exit(1 if worst >= 3 else 0)


if __name__ == "__main__":
    main()
