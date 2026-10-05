import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "exodus_declared_alignment", ROOT / "tools/textual_restoration/align_exodus20_21.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def controls():
    """Synthetic exact-sized controls, not a redistributed SP text fixture."""
    blocks, spaces_left = [], 133
    for number, (start, end, _, _, _) in enumerate(M.DECLARED):
        length = end - start
        spaces = 9 if number == 0 else min(spaces_left, length - 2)
        if number:
            spaces_left -= spaces
        blocks.append("א" + " " * spaces + "ב" * (length - spaces - 1))
    target = " ".join(blocks) + " "
    sp, wlc = {M.TARGET: target}, {M.TARGET: "ָ".join(M.BASE.consonants(blocks[0]))}
    for declaration, value in zip(M.DECLARED[1:], blocks[1:]):
        _, _, _, ref, span = declaration
        if span:
            sp[ref] = "ג" * span[0] + value + " ד "
        else:
            sp[ref] = value + " "
    return sp, wlc


class ExodusDeclaredAlignmentTests(unittest.TestCase):
    def test_complete_lossless_partition_and_counts(self):
        sp, wlc = controls()
        result = M.align(sp, wlc)
        self.assertEqual(result["summary"], {
            "declared_blocks": 11, "partition_parts": 22, "raw_characters": 720,
            "consonants": 567, "retained_core_consonants": 37,
            "added_block_consonants": 530, "accounted_spaces_outside_blocks": 11,
            "unaccounted_raw_characters": 0})
        parts = result["partition"]
        self.assertEqual(parts[0]["character_span"][0], 0)
        self.assertEqual(parts[-1]["character_span"][1], 720)
        for left, right in zip(parts, parts[1:]):
            self.assertEqual(left["character_span"][1], right["character_span"][0])
        self.assertEqual("".join(sp[M.TARGET][p["character_span"][0]:p["character_span"][1]]
                                 for p in parts), sp[M.TARGET])
        self.assertEqual(sum(p["raw_character_count"] for p in parts), 720)
        self.assertEqual(sum(p["consonant_count"] for p in parts), 567)
        for p in parts:
            start, end = p["character_span"]
            self.assertEqual(p["raw_sha256"], M.BASE.sha(sp[M.TARGET][start:end].encode()))
            self.assertEqual(p["consonants_sha256"],
                             M.BASE.sha(M.BASE.consonants(sp[M.TARGET][start:end]).encode()))

    def test_partial_clauses_and_full_node_source_spans_are_explicit(self):
        sp, wlc = controls()
        blocks = M.align(sp, wlc)["blocks"]
        self.assertEqual(blocks[1]["source"]["character_span"], [0, 22])
        self.assertEqual(blocks[2]["source"]["character_span"], [51, 108])
        for b in blocks[1:]:
            target_start, target_end = b["target"]["character_span"]
            source_start, source_end = b["source"]["character_span"]
            self.assertEqual(sp[M.TARGET][target_start:target_end],
                             sp[b["source"]["reference_label"]][source_start:source_end])
            self.assertEqual(b["comparison"], "raw-identical")
        for b in blocks[3:]:
            self.assertEqual(b["source"]["character_span"],
                             [0, len(sp[b["source"]["reference_label"]].rstrip(" "))])
        self.assertEqual(blocks[0]["comparison"], "written-consonants-identical")
        self.assertNotEqual(blocks[0]["target"]["raw_sha256"], blocks[0]["source"]["raw_sha256"])

    def test_sp_source_mutation_fails_closed(self):
        sp, wlc = controls()
        sp["Deut.18.20"] = "ד" + sp["Deut.18.20"][1:]
        with self.assertRaisesRegex(ValueError, "SP raw block equality failed"):
            M.align(sp, wlc)

    def test_wlc_source_mutation_fails_closed_including_final_forms(self):
        sp, wlc = controls()
        for replacement in ("ו", "ך", "כ"):
            with self.subTest(replacement=replacement):
                changed = {M.TARGET: replacement + wlc[M.TARGET][1:]}
                with self.assertRaisesRegex(ValueError, "WLC core consonantal equality failed"):
                    M.align(sp, changed)

    def test_target_extent_count_and_boundary_mutations_fail_closed(self):
        sp, wlc = controls()
        for value in (sp[M.TARGET][:-1], " " + sp[M.TARGET][1:],
                      sp[M.TARGET][:46] + "א" + sp[M.TARGET][47:]):
            with self.subTest(value_length=len(value)):
                with self.assertRaises(ValueError):
                    M.align({**sp, M.TARGET: value}, wlc)
        # Preserve both totals while moving the first external separator.
        value = list(sp[M.TARGET])
        value[45], value[46] = value[46], value[45]
        with self.assertRaises(ValueError):
            M.align({**sp, M.TARGET: "".join(value)}, wlc)

    def test_declared_reordering_and_span_mutation_are_rejected(self):
        sp, wlc = controls()
        declarations = list(M.DECLARED)
        declarations[1], declarations[2] = declarations[2], declarations[1]
        with self.assertRaisesRegex(ValueError, "fixed alignment"):
            M.align(sp, wlc, declarations)
        declarations = list(M.DECLARED)
        declarations[1] = (47, 68, "SP", "Exod.20.22", (0, 21))
        with self.assertRaisesRegex(ValueError, "fixed alignment"):
            M.align(sp, wlc, declarations)

    def test_missing_source_and_no_silent_orthographic_harmonization(self):
        sp, wlc = controls()
        missing = dict(sp)
        del missing["Deut.5.31"]
        with self.assertRaisesRegex(ValueError, "missing declared source"):
            M.align(missing, wlc)
        for suffix in ("ו", "כ", "ך"):
            altered = dict(sp)
            altered["Deut.5.30"] = suffix + altered["Deut.5.30"][1:]
            with self.assertRaisesRegex(ValueError, "SP raw block equality failed"):
                M.align(altered, wlc)

    def test_metadata_only_no_source_strings(self):
        data = M.align(*controls())
        self.assertFalse(any("א" <= char <= "ת" for char in json.dumps(data, ensure_ascii=False)))

    def test_frozen_receipt_pin_and_reproduction_fail_before_alignment(self):
        original = M.FROZEN.read_bytes()
        self.assertEqual(M.BASE.sha(original), M.FROZEN_SHA)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / M.FROZEN.relative_to(ROOT)
            receipt.parent.mkdir(parents=True)
            receipt.write_bytes(original)
            with patch.object(M.BASE, "build", return_value={}):
                with self.assertRaisesRegex(ValueError, "pinned recomputation"):
                    M.build(root, root)
            receipt.write_text("{}")
            with self.assertRaisesRegex(ValueError, "receipt hash mismatch"):
                M.build(root, root)
        self.assertEqual(M.FROZEN.read_bytes(), original)

    def test_output_guard_rejects_source_other_receipt_and_symlinks(self):
        directory = Path("/private/tmp/synthetic-private-sp/tf/7.1.3")
        for output in (M.FROZEN, M.BASE.INCENSE_OUT,
                       ROOT / "sources/ot/wlc/Exod.xml",
                       directory.parent.parent / "replacement.json"):
            with self.subTest(output=str(output)):
                with self.assertRaises(ValueError):
                    M.validate_output(output, directory)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            unrelated = root / "other.json"
            unrelated.write_text("{}")
            with self.assertRaisesRegex(ValueError, "unrelated receipt"):
                M.validate_output(unrelated, directory)
            link = root / "link.json"
            link.symlink_to(unrelated)
            with self.assertRaisesRegex(ValueError, "symlink"):
                M.validate_output(link, directory)
            linked_directory = root / "link-dir"
            linked_directory.symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                M.validate_output(linked_directory / "new.json", directory)
            with self.assertRaisesRegex(ValueError, "verify-only never writes"):
                M.validate_output(root / "absent.json", directory, True)
            self.assertEqual(M.validate_output(root / "new.json", directory), root / "new.json")

    def test_saved_receipt_metadata_integrity_and_actual_block_accounting(self):
        data = json.loads(M.OUT.read_text())
        self.assertEqual(data["target_reference"], M.TARGET)
        self.assertEqual(data["summary"], {
            "declared_blocks": 11, "partition_parts": 22, "raw_characters": 720,
            "consonants": 567, "retained_core_consonants": 37,
            "added_block_consonants": 530, "accounted_spaces_outside_blocks": 11,
            "unaccounted_raw_characters": 0})
        self.assertIn("Fixed human-declared", data["scope"])
        self.assertIn("not exhaustive discovery", data["scope"])
        self.assertEqual(data["generator"]["repo_path"], M.SCRIPT)
        self.assertEqual(data["generator"]["sha256"], M.BASE.sha(Path(M.__file__).read_bytes()))
        self.assertEqual(data["generator"]["pinned_reader_sha256"],
                         M.BASE.sha(Path(M.BASE.__file__).read_bytes()))
        self.assertEqual(data["target"]["raw_sha256"],
                         "3a96dd77625539fa3dc840ccb64d3c820942e4cd2e55995693f618649a5b603a")
        self.assertEqual(data["target"]["consonants_sha256"],
                         "273c6b0d850c92a1dd7fc61b38ac8ab73d16c0a70a3e6059c7f3d2c7288b780d")
        source = data["source"]
        self.assertEqual(source["frozen_screen_sha256"], M.FROZEN_SHA)
        self.assertEqual(M.BASE.sha((ROOT / source["frozen_screen_repo_path"]).read_bytes()), M.FROZEN_SHA)
        self.assertTrue(source["frozen_screen_reproduced"])
        self.assertEqual(source["sp_inputs"], [{"path": "README.md", "sha256": M.BASE.README_SHA}] +
                         [{"path": f"tf/{M.BASE.VERSION}/{name}", "sha256": digest}
                          for name, digest in M.BASE.PINNED.items()])
        for item in source["wlc_inputs"]:
            self.assertEqual(item["sha256"], M.BASE.sha((ROOT / item["path"]).read_bytes()))
        frozen = json.loads(M.FROZEN.read_text())
        self.assertEqual(source["sp_inputs"], frozen["source"]["sp_inputs"])
        self.assertEqual(source["wlc_inputs"], frozen["source"]["wlc_inputs"])
        self.assertEqual([b["target"]["character_span"] for b in data["blocks"]],
                         [[d[0], d[1]] for d in M.DECLARED])
        self.assertEqual([b["target"]["consonant_count"] for b in data["blocks"]],
                         [37, 18, 45, 68, 58, 47, 75, 38, 80, 22, 79])
        for block, declaration in zip(data["blocks"], M.DECLARED):
            self.assertEqual(block["source"]["control"], declaration[2])
            self.assertEqual(block["source"]["reference_label"], declaration[3])
            if declaration[4]:
                self.assertEqual(block["source"]["character_span"], list(declaration[4]))
            self.assertEqual(block["target"]["consonants_sha256"], block["source"]["consonants_sha256"])
            if block["source"]["control"] == "SP":
                self.assertEqual(block["target"]["raw_sha256"], block["source"]["raw_sha256"])
        parts = data["partition"]
        self.assertEqual(parts[0]["character_span"][0], 0)
        self.assertEqual(parts[-1]["character_span"][1], 720)
        for left, right in zip(parts, parts[1:]):
            self.assertEqual(left["character_span"][1], right["character_span"][0])
        self.assertEqual(sum(p["raw_character_count"] for p in parts), 720)
        self.assertEqual(sum(p["consonant_count"] for p in parts), 567)
        for number, (block_part, space_part) in enumerate(zip(parts[::2], parts[1::2])):
            self.assertEqual(block_part["kind"], "declared-block")
            self.assertEqual(block_part["block_id"], data["blocks"][number]["block_id"])
            for key, value in data["blocks"][number]["target"].items():
                self.assertEqual(block_part[key], value)
            self.assertEqual(space_part["kind"], "inter-block-or-terminal-space")
            self.assertEqual(space_part["raw_character_count"], 1)
            self.assertEqual(space_part["consonant_count"], 0)
            self.assertEqual(space_part["raw_sha256"], M.BASE.sha(b" "))
            self.assertEqual(space_part["consonants_sha256"], M.BASE.sha(b""))
        self.assertTrue(all(value is False for value in data["policy"].values()))
        self.assertFalse(any("א" <= char <= "ת" for char in json.dumps(data, ensure_ascii=False)))


if __name__ == "__main__":
    unittest.main()
