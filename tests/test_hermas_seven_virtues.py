"""Guard full virtue chain, conditions, shared cleansing and uncertain command."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/shepherd_of_hermas/repair'
PATHS=[ROOT/r/'extra_canonical/shepherd_of_hermas/016.yaml' for r in ['translation','translation_simplified']]

class SevenVirtuesTests(unittest.TestCase):
    def test_all_eleven_paragraphs_conditions_and_uncertainty(self):
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            ps=doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ',1)[0] for p in ps],[f'VIII.{i}' for i in range(1,12)])
            self.assertIn('seven women',ps[1]);self.assertIn('Lord’s command',ps[1])
            self.assertIn('clasping her hands[b]',ps[2]);self.assertIn('chosen of God are saved[d]',ps[2])
            for phrase in ['girded about and acting bravely[c]','Self-control','daughter','blessed in his life','all evil works','if he refrains from every evil desire','inherit eternal life[e]']:self.assertIn(phrase,ps[3])
            self.assertIn('Simplicity, Knowledge, Innocence, Dignity, and Love[f]',ps[4])
            self.assertIn('able to live',ps[4]);self.assertIn('all',ps[4])
            for name in ['Faith','Self-control','Simplicity','Innocence','Dignity','Knowledge','Love']:self.assertIn(name,ps[6])
            self.assertIn('pure and dignified and divine[i]',ps[6])
            for phrase in ['serves','proves able to hold fast to their works[j]','dwelling in the tower','holy ones of God[k]']:self.assertIn(phrase,ps[7])
            for phrase in ['still being built','end','built up quickly','this reminder and the renewal of your spirits' if doc is docs[0] else 'This reminder and the renewal of your spirits','are enough for you and for the holy ones[m]']:self.assertIn(phrase,ps[8])
            for phrase in ['not revealed to you alone','known to all[n]']:self.assertIn(phrase,ps[9])
            for phrase in ['After three days[r]','first','command you, Hermas','words I am about to say','speak[o] them all[p]','ears of the holy ones, so that','hearing them and doing them','cleansed from their evils[q]','you also with them']:self.assertIn(phrase,ps[10])
            for p in ps:self.assertEqual(p.count('“'),p.count('”'))
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(len(notes),18)
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]',doc['translation']['text'])),set(notes))
            for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1)
            for phrase in ['obeli','first-hand lalēse','ut loquaris','loquere']:self.assertIn(phrase,notes['o'])
            for phrase in ['bracketed panta','Hilgenfeld','editorial emendation']:self.assertIn(phrase,notes['p'])
            self.assertIn('live, as an emendation of codex videre',notes['g'])
            self.assertIn('proposed repair is not counted as preserved',notes['n'])

    def test_source_and_full_adjudication_history_preserved(self):
        a=json.loads((P/'seven-virtues-alignment-20261105.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text())
        self.assertFalse(a['normalized_source_body_changed']);self.assertFalse(a['english_extent_changed'])
        self.assertEqual(hermas.load_normalized_unit('V.3.viii').text,arc['normalized_before'])
        for row in arc['raw_unchanged'].values():self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])
        self.assertEqual(len(arc['nested_unchanged']),14)
        for p,row in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),row['file_sha256'])
        revs=arc['standard_flat']['record']['revisions']
        self.assertTrue(any(r.get('to')=='hold fast to their works' for r in revs))
        self.assertTrue(any(r.get('to','').startswith('this reminder and the renewal') for r in revs))
        for row in json.loads((P/'model_reviews/legacy015-20261105-r1/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])

if __name__=='__main__':unittest.main()
