"""Guard renewal, four-foot cosmology and full repentance/revelation conditions."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/shepherd_of_hermas/repair'
PATHS=[ROOT/r/'extra_canonical/shepherd_of_hermas/021.yaml' for r in ['translation','translation_simplified']]

class FourFeetRevelationTests(unittest.TestCase):
    def test_four_full_paragraphs_repentance_and_qualified_promise(self):
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            ps=doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ',1)[0] for p in ps],[f'XIII.{i}' for i in range(1,5)])
            for phrase in ['third vision','younger[g], beautiful, and cheerful','her appearance was beautiful']:self.assertIn(phrase,ps[0])
            for phrase in ['good message[a]','grieving','forgets his former sorrows','accepts[h] nothing else except','strengthened for the good','his spirit is renewed because of the joy','received a renewal of your spirits[i]','by seeing these good things']:self.assertIn(phrase.lower(),ps[1].lower())
            self.assertEqual(ps[2].count('stool'),2);self.assertNotIn('bench',ps[2])
            for phrase in ['position is firm[j]','four feet[o]','stands firmly','world','held together by four elements[c]']:self.assertIn(phrase,ps[2])
            for phrase in ['repented[f] completely','will be new[d] and firmly founded[l]','repented from their whole heart[k]','revelation complete[e]','about revelation[m]','if anything is needed[n]','it will be revealed to you']:self.assertIn(phrase,ps[3])
            self.assertEqual(ps[3].count('repented'),2)
            self.assertTrue('No longer ask anything' in ps[3] or 'Do not ask anything more' in ps[3])
            for p in ps:self.assertEqual(p.count('“'),p.count('”'))
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(len(notes),16)
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]',doc['translation']['text'])),set(notes))
            for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1)
            self.assertIn('four angles',notes['c']);self.assertIn('four walls',notes['c'])
            self.assertIn('exempli gratia',notes['o'])
            self.assertIn('based partly on reconstructed line length and spacing',notes['m'])
            self.assertIn('conjectural from spacing',notes['n'])
            self.assertIn('S1',notes['n']);self.assertIn('rogaveris',notes['n'])
            self.assertIn('two independent witnesses',notes['o'])

    def test_full_history_source_and_accepted_previous_inputs_preserved(self):
        a=json.loads((P/'four-feet-revelation-alignment-20261105.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text())
        self.assertFalse(a['normalized_source_body_changed']);self.assertFalse(a['english_extent_changed'])
        self.assertEqual(hermas.load_normalized_unit('V.3.xiii').text,arc['normalized_before'])
        for row in arc['raw_unchanged'].values():
            path=Path(row['path']);self.assertFalse(path.is_absolute());self.assertNotIn('..',path.parts)
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),row['file_sha256'])
        self.assertEqual(len(arc['nested_unchanged']),8)
        for p,row in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),row['file_sha256'])
        self.assertTrue(any(r['category']=='doctrine_realignment' and "'accepts'" in r['rationale'] for r in arc['standard_flat']['record']['revisions']))
        for row in json.loads((P/'model_reviews/legacy020-20261105-r3/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])

if __name__=='__main__':unittest.main()
