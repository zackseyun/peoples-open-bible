"""Immutable original25:7 evidence and narrow, explicit successor bounds."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from tools.enoch import legacy_individual_evidence as legacy
from tools.enoch.current_evidence import verify_current

class LegacyIndividualEvidenceTest(unittest.TestCase):
    def fixture(self,directory):
        root=Path(directory).resolve();index=root/legacy.INDEX_REL;index.parent.mkdir(parents=True)
        index.write_bytes((legacy.transaction.ROOT/legacy.INDEX_REL).read_bytes())
        data=json.loads(index.read_text());old=legacy.transaction.APPLICATIONS/legacy.NAME
        target=root/'sources/textual_restoration/applications'/legacy.NAME
        for name in data['files']:
            p=target/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((old/name).read_bytes())
        canonical=root/'translation/extra_canonical/1_enoch/025/007.yaml';canonical.parent.mkdir(parents=True)
        canonical.write_bytes(legacy.subprocess.check_output(['git','show',legacy.COMMIT+':translation/extra_canonical/1_enoch/025/007.yaml'],cwd=legacy.HISTORY_ROOT))
        return root,target,canonical

    def patches(self,root):
        return patch.multiple(legacy.transaction,ROOT=root,APPLICATIONS=root/'sources/textual_restoration/applications',TRANSLATION=root/'translation/extra_canonical/1_enoch')

    def test_actual_historical_artifacts_and_current_or_explicit_successor(self):
        package=legacy.transaction.APPLICATIONS/legacy.NAME
        self.assertTrue(legacy.verify_historical(package)['historical_artifacts_verified'])
        result=verify_current(package)
        self.assertEqual(result['references'],['1 Enoch 25:7'])
        self.assertTrue(result['current_targets_or_reviewed_successors_verified'])
        self.assertFalse(result['full_book_verified'])
        self.assertFalse(result['chapter_publication_approval'])

    def test_original_artifact_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root,package,target=self.fixture(directory)
            (package/'review-pass2/provenance.json').write_text('{}')
            with self.patches(root):
                with self.assertRaisesRegex(ValueError,'Legacy individual artifact hash differs'):
                    legacy.verify_historical(package)

    def test_current_drift_does_not_inherit_old_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            root,package,target=self.fixture(directory)
            with self.patches(root):
                legacy.verify_applied(package)
                target.write_bytes(target.read_bytes()+b'\n# unreviewed drift\n')
                with self.assertRaisesRegex(ValueError,'Legacy installed candidate differs'):
                    legacy.verify_applied(package)
                with self.assertRaisesRegex(ValueError,'No unique installed legacy metadata successor'):
                    legacy.verify_current(package)

    def test_only_exact_reason_enum_and_workflow_metadata_can_change(self):
        old=legacy.historical_record(legacy.transaction.APPLICATIONS/legacy.NAME)
        new=copy.deepcopy(old);new['translation']['footnotes'][0]['reason']='textual_variant'
        new['source']['note']='New accurately described source-review workflow metadata.'
        legacy.check_metadata_payload(old,new)
        for area,key in [('translation','text'),('source','text')]:
            bad=copy.deepcopy(new);bad[area][key]+=' changed'
            with self.assertRaises(ValueError):legacy.check_metadata_payload(old,bad)
        bad=copy.deepcopy(new);bad['translation']['footnotes'][0]['text']+=' changed'
        with self.assertRaises(ValueError):legacy.check_metadata_payload(old,bad)
        bad=copy.deepcopy(new);bad['source']['additional_translation_input']='unapproved new source'
        with self.assertRaises(ValueError):legacy.check_metadata_payload(old,bad)
        bad=copy.deepcopy(new);bad['translation']['footnotes'][0]['reason']='lexical_alternative'
        with self.assertRaises(ValueError):legacy.check_metadata_payload(old,bad)

    def test_pending_manifest_without_receipt_cannot_be_a_current_successor(self):
        with tempfile.TemporaryDirectory() as directory:
            root,package,target=self.fixture(directory)
            with self.patches(root):
                expected=legacy.descriptor(package);target.write_bytes(target.read_bytes()+b'\n# drift\n')
                pending=legacy.transaction.APPLICATIONS/'enoch_full_repair_batch999_pending';pending.mkdir()
                (pending/'manifest.json').write_text(json.dumps({'supersedes_legacy_individuals':{legacy.REFERENCE:expected}}))
                with self.assertRaisesRegex(ValueError,'No unique installed legacy metadata successor'):
                    legacy.verify_current(package)

if __name__=='__main__':unittest.main()
