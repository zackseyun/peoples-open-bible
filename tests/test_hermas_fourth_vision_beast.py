"""Protect complete beast-vision clauses, localized notes and evidence boundaries."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools import draft_shepherd_of_hermas as draft
from tools.hermas import review_repair_draft as review
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/shepherd_of_hermas/repair'
PATHS=[ROOT/r/'extra_canonical/shepherd_of_hermas/022.yaml' for r in ['translation','translation_simplified']]

class FourthVisionBeastTests(unittest.TestCase):
    def test_reviewed_pair_obeys_structured_payload_contract(self):
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            draft.validate_tool_input(dict(english_text=doc['translation']['text'], translation_philosophy=doc['translation']['philosophy'], lexical_decisions=doc['lexical_decisions'], footnotes=doc['translation']['footnotes'], theological_decisions=doc['theological_decisions']))

    def test_complete_clauses_and_notes_at_actual_passages(self):
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            ps=doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ',1)[0] for p in ps],[f'I.{i}' for i in range(1,11)])
            expected={0:['twenty days','pattern[a]','tribulation that is coming[n]'],1:['countryside','Campanian road[b]','ten stadia[c]','public road','easy to travel[o]'],2:['alone','Lord','revelations','visions','holy Church[d]','strengthen me','give repentance[m]','servants who have stumbled','great and glorious name','counted me worthy','wonders'],3:['glorifying','thanks','something like the sound of a voice','Do not be double-minded[e], Hermas','within myself','double-minded','glorious things'],4:['sky','within myself','Perhaps cattle[f]','stadion away'],5:['greater and greater','something divine','sun shone out a little','sea monster[g]','fiery locusts[h]','mouth','hundred feet','head was like a jar[i]'],6:['weep[p]','deliver me[j]','remembered the word','Do not be double-minded, Hermas'],7:['the faith of the Lord[k]','mighty deeds','taught me','took courage','gave myself over to the beast','such a rushing sound that it could ravage a city[l]'],8:['near it','huge sea monster','stretched itself out on the ground','did nothing except thrust out its tongue[q]','did not move at all until I had passed by it[s]'],9:['four colors','black','fiery and blood-red[r]','golden','white']}
            for i,phrases in expected.items():
                for phrase in phrases:self.assertIn(phrase.lower(),ps[i].lower())
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(notes),set('abcdefghijklmnopqrst'))
            self.assertEqual(set(re.findall(r'\[([a-z])\]',doc['translation']['text'])),set(notes))
            for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1)
            self.assertIn('editorial completion',notes['t']);self.assertIn('kneeling',notes['p']);self.assertIn('ca replaces',notes['p'])
            self.assertIn('first hand has ton lithon, the stone',notes['q']);self.assertIn('S1',notes['q'])
            self.assertIn('conjectural',notes['l']);self.assertIn('not complete surviving ink',notes['l'])
            self.assertIn('rare travel',notes['o']);self.assertIn('fire or blood',notes['r'])
            self.assertIn('genitive ambiguity',notes['k']);self.assertIn('not treated as verified topography',notes['b'])
            self.assertFalse(doc['ai_draft']['independent_review']);self.assertEqual(doc['status'],'draft')

    def test_source_history_and_preceding_accepted_inputs_unchanged(self):
        a=json.loads((P/'fourth-vision-beast-alignment-20261105.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text())
        self.assertFalse(a['normalized_source_body_changed']);self.assertFalse(a['english_extent_changed'])
        self.assertEqual(hermas.load_normalized_unit('V.4.i').text,arc['normalized_before'])
        for row in arc['raw_unchanged'].values():
            path=Path(row['path']);self.assertFalse(path.is_absolute());self.assertNotIn('..',path.parts)
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),row['file_sha256'])
        self.assertEqual(len(arc['nested_unchanged']),20)
        for p,row in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),row['file_sha256'])
        original=arc['standard_flat']['record']
        self.assertTrue(any(r['category']=='grammar' and 'degree and result' in r['rationale'] for r in original['revisions']))
        for row in json.loads((P/'model_reviews/legacy021-20261105-r2/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])

if __name__=='__main__':unittest.main()
