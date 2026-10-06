"""Public metadata checks; these do not certify private SP readings or ink."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "sources/textual_restoration/discovery/numbers13_33_alignment.2026-10-05.v1.json"
FROZEN = ROOT / "sources/textual_restoration/discovery/samaritan_parallel_blocks.v1.json"
FROZEN_SHA = "e9b4f42664bf0ff5a37ddeb5e0ce18ec2924f4cb194e0bb1a5a9e903789c0068"
BASELINE = "c14ef7e301576128acd863042cdd667b27051dce"
SPEC = importlib.util.spec_from_file_location(
    "numbers_alignment_reader", ROOT / "tools/textual_restoration/build_samaritan_screen.py")
READER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(READER)


class Numbers1333AlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text())
        cls.frozen = json.loads(FROZEN.read_text())
        cls.lead = next(n for n in cls.frozen["nodes"] if n["sp_reference"] == "Num.13.33")

    def test_frozen_identity_and_all_input_pins(self):
        source = self.record["source"]
        self.assertEqual(self.record["baseline_commit"], BASELINE)
        self.assertEqual(hashlib.sha256(FROZEN.read_bytes()).hexdigest(), FROZEN_SHA)
        self.assertEqual(source["frozen_discovery_sha256"], FROZEN_SHA)
        self.assertEqual(ROOT / source["frozen_discovery_repo_path"], FROZEN)
        self.assertEqual(source["frozen_lead_reference"], "Num.13.33")
        self.assertEqual(source["sp_inputs"], self.frozen["source"]["sp_inputs"])
        self.assertEqual(source["wlc_inputs"], self.frozen["source"]["wlc_inputs"])
        self.assertEqual(len(source["sp_inputs"]), 8)
        self.assertEqual(len(source["wlc_inputs"]), 5)
        for pin in source["wlc_inputs"]:
            self.assertEqual(READER.sha((ROOT / pin["path"]).read_bytes()), pin["sha256"])
        self.assertEqual(source["sp_commit"], READER.COMMIT)
        self.assertEqual(source["sp_version"], READER.VERSION)
        self.assertEqual(READER.sha((ROOT / source["pinned_reader_repo_path"]).read_bytes()),
                         source["pinned_reader_sha256"])
        target = self.record["target"]
        self.assertEqual(target["reference_label"], self.lead["sp_reference"])
        self.assertEqual(target["raw_character_span"], self.lead["sp_character_span"])
        for key in ("raw_character_count", "consonant_count", "raw_sha256", "consonants_sha256"):
            self.assertEqual(target[key], self.lead[key])

    def test_eight_ordered_units_cover_whole_node_losslessly_in_metadata(self):
        segments = self.record["segments"]
        expected = [
            ("Num.13.33", [0, 77], 63),
            ("Deut.1.27", [77, 172], 79),
            ("Deut.1.28", [172, 278], 85),
            ("Deut.1.29", [278, 324], 37),
            ("Deut.1.30", [324, 393], 56),
            ("Deut.1.31", [393, 489], 75),
            ("Deut.1.32", [489, 525], 30),
            ("Deut.1.33", [525, 611], 70),
        ]
        self.assertEqual([(s["content_reference"], s["target_sp_character_span"],
                           s["consonant_count"]) for s in segments], expected)
        self.assertEqual([s["unit_id"] for s in segments], [f"u{i:02}" for i in range(1, 9)])
        for segment in segments:
            start, end = segment["target_sp_character_span"]
            self.assertLess(start, end)
            self.assertEqual(segment["raw_character_count"], end - start)
            self.assertLessEqual(segment["consonant_count"], end - start)
        for left, right in zip(segments, segments[1:]):
            self.assertEqual(left["target_sp_character_span"][1], right["target_sp_character_span"][0])
        self.assertEqual(sum(s["raw_character_count"] for s in segments), 611)
        self.assertEqual(sum(s["consonant_count"] for s in segments), 495)
        self.assertEqual(sum(s["raw_character_count"] for s in segments[1:]), 534)
        self.assertEqual(sum(s["consonant_count"] for s in segments[1:]), 432)
        self.assertEqual(self.record["summary"], {
            "mapped_units": 8, "local_report_raw_characters": 77,
            "local_report_consonants": 63, "added_sequence_raw_characters": 534,
            "added_sequence_consonants": 432, "adapted_Deuteronomy_units": 2,
            "consonantal_equal_SP_Deuteronomy_units": 5,
            "consonantal_equal_WLC_Deuteronomy_units": 2})

    def test_adaptations_and_equal_control_relations_remain_separate(self):
        segments = self.record["segments"]
        self.assertEqual(segments[0]["classification"], "local-report-with-orthographic-differences")
        self.assertEqual(segments[0]["comparison"]["SP"]["consonantal_relation"],
                         "not-applicable-self-node-local-subset")
        self.assertEqual(segments[0]["comparison"]["WLC"]["consonantal_relation"], "different")
        adapted = [s["content_reference"] for s in segments
                   if s["classification"] == "adapted-narrative-parallel"]
        self.assertEqual(adapted, ["Deut.1.27", "Deut.1.29"])
        for segment in segments[1:]:
            ref = segment["content_reference"]
            sp_equal = ref not in adapted
            wlc_equal = ref in {"Deut.1.30", "Deut.1.31"}
            self.assertEqual(segment["comparison"]["SP"]["consonantal_relation"],
                             "equal" if sp_equal else "adapted")
            self.assertEqual(segment["comparison"]["SP"]["raw_full_source_equal"], sp_equal)
            self.assertEqual(segment["comparison"]["WLC"]["consonantal_relation"],
                             "equal" if wlc_equal else ("adapted-narrative" if ref in adapted else "different"))

    def test_full_control_hashes_and_wlc_written_text_are_verified(self):
        refs = ["Num.13.33"] + [f"Deut.1.{i}" for i in range(27, 34)]
        controls = self.record["controls"]
        self.assertEqual([(c["control"], c["reference_label"]) for c in controls],
                         [(kind, ref) for kind in ("SP", "WLC") for ref in refs])
        lookup = {(c["control"], c["reference_label"]): c for c in controls}
        wlc, _ = READER.load_wlc(ROOT / "sources/ot/wlc")
        for ref in refs:
            source = wlc[ref]
            control = lookup[("WLC", ref)]
            self.assertEqual(control["raw_character_count"], len(source))
            self.assertEqual(control["consonant_count"], len(READER.consonants(source)))
            self.assertEqual(control["raw_sha256"], READER.sha(source.encode()))
            self.assertEqual(control["consonants_sha256"], READER.sha(READER.consonants(source).encode()))
        sp_target = lookup[("SP", "Num.13.33")]
        for key in ("raw_character_count", "consonant_count", "raw_sha256", "consonants_sha256"):
            self.assertEqual(sp_target[key], self.record["target"][key])
        for segment in self.record["segments"][1:]:
            if segment["comparison"]["SP"]["raw_full_source_equal"]:
                control = lookup[("SP", segment["content_reference"])]
                for key in ("raw_character_count", "consonant_count", "raw_sha256", "consonants_sha256"):
                    self.assertEqual(segment[key], control[key])

    def test_frozen_exact_spans_are_preserved_inside_full_units(self):
        lookup = {s["content_reference"]: s for s in self.record["segments"]}
        self.assertEqual(len(self.lead["candidate_spans"]), 5)
        for candidate in self.lead["candidate_spans"]:
            sp_controls = [a for a in candidate["parallel_reference_candidates"] if a["control"] == "SP"]
            self.assertEqual(len(sp_controls), 1)
            ref = sp_controls[0]["reference_label"]
            unit = lookup[ref]
            start, end = candidate["sp_character_span"]
            self.assertEqual(unit["target_sp_character_span"], [start, end + 1])
            self.assertEqual(unit["raw_character_count"], candidate["raw_character_count"] + 1)
            self.assertEqual(unit["consonant_count"], candidate["consonant_count"])
            self.assertEqual(unit["consonants_sha256"], candidate["consonants_sha256"])
            self.assertEqual(unit["raw_sha256"], sp_controls[0]["raw_sha256"])

    def test_frozen_private_segment_hashes_and_hash_shapes(self):
        expected = [
            "1255e19bf65778df9f4c177ec89145b4c562f4d2beaa9b85d6570a600f6ff8ae",
            "8c7f889e1d888021e1fb50365123787dd31d9d97a5af92f85e9a1dc201f30ab5",
            "203aed3fb5b6274f84ac9c3967eae8e32e2f1c27717d11740e68f9bfe37d4be4",
            "514484277e69e4be047bda674cfbfc7dd97aa4baf3cecd25f6eebd5a276a4d4b",
            "214b4295af22c1e05960ad0dc840d3e82e5ffd19347d0af3d9cf9f54828d33fb",
            "b2ad94c4a82de56e9c604ab8660a96ca510fe6388a92b6fd42cb106a42aff671",
            "cb76058200f09744cb13b7bf22aaab10350445c7ed0ec9db588d4ac5bfcfacbc",
            "77036409c1093db0b53cca10dae7c40f98295bc44cc46f220589dff4fcaf0fc9",
        ]
        self.assertEqual([s["raw_sha256"] for s in self.record["segments"]], expected)

        def visit(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if key.endswith("sha256"):
                        self.assertRegex(item, r"^[0-9a-f]{64}$")
                    visit(item)
            elif isinstance(value, list):
                for item in value:
                    visit(item)
        visit(self.record)

    def test_metadata_does_not_claim_ancient_votes_pixels_or_publication(self):
        self.assertTrue(all(value is False for value in self.record["policy"].values()))
        self.assertFalse(any("א" <= char <= "ת" for char in json.dumps(self.record, ensure_ascii=False)))
        verification = self.record["verification"]
        self.assertTrue(verification["private_pinned_input_recheck_completed"])
        self.assertTrue(verification["frozen_target_partition_and_candidate_hashes_reproduced"])
        self.assertFalse(verification["whole_corpus_screen_rerun"])
        self.assertIn("do not access the private SP text", verification["public_tests_scope"])
        self.assertIn("not new manuscript pixels", verification["reading_basis"])
        self.assertTrue(any("not independent ancient witness votes" in limit
                            for limit in self.record["limits"]))
        self.assertTrue(any("physical-preservation claim" in limit for limit in self.record["limits"]))


if __name__ == "__main__":
    unittest.main()
