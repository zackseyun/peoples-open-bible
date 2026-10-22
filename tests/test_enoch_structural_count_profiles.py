"""Raw counter serializers remain exact and never promote wording or release."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from tools.enoch import bounded_application as t
from tools.enoch import audit_pob_source_coverage as coverage
try:
    from tools.enoch import structural_count_profiles as profiles
    STAGE=t.ROOT
except ImportError:
    STAGE=Path(__file__).resolve().parent
    spec=importlib.util.spec_from_file_location('profiles',STAGE/'structural_count_profiles.py')
    profiles=importlib.util.module_from_spec(spec);spec.loader.exec_module(profiles)

class CountProfilesTest(unittest.TestCase):
    def fixture(self,root,scope):
        index=next((STAGE/'sources/enoch/coverage'/scope).glob('paired-count-index-v2.json'))
        data=json.loads(index.read_text())
        for name in data['files']:
            out=root/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((STAGE/name).read_bytes())
        return data

    def write(self,root,data):
        # Rebind derivative receipts, allowing tests to reach semantics rather than
        # stopping solely at outer artifact hashes. No real source receipt changes.
        def read(key):return json.loads((root/data[key]).read_text())
        def put(key,value):(root/data[key]).write_text(json.dumps(value))
        def sha(key):return t.sha((root/data[key]).read_bytes())
        author,review,pv=read('author_provenance'),read('review'),read('provenance')
        author['inventory_sha256']=sha('input');put('author_provenance',author)
        review['input_sha256']=sha('input');put('review',review)
        pv['input_sha256']=sha('input');pv['review_sha256']=sha('review')
        if 'author_provenance_sha256' in pv:pv['author_provenance_sha256']=sha('author_provenance')
        if 'observed_units' in data:pv['observed_unit_spans_sha256']=sha('observed_units')
        if 'photo_hashes' in data:pv['photo_hashes_sha256']=sha('photo_hashes')
        put('provenance',pv)
        data['files']={n:t.sha((root/n).read_bytes()) for n in data['files']}
        index=root/'index.json';index.write_text(json.dumps(data));return index

    def reject(self,scope,key,change,message):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);data=self.fixture(root,scope)
            path=root/data[key];value=json.loads(path.read_text());change(value);path.write_text(json.dumps(value))
            index=self.write(root,data)
            with self.assertRaisesRegex(ValueError,message):profiles.load(index,root)

    def test_both_exact_raw_profiles_derive323_units_without_release_mutation(self):
        before=copy.deepcopy(coverage.EXPECTED_VERSES)
        counts={}
        for scope in ('count52-69-20261022','count91-103-20261022'):
            index=STAGE/'sources/enoch/coverage'/scope/'paired-count-index-v2.json'
            counts.update(profiles.load(index,STAGE))
        self.assertEqual(len(counts),30)
        self.assertEqual(sum(len(x['units']) for x in counts.values()),323)
        self.assertEqual(len(counts[60]['units']),25)
        self.assertEqual(len(counts[69]['units']),29)
        self.assertEqual(len(counts[91]['units']),19)
        self.assertNotIn(97,counts)
        self.assertEqual(coverage.EXPECTED_VERSES,before)
        self.assertTrue(all(x['kind']=='paired_structural_only_not_wording_or_reader_release_approval' for x in counts.values()))

    def test_count_only_inventory_needs_no_canonical_translation_files(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);data=self.fixture(root,'count52-69-20261022')
            self.assertEqual(len(profiles.load(self.write(root,data),root)),18)
            self.assertFalse((root/'translation').exists())

    def test_original_total_drift_rejected(self):
        self.reject('count52-69-20261022','input',lambda x:x.update(total_units=181),'original total')

    def test_original_sequence_drift_rejected(self):
        self.reject('count52-69-20261022','input',lambda x:x['chapters'][0]['numbered_units'].pop(),'numbered-unit')

    def test_boolean_count_rejected(self):
        self.reject('count52-69-20261022','input',lambda x:x['chapters'][0].update(actual_unit_count=True),'positive integers')

    def test_duplicate_chapter_rejected(self):
        self.reject('count52-69-20261022','input',lambda x:x['chapters'].append(x['chapters'][0]),'duplicated')

    def test_explicit_unit_id_drift_rejected(self):
        self.reject('count52-69-20261022','input',lambda x:x['units'][0].update(verse=2),'explicit unit identity')

    def test_rebound_disagreeing_independent_span_rejected(self):
        self.reject('count52-69-20261022','observed_units',lambda x:x[0].update(pdf_pages=[132]),'spans|page span')

    def test_rerender_disagreement_rejected(self):
        self.reject('count52-69-20261022','photo_hashes',lambda x:x[0].update(independent_rerender_sha256='0'*64),'rerender')

    def test_same_counter_rejected(self):
        self.reject('count52-69-20261022','author_provenance',lambda x:x.update(counter_id='/root/enoch52_69_count_review'),'roles|identity')

    def test_raw_wording_promotion_rejected(self):
        self.reject('count52-69-20261022','review',lambda x:x.update(wording_approval=True),'original total')

    def test_context_digest_not_ignored(self):
        self.reject('count91-103-20261022','author_provenance',lambda x:x['scan_image_sha256'].update({'pdf226.png':'bad'}),'photo name/digest')

    def test_malformed_photo_name_fails_closed(self):
        self.reject('count91-103-20261022','author_provenance',lambda x:x['scan_image_sha256'].update({'garbage':'0'*64}),'photo name/digest')

    def test_excluded97_scope_cannot_be_promoted(self):
        self.reject('count91-103-20261022','input',lambda x:x['scope']['chapters'].append(97),'exclusion scope')

    def test_raw_91total_drift_rejected(self):
        self.reject('count91-103-20261022','input',lambda x:x['summary'].update(printed_units=144),'original total')

    def test_52chapter_boundary_drift_rejected(self):
        self.reject('count52-69-20261022','input',lambda x:x['chapters'][0].update(pdf_start=133),'chapter boundary')

    def test_91chapter_boundary_drift_rejected(self):
        self.reject('count91-103-20261022','input',lambda x:x['chapters'][0]['chapter_pdf_pages'].pop(),'chapter boundary')

    def test_raw_91wording_promotion_rejected(self):
        self.reject('count91-103-20261022','review',lambda x:x.update(wording_approval=True),'count-only')

if __name__=='__main__':unittest.main()
