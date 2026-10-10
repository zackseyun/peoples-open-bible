"""Reference-level provenance safeguards; not verification of manuscript readings."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools.textual_restoration import audit_samaritan_editorial_issues as M


class SamaritanEditorialAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved = json.loads(M.OUT.read_text())

    def issue(self, ref=None, explanation="Considered a scribal error and harmonized with the MT"):
        return {"0": {"data_version": "6.3", "tf_node": 100,
                      "section": ref or ["Genesis", 1, 1], "explanation": explanation}}

    def pools(self):
        return ({"largest_length_difference_leads": [{"reference_label": "Gen.1.1"}],
                 "numbering_or_repetition_review": [{"reference_label": "Gen.1.2",
                    "other_exact_wlc_reference_candidates": ["Gen.1.1", "Gen.1.1"]}]},
                {"nodes": [{"sp_reference": "Gen.1.2", "candidate_spans": [
                    {"parallel_reference_candidates": [
                        {"control": "SP", "reference_label": "Gen.1.1"},
                        {"control": "SP", "reference_label": "Gen.1.1"},
                        {"control": "WLC", "reference_label": "Gen.1.3"}]}]}]})

    def test_saved_annotation_and_unique_section_denominators(self):
        d = self.saved
        self.assertEqual(d["summary"]["issue_annotations"], 29)
        self.assertEqual(d["summary"]["unique_reference_sections"], 27)
        self.assertEqual(len(d["annotations"]), 29)
        self.assertEqual(len(d["current_sections"]), 27)
        self.assertEqual(d["summary"]["annotation_versions"], {"4.1": 13, "6.3": 16})
        self.assertEqual(d["summary"]["annotation_categories"], {
            "other-analysis-or-reading-concern": 13,
            "reported-harmonization-to-core-sp": 2, "reported-harmonization-to-mt": 14})
        self.assertEqual(d["summary"]["current_section_comparisons"], {"different": 27})
        self.assertEqual(sorted(int(r["issue_id"]) for r in d["annotations"]), list(range(29)))
        flattened = [i for u in d["current_sections"] for i in u["issue_ids"]]
        self.assertEqual(sorted(flattened, key=int), [str(i) for i in range(29)])

    def test_saved_pools_are_distinct_reference_denominators_not_votes(self):
        rows = self.saved["lead_intersections"]
        self.assertEqual([r["distinct_reference_labels"] for r in rows], [20, 15, 46, 20, 124, 92])
        self.assertTrue(all(r["annotated_reference_labels"] == [] for r in rows))
        screen = json.loads((M.ROOT / M.SCREEN_PATH).read_text())
        parallel = json.loads((M.ROOT / M.PARALLEL_PATH).read_text())
        pools = M.reference_pools(screen, parallel)
        refs = {a["reference_label"] for a in self.saved["annotations"]}
        for row in rows:
            pool = pools[row["pool"]]
            self.assertEqual(len(pool), row["distinct_reference_labels"])
            self.assertEqual(sorted(refs & pool, key=M.S.ref_key), row["annotated_reference_labels"])

    def test_frozen_receipts_and_reader_pins_are_unchanged(self):
        s = self.saved["source"]
        self.assertEqual(s["issues_sha256"], M.ISSUES_SHA)
        for field, expected in (("frozen_screen", M.SCREEN_SHA), ("frozen_parallel", M.PARALLEL_SHA)):
            record = s[field]
            self.assertEqual(record["sha256"], expected)
            self.assertEqual(M.S.sha((M.ROOT / record["repo_path"]).read_bytes()), expected)
        for record in s["wlc_inputs"]:
            self.assertEqual(M.S.sha((M.ROOT / record["path"]).read_bytes()), record["sha256"])
        self.assertEqual(s["sp_inputs"], [{"path": "README.md", "sha256": M.S.README_SHA}] + [
            {"path": f"tf/{M.S.VERSION}/{name}", "sha256": digest} for name, digest in M.S.PINNED.items()])

    def test_policies_do_not_certify_sign_edits_or_unannotated_manuscripts(self):
        self.assertTrue(all(v is False for v in self.saved["policy"].values()))
        self.assertIn("whether current sign.tf was altered", self.saved["limitations"])
        self.assertIn("not certified complete", self.saved["limitations"])
        self.assertIn("not promoted to stable token identities", self.saved["mapping"])
        output = json.dumps(self.saved, ensure_ascii=False)
        self.assertFalse(any("א" <= c <= "ת" for c in output))

    def test_synthetic_cross_pool_intersection_preserves_alternatives(self):
        screen, parallel = self.pools()
        result = M.audit(self.issue(), {"Gen.1.1": "אב "}, {"Gen.1.1": "אב"}, screen, parallel)
        rows = {r["pool"]: r for r in result["lead_intersections"]}
        self.assertEqual(rows["parallel_sp_alternatives"]["distinct_reference_labels"], 1)
        self.assertEqual(rows["parallel_sp_alternatives"]["annotated_reference_labels"], ["Gen.1.1"])
        self.assertEqual(rows["parallel_wlc_alternatives"]["annotated_reference_labels"], [])
        self.assertEqual(result["current_sections"][0]["same_label_consonantal_comparison"], "equal")
        self.assertEqual(result["annotations"][0]["category"], "reported-harmonization-to-mt")
        self.assertEqual(result["annotations"][0]["annotation_tf_node"], 100)

    def test_multiple_annotations_do_not_become_multiple_sections(self):
        issues = self.issue()
        issues["1"] = copy.deepcopy(issues["0"])
        issues["1"]["explanation"] = "Interpretive analysis remains uncertain"
        result = M.audit(issues, {"Gen.1.1": "אב"}, {"Gen.1.1": "גד"}, *self.pools())
        self.assertEqual(result["summary"]["issue_annotations"], 2)
        self.assertEqual(result["summary"]["unique_reference_sections"], 1)
        self.assertEqual(result["current_sections"][0]["issue_ids"], ["0", "1"])

    def test_invalid_or_missing_annotation_sections_fail(self):
        for section in (["Other", 1, 1], ["Genesis", True, 1], ["Genesis", 0, 1], ["Genesis", 1]):
            with self.assertRaises(ValueError):
                M.issue_rows(self.issue(section))
        with self.assertRaisesRegex(ValueError, "absent"):
            M.audit(self.issue(), {}, {}, *self.pools())
        with self.assertRaisesRegex(ValueError, "empty"):
            M.issue_rows({})

    def test_changed_pin_and_unknown_harmonization_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "issues.json"
            path.write_text("{}")
            with self.assertRaisesRegex(ValueError, "pinned hash mismatch"):
                M.pinned_json(path, M.ISSUES_SHA)
        with self.assertRaisesRegex(ValueError, "unrecognized harmonization"):
            M.issue_rows(self.issue(explanation="harmonized to another unidentified source"))

    def test_registry_preserves_source_class_and_affected_layer_limit(self):
        registry = json.loads((M.ROOT / "sources/textual_restoration/ot_witness_registry.v1.json").read_text())
        row = next(w for w in registry["witnesses"] if w["id"] == "dt-ucph-samaritan-7-1-3")
        self.assertEqual(row["witness_class"], "modern-transcription")
        self.assertEqual(row["date_basis"]["kind"], "edition-publication")
        self.assertIn("affected feature layer unverified", row["textual_role"])
        self.assertIn("not certified as an unaltered diplomatic transcription", row["textual_role"])
        self.assertTrue(any(a["url"] == self.saved["source"]["issues_url"] for a in row["access"]))


if __name__ == "__main__":
    unittest.main()
