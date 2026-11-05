"""Complete tree-parable scope and explicit non-leading identity anchor."""
import copy,hashlib,json,unittest
from pathlib import Path
from unittest.mock import patch
import yaml
from tools import shepherd_of_hermas as h,draft_shepherd_of_hermas as d
from tools.hermas import review_repair_draft as review
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'sources/shepherd_of_hermas/repair'
PATHS=[ROOT/root/'extra_canonical/shepherd_of_hermas/049.yaml' for root in ['translation','translation_simplified']]
class TreesTests(unittest.TestCase):
    def test_complete_scope_selection_and_preserved_history(self):
        a=json.loads((P/'three-four-trees-restoration-20261104.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text());sel=a['bounded_manuscript_selection']
        self.assertEqual(sel['after'],sel['before'].replace(sel['removed_phrase'],''));self.assertEqual(h.load_normalized_unit('S.4').text,sel['after']);self.assertEqual(h.load_normalized_unit('S.3').text,arc['normalized_s03_before'])
        self.assertIn('[οἱ ἐλάχιστοι', (ROOT/'sources/shepherd_of_hermas/transcribed/raw/hermas_lightfoot1891_g31_p0362.txt').read_text())
        self.assertEqual(len(arc['nested_unchanged']),24)
        for path,item in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),item['file_sha256'])
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            ps=doc['translation']['text'].split('\n\n');self.assertEqual([p.split('. ',1)[0] for p in ps],[f'III.{n}' for n in range(1,4)]+[f'IV.{n}' for n in range(1,9)])
            self.assertNotIn('least',doc['translation']['text']);self.assertIn('flourishing',ps[5]);self.assertIn('did not repent',ps[6]);self.assertIn('did not know',ps[6]);self.assertIn('receive nothing',ps[8]);self.assertIn('pure',ps[9]);self.assertIn('whoever',ps[10].lower());self.assertNotIn('wealth complete',doc['translation']['text'])
            for note in doc['translation']['footnotes']:self.assertEqual(doc['translation']['text'].count('['+note['marker']+']'),1)
        std,simple=docs;payload=dict(english_text=std['translation']['text'],translation_philosophy=std['translation']['philosophy'],lexical_decisions=std['lexical_decisions'],footnotes=std['translation']['footnotes'],theological_decisions=std['theological_decisions']);self.assertEqual(std['ai_draft']['output_hash'],d.sha256_hex(d.canonical_json(payload)));self.assertEqual(simple['ai_draft']['output_hash'],d.sha256_hex(simple['translation']['text']))
        receipt=json.loads((P/'model_reviews/legacy048-20261104-r2/receipt.json').read_text())
        for item in receipt['input_manifest']:self.assertEqual(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest(),item['file_sha256'])
    def test_anchor_requires_unique_chronological_contiguous_hashed_spans(self):
        docs,_=review.load_pair(*PATHS);self.assertEqual(docs[0]['id'],'HERM.S.4');self.assertEqual(docs[0]['source']['identity_anchor_unit_id'],'S.4');self.assertEqual(docs[0]['source']['source_unit_spans'][0]['unit_id'],'S.3')
        original=Path.read_bytes
        for mode in ['missing','wrong','reverse','duplicate','bad_sequence','bad_hash']:
            def changed(path):
                raw=original(path)
                if path==PATHS[0]:
                    doc=yaml.safe_load(raw);s=doc['source']
                    if mode=='missing':s.pop('identity_anchor_unit_id')
                    if mode=='wrong':s['identity_anchor_unit_id']='S.3'
                    if mode=='reverse':s['source_unit_spans'].reverse()
                    if mode=='duplicate':s['source_unit_spans'].append(copy.deepcopy(s['source_unit_spans'][0]))
                    if mode=='bad_sequence':s['source_unit_spans'][0]['current_source_sequence']=1
                    if mode=='bad_hash':s['source_unit_spans'][0]['text_sha256']='wrong'
                    return yaml.safe_dump(doc,allow_unicode=True).encode()
                return raw
            with patch.object(Path,'read_bytes',changed):
                with self.assertRaises(ValueError,msg=mode):review.load_pair(*PATHS)
if __name__=='__main__':unittest.main()
