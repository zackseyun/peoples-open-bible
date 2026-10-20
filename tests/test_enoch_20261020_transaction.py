"""Exact reviewed units, mechanical fixes and still-held boundaries."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import jsonschema
import yaml

from tools.textual_restoration import enoch_20261020_transaction as transaction


class EnochOctober20Test(unittest.TestCase):
    def test_exact_review_scope_and_installed_or_ready_bytes(self):
        applied = (transaction.PACKAGE / 'application.json').exists()
        result = transaction.verify(applied=applied)
        self.assertEqual(len(result['references']), 15)
        self.assertFalse(result['chapter_publication_approval'])
        baseline = json.loads((transaction.PACKAGE / 'manifest.json').read_text())['canonical_baseline_sha256']
        # Scope this historical hold to this application. A later independently
        # approved restoration must not fail merely because its file now exists.
        for c, v in ((18, 12), (18, 13), (18, 16), (28, 2), (28, 3), (84, 6), (97, 10)):
            self.assertNotIn((c, v), transaction.REFS)
            self.assertNotIn(f'{c:03d}/{v:03d}.yaml', baseline)

    def test_candidates_conform_to_schema_and_preserve_medium_confidence(self):
        schema = json.loads((transaction.ROOT / 'schema/verse.schema.json').read_text())
        for c, v in transaction.REFS:
            record = yaml.safe_load((transaction.PACKAGE / f'{c:03d}-{v:03d}.candidate.yaml').read_text())
            jsonschema.validate(record, schema)
            self.assertEqual(record['source']['confidence'], 'medium')
            self.assertFalse(record['source_correction']['human_specialist_certification'])

    def test_input_artifact_tampering_is_rejected(self):
        manifest = json.loads((transaction.PACKAGE / 'manifest.json').read_text())
        changed = copy.deepcopy(manifest)
        filename = next(iter(changed['files']))
        changed['files'][filename] = '0' * 64
        with patch.object(transaction, 'load_manifest', wraps=transaction.load_manifest):
            # Exercise the real checksum check, not a mock success response.
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'manifest.json').write_text(json.dumps(changed))
                # Only the first checked artifact is needed to reach failure.
                target = root / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((transaction.PACKAGE / filename).read_bytes())
                with patch.object(transaction, 'PACKAGE', root):
                    with self.assertRaisesRegex(ValueError, 'Package artifact changed'):
                        transaction.load_manifest()

    def test_duplicate_repairs_leave_source_and_surviving_words_unchanged(self):
        for c, v in ((81, 4), (89, 26)):
            stem = f'{c:03d}-{v:03d}'
            old = yaml.safe_load((transaction.PACKAGE / f'{stem}.baseline.yaml').read_text())
            new = yaml.safe_load((transaction.PACKAGE / f'{stem}.candidate.yaml').read_text())
            self.assertEqual(old['source']['text'], new['source']['text'])
            self.assertLess(len(new['translation']['text']), len(old['translation']['text']))
        new = yaml.safe_load((transaction.PACKAGE / '089-026.candidate.yaml').read_text())
        self.assertEqual(new['translation']['text'].count('And when they saw the Lord of the sheep,'), 1)
        self.assertEqual(new['translation']['text'].count('so as to flee from before his face;'), 1)

    def test_held_chapter84_is_not_installed_by_candidate_acceptances(self):
        held = json.loads((transaction.PACKAGE / 'held_chapter84/review.json').read_text())
        self.assertTrue(any(r['verdict'] == 'hold' for r in held['reviews']))
        self.assertFalse(any(c == 84 for c, _ in transaction.REFS))

    def test_verify_applied_checks_each_current_target_even_without_full_corpus_check(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for c, v in transaction.REFS:
                path = root / f'{c:03d}/{v:03d}.yaml'
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(transaction.TRANSLATION/f'{c:03d}/{v:03d}.yaml', path)
            changed = root/'018/001.yaml'
            changed.write_bytes(changed.read_bytes()+b'\n# tampered fixture\n')
            with patch.object(transaction, 'TRANSLATION', root):
                with self.assertRaisesRegex(ValueError, 'Applied candidate differs'):
                    transaction.verify(applied=True, check_corpus=False)


if __name__ == '__main__':
    unittest.main()
