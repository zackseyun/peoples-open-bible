import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "samaritan_parallel_blocks", ROOT / "tools/textual_restoration/screen_samaritan_parallel_blocks.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class SamaritanParallelBlockTests(unittest.TestCase):
    def node(self, text, wlc):
        return M.discover_node("Gen.1.1", text, M.wlc_index(wlc))

    def test_cross_book_references_and_all_repeated_alternatives(self):
        node = self.node("אב גד אב גד  ", {"Num.1.1": "אב גד", "Exod.1.1": "אב גד"})
        self.assertEqual([c["sp_character_span"] for c in node["candidate_spans"]], [[0, 5], [6, 11]])
        for candidate in node["candidate_spans"]:
            self.assertEqual([r["reference_label"] for r in candidate["parallel_reference_candidates"]],
                             ["Exod.1.1", "Num.1.1"])

    def test_overlapping_candidates_are_retained_without_selection(self):
        node = self.node("אב גד הו", {"Gen.1.1": "אב גד", "Lev.1.1": "גד הו"})
        self.assertEqual([c["sp_character_span"] for c in node["candidate_spans"]], [[0, 5], [3, 8]])
        middle = next(p for p in node["partition"] if p["sp_character_span"] == [3, 5])
        self.assertEqual(middle["coverage"], "overlapping")
        self.assertEqual(middle["candidate_ids"], ["m001", "m002"])

    def test_within_word_hits_are_rejected_at_both_endpoints(self):
        node = self.node("זאב אבז אב", {"Gen.1.1": "אב"})
        self.assertEqual([c["sp_character_span"] for c in node["candidate_spans"]], [[8, 10]])

    def test_matres_final_forms_and_full_verse_extent_are_preserved(self):
        node = self.node("קטורת מלך אב", {"Gen.1.1": "קטרת", "Gen.1.2": "מלכ", "Gen.1.3": "אב גד"})
        self.assertEqual(node["candidate_spans"], [])

    def test_short_repeated_formula_has_no_minimum_length(self):
        node = self.node("אב אב", {"Gen.1.1": "אב", "Deut.1.1": "אב"})
        self.assertEqual(len(node["candidate_spans"]), 2)
        self.assertTrue(all(len(c["parallel_reference_candidates"]) == 2 for c in node["candidate_spans"]))

    def test_sp_parallel_self_exclusion_and_control_alternatives(self):
        sp = {"Gen.1.1": "אב גד  ", "Deut.1.1": "אב גד ", "Num.1.1": "אב גד"}
        index = M.source_index(sp, "SP")
        for key, alternatives in M.wlc_index({"Exod.1.1": "אב גד"}).items():
            index.setdefault(key, []).extend(alternatives)
        node = M.discover_node("Gen.1.1", sp["Gen.1.1"], index)
        self.assertEqual(len(node["candidate_spans"]), 1)
        alternatives = node["candidate_spans"][0]["parallel_reference_candidates"]
        self.assertEqual([(a["control"], a["reference_label"]) for a in alternatives],
                         [("SP", "Num.1.1"), ("SP", "Deut.1.1"), ("WLC", "Exod.1.1")])
        deut = alternatives[1]
        self.assertEqual(deut["source_character_span"], [0, len(sp["Deut.1.1"])])
        self.assertEqual(deut["raw_sha256"], M.sha(sp["Deut.1.1"].encode()))
        self.assertEqual(M.discover_node("Gen.1.1", sp["Gen.1.1"],
                         M.source_index({"Gen.1.1": sp["Gen.1.1"]}, "SP"))["candidate_spans"], [])

    def test_lossless_partition_keeps_unmatched_letters_and_spaces(self):
        text = "  זח אב גד הו טי  "
        node = self.node(text, {"Gen.1.1": "אב גד", "Lev.1.1": "גד הו"})
        parts = node["partition"]
        self.assertEqual(parts[0]["sp_character_span"][0], 0)
        self.assertEqual(parts[-1]["sp_character_span"][1], len(text))
        self.assertEqual("".join(text[s:e] for s, e in (p["sp_character_span"] for p in parts)), text)
        self.assertEqual(sum(p["raw_character_count"] for p in parts), len(text))
        self.assertEqual(sum(p["consonant_count"] for p in parts), len(M.consonants(text)))
        for part in parts:
            start, end = part["sp_character_span"]
            self.assertEqual(part["raw_sha256"], M.sha(text[start:end].encode()))
            self.assertEqual(part["consonants_sha256"], M.sha(M.consonants(text[start:end]).encode()))

    def test_no_candidate_still_has_complete_partition(self):
        node = self.node("אב  ", {"Gen.1.1": "גד"})
        self.assertEqual(node["partition"][0]["sp_character_span"], [0, 4])
        self.assertEqual(node["partition"][0]["coverage"], "unmatched")

    def test_all_20_frozen_leads_accounted_in_frozen_order(self):
        frozen = json.loads(M.FROZEN.read_text())
        leads = frozen["largest_length_difference_leads"]
        sp = {lead["reference_label"]: "אב  " for lead in leads}
        nodes = M.discover(sp, {"Gen.1.1": "גד"}, leads)
        self.assertEqual([n["sp_reference"] for n in nodes], [l["reference_label"] for l in leads])
        self.assertEqual(len(nodes), 20)
        self.assertTrue(all(n["partition"] for n in nodes))
        with self.assertRaisesRegex(ValueError, "exactly 20"):
            M.discover(sp, {"Gen.1.1": "גד"}, leads[:-1])
        with self.assertRaisesRegex(ValueError, "absent"):
            M.discover({}, {"Gen.1.1": "גד"}, leads)

    def test_metadata_has_no_hebrew_source_text(self):
        text = "בראשית ברא  "
        output = json.dumps(self.node(text, {"Gen.1.1": "בראשית ברא"}), ensure_ascii=False)
        self.assertFalse(any("א" <= char <= "ת" for char in output))

    def test_result_is_independent_of_wlc_input_order(self):
        first = {"Num.1.1": "אב", "Gen.1.1": "אב גד", "Exod.1.1": "אב"}
        self.assertEqual(self.node("אב גד אב  ", first),
                         self.node("אב גד אב  ", dict(reversed(list(first.items())))))

    def test_frozen_receipt_and_reproduction_fail_before_discovery(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            frozen = root / M.FROZEN.relative_to(ROOT)
            frozen.parent.mkdir(parents=True)
            frozen.write_bytes(M.FROZEN.read_bytes())
            with patch.object(M.BASE, "build", return_value={}):
                with self.assertRaisesRegex(ValueError, "differs from pinned recomputation"):
                    M.build(root, root)
            frozen.write_text("{}")
            with self.assertRaisesRegex(ValueError, "receipt hash mismatch"):
                M.build(root, root)

    def test_saved_discovery_counts_and_partition_invariants(self):
        data = json.loads(M.OUT.read_text())
        summary = data["summary"]
        self.assertEqual(summary["selected_sp_nodes"], 20)
        self.assertEqual(summary["searched_wlc_verses"], 5853)
        self.assertEqual(summary["searched_sp_nodes"], 5841)
        self.assertEqual(summary["eligible_sp_nodes_per_target"], 5840)
        self.assertEqual(summary["candidate_spans"], 68)
        self.assertEqual(summary["reference_alternatives"], 502)
        self.assertEqual(summary["by_control"], {
            "WLC": {"nodes_with_candidates": 15, "candidate_spans": 29, "reference_alternatives": 233},
            "SP": {"nodes_with_candidates": 19, "candidate_spans": 59, "reference_alternatives": 269}})
        self.assertEqual(summary["sp_raw_characters"], 9143)
        self.assertEqual(summary["matched_raw_characters"], 4672)
        self.assertEqual(summary["unmatched_raw_characters"], 4471)
        self.assertEqual(summary["sp_consonants"], 7266)
        self.assertEqual(summary["matched_consonants"], 3763)
        self.assertEqual(summary["unmatched_consonants"], 3503)
        self.assertEqual(summary["overlapping_partition_spans"], 0)
        self.assertEqual(data["source"]["frozen_screen_sha256"], M.FROZEN_SHA)
        self.assertTrue(data["source"]["frozen_screen_reproduced"])
        self.assertEqual(data["generator"]["sha256"], M.sha(Path(M.__file__).read_bytes()))
        frozen = json.loads(M.FROZEN.read_text())
        self.assertEqual([n["sp_reference"] for n in data["nodes"]],
                         [l["reference_label"] for l in frozen["largest_length_difference_leads"]])
        for node in data["nodes"]:
            parts = node["partition"]
            self.assertEqual(parts[0]["sp_character_span"][0], 0)
            self.assertEqual(parts[-1]["sp_character_span"][1], node["raw_character_count"])
            for left, right in zip(parts, parts[1:]):
                self.assertEqual(left["sp_character_span"][1], right["sp_character_span"][0])
            self.assertEqual(sum(p["raw_character_count"] for p in parts), node["raw_character_count"])
            self.assertEqual(sum(p["consonant_count"] for p in parts), node["consonant_count"])
            candidates = {c["candidate_id"]: c for c in node["candidate_spans"]}
            for part in parts:
                start, end = part["sp_character_span"]
                self.assertEqual(part["candidate_ids"], [cid for cid, c in candidates.items()
                                 if c["sp_character_span"][0] <= start and end <= c["sp_character_span"][1]])
            for candidate in candidates.values():
                for alternative in candidate["parallel_reference_candidates"]:
                    self.assertFalse(alternative["control"] == "SP"
                                     and alternative["reference_label"] == node["sp_reference"])
                    self.assertEqual(alternative["consonants_sha256"], candidate["consonants_sha256"])
        self.assertTrue(all(value is False for value in data["policy"].values()))
        self.assertFalse(any("א" <= char <= "ת" for char in json.dumps(data, ensure_ascii=False)))


if __name__ == "__main__":
    unittest.main()
