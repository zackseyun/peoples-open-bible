"""Current partial32 repairs and counterproof to two historical-only gates."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t, legacy32_evidence as legacy
from tools.enoch.current_evidence import verify_current
from tools.enoch.full_repair_progress import build
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader

P = t.APPLICATIONS/'enoch_full_repair_batch12_20261022'


def record(v):
    return yaml.load((t.TRANSLATION/f'032/{v:03d}.yaml').read_bytes(), Loader=t.LOADER)


class FullRepairBatch12Test(unittest.TestCase):
    def test_exact_four_existing_units_and_two_distinct_deferred_reasons(self):
        result = verify_current(P)
        m = t.load_manifest(P)
        receipt = json.loads((P/'application.json').read_text())
        self.assertEqual(result['references'], [f'1 Enoch 32:{v}' for v in (1, 2, 4, 5)])
        self.assertEqual(result['candidate_files'], 4)
        self.assertEqual(receipt['snapshot_file_count'], 962)
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        self.assertEqual(m['chapter_inventories'], [])
        self.assertEqual(m['source_only_count_inventories'][0]['units'], list(range(1, 7)))
        not_applied = {r['reference']: r for r in m['not_applied']}
        self.assertEqual(not_applied['1 Enoch 32:3']['verdicts'], ['hold', 'hold'])
        self.assertEqual(not_applied['1 Enoch 32:6']['verdicts'], ['accept', 'accept'])
        self.assertIn('release deferred', not_applied['1 Enoch 32:6']['reason'])
        self.assertEqual(t.sha((t.TRANSLATION/'032/003.yaml').read_bytes()),
                         m['canonical_baseline_sha256']['032/003.yaml'])
        self.assertFalse((t.TRANSLATION/'032/006.yaml').exists())
        for v in (1, 2, 4, 5):
            self.assertFalse(record(v)['source_correction']['selected_edition_chapter_reviewed'])

    def test_32_1_old_bounded_north_hold_is_not_relabelled_as_full_approval(self):
        result = verify_current(t.APPLICATIONS/legacy.NAMES[0])
        self.assertEqual(result['historical_accepted_individual_review_passes'], 0)
        self.assertEqual(result['historical_scope'], 'bounded_north_and_aromatics_only')
        self.assertEqual(len(result['reviewed_supersessions']), 1)
        self.assertNotEqual(result['historical_canonical_sha256'], result['current_canonical_sha256'])
        d = record(1)
        self.assertIn('these aromatics, toward the north', d['translation']['text'])
        self.assertNotIn('south', d['translation']['text'].lower())
        self.assertTrue(d['source_correction']['individual_unit_application_approved'])
        m = t.load_manifest(P)
        self.assertTrue(all('ch32-original' in b['input'] for b in m['review_bindings'][d['reference']]))

    def test_32_2_editor_repair_does_not_normalize_selected_daggers(self):
        d = record(2)
        self.assertIn('†ኅንኩ፡†', d['source']['text'])
        self.assertEqual(d['source']['confidence'], 'low')
        extra = d['source']['additional_translation_input']
        self.assertEqual(len(extra), 1)
        self.assertEqual(extra[0]['reading'], 'ሖርኩ')
        self.assertEqual(extra[0]['required_internal_explanation_marker'], 'b')
        self.assertIn('editorially assisted', d['translation']['footnotes'][1]['text'])
        self.assertIn('angel Zutel', d['translation']['text'])

    def test_32_4_does_not_guess_botanical_species_or_hide_intrinsic_uncertainty(self):
        d = record(4)
        self.assertIn('ḥamara ṣərāʾ', d['translation']['text'])
        self.assertIn('ሐመረ፡ ጽራእ', d['source']['text'])
        self.assertIn('a cluster of grapes', d['translation']['text'])
        self.assertNotIn('carob tree', d['translation']['text'])
        self.assertEqual(d['source']['confidence'], 'low')
        self.assertEqual(d['source']['transcription_uncertainties'][0]['type'], 'unresolved_lexical_comparison')
        self.assertIn('provisional critical treatment', d['translation']['footnotes'][0]['text'])
        self.assertIn('column752 to378', d['translation']['footnotes'][1]['text'])
        parent = json.loads((P/'history/ch32-critical-followup-parent-independent/provenance.json').read_text())
        self.assertIn('673–674', parent['auxiliary_locator_controls'])
        self.assertIn('Rejected', parent['auxiliary_locator_controls']['273'])

    def test_32_5_keeps_actual_joining_brackets_and_low_confidence(self):
        d = record(5)
        old = legacy.historical_record('1 Enoch 32:5')
        self.assertEqual(d['source']['text'], old['source']['text'])
        self.assertIn('ሠናይዝ', d['source']['text'])
        self.assertNotIn('ሠናይ፡ ዝ', d['source']['text'])
        self.assertIn('[beautiful and]', d['translation']['text'])
        self.assertEqual(d['translation']['text'], old['translation']['text'])
        self.assertEqual(d['source']['confidence'], 'low')
        self.assertEqual(d['source']['transcription_uncertainties'][0]['type'], 'printed_editorial_bracket_status')
        self.assertEqual(d['translation']['footnotes'][0]['reason'], 'textual_variant')
        original = json.loads((P/'history/ch32-critical-followup-parent-independent/independent-review.json').read_text())
        adverse = json.loads((P/'history/ch32-critical-followup-parent-independent/adverse-separator-addendum.json').read_text())
        self.assertEqual(original['reviews'][2]['verdict'], 'accept')
        self.assertEqual(adverse['verdict'], 'revise')
        self.assertEqual(adverse['affected_reference'], '1 Enoch 32:5')
        result = verify_current(t.APPLICATIONS/legacy.NAMES[1])
        self.assertEqual(result['historical_accepted_individual_review_passes'], 2)
        self.assertEqual(len(result['reviewed_supersessions']), 1)

    def test_no_new_reader_chapter_or_unrelated_export_change(self):
        m = t.load_manifest(P)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(t.TRANSLATION, root/'1_enoch')
            for ref in m['references']:
                c, v = t.parse_ref(ref)
                blob = m['baseline_git_blobs'][f'{c:03d}/{v:03d}.yaml']['blob']
                (root/f'1_enoch/{c:03d}/{v:03d}.yaml').write_bytes(
                    subprocess.check_output(['git', 'cat-file', 'blob', blob], cwd=t.ROOT))
            with patch.object(reader, 'EXTRA_CANONICAL_ROOT', root):
                before = reader.export_extra_canonical_book('ENO')
            after = reader.export_extra_canonical_book('ENO')
        self.assertEqual(before, after)
        self.assertNotIn(32, [c['chapter'] for c in after['chapters']])

    def test_exact_explanations_and_structured_controls_survive_individual_export_and_prompt(self):
        for v in (1, 2, 4, 5):
            d = record(v)
            out = reader._export_record_verse(v, d)
            self.assertEqual(out['footnotes'], d['translation']['footnotes'])
            self.assertEqual(out['footnote_review'], reader.PROTOCOL)
            bundle = build_enoch_prompt(32, v)
            for k in ('text', 'confidence', 'transcription_uncertainties', 'additional_translation_input'):
                if k in d['source']:
                    self.assertEqual(out['source_critical'][k], d['source'][k])
                    self.assertEqual(bundle.source_payload[k], d['source'][k])

    def test_legacy32_manifest_cannot_upgrade_old_scope_or_change_receipt(self):
        for key, value in [('historical_scope', 'entire_chapter_accepted'), ('receipt_sha256', '0'*64)]:
            with tempfile.TemporaryDirectory() as directory:
                target = Path(directory)/'package'
                shutil.copytree(P, target)
                m = json.loads((target/'manifest.json').read_text())
                m['supersedes_legacy32']['1 Enoch 32:1'][key] = value
                (target/'manifest.json').write_text(json.dumps(m))
                with self.assertRaisesRegex(ValueError, 'Legacy32 successor scope'):
                    t.verify(target, evidence_only=True)

    def test_raw_legacy_artifact_drift_fails_closed(self):
        index = legacy.read_index()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in [legacy.INDEX, *index['files']]:
                target = root/name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(t.ROOT/name, target)
            name = next(n for n in index['files'] if n.endswith('bounded-followup/review.json'))
            (root/name).write_text('{}')
            with patch.object(t, 'ROOT', root), self.assertRaisesRegex(ValueError, 'original artifact differs'):
                legacy.read_index()

    def test_current_progress_is_not_whole_book_or_chapter32_completion(self):
        r = build()
        self.assertGreaterEqual(r['current_units_with_imported_review_evidence'], 370)
        self.assertNotIn(32, r['chapters_with_complete_imported_selected_edition_review'])
        self.assertFalse(r['completion_proven'])
        self.assertFalse(r['artwork_publication_approval'])


if __name__ == '__main__':
    unittest.main()
