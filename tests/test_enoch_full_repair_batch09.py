"""Exact paired52units, not a complete-book or newly reconstructed text claim."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools import export_reader_bible as reader
from tools.enoch import bounded_application as t, verse_parser, selected_edition_sources
from tools.enoch.current_evidence import verify_current
from tools.enoch.full_repair_progress import build
from tools.enoch.build_translation_prompt import build_enoch_prompt

P = t.APPLICATIONS/'enoch_full_repair_batch09_20261022'
FULL = {58: 6}
PARTIAL = {59: 3, 60: 25, 61: 13, 62: 16, 63: 12, 64: 2}


def record(c, v):
    return yaml.load((t.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(), Loader=t.LOADER)


class FullRepairBatch09Test(unittest.TestCase):
    def test_exact_application_preserves_all25_held_preimages_and_no97_release(self):
        result = verify_current(P)
        self.assertEqual(result['candidate_files'], 52)
        self.assertFalse(result['full_book_verified'])
        m = t.load_manifest(P)
        receipt = json.loads((P/'application.json').read_text())
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        self.assertEqual(m['supersedes'], {})
        self.assertEqual(len(m['references']), 52)
        self.assertEqual(len(m['not_applied']), 25)
        for row in m['not_applied']:
            c, v = t.parse_ref(row['reference']); rel = f'{c:03d}/{v:03d}.yaml'
            self.assertEqual(receipt['canonical_after_sha256'].get(rel),
                             m['canonical_baseline_sha256'].get(rel))
        self.assertFalse(any(t.parse_ref(ref)[0] == 97 for ref in m['references']))
        for rel, digest in m['canonical_baseline_sha256'].items():
            if rel.startswith('097/'):
                self.assertEqual(receipt['canonical_after_sha256'][rel], digest)
        self.assertNotIn('097/010.yaml', receipt['canonical_after_sha256'])

    def test_full18_deferred_without_guessing_its_remaining_glyph(self):
        m = t.load_manifest(P)
        receipt = json.loads((P/'application.json').read_text())
        self.assertFalse(any(t.parse_ref(ref)[0] == 18 for ref in m['references']))
        for rel, digest in m['canonical_baseline_sha256'].items():
            if rel.startswith('018/'):
                self.assertEqual(receipt['canonical_after_sha256'][rel], digest)
        self.assertNotIn('018/013.yaml', receipt['canonical_after_sha256'])
        self.assertNotIn('018/016.yaml', receipt['canonical_after_sha256'])

    def test_direct_raw_and_two_row_delta_bindings_do_not_forge_full47_v3_review(self):
        m = t.load_manifest(P)
        old_binding = m['review_bindings']['1 Enoch 58:1'][1]
        self.assertEqual(old_binding['input'], 'final/ch58-61/independent-input.json')
        raw = json.loads((P/old_binding['review']).read_text())
        self.assertEqual(next(r for r in t.review_entries(raw) if r['reference']=='1 Enoch 58:5')['verdict'], 'revise')
        for ref in ('1 Enoch 58:5', '1 Enoch 60:21'):
            binding = m['review_bindings'][ref][1]
            self.assertEqual(binding['reviewer_id'], '/root')
            delta = json.loads((P/binding['review']).read_text())
            self.assertFalse(delta['full47_review_claimed'])
            self.assertEqual({r['reference'] for r in t.review_entries(delta)},
                             {'1 Enoch 58:5', '1 Enoch 60:21'})

    def test_60_21_is_low_confidence_extant_fragment_not_invented_completion(self):
        d = record(60, 21)
        self.assertEqual(d['source']['confidence'], 'low')
        self.assertTrue(d['source']['text'].endswith('....'))
        self.assertNotIn('⟦?⟧', d['source']['text'])
        self.assertTrue(d['source']['transcription_uncertainties'])
        self.assertIn('[The conclusion is missing in the selected text.]', d['translation']['text'])
        self.assertNotIn('Not ready for publication pending', d['translation']['footnotes'][0]['text'])
        out = reader._export_record_verse(21, d)
        for key in ('text', 'note', 'confidence', 'transcription_uncertainties'):
            self.assertEqual(out['source_critical'][key], d['source'][key])
        self.assertEqual(out['footnotes'], d['translation']['footnotes'])
        bundle = build_enoch_prompt(60, 21)
        self.assertEqual(bundle.source_payload['confidence'], 'low')
        self.assertEqual(bundle.source_payload['transcription_uncertainties'],
                         d['source']['transcription_uncertainties'])

    def test_count_only_neighbors_are_not_whole_chapter_or_release_approval(self):
        m = t.load_manifest(P)
        self.assertEqual({x['chapter']: len(x['units']) for x in m['chapter_inventories']}, FULL)
        self.assertEqual({x['chapter']: len(x['units']) for x in m['source_only_count_inventories']}, PARTIAL)
        for c in PARTIAL:
            refs = sorted(t.parse_ref(ref)[1] for ref in m['references'] if t.parse_ref(ref)[0] == c)
            overrides = selected_edition_sources.load_unit_overrides(c)
            # Any older unit overrides remain older evidence, not newly
            # accepted wording in this batch.
            imported = [r['verse'] for r in overrides if '/'+P.name+'/' in r['evidence']]
            self.assertEqual(imported, refs)
            self.assertTrue(all(not record(c, v)['source_correction']['selected_edition_chapter_reviewed']
                                for v in refs))

    def test_reader_adds_only_complete58_and_retains_exact_selected_explanations(self):
        m = t.load_manifest(P)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); old = root/'1_enoch'; shutil.copytree(t.TRANSLATION, old)
            for ref in m['references']:
                c, v = t.parse_ref(ref); rel = f'{c:03d}/{v:03d}.yaml'; target = old/rel
                if rel in m['baseline_git_blobs']:
                    target.write_bytes(subprocess.check_output(['git', 'cat-file', 'blob',
                        m['baseline_git_blobs'][rel]['blob']], cwd=t.ROOT))
                else:
                    target.unlink()
            with patch.object(reader, 'EXTRA_CANONICAL_ROOT', root):
                before = reader.export_extra_canonical_book('ENO')
            after = reader.export_extra_canonical_book('ENO')
        before = {c['chapter']: c for c in before['chapters']}
        after = {c['chapter']: c for c in after['chapters']}
        self.assertEqual(sorted(set(after)-set(before)), [58])
        self.assertEqual({c: d for c, d in after.items() if c not in {*FULL, *PARTIAL}},
                         {c: d for c, d in before.items() if c not in {*FULL, *PARTIAL}})
        for c, n in FULL.items():
            self.assertEqual([r['verse'] for r in after[c]['verses']], list(range(1, n+1)))
            for row in after[c]['verses']:
                self.assertEqual(row.get('footnotes', []),
                                 record(c, row['verse'])['translation'].get('footnotes', []))

    def test_progress_is_explicitly_not_all108_or_live_new_candidate_ui_proof(self):
        report = build()
        self.assertGreaterEqual(report['current_units_with_imported_review_evidence'], 310)
        self.assertTrue(set(FULL) <= set(report['chapters_with_complete_imported_selected_edition_review']))
        self.assertEqual(report['evidence_inventory_warnings'], [])
        self.assertFalse(report['completion_proven'])
        gate = json.loads((P/'explanation-delivery-gate.json').read_text())
        self.assertFalse(gate['candidate_public_delivery_verified'])
        self.assertFalse(gate['candidate_live_browser_verified'])
        self.assertFalse(gate['physical_device_verified'])


if __name__ == '__main__':
    unittest.main()
