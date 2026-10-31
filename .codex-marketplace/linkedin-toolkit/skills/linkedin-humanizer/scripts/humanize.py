#!/usr/bin/env python3
"""
humanize.py - the mechanical half of the humanizer's Pass 1, as code.

Adapted from Jake Schincariol's humanize.py (linkedin-agent-skill, MIT) to the
V3 rules in ../SKILL.md. Three passes, in this order:

  1. INVISIBLE   delete or normalise characters a keyboard never produces:
                 zero-width joiners, word joiners, soft hyphens, BOMs, Unicode
                 tag characters, non-breaking and narrow spaces. Forensic tier,
                 always on.
  2. TYPOGRAPHIC curly quotes -> straight, ellipsis -> three dots, double
                 hyphen -> comma, en dash between clauses -> comma. Em dashes are
                 CAPPED, not banned: about 1 per 100 words survives, and only the
                 excess becomes a comma. Zero em dashes is its own tell.
  3. LEXICAL     the lexicon is judged per paragraph. A paragraph with 3+
                 markers gets its markers replaced; one or two markers in a
                 paragraph are reported and left alone. --replace-all restores
                 the old replace-everywhere behaviour.

Structural tells (reveal bridges, staccato runs, stacked triads, "not just X,
it's Y") are REPORTED, never rewritten. Changing a sentence's shape needs
judgement, which is the model's job in Passes 2-4, not a regex's.

Nothing leaves the machine. No dependencies.

Usage
  python3 humanize.py draft.txt
  python3 humanize.py draft.txt --report
  pbpaste | python3 humanize.py - --report
  python3 humanize.py draft.txt --json
  python3 humanize.py draft.txt -o clean.txt
"""

import argparse
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, "lexicon.json")

URL_RE = re.compile(r"https?://\S+|www\.\S+|\S+@\S+\.\S+")
SENT_RE = re.compile(r"[^.!?\n]+[.!?]*")
WORD_RE = re.compile(r"[A-Za-z']+")
PARA_SPLIT = re.compile(r"(\n[ \t]*\n)")

#: Paragraph marker count at which the lexical pass rewrites (V3: "Three or more is").
DENSITY_THRESHOLD = 3


def load_lexicon(path=LEX):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _cp(spec):
    """'U+200B' -> 0x200B;  'U+E0000-U+E007F' -> (start, end)."""
    if "-" in spec:
        a, b = spec.split("-")
        return (int(a[2:], 16), int(b[2:], 16))
    return int(spec[2:], 16)


def protect_urls(text):
    """Swap URLs for placeholders so no pass rewrites inside a link."""
    found = []

    def stash(m):
        found.append(m.group(0))
        return f"\x00URL{len(found) - 1}\x00"

    return URL_RE.sub(stash, text), found


def restore_urls(text, found):
    for i, url in enumerate(found):
        text = text.replace(f"\x00URL{i}\x00", url)
    return text


def pass_invisible(text, lex):
    """Delete or space-normalise invisible characters. Returns (text, hits)."""
    hits = []
    for entry in lex["invisible"]:
        cp = _cp(entry["cp"])
        if isinstance(cp, tuple):
            pattern = "[" + re.escape(chr(cp[0])) + "-" + re.escape(chr(cp[1])) + "]"
        else:
            pattern = re.escape(chr(cp))
        n = len(re.findall(pattern, text))
        if n:
            hits.append({"name": entry["cp"] + " " + entry["name"], "count": n,
                         "action": entry["action"]})
            text = re.sub(pattern, "" if entry["action"] == "delete" else " ", text)
    # Any remaining Cf (format) character is invisible by definition. The URL
    # placeholders use \x00, which is Cc, so they survive this.
    stray = [c for c in text if unicodedata.category(c) == "Cf"]
    if stray:
        hits.append({"name": "other invisible format chars", "count": len(stray),
                     "action": "delete"})
        text = "".join(c for c in text if unicodedata.category(c) != "Cf")
    return text, hits


