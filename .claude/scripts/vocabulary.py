"""The status words a library may use, in the four languages it may be kept in.

A library writes its status in its own language. The tools read all of them
and reason about four canonical values, so a Norwegian page marked
"avsluttet" counts as closed exactly like an English one marked "closed".

fmquery.py and hooks/validate.py both import this file. Add a word here and
both learn it. Keep the canonical keys as they are, the app and the
dashboard depend on them.
"""
import unicodedata

# canonical value -> every spelling accepted for it, lower case.
# English, Danish, Norwegian (bokmal), Swedish. Letters outside ASCII are
# written as escapes so the file reads the same on any machine.
STATUS_WORDS = {
    "active": ("active", "aktiv"),
    "waiting": ("waiting", "afventer", "venter", "avventer", "v\u00e4ntar", "inv\u00e4ntar"),
    "on_hold": ("on_hold", "on hold", "i_bero", "i bero", "p\u00e5_vent", "p\u00e5 vent",
                "vilande", "pausad", "pauset"),
    "closed": ("closed", "afsluttet", "avsluttet", "avslutad", "lukket", "st\u00e4ngd"),
}

STATUS_VALUES = tuple(STATUS_WORDS)
CLOSED = {"closed", "on_hold"}

_LOOKUP = {w: canon for canon, words in STATUS_WORDS.items() for w in words}


def canonical_status(value):
    """The canonical status for a frontmatter value, or '' when it is not one.

    Reads the whole value first and then its first word, so both "i bero"
    and "waiting (on the client)" are understood.
    """
    s = unicodedata.normalize("NFC", str(value or "")).strip().strip("\"'").lower()
    if not s:
        return ""
    if s in _LOOKUP:
        return _LOOKUP[s]
    first = s.replace(",", " ").replace("(", " ").split()[0]
    return _LOOKUP.get(first, "")


def is_status_word(value):
    """True when the whole value is an accepted status word, nothing more."""
    s = unicodedata.normalize("NFC", str(value or "")).strip().strip("\"'").lower()
    return s in _LOOKUP
