#!/usr/bin/env python3
"""
score.py - a five-check panel for the reader tells the humanizer removes.

Adapted from Jake Schincariol's detect.py (linkedin-agent-skill, MIT) to the
V3 rules in ../SKILL.md. Every score is computed locally from the text alone.
Nothing is uploaded.

What this is:  a reader-tell estimate. It measures the things expert readers
and LinkedIn's slop filter react to: machine-flat or staccato rhythm, missing
specifics, paragraph-dense stock vocabulary, typographic leakage, and voice.

What this is NOT:  GPTZero, Pangram, Originality or Turnitin. It does not call
them and cannot predict them. On 100-300 word posts their scores are noise
anyway (see ../sub-skills/detector-tester.md). Never report this number as
"undetectable".

Each check returns a score from 0 to 100. Higher reads more human.

Usage
  python3 score.py draft.txt
  pbpaste | python3 score.py -
  python3 score.py draft.txt --json
  python3 score.py before.txt after.txt      # compare two drafts
"""

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from humanize import (  # noqa: E402  (sibling module, same folder)
    LEX, WORD_RE, _compiled_entries, count_markers, fragment_count, paragraph_rhythm, without_urls,
)

CONTRACTIONS = re.compile(r"\b\w+'(?:s|t|re|ve|ll|d|m)\b", re.IGNORECASE)
PRONOUNS = re.compile(r"\b(i|me|my|mine|we|us|our|you|your)\b", re.IGNORECASE)
NUMBERS = re.compile(r"\b\d[\d,.]*%?\b|\$\d")
PROPER = re.compile(r"(?<![.!?]\s)(?<!^)\b[A-Z][a-z]{2,}\b", re.MULTILINE)


def clamp(n):
    return max(0.0, min(100.0, n))


def scale(value, human, machine):
    """Map value onto 0-100 where `human` -> 100 and `machine` -> 0."""
    if human == machine:
        return 50.0
    return clamp((value - machine) / (human - machine) * 100)


def words(text):
    return WORD_RE.findall(text)


def structural_tells(text, lex):
    """Lexicon structures (reveal bridges, negative parallelism, bait...) at or
    above their minimum count. Returns (count, ids)."""
    tells, ids = 0, []
    for s in lex["structures"]:
        try:
            n = len(re.compile(s["regex"], re.MULTILINE).findall(text))
        except re.error:
            continue
        if n >= s.get("min_count", 1):
            tells += n
            ids.append(s["id"])
    return tells, ids


def check_structure(text, lex):
    """Sentence structure is 36% of what expert readers cite. Penalise reveal
    bridges and other staged shapes, machine-flat paragraphs and staccato runs.
    Variance is never rewarded: manufactured long/short alternation is itself
    a tell."""
    flat = paragraph_rhythm(text)
    frags = fragment_count(text)
    tells, ids = structural_tells(text, lex)
    score = 100 - 25 * tells - 30 * len(flat) - 20 * max(0, frags - 2)
    detail = (f"{tells} staged shape(s), {len(flat)} machine-flat paragraph(s), "
              f"{frags} standalone fragment(s) (2 allowed)")
    if ids:
        detail += " [" + ", ".join(ids[:4]) + "]"
    return clamp(score), detail


def check_specificity(text):
    """Numbers, names and concrete nouns. Slop is abstract."""
    w = words(text)
    if len(w) < 25:
        return 50.0, "too short to judge"
    hits = len(NUMBERS.findall(text)) + len(set(PROPER.findall(text)))
    density = hits * 100 / len(w)
    score = scale(density, human=6.0, machine=0.5)
    return score, f"{hits} concrete markers, {density:.1f} per 100 words (want 4+)"


def check_vocabulary(text, lex):
    """Stock vocabulary judged by the densest paragraph. One or two markers in
    a paragraph is not a verdict; three or more is."""
    compiled = _compiled_entries(lex)
    per_para = [count_markers(p, compiled) for p in re.split(r"\n[ \t]*\n", text)]
    worst = max((len(h) for h in per_para), default=0)
    total = sum(len(h) for h in per_para)
    score = {0: 100.0, 1: 100.0, 2: 80.0, 3: 40.0}.get(worst, 10.0)
    found = sorted({e["find"] for h in per_para for e in h})
    detail = f"{total} stock term(s), densest paragraph has {worst}"
    if found:
        detail += " (" + ", ".join(found[:4]) + (", ..." if len(found) > 4 else "") + ")"
    return score, detail


