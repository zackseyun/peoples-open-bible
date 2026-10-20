"""Exact current repair evidence, not a whole-book completion certificate."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import yaml
from tools.enoch import bounded_application as transaction
from tools.enoch import full_repair_progress as progress
from tools import export_mobile_bible as mobile

PACKAGE = transaction.APPLICATIONS / 'enoch_full_repair_batch02_20261020'
COUNTS = {36: 4, 37: 5, 38: 6, 39: 14, 45: 6}


def record(c, v):
    return yaml.load((transaction.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_text(),
                     Loader=transaction.LOADER)


class FullRepairBatch02Test(unittest.TestCase):
    def test_exact_35_installed_units_and_unrelated_preimages(self):
        result = transaction.verify(PACKAGE, applied=True)
        self.assertEqual(result['candidate_files'], 35)
        manifest = transaction.load_manifest(PACKAGE)
        additions = [ref for ref in manifest['references']
                     if (lambda cv: f'{cv[0]:03d}/{cv[1]:03d}.yaml' not in
                         manifest['canonical_baseline_sha256'])(transaction.parse_ref(ref))]
        self.assertEqual(len(additions), 10)
        receipt = json.loads((PACKAGE/'application.json').read_text())
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        self.assertEqual(len(receipt['canonical_after_sha256']), 902)
        self.assertFalse(result['full_book_verified'])

    def test_five_complete_selected_edition_chapters_are_progress_not_completion(self):
        result = progress.build()
        self.assertGreaterEqual(result['current_units_with_imported_review_evidence'], 35)
        self.assertTrue(set(COUNTS) <= set(result['chapters_with_complete_imported_selected_edition_review']))
        self.assertEqual(len(result['chapters']), 108)
        self.assertEqual(result['evidence_inventory_warnings'], [])
        self.assertFalse(result['completion_proven'])
        for c, count in COUNTS.items():
            self.assertEqual(result['chapters'][c-1]['expected_units'], list(range(1,count+1)))

    def test_material_source_and_english_repairs(self):
        self.assertIn('ቀዳማ፲', record(38,1)['source']['text'])
        self.assertIn('anomalous', record(38,1)['translation']['footnotes'][0]['text'])
        self.assertIn('ይትለሐዩ', record(39,7)['source']['text'])
        self.assertNotIn('ይትሰሐዩ', record(39,7)['source']['text'])
        self.assertIn('ጕንዳየ', record(39,10)['source']['text'])
        self.assertIn('I blessed him and praised him', record(39,10)['translation']['text'])
        self.assertEqual(record(39,10)['translation']['footnotes'], [])
        self.assertIn('praise his work', record(36,4)['translation']['text'])
        self.assertIn('ሰከዩ', record(45,3)['source']['text'])
        self.assertNotIn('oracle', record(36,2)['source']['note'].casefold())

    def test_mobile_export_adds_only_these_five_chapters_and_retains_notes(self):
        manifest = transaction.load_manifest(PACKAGE)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root/'1_enoch'
            shutil.copytree(transaction.TRANSLATION, old)
            for ref in manifest['references']:
                c,v = transaction.parse_ref(ref)
                relative = f'{c:03d}/{v:03d}.yaml'
                target = old/relative
                if relative in manifest['baseline_git_blobs']:
                    blob = manifest['baseline_git_blobs'][relative]['blob']
                    target.write_bytes(subprocess.run(['git','cat-file','blob',blob],
                        cwd=transaction.ROOT, check=True, capture_output=True).stdout)
                else:
                    target.unlink()
            with patch.object(mobile, 'EXTRA_CANONICAL_ROOT', root):
                before = mobile.export_extra_canonical_book('ENO')
            after = mobile.export_extra_canonical_book('ENO')
        before = {c['chapter']: c for c in before['chapters']}
        after = {c['chapter']: c for c in after['chapters']}
        self.assertEqual(sorted(set(after)-set(before)), list(COUNTS))
        self.assertEqual({c:d for c,d in after.items() if c not in COUNTS}, before)
        for c,count in COUNTS.items():
            self.assertEqual([v['verse'] for v in after[c]['verses']], list(range(1,count+1)))
        self.assertTrue(after[38]['verses'][0]['footnotes'])


if __name__ == '__main__':
    unittest.main()
