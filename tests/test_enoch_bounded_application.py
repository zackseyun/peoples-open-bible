"""Transaction safety, not a claim of translation accuracy from fixtures."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import yaml
from tools.enoch import bounded_application as transaction
from tools.enoch.current_evidence import verify_current


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


@contextmanager
def retirement_fixture():
    with fixture() as (package, translation, manifest, repin):
        raw = b'test-only: misaddressed fixture\n'
        (translation/'001/002.yaml').write_bytes(raw)
        manifest['canonical_baseline_sha256']['001/002.yaml'] = transaction.sha(raw)
        manifest['baseline_git_blobs']['001/002.yaml'] = {'blob': 'fixture-not-a-real-git-blob'}
        row = {'reference': '1 Enoch 1:2', 'action': 'retire_misaddressed_record',
               'baseline_sha256': transaction.sha(raw), 'reason': 'fixture address error',
               'replacement_references': ['1 Enoch 1:1']}
        bindings = []
        for role in ('author', 'independent_reviewer'):
            inp, review, provenance = (f'retire-{role}-{kind}.json'
                                      for kind in ('input', 'review', 'provenance'))
            (package/inp).write_text(json.dumps([row]))
            (package/review).write_text(json.dumps({'reviews': [
                {'reference': row['reference'], 'verdict': 'accept'}]}))
            proof = json.loads((package/f'{role}-provenance.json').read_text())
            proof.update(input_sha256=transaction.sha((package/inp).read_bytes()),
                         review_sha256=transaction.sha((package/review).read_bytes()))
            (package/provenance).write_text(json.dumps(proof))
            bindings.append({'input':inp, 'review':review, 'provenance':provenance,
                             'reviewer_id':role})
        manifest['retirements'] = [{**row, 'review_bindings': bindings}]
        repin()
        def check_preimage(m, relative, digest):
            assert relative == '001/002.yaml' and digest == transaction.sha(raw)
        with patch.object(transaction, 'verify_git_preimage', side_effect=check_preimage):
            yield package, translation, manifest, repin


@contextmanager
def succession_fixture():
    with fixture() as (package, translation, manifest, repin):
        transaction.apply(package)
        old = package.parent/'enoch_full_repair_batch_fixtureA'
        new = package.parent/'enoch_full_repair_batch_fixtureB'
        shutil.copytree(package,old);shutil.copytree(package,new)
        (new/'application.json').unlink()
        old_bytes = (old/'001-001.candidate.yaml').read_bytes()
        old_hash = transaction.sha(old_bytes)
        candidate = yaml.safe_load(old_bytes)
        candidate['translation']['text']='An independently reviewed replacement.'
        candidate['source_correction']['baseline_sha256']=old_hash
        (new/'001-001.candidate.yaml').write_text(yaml.safe_dump(candidate,allow_unicode=True))
        for role in ('author','independent_reviewer'):
            inp=new/f'{role}-input.json';rows=json.loads(inp.read_text())
            rows[0]['translation']=candidate['translation'];inp.write_text(json.dumps(rows))
            p=new/f'{role}-provenance.json';proof=json.loads(p.read_text())
            proof['input_sha256']=transaction.sha(inp.read_bytes());p.write_text(json.dumps(proof))
        m=json.loads((new/'manifest.json').read_text())
        m['canonical_baseline_sha256']={'001/001.yaml':old_hash}
        m['baseline_git_blobs']={'001/001.yaml':{'blob':'fixture-only'}}
        m['supersedes']={'1 Enoch 1:1':{'package':old.name,
            'manifest_sha256':transaction.sha((old/'manifest.json').read_bytes()),
            'candidate_sha256':old_hash}}
        def repin_new():
            m['files']={str(p.relative_to(new)):transaction.sha(p.read_bytes())
                for p in new.iterdir() if p.is_file() and p.name not in ('manifest.json','application.json')}
            (new/'manifest.json').write_text(json.dumps(m))
        repin_new()
        def check_preimage(manifest,relative,digest):
            assert relative=='001/001.yaml' and digest==old_hash
        with patch.object(transaction,'APPLICATIONS',package.parent), \
                patch.object(transaction,'verify_git_preimage',side_effect=check_preimage):
            yield old,new,translation,m,repin_new


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

    def test_retirement_requires_exact_accepted_map_and_replacement(self):
        with retirement_fixture() as (package, translation, manifest, repin):
            result = transaction.apply(package)
            self.assertEqual(result['retired_references'], ['1 Enoch 1:2'])
            self.assertFalse((translation/'001/002.yaml').exists())
            self.assertTrue((translation/'001/001.yaml').exists())
            transaction.verify(package, applied=True, check_corpus=True)

    def test_unreviewed_retirement_cannot_piggyback_on_verse_acceptance(self):
        with retirement_fixture() as (package, translation, manifest, repin):
            p=package/'retire-independent_reviewer-review.json'
            review=json.loads(p.read_text());review['reviews'][0]['verdict']='hold'
            p.write_text(json.dumps(review));repin()
            with self.assertRaisesRegex(ValueError, 'not accepted'):
                transaction.apply(package)
            self.assertTrue((translation/'001/002.yaml').exists())
            self.assertFalse((translation/'001/001.yaml').exists())

    def test_retirement_map_drift_is_rejected_even_if_manifest_is_repinned(self):
        with retirement_fixture() as (package, translation, manifest, repin):
            manifest['retirements'][0]['reason'] = 'different unreviewed reason';repin()
            with self.assertRaisesRegex(ValueError, 'differs from accepted exact address map'):
                transaction.verify(package)

    def test_retirement_cannot_point_outside_candidate_scope_or_overlap_it(self):
        with retirement_fixture() as (package, translation, manifest, repin):
            manifest['retirements'][0]['replacement_references']=['1 Enoch 2:1'];repin()
            with self.assertRaisesRegex(ValueError, 'reviewed replacement'):
                transaction.verify(package)
            manifest['retirements'][0]['reference']='1 Enoch 1:1';repin()
            with self.assertRaisesRegex(ValueError, 'overlap'):
                transaction.verify(package)

    def test_failure_after_retirement_restores_retired_bytes(self):
        with retirement_fixture() as (package, translation, manifest, repin):
            before=(translation/'001/002.yaml').read_bytes()
            original=transaction.verify
            def fail_after(*args, **kwargs):
                if kwargs.get('applied'): raise RuntimeError('post-retirement fixture failure')
                return original(*args, **kwargs)
            with patch.object(transaction, 'verify', side_effect=fail_after):
                with self.assertRaisesRegex(RuntimeError, 'post-retirement'):
                    transaction.apply(package)
            self.assertEqual((translation/'001/002.yaml').read_bytes(), before)
            self.assertFalse((translation/'001/001.yaml').exists())

    def test_reintroduced_retired_record_fails_installed_verification(self):
        with retirement_fixture() as (package, translation, manifest, repin):
            transaction.apply(package)
            (translation/'001/002.yaml').write_text('reintroduced: wrong address\n')
            with self.assertRaisesRegex(ValueError, 'still exists'):
                transaction.verify(package, applied=True)

    def test_reviewed_successor_preserves_strict_old_verifier_and_history(self):
        with succession_fixture() as (old,new,translation,m,repin):
            old_before={p.name:p.read_bytes() for p in old.iterdir() if p.is_file()}
            transaction.apply(new)
            with self.assertRaisesRegex(ValueError,'Applied candidate differs'):
                transaction.verify(old,applied=True)
            result=verify_current(old)
            self.assertTrue(result['canonical_targets_checked'])
            self.assertEqual(result['reviewed_supersessions'][0]['superseded_by'],new.name)
            self.assertEqual(old_before,{p.name:p.read_bytes() for p in old.iterdir() if p.is_file()})

    def test_new_bytes_without_explicit_successor_are_not_certified(self):
        with succession_fixture() as (old,new,translation,m,repin):
            transaction.apply(new)
            m.pop('supersedes');repin()
            with self.assertRaisesRegex(ValueError,'No unique explicitly reviewed'):
                verify_current(old)

    def test_wrong_historical_manifest_pointer_is_rejected(self):
        with succession_fixture() as (old,new,translation,m,repin):
            m['supersedes']['1 Enoch 1:1']['manifest_sha256']='0'*64;repin()
            with self.assertRaisesRegex(ValueError,'historical manifest/candidate/preimage'):
                transaction.apply(new)

    def test_future_accepted_but_uninstalled_successor_does_not_authorize_drift(self):
        with succession_fixture() as (old,new,translation,m,repin):
            (translation/'001/001.yaml').write_text('arbitrary: unapproved bytes\n')
            with self.assertRaisesRegex(ValueError,'No unique explicitly reviewed'):
                verify_current(old)

    def test_held_successor_is_rejected_even_with_receipt_and_repinning(self):
        with succession_fixture() as (old,new,translation,m,repin):
            transaction.apply(new)
            p=new/'independent_reviewer-review.json';review=json.loads(p.read_text())
            review['reviews'][0]['verdict']='hold';p.write_text(json.dumps(review));repin()
            with self.assertRaisesRegex(ValueError,'not accepted'):
                verify_current(old)

    def test_historical_only_mode_never_claims_current_target_check(self):
        with succession_fixture() as (old,new,translation,m,repin):
            transaction.apply(new)
            self.assertFalse(transaction.verify(old,evidence_only=True)['canonical_targets_checked'])
            with self.assertRaisesRegex(ValueError,'cannot claim installed'):
                transaction.verify(old,evidence_only=True,applied=True)


if __name__ == '__main__':
    unittest.main()
