"""Current-state checks for 1 Enoch after the meaning-first pass (2026-11).

The source layer and the English layer are checked separately:

- Ge'ez: every unit accepted by the 2026 source review must still carry exactly
  its reviewed text. Nothing may change reviewed Ge'ez silently.
- Structure: all 1,061 printed units have one record each, with matching ids.
- English: every record has English produced by the meaning pass, its footnote
  markers match its notes, and the notes are written for readers rather than
  reviewers.

The older per-batch receipt tests (tests/test_enoch_*_application.py,
test_enoch_full_repair_batch*.py, ...) check that installed files equal the
exact candidates of each review packet. They describe the corpus as of the
pre-meaning-pass commit recorded in docs/ENOCH_MEANING_FIRST_2026-11.md and are
run against that commit, not today's files.
"""
import json
import pathlib
import re
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOOK = ROOT / "translation/extra_canonical/1_enoch"
PROMPT_ID = "pob_meaning_first_enoch_v1"
MARKER = re.compile(r"\[([a-z]{1,2})\]")
# Words that belong to the editing record, not to a note a reader needs.
REVIEWER_TALK = re.compile(
    r"Dillmann|Charles|col(?:umn)?s?\s?\d|printed\s?\d|selected (?:main )?print|apparatus|\bOCR\b|"
    r"not imported|not adopted|retained|\bPDF\b|candidate|review",
    re.IGNORECASE,
)
GLUED = re.compile(r"[A-Za-z][ሀ-፿]|[ሀ-፿][A-Za-z]|[a-z]{3,}\d{2,}")


def records():
    for path in sorted(BOOK.glob("[0-9][0-9][0-9]/[0-9][0-9][0-9].yaml")):
        yield path, yaml.safe_load(path.read_text(encoding="utf-8")) or {}


class EnochStructure(unittest.TestCase):
    def test_every_printed_unit_has_one_record(self):
        counts = json.loads((ROOT / "sources/enoch/coverage/printed_unit_counts.json").read_text())
        expected = {(int(c), v) for c, n in counts["chapters"].items() for v in range(1, n + 1)}
        expected |= {tuple(x) for x in counts.get("extra_reader_addresses", [])}
        actual = {(int(p.parent.name), int(p.stem)) for p, _ in records()}
        self.assertEqual(sorted(expected - actual), [], "printed units without a record")
        self.assertEqual(sorted(actual - expected), [], "records outside the printed count")

    def test_ids_match_paths(self):
        for path, rec in records():
            ch, vs = int(path.parent.name), int(path.stem)
            self.assertEqual(rec.get("id"), f"1EN.{ch}.{vs}", path)
            self.assertEqual(rec.get("reference"), f"1 Enoch {ch}:{vs}", path)
            self.assertTrue((rec.get("source") or {}).get("text"), f"{path}: no Ge'ez")


class EnochReviewedSource(unittest.TestCase):
    def test_reviewed_geez_is_unchanged(self):
        snapshot = json.loads((ROOT / "sources/enoch/coverage/reviewed_geez_2026-11-09.json").read_text())
        units = snapshot["units"]
        self.assertGreater(len(units), 500)
        for ref, unit in units.items():
            ch, vs = (int(x) for x in ref.split(":"))
            rec = yaml.safe_load((BOOK / f"{ch:03d}" / f"{vs:03d}.yaml").read_text(encoding="utf-8"))
            self.assertEqual(rec["source"]["text"], unit["text"], f"1 Enoch {ref}: reviewed Ge'ez changed")
            self.assertEqual(rec["source"].get("validation"), unit["validation"], ref)


class EnochEnglish(unittest.TestCase):
    def test_every_record_has_meaning_pass_english(self):
        for path, rec in records():
            tr = rec.get("translation") or {}
            self.assertTrue((tr.get("text") or "").strip(), f"{path}: no English")
            self.assertEqual((rec.get("meaning_pass") or {}).get("prompt_id"), PROMPT_ID, path)
            self.assertEqual(tr.get("philosophy"), "dynamic", path)

    def test_markers_match_notes(self):
        for path, rec in records():
            tr = rec.get("translation") or {}
            markers = MARKER.findall(tr.get("text") or "")
            notes = [n.get("marker") for n in tr.get("footnotes") or []]
            self.assertEqual(markers, notes, path)
            self.assertEqual(markers, [chr(ord("a") + i) for i in range(len(markers))], path)

    def test_notes_are_written_for_readers(self):
        problems = []
        for path, rec in records():
            for note in (rec.get("translation") or {}).get("footnotes") or []:
                text = note.get("text") or ""
                if REVIEWER_TALK.search(text) or GLUED.search(text) or len(text) > 400:
                    problems.append(f"{rec['reference']} [{note.get('marker')}]: {text[:120]}")
        self.assertEqual(problems, [], "\n".join(problems[:20]))


if __name__ == "__main__":
    unittest.main()
