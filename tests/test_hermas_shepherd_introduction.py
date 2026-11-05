"""Guard complete recognition, instruction and two-conditional chains in Vision5."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import draft_shepherd_of_hermas as draft
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/shepherd_of_hermas/repair'
PATHS=[ROOT/r/'extra_canonical/shepherd_of_hermas/025.yaml' for r in ['translation','translation_simplified']]

class ShepherdIntroductionTests(unittest.TestCase):
    def test_complete_narrative_instructions_conditions_and_local_notes(self):
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            ps=doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ',1)[0] for p in ps],[f'V.{i}' for i in range(1,8)])
            expected={0:['prayed in the house','couch[i]','glorious in appearance','shepherd’s guise[a]','white skin[j]','bag on his shoulders','staff in his hand','greeted me[b]','returned his greeting'],1:['immediately','beside me','sent by the most venerable angel[k]','dwell with you','rest of the days of your life'],2:['I thought','test me[g]','Who then are you','I was handed over[l]','Do you not recognize me','No','I am the Shepherd to whom you were handed over'],3:['While he was still speaking','appearance','handed over','immediately','fear seized me','completely crushed with grief','because I had answered him so wickedly and senselessly'],4:['be strengthened in my mandates[c]','about to command you','show you again all the things you saw before','the very main points[e]','beneficial for you[f]','First of all, write my mandates and the parables[d]','other things','so you will write','For this reason','command you first to write the mandates and parables','read them readily at hand and be able to keep them[n]'],5:['I wrote the mandates and the parables, just as he commanded me'],6:['you keep them','walk in them and do them[o]','pure heart[p]','receive from the Lord all that he promised you','you do not repent[h]','still add to your sins','receive from the Lord the opposite things[q]','Shepherd, the angel of repentance[r]','commanded me to write all these things in this way']}
            for i,phrases in expected.items():
                plain=ps[i].replace('keep them, walk','keep them and walk').replace('“I,” he says, “am','“I am')
                for phrase in phrases:self.assertIn(phrase.lower(),plain.lower())
            self.assertEqual(doc['translation']['text'].count('handed over'),3)
            self.assertNotIn('especially',ps[4])
            self.assertEqual(ps[6].lower().count('if'),2)
            self.assertEqual(ps[6].count('from the Lord'),2)
            for p in ps:self.assertEqual(p.count('“'),p.count('”'))
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(notes),set('abcdefghijklmnopqr'))
            self.assertEqual(set(re.findall(r'\[([a-z])\]',doc['translation']['text'])),set(notes))
            for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1)
            self.assertIn('not the man’s bodily complexion',notes['j'])
            self.assertIn('not the entire Vision5.7 warning',notes['n'])
            self.assertIn('angel of justice',notes['k']);self.assertIn('pure mind',notes['p'])
            self.assertIn('not purifying yourselves',notes['q'])
            self.assertIn('not an assertion of the shepherd’s actual intention',notes['g'])
            draft.validate_tool_input(dict(english_text=doc['translation']['text'],translation_philosophy=doc['translation']['philosophy'],lexical_decisions=doc['lexical_decisions'],footnotes=doc['translation']['footnotes'],theological_decisions=doc['theological_decisions']))
            self.assertEqual(doc['status'],'draft');self.assertFalse(doc['ai_draft']['independent_review'])

    def test_full_history_source_and_bounded_quotation_preserved(self):
        a=json.loads((P/'shepherd-introduction-alignment-20261105.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text())
        self.assertFalse(a['normalized_source_body_changed']);self.assertFalse(a['english_extent_changed'])
        self.assertEqual(hermas.load_normalized_unit('V.5').text,arc['normalized_before'])
        for row in arc['raw_unchanged'].values():
            path=Path(row['path']);self.assertFalse(path.is_absolute());self.assertNotIn('..',path.parts)
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),row['file_sha256'])
        self.assertEqual(len(arc['nested_unchanged']),14)
        for p,row in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),row['file_sha256'])
        revs=arc['standard_flat']['record']['revisions']
        self.assertTrue(any(r['category']=='doctrine_realignment' and 'handed over' in r['rationale'] for r in revs))
        e=json.loads((P/'shepherd-introduction-witness-extracts-20261105.v1.json').read_text())
        q=next(x for x in e['excerpts'] if x['edition']=='ClementStromata')
        self.assertEqual(q['ancient_greek'],'ἵνα ὑπὸ χεῖρα ἀναγινώσκῃς αὐτὰς καὶ δυνηθῇς φυλάξαι αὐτάς.')
        self.assertIn('does not quote the completeV5.7',q['finding'])
        r=json.loads((P/'model_reviews/legacy024-20261105-r2/receipt.json').read_text())
        for row in r['input_manifest']+[r['supplemental_evidence']]:
            self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])

if __name__=='__main__':unittest.main()
