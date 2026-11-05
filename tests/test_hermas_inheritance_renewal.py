"""Guard interpreter attribution, full posture chain and conditional disclosure."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/shepherd_of_hermas/repair'
PATHS=[ROOT/r/'extra_canonical/shepherd_of_hermas/020.yaml' for r in ['translation','translation_simplified']]

class InheritanceRenewalTests(unittest.TestCase):
    def test_interpreter_chain_and_full_condition(self):
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            ps=doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ',1)[0] for p in ps],[f'XII.{i}' for i in range(1,4)])
            for phrase in ['second vision','her standing','younger and more cheerful than before','flesh','hair were older','he says[g]']:self.assertIn(phrase,ps[0])
            self.assertNotIn('she says',doc['translation']['text'])
            for phrase in ['given up hope for himself','weakness','poverty[h]','nothing','last day of his life','inheritance is left to him','he rises up[i]','puts on strength','no longer lies down, but stands','already corrupted by his former deeds','is renewed[j]','no longer sits, but takes courage[b]','the Lord revealed to you[k]']:self.assertIn(phrase,ps[1])
            for phrase in ['had compassion on you[n]','renewed your spirits[l]','put away your softness[c]','were strengthened in faith[d]','Lord saw your strengthening[m]','he rejoiced','building of the tower[f]','will make other things known','if, with a whole heart, you are at peace among yourselves[e]']:self.assertIn(phrase,ps[2])
            for p in ps:self.assertEqual(p.count('“'),p.count('”'))
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(len(notes),14)
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]',doc['translation']['text'])),set(notes))
            for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1)
            self.assertIn('male interpreter',notes['g'])
            self.assertTrue(notes['a'].startswith('Countenance renders' if doc is docs[0] else 'Face renders'))
            self.assertIn('S1 marginal addition over an empty first-hand reading',notes['k'])
            self.assertIn('editorial supply from Greek',notes['j'])
            self.assertIn('their strengthening',notes['m'])
            self.assertIn('whole-heart mutual love',notes['e'])
            self.assertIn('commands to renew the soul',notes['c'])
            self.assertIn('P.Amh.II190 b–c recto',notes['d'])
            self.assertIn('outside this fragment',notes['f'])
            self.assertIn('not fresh recto photograph collation',notes['m'])

    def test_full_prior_posture_decision_and_source_unchanged(self):
        a=json.loads((P/'inheritance-renewal-alignment-20261105.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text())
        self.assertFalse(a['normalized_source_body_changed']);self.assertFalse(a['english_extent_changed'])
        self.assertEqual(hermas.load_normalized_unit('V.3.xii').text,arc['normalized_before'])
        self.assertEqual(a['speaker_correction']['before'],'she says')
        for row in arc['raw_unchanged'].values():
            path=Path(row['path']);self.assertFalse(path.is_absolute());self.assertNotIn('..',path.parts)
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),row['file_sha256'])
        self.assertEqual(len(arc['nested_unchanged']),6)
        for p,row in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),row['file_sha256'])
        revs=arc['standard_flat']['record']['revisions']
        self.assertTrue(any(r['category']=='doctrine_realignment' and 'kinetic chain' in r['rationale'] for r in revs))
        for row in json.loads((P/'model_reviews/legacy019-20261105-r1/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])

if __name__=='__main__':unittest.main()
