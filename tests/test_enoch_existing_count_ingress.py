"""Independent full source counts bound partial words, never approve them."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools.enoch import bounded_application as t,existing_count_ingress as ingress,selected_edition_sources as sources
P=t.APPLICATIONS/'enoch_full_repair_batch29_20261024'
class ExistingCountIngressTest(unittest.TestCase):
    def manifest(self):return t.load_manifest(P)
    def test_existing_actual_profile_bounds_two_declared_chapters_only(self):
        result=ingress.validate(self.manifest());self.assertEqual({c:r['units']for c,r in result.items()},{53:list(range(1,8)),54:list(range(1,11))})
        self.assertEqual(t.sha(t.artifact(t.ROOT,ingress.INDEX).read_bytes()),ingress.INDEX_SHA)
        for row in self.manifest()['existing_paired_count_ingress']:self.assertFalse(row['wording_approval']);self.assertFalse(row['reader_release_policy_changed'])
    def test_no_implicit_undeclared_count_fallback(self):
        m=self.manifest();m.pop('existing_paired_count_ingress');self.assertEqual(ingress.validate(m),{})
        registry={'chapters':{},'units':{'53:5':P.name},'metadata_units':{}}
        with patch.object(sources,'registry_data',return_value=registry),patch.object(sources,'package_evidence',return_value=(P,m)):
            with self.assertRaisesRegex(ValueError,'declared printed count'):sources.load_unit_overrides(53)
    def test_wrong_profile_index_digest_units_and_approval_flags_rejected(self):
        for field,value in [('profile_index','unreviewed.json'),('profile_index_sha256','0'*64),('units',[1,2]),('wording_approval',True),('reader_release_policy_changed',True),('independent_count_confirmation',False)]:
            with self.subTest(field=field):
                m=self.manifest();m['existing_paired_count_ingress'][0][field]=value
                with self.assertRaisesRegex(ValueError,'scope, evidence or approval'):ingress.validate(m)
    def test_duplicate_overlap_or_absent_language_chapter_rejected(self):
        for mode in('duplicate','overlap','no_language_chapter'):
            with self.subTest(mode=mode):
                m=self.manifest()
                if mode=='duplicate':m['existing_paired_count_ingress'].append(copy.deepcopy(m['existing_paired_count_ingress'][0]))
                elif mode=='overlap':m['source_only_count_inventories']=[{'chapter':53}]
                else:m['references']=['1 Enoch 54:9']
                with self.assertRaises(ValueError):ingress.validate(m)
    def test_individual_address_still_bounded(self):
        m=self.manifest();m['references']=['1 Enoch 53:8','1 Enoch 54:9']
        with self.assertRaisesRegex(ValueError,'exceeds existing paired'):ingress.validate(m)
    def test_count_does_not_replace_two_language_reviewers(self):
        import shutil
        with tempfile.TemporaryDirectory()as directory:
            q=Path(directory)/'package';shutil.copytree(P,q);m=json.loads((q/'manifest.json').read_text());m['review_bindings']['1 Enoch 53:5']=m['review_bindings']['1 Enoch 53:5'][:1];(q/'manifest.json').write_text(json.dumps(m))
            with self.assertRaisesRegex(ValueError,'Two distinct reviewers'):t.verify(q,evidence_only=True)
    def test_original_profile_drift_rejected(self):
        actual=t.artifact
        with tempfile.TemporaryDirectory()as directory:
            q=Path(directory)/'index.json';q.write_bytes(actual(t.ROOT,ingress.INDEX).read_bytes()+b'\n')
            with patch.object(t,'artifact',side_effect=lambda root,path:q if path==ingress.INDEX else actual(root,path)):
                with self.assertRaisesRegex(ValueError,'profile index differs'):ingress.validate(self.manifest())
    def test_real_source_ingress_does_not_promote_unreviewed_neighbors(self):
        registry=sources.registry_data();self.assertEqual(registry['units']['53:5'],P.name);self.assertEqual(registry['units']['54:9'],P.name)
        for c in(53,54):self.assertNotIn(str(c),registry['chapters'])
        self.assertFalse((t.TRANSLATION/'053/006.yaml').exists());self.assertNotIn('53:6',registry['units'])
        self.assertEqual(next(r['source']['text']for r in sources.load_unit_overrides(53)if r['verse']==5),__import__('yaml').safe_load((t.TRANSLATION/'053/005.yaml').read_text())['source']['text'])
