"""The accepted 97:1,3,5,8 repair must not publish incomplete chapter 97."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tools.textual_restoration import enoch_97_partial_transaction as transaction


class Enoch97PartialTransactionTest(unittest.TestCase):
    def test_reviewed_scope_and_source_hold(self):
        if (transaction.PACKAGE.parent/'enoch_full_repair_batch11_20261022/application.json').is_file():
            # Original assertions below are replayed unchanged at pinned49ed;
            # current full29/97 treatments have separate batch11 counterproof.
            from tools.enoch.replay_29_97_pre_successor import replay
            result = replay('97:test_reviewed_scope_and_source_hold')
            self.assertEqual((result['tests_run'], result['skipped'], result['expected_failures']), (1, 0, 0))
            self.assertFalse(result['current_corpus_validated'])
            return
        manifest = json.loads((transaction.PACKAGE / 'manifest.json').read_text())
        review = json.loads((transaction.REVIEW / 'review/review.json').read_text())
        self.assertEqual(manifest['references'], [f'1 Enoch 97:{n}' for n in (1, 3, 5, 8)])
        self.assertEqual([row['verdict'] for row in review['reviews']], ['accept'] * 4)
        self.assertFalse(review['chapter_complete'])
        self.assertFalse(manifest['chapter_publication_approval'])
        self.assertFalse((transaction.TRANSLATION / '097/010.yaml').exists())

    def test_transaction_or_installed_bytes_and_export_hold(self):
        if (transaction.PACKAGE.parent/'enoch_full_repair_batch11_20261022/application.json').is_file():
            # Original assertions below are replayed unchanged at pinned49ed;
            # current full29/97 treatments have separate batch11 counterproof.
            from tools.enoch.replay_29_97_pre_successor import replay
            result = replay('97:test_transaction_or_installed_bytes_and_export_hold')
            self.assertEqual((result['tests_run'], result['skipped'], result['expected_failures']), (1, 0, 0))
            self.assertFalse(result['current_corpus_validated'])
            return
        receipt = transaction.PACKAGE / 'application.json'
        if receipt.exists():
            self.assertEqual(transaction.verify_applied()['status'], 'applied_verified')
        else:
            self.assertEqual(len(transaction.verify()['candidate_sha256']), 4)
        delta = transaction.verify_export_delta()
        self.assertTrue(delta['chapter97_still_excluded_from_mobile_export'])
        self.assertEqual(delta['source_missing_verses'], [10])

    def test_applied_verifier_rejects_review_and_receipt_drift(self):
        if (transaction.PACKAGE.parent/'enoch_full_repair_batch11_20261022/application.json').is_file():
            # Original assertions below are replayed unchanged at pinned49ed;
            # current full29/97 treatments have separate batch11 counterproof.
            from tools.enoch.replay_29_97_pre_successor import replay
            result = replay('97:test_applied_verifier_rejects_review_and_receipt_drift')
            self.assertEqual((result['tests_run'], result['skipped'], result['expected_failures']), (1, 0, 0))
            self.assertFalse(result['current_corpus_validated'])
            return
        for field in ('accepted_review_sha256', 'receipt_manifest_sha256'):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / 'application'
                shutil.copytree(transaction.PACKAGE, package)
                target = package / ('manifest.json' if field == 'accepted_review_sha256' else 'application.json')
                record = json.loads(target.read_text())
                record['accepted_review_sha256' if field == 'accepted_review_sha256' else 'manifest_sha256'] = '0' * 64
                target.write_text(json.dumps(record))
                with patch.object(transaction, 'PACKAGE', package):
                    with self.assertRaises(ValueError):
                        transaction.verify_applied()

    def test_clean_checkout_can_verify_installed_evidence_but_not_apply_without_pdf(self):
        if (transaction.PACKAGE.parent/'enoch_full_repair_batch11_20261022/application.json').is_file():
            # Original assertions below are replayed unchanged at pinned49ed;
            # current full29/97 treatments have separate batch11 counterproof.
            from tools.enoch.replay_29_97_pre_successor import replay
            result = replay('97:test_clean_checkout_can_verify_installed_evidence_but_not_apply_without_pdf')
            self.assertEqual((result['tests_run'], result['skipped'], result['expected_failures']), (1, 0, 0))
            self.assertFalse(result['current_corpus_validated'])
            return
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory)/'not-rehydrated.pdf'
            before = {n:transaction.verse_file(n).read_bytes() for n in transaction.VERSES}
            with patch.object(transaction,'PRIMARY_PDF',missing):
                result=transaction.verify_applied()
                self.assertFalse(result['primary_pdf_checked'])
                with self.assertRaisesRegex(ValueError,'Rehydrate the pinned primary PDF'):
                    transaction.apply()
            self.assertEqual(before,{n:transaction.verse_file(n).read_bytes() for n in transaction.VERSES})

    def test_present_bad_primary_pdf_is_not_skipped_by_installed_verification(self):
        if (transaction.PACKAGE.parent/'enoch_full_repair_batch11_20261022/application.json').is_file():
            # Original assertions below are replayed unchanged at pinned49ed;
            # current full29/97 treatments have separate batch11 counterproof.
            from tools.enoch.replay_29_97_pre_successor import replay
            result = replay('97:test_present_bad_primary_pdf_is_not_skipped_by_installed_verification')
            self.assertEqual((result['tests_run'], result['skipped'], result['expected_failures']), (1, 0, 0))
            self.assertFalse(result['current_corpus_validated'])
            return
        with tempfile.TemporaryDirectory() as directory:
            bad=Path(directory)/'bad.pdf';bad.write_bytes(b'not an actual source edition')
            with patch.object(transaction,'PRIMARY_PDF',bad):
                with self.assertRaisesRegex(ValueError,'Primary PDF changed'):
                    transaction.verify_applied()

    def test_source_identity_is_pinned_even_when_primary_binary_is_absent(self):
        if (transaction.PACKAGE.parent/'enoch_full_repair_batch11_20261022/application.json').is_file():
            # Original assertions below are replayed unchanged at pinned49ed;
            # current full29/97 treatments have separate batch11 counterproof.
            from tools.enoch.replay_29_97_pre_successor import replay
            result = replay('97:test_source_identity_is_pinned_even_when_primary_binary_is_absent')
            self.assertEqual((result['tests_run'], result['skipped'], result['expected_failures']), (1, 0, 0))
            self.assertFalse(result['current_corpus_validated'])
            return
        with tempfile.TemporaryDirectory() as directory:
            package=Path(directory)/'package';shutil.copytree(transaction.PACKAGE,package)
            manifest=package/'manifest.json';data=json.loads(manifest.read_text())
            data['source_pdf_sha256']='0'*64;manifest.write_text(json.dumps(data))
            with patch.object(transaction,'PACKAGE',package), \
                    patch.object(transaction,'PRIMARY_PDF',Path(directory)/'absent.pdf'):
                with self.assertRaisesRegex(ValueError,'Primary source identity changed'):
                    transaction.verify_applied()


if __name__ == '__main__':
    unittest.main()
