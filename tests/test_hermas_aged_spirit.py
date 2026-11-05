"""Guard complete aged-spirit comparison, negations and history portability."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/shepherd_of_hermas/repair'
PATHS=[ROOT/r/'extra_canonical/shepherd_of_hermas/019.yaml' for r in ['translation','translation_simplified']]

class AgedSpiritTests(unittest.TestCase):
    def test_four_paragraphs_negatives_causes_and_full_purpose(self):
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            ps=doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ',1)[0] for p in ps],[f'XI.{i}' for i in range(1,5)])
            self.assertIn('three forms[a]',ps[0])
            for phrase in ['first vision','old woman','chair','your spirit[b]','old and already withered','no strength','softness[c]','double-mindedness[d]']:self.assertIn(phrase,ps[1])
            for phrase in ['aged','no longer','hope of being renewed[f]','nothing','their sleep[e]','softened[g]','affairs of life','yourselves over to negligence[h]','did not cast your anxieties upon the Lord[i]','your mind has been shattered[j]','grown old in your sorrows[k]']:self.assertIn(phrase,ps[2])
            for phrase in ['I would like to know, sir[l]','every weak person' if doc is docs[0] else 'Every weak person','chair because of his weakness','the weakness of his body may be steadied[m]','pattern of the first vision[n]']:self.assertIn(phrase,ps[3])
            self.assertTrue('in order that' in ps[3] or 'so that' in ps[3])
            for p in ps:self.assertEqual(p.count('“'),p.count('”'))
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(len(notes),14)
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]',doc['translation']['text'])),set(notes))
            for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1)
            self.assertIn('singular while your addresses more than one person',notes['b'])
            self.assertIn('hamartiōn, sins',notes['c']);self.assertIn('first added by S1',notes['n'])
            self.assertIn('unreadable-character gap',notes['j']);self.assertIn('bracketed',notes['m'])
            self.assertIn('earlier I wanted to know',notes['l'])

    def test_source_and_all_prior_adjudications_archived(self):
        a=json.loads((P/'aged-spirit-alignment-20261105.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text())
        self.assertFalse(a['normalized_source_body_changed']);self.assertFalse(a['english_extent_changed'])
        self.assertEqual(hermas.load_normalized_unit('V.3.xi').text,arc['normalized_before'])
        for row in arc['raw_unchanged'].values():
            path=Path(row['path']);self.assertFalse(path.is_absolute());self.assertNotIn('..',path.parts)
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),row['file_sha256'])
        self.assertEqual(len(arc['nested_unchanged']),4)
        for p,row in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),row['file_sha256'])
        self.assertIn('doctrine_realignment',[r['category'] for r in arc['standard_flat']['record']['revisions']])
        for row in json.loads((P/'model_reviews/legacy016-20261105-r2/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])

if __name__=='__main__':unittest.main()
