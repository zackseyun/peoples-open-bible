"""Guard the Mandate/Similitude boundary and S1 printed-source correction."""
import hashlib,json,unittest
from pathlib import Path
import yaml
from tools import shepherd_of_hermas as h,draft_shepherd_of_hermas as d
ROOT=Path(__file__).resolve().parents[1];REPAIR=ROOT/'sources/shepherd_of_hermas/repair'
class OneCityTests(unittest.TestCase):
    def test_printed_correction_and_complete_distinct_scope(self):
        arc=json.loads((REPAIR/'legacy47-48-before-city-restoration-20261104.v1.json').read_text());audit=json.loads((REPAIR/'one-city-restoration-20261104.v1.json').read_text());row=audit['english_drafts'][0]
        self.assertEqual(h.load_normalized_unit('S.1').text,arc['normalized_s01_before'].replace('οὐ δύναται ἐπανακάμψαι','οὐ διανοεῖται ἐπανακάμψαι'))
        raw=(ROOT/'sources/shepherd_of_hermas/transcribed/raw/hermas_lightfoot1891_g31_p0357.txt').read_text();self.assertIn('2 διανοεῖται] conj. Hollenberg',raw)
        # Neighboring Mandate text and accepted review inputs must stay intact.
        for n in range(41,47):
            receipt=json.loads((REPAIR/f'model_reviews/legacy{n:03}-20261104-r{3 if n==45 else 2}/receipt.json').read_text())
            for item in receipt['input_manifest']:self.assertEqual(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest(),item['file_sha256'])
        for kind in ['standard','simplified']:
            doc=yaml.safe_load((ROOT/row[kind+'_path']).read_text());ps=doc['translation']['text'].split('\n\n')
            self.assertEqual(doc['source']['text'],h.load_normalized_unit('S.1').text);self.assertEqual(len(ps),11)
            self.assertIn('foreign land',ps[0]);self.assertIn('does not intend',ps[1]);self.assertIn('certainly not',ps[4]);self.assertIn('if his commandments are kept',ps[6]);self.assertIn('buy afflicted souls',ps[7]);self.assertIn('widows and orphans',ps[7]);self.assertIn('you will be saved',ps[10]);self.assertNotIn('devil',doc['translation']['text']);self.assertNotIn('if the turning',doc['translation']['text'])
            for note in doc['translation']['footnotes']:self.assertEqual(doc['translation']['text'].count('['+note['marker']+']'),1)
            self.assertEqual(d.sha256_hex(doc['translation']['text']),row[kind+'_text_sha256']);self.assertEqual(doc['status'],'draft');self.assertFalse(doc['ai_draft']['independent_review'])
    def test_preserved_donor_and_nested_history_and_hashes(self):
        arc=json.loads((REPAIR/'legacy47-48-before-city-restoration-20261104.v1.json').read_text());self.assertEqual(len(arc['nested_unchanged']),16)
        for path,item in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),item['file_sha256'])
        donor='translation/extra_canonical/shepherd_of_hermas/048.yaml'
        later=json.loads((REPAIR/'legacy48-49-before-elm-restoration-20261104.v1.json').read_text())
        self.assertEqual(later['flats'][donor],arc['flats'][donor])
        current=yaml.safe_load((ROOT/donor).read_text())
        self.assertEqual(current['source_grounding']['evidence_record'],'sources/shepherd_of_hermas/repair/two-elm-vine-restoration-20261104.v1.json')
        self.assertEqual(current['source']['unit_id'],'S.2')
        self.assertEqual(len(current['translation']['text'].split('\n\n')),10)
        std=yaml.safe_load((ROOT/'translation/extra_canonical/shepherd_of_hermas/047.yaml').read_text());simple=yaml.safe_load((ROOT/'translation_simplified/extra_canonical/shepherd_of_hermas/047.yaml').read_text())
        payload=dict(english_text=std['translation']['text'],translation_philosophy=std['translation']['philosophy'],lexical_decisions=std['lexical_decisions'],footnotes=std['translation']['footnotes'],theological_decisions=std['theological_decisions'])
        self.assertEqual(std['ai_draft']['output_hash'],d.sha256_hex(d.canonical_json(payload)));self.assertEqual(simple['base_translation']['text'],std['translation']['text']);self.assertEqual(simple['base_translation']['sha256'],d.sha256_hex(std['translation']['text']));self.assertEqual(simple['ai_draft']['output_hash'],d.sha256_hex(simple['translation']['text']))
if __name__=='__main__':unittest.main()
