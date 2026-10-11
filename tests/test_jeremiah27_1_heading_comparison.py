"""Provenance and non-application checks, not certification of textual priority."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "sources/textual_restoration/comparisons/"
CASE = PREFIX + "jeremiah27_1_heading.2026-10-10.v2.json"
CONTRACT = PREFIX + "jeremiah27_1_heading_contract.2026-10-10.v2.json"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def manifest_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":")).encode())


class Jeremiah271HeadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = json.loads((ROOT / CASE).read_text())
        cls.contract = json.loads((ROOT / CONTRACT).read_text())

    def test_frozen_case_report_and_local_evidence_pins(self):
        for path, expected in self.contract["pins"].items():
            self.assertEqual(sha((ROOT / path).read_bytes()), expected, path)
        original = json.loads((ROOT / self.contract["original_contract"]).read_text())
        for path, expected in original["pins"].items():
            self.assertEqual(sha((ROOT / path).read_bytes()), expected, path)
        for path, expected in self.case["integrity"]["pins"].items():
            # This binds the method actually used for the historical case,
            # not future edits to the method. Source evidence stays live.
            raw = (subprocess.check_output(['git', 'show',
                    self.case['baseline_revision'] + ':' + path], cwd=ROOT)
                   if path == 'docs/TEXTUAL_ADJUDICATION_METHOD.md'
                   else (ROOT / path).read_bytes())
            self.assertEqual(sha(raw), expected, path)
        for record in [self.case["baseline"], *self.case["context_read"]]:
            raw = subprocess.check_output(["git", "show",
                self.case["baseline_revision"] + ":" + record["path"]], cwd=ROOT)
            self.assertEqual(sha(raw), record["sha256"])
            verse = yaml.safe_load(raw)
            self.assertEqual(verse["source"], record["source"])
            self.assertEqual(verse["translation"]["text"], record["english"])

    def test_query_control_does_not_turn_lacuna_into_omission(self):
        screen = self.case["qdr_screen"]
        self.assertEqual(screen["correct_source_reference_label"], "Jer")
        self.assertTrue(screen["positive_control_passed"])
        self.assertEqual(screen["query_results"]["Jer 42:7"]["witnesses"], ["2Q13"])
        self.assertTrue(screen["initial_wrong_full_name_query_discarded"])
        self.assertTrue(screen["absence_is_no_local_tag_not_attested_omission"])
        for verse, lines in [(1, 1), (2, 2), (3, 3)]:
            hit = screen["query_results"][f"Jer 27:{verse}"]
            self.assertEqual(hit, {"witnesses": ["4Q72"], "lines": lines})
        fragment = self.case["controls"][0]
        self.assertEqual(fragment["available_lines_read"], 4)
        self.assertEqual(fragment["preserved_heading_tail"], "אמר")
        for key in ["king_name_preserved", "full_heading_preserved", "received_pointing_attested"]:
            self.assertFalse(fragment[key])

    def test_alternatives_and_nonuniversal_version_claims(self):
        alternatives = {a["id"]: a for a in self.case["alternatives"]}
        self.assertEqual(set(alternatives), {"long_Jehoiakim", "long_Zedekiah", "short_no_heading"})
        self.assertEqual(alternatives["long_Zedekiah"]["normalized_unpointed_name"], "צדקיה")
        self.assertEqual(self.case["controls"][1]["reading"], "צדקיה")
        archived = json.loads((ROOT / self.case["supersedes"]).read_text())
        self.assertEqual(archived["controls"][1]["reading"], "צדקיהו")
        self.assertEqual(len(self.case["versioned_corrections"]), 2)
        self.assertIsNone(alternatives["long_Zedekiah"]["full_pointed_candidate"])
        self.assertFalse(alternatives["long_Zedekiah"]["exact_replacement_pointing_or_accents_attested"])
        hebrew = self.case["controls"][1]
        self.assertEqual([s["id"] for s in hebrew["states"]], ["224", "590", "154"])
        self.assertTrue(all(not s["fresh_manuscript_reading"] for s in hebrew["states"]))
        self.assertFalse(self.case["controls"][3]["manuscript_unanimity_claimed"])
        greek = self.case["controls"][5]
        self.assertFalse(greek["all_Greek_heading_absence_claimed"])
        self.assertEqual(greek["name"], "Ιωακειμ")
        self.assertIn("Qmg", greek["positive_apparatus"])

    def test_proposal_is_not_source_application_or_historical_approval(self):
        decision = self.case["proposed_decision"]
        self.assertEqual(decision["historical_name_priority"], "unresolved")
        self.assertEqual(decision["whole_heading_priority"], "unresolved")
        self.assertEqual(decision["working_preference"], "held")
        self.assertTrue(decision["reviewer_disagreement_preserved"])
        for field in ["canonical_source_changed", "canonical_english_changed",
                      "source_candidate_constructed", "promotion_approved",
                      "chronological_preference_used", "novel_reading_demonstrated",
                      "fresh_image_reading", "canon_changed", "publication_approved"]:
            self.assertFalse(decision[field])
        self.assertEqual(self.contract["independent_source_reviews"], 1)
        self.assertFalse(self.contract["repeat_until_agreement"])
        self.assertEqual(self.contract["english_preference_votes"], 0)

    def test_historical_book_and_chapter_manifest(self):
        archive = subprocess.check_output(["git", "archive", self.case["baseline_revision"],
                                           "translation/ot/jeremiah"], cwd=ROOT)
        historical = {}
        with tarfile.open(fileobj=io.BytesIO(archive)) as snapshot:
            for entry in snapshot.getmembers():
                if entry.isfile() and entry.name.endswith(".yaml"):
                    historical[entry.name] = sha(snapshot.extractfile(entry).read())
        integrity = self.case["integrity"]
        self.assertEqual(len(historical), integrity["jeremiah_files"])
        self.assertEqual(manifest_sha(historical), integrity["jeremiah_manifest_sha256"])
        chapter = {p: s for p, s in historical.items() if "/027/" in p}
        self.assertEqual(len(chapter), integrity["chapter27_files"])
        self.assertEqual(manifest_sha(chapter), integrity["chapter27_manifest_sha256"])


if __name__ == "__main__":
    unittest.main()
