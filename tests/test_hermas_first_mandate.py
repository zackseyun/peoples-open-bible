"""Guard complete creation quantifiers, conduct chain and conditional life refrain."""
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
PATHS=[ROOT/r/'extra_canonical/shepherd_of_hermas/026.yaml' for r in ['translation','translation_simplified']]

class FirstMandateTests(unittest.TestCase):
    def test_two_complete_paragraphs_and_bounded_notes(self):
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            ps=doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ',1)[0] for p in ps],['I.1','I.2'])
            for phrase in ['First of all','believe that God is one[f]','created and set in order all things[g]','brought all things into being from what was not[a]','encompasses all things','while he alone is uncontainable[b]']:self.assertIn(phrase,ps[0])
            self.assertEqual(ps[0].count('all things'),3)
            for phrase in ['put your trust in him[h] and fear him','practice self-control[c]','Keep these things','you will throw off every wickedness from yourself[j]','put on every virtue of righteousness[d]','you will live to God[e], if you keep this command[i]']:self.assertIn(phrase,ps[1])
            self.assertIn('having feared',ps[1].lower())
            self.assertNotIn('live for God',doc['translation']['text'])
            self.assertNotIn('through the Word',doc['translation']['text'])
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(notes),set('abcdefghij'))
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]',doc['translation']['text'])),set(notes))
            for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1)
            self.assertIn('extra clause is not in the selected Greek',notes['b'])
            self.assertIn('not two independent Hermas manuscript votes',notes['f'])
            self.assertIn('digital duplication is not promoted',notes['g'])
            self.assertIn('stopping before the final all things',notes['g'])
            self.assertIn('live to the Lord',notes['e'])
            self.assertIn('not presented as unconditional',notes['i'])
            draft.validate_tool_input(dict(english_text=doc['translation']['text'],translation_philosophy=doc['translation']['philosophy'],lexical_decisions=doc['lexical_decisions'],footnotes=doc['translation']['footnotes'],theological_decisions=doc['theological_decisions']))
            self.assertEqual(doc['status'],'draft');self.assertFalse(doc['ai_draft']['independent_review'])

    def test_prior_consistency_trust_decisions_source_and_accepted_inputs_preserved(self):
        a=json.loads((P/'first-mandate-alignment-20261105.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text())
        self.assertFalse(a['normalized_source_body_changed']);self.assertFalse(a['english_extent_changed'])
        self.assertFalse(a['contextual_397_policy_member'])
        self.assertEqual(hermas.load_normalized_unit('M.1').text,arc['normalized_before'])
        for row in arc['raw_unchanged'].values():
            path=Path(row['path']);self.assertFalse(path.is_absolute());self.assertNotIn('..',path.parts)
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),row['file_sha256'])
        self.assertEqual(len(arc['nested_unchanged']),2)
        for p,row in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),row['file_sha256'])
        revs=arc['standard_flat']['record']['revisions']
        self.assertTrue(any(r['category']=='consistency' and 'live to God' in r['rationale'] for r in revs))
        self.assertTrue(any(r['category']=='doctrine_realignment' and 'put your trust' in r['rationale'] for r in revs))
        r=json.loads((P/'model_reviews/legacy025-20261105-r1/receipt.json').read_text())
        for row in r['input_manifest']+[r['supplemental_evidence']]:self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])

if __name__=='__main__':unittest.main()
