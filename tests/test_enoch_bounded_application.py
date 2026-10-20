"""Transaction safety, not a claim of translation accuracy from fixtures."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml
from tools.enoch import bounded_application as transaction


@contextmanager
def fixture():
    actual_schema = (transaction.ROOT / 'schema/verse.schema.json').read_bytes()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        translation = root / 'translation/extra_canonical/1_enoch'
        (translation / '001').mkdir(parents=True)
        (root / 'schema').mkdir()
        (root / 'schema/verse.schema.json').write_bytes(actual_schema)
        pdf = root / 'sources/enoch/scans/charles_1906_ethiopic.pdf'
        pdf.parent.mkdir(parents=True)
        pdf.write_bytes(b'test-only primary fixture, not a source edition')
        digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
        package = root / 'package'
        package.mkdir()
        with patch.object(transaction, 'ROOT', root), \
                patch.object(transaction, 'TRANSLATION', translation), \
                patch.object(transaction, 'PRIMARY_SHA', digest):
            row = {'reference': '1 Enoch 1:1',
                   'source': {'edition': 'charles-1906-enoch', 'language': 'Geez',
                              'text': 'ሀ።', 'pages': [1], 'confidence': 'medium'},
                   'translation': {'text': 'A fixture line.', 'philosophy': 'optimal-equivalence',
                                   'footnotes': []}}
            candidate = {'id': '1EN.1.1', 'reference': row['reference'], 'book': '1 Enoch',
                         'source': row['source'], 'translation': row['translation'], 'status': 'draft',
                         'ai_draft': {'model_id': 'fixture', 'model_version': 'fixture',
                                      'prompt_id': 'fixture', 'prompt_sha256': '0'*64,
                                      'timestamp': '2026-10-20T00:00:00Z', 'output_hash': '0'*64},
                         'source_correction': {'baseline_sha256': None,
                                              'individual_unit_application_approved': True,
                                              'full_book_verified': False,
                                              'human_specialist_certification': False,
                                              'manuscript_witness_certification': False,
                                              'graphic_publication_approved': False},
                         'enoch_witnesses': {'available_witnesses': [
                             {'witness': 'charles_1906', 'text': row['source']['text']}]}}
            (package / '001-001.candidate.yaml').write_text(yaml.safe_dump(candidate, allow_unicode=True))
            bindings = []
            for role in ('author', 'independent_reviewer'):
                input_name, review_name, provenance_name = (f'{role}-{kind}.json' for kind in ('input', 'review', 'provenance'))
                (package / input_name).write_text(json.dumps([row]))
                (package / review_name).write_text(json.dumps({'chapter_complete': False,
                    'reviews': [{'reference': row['reference'], 'verdict': 'accept'}]}))
                (package / provenance_name).write_text(json.dumps({
                    'reviewer_id': role, 'role': role, 'source_pdf_sha256': digest,
                    'scan_image_sha256': {'test-only-fixture': digest},
                    'input_sha256': transaction.sha((package/input_name).read_bytes()),
                    'review_sha256': transaction.sha((package/review_name).read_bytes())}))
                bindings.append({'input': input_name, 'review': review_name,
                                 'provenance': provenance_name, 'reviewer_id': role})
            manifest = {'kind': 'enoch-reviewed-units-v1', 'references': [row['reference']],
                        'primary_pdf_sha256': digest, 'full_book_verified': False,
                        'graphic_publication_approved': False,
                        'canonical_baseline_sha256': {}, 'baseline_git_blobs': {},
                        'review_bindings': {row['reference']: bindings}}
            def repin():
                manifest['files'] = {str(f.relative_to(package)): transaction.sha(f.read_bytes())
                    for f in package.iterdir() if f.is_file() and f.name not in ('manifest.json', 'application.json')}
                (package/'manifest.json').write_text(json.dumps(manifest))
            repin()
            yield package, translation, manifest, repin


class BoundedApplicationTest(unittest.TestCase):
    def test_apply_is_bounded_and_receipt_is_historical(self):
        with fixture() as (package, translation, manifest, repin):
            self.assertEqual(transaction.verify(package)['candidate_files'], 1)
            receipt = transaction.apply(package)
            self.assertEqual(receipt['status'], 'applied_verified')
            self.assertFalse(receipt['full_book_verified'])
            self.assertTrue((translation/'001/001.yaml').exists())
            # Later independent work elsewhere must not invalidate an old unit.
            (translation/'001/002.yaml').write_text('later: independently repaired\n')
            self.assertEqual(transaction.verify(package, applied=True)['candidate_files'], 1)

    def test_held_review_is_not_an_application_approval(self):
        with fixture() as (package, _, manifest, repin):
            p=package/'independent_reviewer-review.json';d=json.loads(p.read_text())
            d['reviews'][0]['verdict']='hold';p.write_text(json.dumps(d));repin()
            with self.assertRaisesRegex(ValueError, 'not accepted'):
                transaction.verify(package)

    def test_changed_input_or_candidate_is_rejected(self):
        with fixture() as (package, _, manifest, repin):
            p=package/'author-input.json';p.write_text(p.read_text()+' ')
            with self.assertRaisesRegex(ValueError, 'artifact changed'):
                transaction.verify(package)

    def test_two_author_reviews_do_not_count_as_independent(self):
        with fixture() as (package, _, manifest, repin):
            p=package/'independent_reviewer-provenance.json';d=json.loads(p.read_text())
            d['role']='author';p.write_text(json.dumps(d));repin()
            with self.assertRaisesRegex(ValueError, 'Independent source assessment'):
                transaction.verify(package)

    def test_scope_escape_and_invalid_reference_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'escapes'):
                transaction.artifact(Path(directory), '../outside.json')
        for ref in ('1 Enoch 0:1', '1 Enoch 109:1', '1 Enoch 1:0', '2 Enoch 1:1'):
            with self.assertRaises(ValueError): transaction.parse_ref(ref)

    def test_failure_after_writes_rolls_back_and_does_not_leave_receipt(self):
        with fixture() as (package, translation, manifest, repin):
            original = transaction.verify
            def fail_after(*args, **kwargs):
                if kwargs.get('applied'): raise RuntimeError('injected post-write failure')
                return original(*args, **kwargs)
            with patch.object(transaction, 'verify', side_effect=fail_after):
                with self.assertRaisesRegex(RuntimeError, 'post-write'):
                    transaction.apply(package)
            self.assertFalse((translation/'001/001.yaml').exists())
            self.assertFalse((package/'application.json').exists())
            self.assertFalse(list(translation.rglob('*.enoch-pending')))

    def test_unrelated_preimage_change_prevents_writes(self):
        with fixture() as (package, translation, manifest, repin):
            (translation/'001/002.yaml').write_text('unrelated: preserve\n')
            with self.assertRaisesRegex(ValueError, 'exceed'):
                transaction.apply(package)
            self.assertFalse((translation/'001/001.yaml').exists())


if __name__ == '__main__':
    unittest.main()
