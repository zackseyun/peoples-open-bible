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
        manifest = json.loads((transaction.PACKAGE / 'manifest.json').read_text())
        review = json.loads((transaction.REVIEW / 'review/review.json').read_text())
        self.assertEqual(manifest['references'], [f'1 Enoch 97:{n}' for n in (1, 3, 5, 8)])
        self.assertEqual([row['verdict'] for row in review['reviews']], ['accept'] * 4)
        self.assertFalse(review['chapter_complete'])
        self.assertFalse(manifest['chapter_publication_approval'])
        self.assertFalse((transaction.TRANSLATION / '097/010.yaml').exists())

    def test_transaction_or_installed_bytes_and_export_hold(self):
        receipt = transaction.PACKAGE / 'application.json'
        if receipt.exists():
            self.assertEqual(transaction.verify_applied()['status'], 'applied_verified')
        else:
            self.assertEqual(len(transaction.verify()['candidate_sha256']), 4)
        delta = transaction.verify_export_delta()
        self.assertTrue(delta['chapter97_still_excluded_from_mobile_export'])
        self.assertEqual(delta['source_missing_verses'], [10])

    def test_applied_verifier_rejects_review_and_receipt_drift(self):
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


if __name__ == '__main__':
    unittest.main()