def _cap_em_dashes(text, per_100):
    """Keep the first `allowed` em dashes, turn the rest into commas."""
    allowed = max(1, len(WORD_RE.findall(text)) * per_100 // 100)
    seen = 0

    def repl(m):
        nonlocal seen
        seen += 1
        return m.group(0) if seen <= allowed else ", "

    return re.sub(r"\s*—\s*", repl, text), allowed


def pass_typographic(text, lex):
    hits = []
    for entry in lex["typographic"]:
        ch = entry["from"]
        n = text.count(ch)
        if not n:
            continue
        if ch == "—":
            text, allowed = _cap_em_dashes(text, entry.get("cap_per_100_words", 1))
            replaced = max(0, n - allowed)
            if replaced:
                hits.append({"name": f"{ch} {entry['name']}", "count": replaced,
                             "to": f", (kept {min(n, allowed)}, cap is {allowed} for this length)"})
            continue
        hits.append({"name": f"{ch} {entry['name']}", "count": n, "to": entry["to"].strip() or "(space)"})
        if ch == "–":
            text = re.sub(r"\s*–\s*(?=\d)", "-", text)      # 5-10 ranges
            text = re.sub(r"\s+–\s+", ", ", text)            # used as a clause dash
            text = text.replace("–", "-")
        else:
            text = text.replace(ch, entry["to"])
    # A double hyphen used as a dash: never a period, so a comma.
    n = len(re.findall(r"(?<=\w) ?-- ?(?=\w)", text))
    if n:
        hits.append({"name": "-- double hyphen", "count": n, "to": ","})
        text = re.sub(r"(?<=\w) ?-- ?(?=\w)", ", ", text)
    # A comma inserted before existing punctuation reads wrong.
    text = re.sub(r",\s*([,.;:!?])", r"\1", text)
    text = re.sub(r",[ \t]*\n", "\n", text)
    return text, hits


def _match_case(src, repl):
    if not repl:
        return repl
    if src.isupper() and len(src) > 1:
        return repl.upper()
    if src[0].isupper():
        return repl[0].upper() + repl[1:]
    return repl


def _compiled_entries(lex):
    entries = sorted(lex["phrases"] + lex["words"], key=lambda e: len(e["find"]), reverse=True)
    return [(e, re.compile(r"\b" + re.escape(e["find"]).replace(r"\ ", r"\s+") + r"\b", re.IGNORECASE))
            for e in entries]


def count_markers(paragraph, compiled):
    """Lexicon hits in one paragraph. Longest entries claim their span first,
    so "delve into" is one marker, not "delve into" plus "delve"."""
    taken, hits = [], []
    for entry, pattern in compiled:
        for m in pattern.finditer(paragraph):
            if any(m.start() < b and a < m.end() for a, b in taken):
                continue
            taken.append((m.start(), m.end()))
            hits.append(entry)
    return hits


def _clean_after_deletions(text):
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"(?m)^[ \t]*([,.;:])\s*", "", text)
    text = re.sub(r"[ \t]+([,.;:!?])", r"\1", text)
    text = re.sub(r"(?m)^[ \t]+$", "", text)
    return text