def check_fingerprint(text):
    """Characters a phone keyboard does not produce, plus em dashes past the cap."""
    text = without_urls(text)
    invisible = sum(1 for c in text if unicodedata.category(c) == "Cf")
    em = text.count("—")
    cap = max(1, len(words(text)) // 100)
    excess_em = max(0, em - cap)
    curly = sum(text.count(c) for c in "‘’“”")
    ellip = text.count("…")
    nbsp = sum(text.count(c) for c in "   ")
    total = invisible * 4 + excess_em * 2 + curly + ellip + nbsp
    per1k = total * 1000 / max(len(text), 1)
    score = scale(per1k, human=0.0, machine=12.0)
    detail = (f"{invisible} invisible, {em} em dash ({excess_em} over the cap of {cap}), "
              f"{curly} curly quote, {ellip} ellipsis, {nbsp} hard space")
    return score, detail


def check_voice(text):
    """Contractions, person, and list shapes models default to."""
    w = words(text)
    if len(w) < 25:
        return 50.0, "too short to judge"
    per100 = 100 / len(w)
    contractions = len(CONTRACTIONS.findall(text)) * per100
    person = len(PRONOUNS.findall(text)) * per100
    bullets = [len(b.split()) for b in re.findall(r"(?m)^\s*[-*•]\s+(.+)$", text)]
    uniform = len(bullets) >= 3 and statistics.pstdev(bullets) < 1.6
    # Contractions are the weaker signal: plenty of careful human writers skip them.
    score = scale(contractions, human=2.0, machine=0.0) * 0.4 + scale(person, human=8.0, machine=1.0) * 0.6
    if uniform:
        score -= 15
    detail = (f"{contractions:.1f} contractions, {person:.1f} personal pronouns per 100 words"
              + (", uniform bullets" if uniform else ""))
    return clamp(score), detail


CHECKS = ["STRUCTURE", "SPECIFICITY", "VOCABULARY", "FINGERPRINT", "VOICE"]


def run(text, lex):
    results = {
        "STRUCTURE": check_structure(text, lex),
        "SPECIFICITY": check_specificity(text),
        "VOCABULARY": check_vocabulary(text, lex),
        "FINGERPRINT": check_fingerprint(text),
        "VOICE": check_voice(text),
    }
    scores = [results[c][0] for c in CHECKS]
    # The weakest check drags the verdict: a reader only needs one tell.
    overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4
    verdict = "READS HUMAN" if overall >= 70 and min(scores) >= 55 else (
        "MIXED" if overall >= 50 else "READS AI")
    return results, overall, verdict


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render(results, overall, verdict, label=None, out=sys.stdout):
    title = "READER-TELL PANEL" + (f"  -  {label}" if label else "")
    print("\n" + title, file=out)
    print("=" * max(len(title), 62), file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {name:<12} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<12} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'OVERALL':<12} {bar(overall)} {overall:5.1f}   {verdict}", file=out)
    if verdict != "READS HUMAN":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print(f"\n  Weakest signal: {weakest}. Fix that first.", file=out)
    print("  Local reader-tell estimate, not an AI-detector score.\n", file=out)


def main():
    ap = argparse.ArgumentParser(description="Score a draft for reader-visible AI tells.")
    ap.add_argument("input", nargs="?", default="-", help="file, or - for stdin")
    ap.add_argument("compare", nargs="?", help="second file, to show before/after")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lexicon", default=LEX)
    args = ap.parse_args()

    with open(args.lexicon, encoding="utf-8") as fh:
        lex = json.load(fh)

    def read(path):
        if path == "-":
            return sys.stdin.read()
        with open(path, encoding="utf-8") as fh:
            return fh.read()

    targets = [(args.input, read(args.input))]
    if args.compare:
        targets.append((args.compare, read(args.compare)))

    runs = [(name, *run(text, lex)) for name, text in targets]
    payload = [{
        "source": name,
        "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
        "overall": round(overall, 1),
        "verdict": verdict,
    } for name, results, overall, verdict in runs]

    if args.json:
        print(json.dumps(payload if args.compare else payload[0], indent=2))
    else:
        for name, results, overall, verdict in runs:
            render(results, overall, verdict, label=os.path.basename(name) if args.compare else None)
        if args.compare:
            a, b = payload
            print(f"  {a['overall']:.1f} {a['verdict']}  ->  "
                  f"{b['overall']:.1f} {b['verdict']}   ({b['overall'] - a['overall']:+.1f})\n")

    sys.exit(0 if payload[-1]["verdict"] == "READS HUMAN" else 1)


if __name__ == "__main__":
    main()
