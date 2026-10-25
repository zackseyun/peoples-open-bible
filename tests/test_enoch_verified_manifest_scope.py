"""Remove duplicate work without caching across reads or skipping any gates."""
import json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools.enoch import bounded_application as t
from tools.enoch.current_evidence import verify_current
P=t.APPLICATIONS/'enoch_full_repair_batch29_20261024'
class VerifiedManifestScopeTest(unittest.TestCase):
    def test_one_current_read_validates_manifest_once(self):
        with patch.object(t,'load_manifest',wraps=t.load_manifest)as load:
            r=verify_current(P)
        self.assertEqual(load.call_count,1);self.assertEqual(r['references'],['1 Enoch 53:5','1 Enoch 54:9'])
    def test_distinct_calls_are_always_fresh(self):
        with patch.object(t,'load_manifest',wraps=t.load_manifest)as load:
            verify_current(P);verify_current(P)
        self.assertEqual(load.call_count,2)
    def test_invalid_language_does_not_emit_validated_snapshot(self):
        with tempfile.TemporaryDirectory()as directory:
            q=Path(directory)/'package';shutil.copytree(P,q);m=json.loads((q/'manifest.json').read_text());m['review_bindings']['1 Enoch 53:5']=m['review_bindings']['1 Enoch 53:5'][:1];(q/'manifest.json').write_text(json.dumps(m));out={}
            with self.assertRaises(ValueError):t.verify(q,evidence_only=True,_validated_manifest=out)
            self.assertEqual(out,{})
    def test_changed_manifest_after_full_verification_cannot_be_reused(self):
        actual=t.verify
        with tempfile.TemporaryDirectory()as directory:
            q=Path(directory)/'package';shutil.copytree(P,q)
            def mutate(*args,**kwargs):
                result=actual(*args,**kwargs);p=q/'manifest.json';p.write_bytes(p.read_bytes()+b'\n');return result
            with patch.object(t,'verify',side_effect=mutate):
                with self.assertRaisesRegex(ValueError,'Manifest changed after verified snapshot'):verify_current(q)
    def test_artifact_drift_between_separate_reads_is_rejected(self):
        with tempfile.TemporaryDirectory()as directory:
            q=Path(directory)/'package';shutil.copytree(P,q);verify_current(q);p=q/'integration-instructions.txt';p.write_bytes(p.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'Pinned application artifact changed'):verify_current(q)
    def test_canonical_drift_between_separate_reads_is_rejected(self):
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory)
            for rel in('053/005.yaml','054/009.yaml'):
                p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(t.TRANSLATION/rel,p)
            with patch.object(t,'TRANSLATION',root):
                verify_current(P);p=root/'054/009.yaml';p.write_bytes(p.read_bytes()+b'\n')
                with self.assertRaises(ValueError):verify_current(P)