def pass_lexical(text, lex, replace_all=False):
    """Replace markers in paragraphs at or above the density threshold."""
    compiled = _compiled_entries(lex)
    replaced, left = {}, {}
    parts = PARA_SPLIT.split(text)
    for i in range(0, len(parts), 2):
        para = parts[i]
        hits = count_markers(para, compiled)
        if not hits:
            continue
        bucket = replaced if (replace_all or len(hits) >= DENSITY_THRESHOLD) else left
        for entry in hits:
            key = entry["find"]
            bucket.setdefault(key, {"find": key, "replace": entry["replace"] or "(deleted)",
                                    "count": 0, "family": entry["family"]})
            bucket[key]["count"] += 1
        if bucket is replaced:
            for entry, pattern in compiled:
                para = pattern.sub(lambda m, e=entry: _match_case(m.group(0), e["replace"]), para)
            parts[i] = _clean_after_deletions(para)
    text = "".join(parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text, list(replaced.values()), list(left.values())


def without_urls(text):
    """Links have dots and dashes that are not punctuation; measure prose only."""
    return URL_RE.sub("link", text)


def paragraph_rhythm(text):
    """Paragraphs where every sentence runs the same length (machine-flat)."""
    flat = []
    for para in re.split(r"\n[ \t]*\n", without_urls(text)):
        lens = [len(s.split()) for s in SENT_RE.findall(para) if len(s.split()) > 2]
        if len(lens) < 4:
            continue
        mean = sum(lens) / len(lens)
        cv = ((sum((n - mean) ** 2 for n in lens) / len(lens)) ** 0.5) / mean if mean else 0
        if cv < 0.2:
            flat.append(round(cv, 2))
    return flat


def fragment_count(text):
    """Standalone fragments: one- or two-word sentences ("Done." "Worth it.").
    V3 allows two per post."""
    return sum(1 for s in SENT_RE.findall(without_urls(text))
               if 0 < len(s.split()) <= 2 and s.strip()[-1:] in ".!")


def scan_structures(text, lex):
    flags = []
    for s in lex["structures"]:
        try:
            pattern = re.compile(s["regex"], re.MULTILINE)
        except re.error:
            continue
        found = pattern.findall(text)
        if len(found) >= s.get("min_count", 1):
            flags.append({"name": s["name"], "count": len(found), "fix": s["fix"]})
    flat = paragraph_rhythm(text)
    if flat:
        flags.append({
            "name": "Machine-flat paragraph (every sentence the same length)",
            "count": len(flat),
            "fix": "Edit one sentence in that paragraph. Never alternate long/short across the post: that seesaw is the humanizer fingerprint.",
        })
    frags = fragment_count(text)
    if frags > 2:
        flags.append({
            "name": "Staccato fragments (more than 2 in the post)",
            "count": frags,
            "fix": "Merge fragments back into full sentences. Fragment runs are the top 2026 tell.",
        })
    return flags


def humanize(text, lex, replace_all=False):
    text, urls = protect_urls(text)
    text, inv = pass_invisible(text, lex)
    text, typo = pass_typographic(text, lex)
    text, lexi, below = pass_lexical(text, lex, replace_all=replace_all)
    text = restore_urls(text, urls)
    return text.strip() + "\n", {
        "invisible": inv,
        "typographic": typo,
        "lexical": lexi,
        "lexical_below_threshold": below,
        "structures": scan_structures(text, lex),
    }


def render_report(report, out=sys.stderr):
    def head(title):
        print(f"\n{title}\n" + "-" * len(title), file=out)

    total = sum(h["count"] for k in ("invisible", "typographic", "lexical") for h in report[k])

    head("HUMANIZE REPORT")
    print(f"{total} mechanical fixes, "
          f"{len(report['structures'])} structural tells flagged for rewrite", file=out)

    if report["invisible"]:
        head("1. INVISIBLE CHARACTERS")
        for h in report["invisible"]:
            print(f"  {h['count']:>3}x  {h['name']}  -> {h['action']}", file=out)
    if report["typographic"]:
        head("2. TYPOGRAPHY")
        for h in report["typographic"]:
            print(f"  {h['count']:>3}x  {h['name']}  -> {h['to']}", file=out)
    if report["lexical"]:
        head(f"3. LEXICON  (replaced in paragraphs with {DENSITY_THRESHOLD}+ markers)")
        for h in report["lexical"]:
            print(f"  {h['count']:>3}x  {h['find']}  -> {h['replace']}   [{h['family']}]", file=out)
    if report["lexical_below_threshold"]:
        head("3b. LEXICON LEFT ALONE  (1-2 per paragraph is not a verdict)")
        for h in report["lexical_below_threshold"]:
            print(f"  {h['count']:>3}x  {h['find']}", file=out)
    if report["structures"]:
        head("4. STRUCTURAL TELLS  (not auto-fixed - rewrite these yourself)")
        for h in report["structures"]:
            print(f"  {h['count']:>3}x  {h['name']}\n        {h['fix']}", file=out)
    if not any(report.values()):
        head("CLEAN")
        print("  Nothing to change.", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Mechanical clean-up of a draft (humanizer Pass 1).")
    ap.add_argument("input", nargs="?", default="-", help="file, or - for stdin")
    ap.add_argument("-o", "--out", help="write cleaned text here instead of stdout")
    ap.add_argument("--report", action="store_true", help="print what changed, to stderr")
    ap.add_argument("--json", action="store_true", help="emit {text, report} as JSON")
    ap.add_argument("--replace-all", action="store_true",
                    help="replace every lexicon marker, ignoring paragraph density")
    ap.add_argument("--lexicon", default=LEX, help="path to lexicon.json")
    args = ap.parse_args()

    if args.input == "-":
        raw = sys.stdin.read()
    else:
        with open(args.input, encoding="utf-8") as fh:
            raw = fh.read()
    lex = load_lexicon(args.lexicon)
    clean, report = humanize(raw, lex, replace_all=args.replace_all)

    if args.json:
        print(json.dumps({"text": clean, "report": report}, indent=2, ensure_ascii=False))
        return
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(clean)
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(clean)
    if args.report:
        render_report(report)


if __name__ == "__main__":
    main()
