"""The local cleaner and scorer have to agree with the rules the skill states.

`scripts/humanize.py` and `scripts/score.py` came from a pack whose rules were
the 2024 ones: every em dash out, every listed word replaced, sentence-length
variance rewarded. The humanizer's V3 says the opposite on all three. A script
that quietly applies the old rules undoes the skill it ships inside, so the V3
rules are pinned here.

Offline, standard library only.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills" / "linkedin-humanizer" / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


humanize = load("humanize")
score = load("score")
LEX = json.loads((SCRIPTS / "lexicon.json").read_text(encoding="utf-8"))

HUMAN = (
    "We lost Carta as a client on 14 Feb. I had predicted three months of runway after that; "
    "it took eleven, and the March invoice from Vercel was $4,730.\n\n"
    "I didn't see it coming. Our biggest account had renewed twice and the champion, Maya, "
    "had just been promoted. What changed was a new CFO who cut every tool under $10k a year.\n\n"
    "So here is what we do now: every account over 20% of revenue gets a second contact by month two. "
    "Would that have saved Carta? Probably not, but it would have told us in December instead of February.\n"
)


class Cleaner(unittest.TestCase):
    def clean(self, text):
        return humanize.humanize(text, LEX)

    def test_invisible_characters_are_removed(self):
        out, report = self.clean("ship​ped on time﻿")
        self.assertEqual(out.strip(), "shipped on time")
        self.assertTrue(report["invisible"])

    def test_one_em_dash_survives_in_a_short_post(self):
        """V3: zero em dashes is its own tell. Cap, do not ban."""
        out, _ = self.clean("We shipped it — late, but shipped.")
        self.assertEqual(out.count("—"), 1)

    def test_only_the_excess_em_dashes_become_commas(self):
        out, _ = self.clean("One — two — three — four.")
        self.assertEqual(out.count("—"), 1)
        self.assertNotIn(". ", out.replace("four.", ""), "an em dash must never become a period")

    def test_a_single_marker_in_a_paragraph_is_left_alone(self):
        text = "We leverage our own data here.\n"
        out, report = self.clean(text)
        self.assertIn("leverage", out)
        self.assertEqual(report["lexical"], [])
        self.assertTrue(report["lexical_below_threshold"])

    def test_a_dense_paragraph_is_rewritten(self):
        out, report = self.clean("We leverage robust tools to streamline the work.\n")
        self.assertNotRegex(out.lower(), r"leverage|robust|streamline")
        self.assertEqual(len(report["lexical"]), 3)

    def test_density_is_per_paragraph_not_per_post(self):
        text = "We leverage this.\n\nIt is robust.\n\nIt will streamline things.\n"
        out, report = self.clean(text)
        self.assertEqual(report["lexical"], [], "three markers spread over three paragraphs are not a verdict")
        self.assertIn("leverage", out)

    def test_urls_are_never_rewritten(self):
        url = "https://example.com/leverage—robust-streamline"
        out, _ = self.clean(f"We leverage robust tools to streamline it. {url}\n")
        self.assertIn(url, out)

    def test_structures_are_flagged_not_rewritten(self):
        text = "It's not just a tool, it's a mindset.\n"
        out, report = self.clean(text)
        self.assertEqual(out, text)
        self.assertTrue(any("not just" in f["name"] for f in report["structures"]))

    def test_one_natural_triad_is_not_flagged(self):
        _, report = self.clean("We hired, trained, and shipped.\n")
        self.assertFalse(any(f["name"].startswith("Rule") or "triad" in f["name"].lower()
                             for f in report["structures"]))

    def test_a_clean_human_draft_is_untouched(self):
        out, report = self.clean(HUMAN)
        self.assertEqual(out, HUMAN)
        self.assertFalse(any(report[k] for k in ("invisible", "typographic", "lexical", "structures")))


class Panel(unittest.TestCase):
    def verdict(self, text):
        return score.run(text, LEX)[2]

    def test_a_specific_human_draft_reads_human(self):
        self.assertEqual(self.verdict(HUMAN), "READS HUMAN")

    def test_variance_is_not_rewarded(self):
        """Manufactured long/short alternation must not raise the score."""
        staccato = HUMAN + "\nShort. Punchy. Done. Really.\n"
        self.assertLess(score.check_structure(staccato, LEX)[0], score.check_structure(HUMAN, LEX)[0])

    def test_reveal_bridges_drag_the_verdict(self):
        bridged = HUMAN + "\nThe result?\n\nIt's not just churn, it's a warning.\n\nThoughts?\n"
        self.assertNotEqual(self.verdict(bridged), "READS HUMAN")

    def test_em_dashes_under_the_cap_cost_nothing(self):
        with_one = HUMAN.replace("; it took eleven", " — it took eleven")
        self.assertEqual(score.check_fingerprint(with_one)[0], 100.0)

    def test_the_panel_never_claims_to_be_a_detector(self):
        source = (SCRIPTS / "score.py").read_text(encoding="utf-8")
        self.assertIn("not an AI-detector score", source)


class Lexicon(unittest.TestCase):
    def test_every_structure_regex_compiles(self):
        for s in LEX["structures"]:
            re.compile(s["regex"], re.MULTILINE)

    def test_the_em_dash_entry_is_a_cap(self):
        em = next(e for e in LEX["typographic"] if e["from"] == "—")
        self.assertGreaterEqual(em.get("cap_per_100_words", 0), 1)


class ProfileRubric(unittest.TestCase):
    def test_the_rubric_totals_100(self):
        text = (ROOT / "skills" / "linkedin-profile-optimizer" / "references" / "score-rubric.md").read_text(encoding="utf-8")
        points = [int(m) for m in re.findall(r"^\| [^|]+ \| (\d+) \|", text, re.M)]
        self.assertEqual(len(points), 12)
        self.assertEqual(sum(points), 100)


if __name__ == "__main__":
    unittest.main()
