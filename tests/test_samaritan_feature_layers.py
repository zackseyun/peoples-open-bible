"""Current digital-layer diagnostics do not certify manuscript letters."""
import copy
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools.textual_restoration import check_samaritan_feature_layers as M


class SamaritanFeatureLayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved = json.loads(M.OUT.read_text())

    def feature(self, data):
        return ("@node\n@valueType=str\n@version=7.1.3\n\n" + data).encode()

    def inputs(self):
        issues = {"3": {"data_version": "4.1", "tf_node": 10,
                  "section": ["Exodus", 19, 24], "explanation": "Interpretive concern"}}
        api = SimpleNamespace(
            F=SimpleNamespace(otype=SimpleNamespace(s=lambda kind: [10], v=lambda n: "word"),
                              sign=SimpleNamespace(v=lambda slot: {1: "שׁ", 2: " "}[slot])),
            T=SimpleNamespace(sectionFromNode=lambda n: ("Exodus", 19, 24)),
            L=SimpleNamespace(d=lambda n, otype: [1, 2]))
        features = {"g_cons": {10: "C"}, "g_cons_raw": {10: "C"},
                    "g_cons_utf8": {10: "ש"}, "lex": {10: "HRS["}}
        return api, issues, features

    def test_implicit_node_rows_and_sparse_restarts_are_parsed(self):
        self.assertEqual(M.parse_node_feature(self.feature("10\tK\nJXRSW\n20\tHLK[\n")),
                         {10: "K", 11: "JXRSW", 20: "HLK["})

    def test_changed_or_unsupported_feature_formats_fail(self):
        for raw in (self.feature("10-11\tK\n"), self.feature("10\tK\n10\tK\n"),
                    self.feature("10\t\n"), self.feature(""),
                    b"@edge\n@valueType=str\n@version=7.1.3\n\n10\tK\n",
                    self.feature("10\tK\textra\n")):
            with self.assertRaises(ValueError):
                M.parse_node_feature(raw)

    def test_no_implicit_online_acquisition_and_changed_pins_fail(self):
        for directory, fetch in ((None, False), (M.S.ROOT, True)):
            with self.assertRaises(ValueError):
                M.load_features(directory, fetch)
        with patch.object(M, "urlopen") as remote:
            remote.return_value.__enter__.return_value.read.return_value = self.feature("10\tK\n")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                M.load_features(None, True)
        with self.assertRaises(ValueError):
            M.feature_url("unknown")

    def test_current_locator_type_section_and_feature_coverage_are_required(self):
        api, issues, features = self.inputs()
        bad = copy.deepcopy(features)
        bad["lex"][11] = "HLK["
        with self.assertRaisesRegex(ValueError, "coverage"):
            M.inspect_locators(api, issues, bad)
        api.T.sectionFromNode = lambda n: ("Exodus", 19, 23)
        with self.assertRaisesRegex(ValueError, "section differs"):
            M.inspect_locators(api, issues, features)
        api.F.otype.v = lambda n: "phrase"
        with self.assertRaisesRegex(ValueError, "current word"):
            M.inspect_locators(api, issues, features)

    def test_normalized_surface_agreement_preserves_distinct_original_hashes(self):
        result = M.inspect_locators(*self.inputs())[0]
        self.assertTrue(result["surface_consonants_equal"])
        self.assertTrue(result["g_cons_equals_g_cons_raw"])
        self.assertNotEqual(result["sign_text_sha256"], result["utf8_feature_sha256"])
        self.assertEqual(result["target_excerpt"]["signs_without_trailing_space"], "שׁ")
        self.assertEqual(result["target_excerpt"]["lex"], "HRS[")

    def test_surface_disagreement_is_retained_not_silently_corrected(self):
        api, issues, features = self.inputs()
        features["g_cons_utf8"][10] = "ס"
        features["g_cons_raw"][10] = "F"
        row = M.inspect_locators(api, issues, features)[0]
        self.assertFalse(row["surface_consonants_equal"])
        self.assertFalse(row["g_cons_equals_g_cons_raw"])

    def test_saved_current_diagnostic_denominators_and_bounded_excerpts(self):
        d = self.saved
        self.assertEqual(d["summary"], {"annotation_locators": 29, "utf8_surface_matches": 29,
                                        "transliterated_features_identical": 29})
        self.assertEqual(len(d["rows"]), 29)
        self.assertEqual({r["issue_id"] for r in d["rows"]}, {str(i) for i in range(29)})
        targets = {r["issue_id"]: r for r in d["rows"] if "target_excerpt" in r}
        self.assertEqual(set(targets), {"3", "16"})
        self.assertEqual(targets["3"]["target_excerpt"], {
            "signs_without_trailing_space": "ך", "g_cons": "K", "g_cons_raw": "K",
            "g_cons_utf8": "ך", "lex": "HLK["})
        self.assertEqual(targets["16"]["target_excerpt"], {
            "signs_without_trailing_space": "יחרסו", "g_cons": "JXRSW", "g_cons_raw": "JXRSW",
            "g_cons_utf8": "יחרסו", "lex": "HRS["})
        for row in targets.values():
            self.assertEqual(row["reference_label"], "Exod.19.24")

    def test_source_features_are_pinned_external_and_do_not_claim_diplomatic_status(self):
        d = self.saved
        self.assertTrue(all(v is False for v in d["policy"].values()))
        self.assertIn("does not verify their historical token identity", d["mapping"])
        self.assertIn("not unnormalized byte equality", d["mapping"])
        self.assertEqual({i["feature"]: i["sha256"] for i in d["source"]["feature_inputs"]}, M.FEATURE_PINS)
        self.assertTrue(all(i["word_nodes"] == 114889 for i in d["source"]["feature_inputs"]))
        self.assertTrue(all(i["url"] == M.feature_url(i["feature"]) for i in d["source"]["feature_inputs"]))
        self.assertEqual(d["source"]["issues_sha256"], M.A.ISSUES_SHA)


if __name__ == "__main__":
    unittest.main()
