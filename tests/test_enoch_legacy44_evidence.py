"""Original44 editorial history is a preimage proof, never a paired vote."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from tools.enoch import bounded_application as t, legacy44_evidence as legacy


class Legacy44EvidenceTest(unittest.TestCase):
    def manifest(self):
        blob = subprocess.check_output(['git', 'rev-parse', legacy.APPLIED+':'+legacy.PATH],
                                       cwd=t.ROOT).decode().strip()
        return {'references': [legacy.REF], 'supersedes_legacy44': legacy.declaration(),
                'canonical_baseline_sha256': {legacy.RELATIVE: legacy.AFTER_SHA},
                'baseline_git_blobs': {legacy.RELATIVE: {'blob': blob}}}

    def test_exact_history_and_no_independent_vote_promotion(self):
        result = legacy.verify_historical()
        self.assertEqual(result['historical_canonical_sha256'], legacy.AFTER_SHA)
        self.assertEqual(result['historical_independent_review_passes_proven'], 0)
        self.assertEqual(result['new_source_or_English_reviews'], 0)
        self.assertFalse(result['graphic_publication_approved'])
        self.assertFalse(result['full_book_verified'])
        self.assertEqual(t.sha(legacy.historical_bytes(before=True)), legacy.BEFORE_SHA)
        self.assertEqual(t.sha(legacy.historical_bytes()), legacy.AFTER_SHA)

    def test_declaration_returns_fresh_exact_reference_mapping(self):
        first = legacy.declaration();first[legacy.REF]['receipt_sha256'] = '0'*64
        self.assertEqual(legacy.declaration()[legacy.REF]['receipt_sha256'], legacy.RECEIPT_SHA)
        self.assertEqual(set(legacy.declaration()), {legacy.REF})

    def test_exact_preimage_validates_without_recursive_new_pair_verification(self):
        with patch.object(t, 'verify', side_effect=AssertionError('recursive verification')):
            legacy.validate_declared_successor(self.manifest())

    def test_wrong_receipt_scope_and_extra_reference_declarations_reject(self):
        for mutate in (
            lambda m:m['supersedes_legacy44'][legacy.REF].update(receipt_sha256='0'*64),
            lambda m:m['supersedes_legacy44'][legacy.REF].update(historical_scope='paired_whole_chapter_approval'),
            lambda m:m['supersedes_legacy44'].update({'1 Enoch 44:2':legacy.declaration()[legacy.REF]}),
            lambda m:m.update(references=['1 Enoch 43:1']),
            lambda m:m.pop('supersedes_legacy44')):
            manifest=self.manifest();mutate(manifest)
            with self.subTest(manifest=manifest),self.assertRaisesRegex(ValueError,'declaration'):
                legacy.validate_declared_successor(manifest)

    def test_wrong_canonical_and_actual_git_blob_preimages_reject(self):
        manifest=self.manifest();manifest['canonical_baseline_sha256'][legacy.RELATIVE]='0'*64
        with self.assertRaisesRegex(ValueError,'canonical preimage'):
            legacy.validate_declared_successor(manifest)
        manifest=self.manifest()
        manifest['baseline_git_blobs'][legacy.RELATIVE]['blob']=subprocess.check_output(
            ['git','rev-parse',legacy.BASE+':'+legacy.PATH],cwd=t.ROOT).decode().strip()
        with self.assertRaisesRegex(ValueError,'Historical Git preimage'):
            legacy.validate_declared_successor(manifest)

    def test_modified_original_receipt_rejects_even_if_valid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);raw=(t.APPLICATIONS/legacy.RECEIPT).read_bytes()
            receipt=json.loads(raw);receipt['human_specialist_review']=True
            (root/legacy.RECEIPT).write_text(json.dumps(receipt))
            with patch.object(t,'APPLICATIONS',root),self.assertRaisesRegex(ValueError,'receipt hash'):
                legacy.verify_historical()

    def test_manifest_loader_enforces_new_key_instead_of_ignoring_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);candidate=b'not a paired approval'
            (root/'044-001.candidate.yaml').write_bytes(candidate)
            manifest=self.manifest()
            manifest.update(kind='enoch-reviewed-units-v1',primary_pdf_sha256=t.PRIMARY_SHA,
                            full_book_verified=False,graphic_publication_approved=False,
                            files={'044-001.candidate.yaml':t.sha(candidate)},
                            review_bindings={legacy.REF:[]})
            (root/'manifest.json').write_text(json.dumps(manifest))
            # Loading history does not validate or manufacture the fresh pair.
            self.assertEqual(t.load_manifest(root)['supersedes_legacy44'],legacy.declaration())
            with self.assertRaisesRegex(ValueError,'Two distinct reviewers'):
                t.reviewed_rows(root,[],legacy.REF,manifest['files'])
            manifest['supersedes_legacy44'][legacy.REF]['receipt_sha256']='0'*64
            (root/'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,'Legacy44 successor declaration'):
                t.load_manifest(root)

    def test_wrong_actual_historical_git_bytes_reject(self):
        real=subprocess.check_output
        def changed(command,**kwargs):
            raw=real(command,**kwargs)
            return raw+b'\n' if command[-1]==legacy.APPLIED+':'+legacy.PATH else raw
        with patch.object(legacy.subprocess,'check_output',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'actual historical Git'):
                legacy.verify_historical()


if __name__=='__main__':unittest.main()
