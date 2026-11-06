"""Guard truth/deposit conditions and limited attestation of the excerpt and gap."""
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
PATHS=[ROOT/r/'extra_canonical/shepherd_of_hermas/028.yaml' for r in ['translation','translation_simplified']]

class ThirdMandateTests(unittest.TestCase):
    def test_full_conditions_negatives_and_adjudicated_terms(self):
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            ps=doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ',1)[0] for p in ps],[f'III.{i}' for i in range(1,6)])
            for phrase in ['Love truth[p]','all truth','in this flesh[h]','before all people[g]','Lord who dwells in you','true in every word','no falsehood with him']:self.assertIn(phrase,ps[0])
            for phrase in ['reject the Lord','defrauders of the Lord[a]','deposit','received from him a spirit without falsehood[q]','If they return it false','have become defrauders[i]']:self.assertIn(phrase,ps[1])
            for phrase in ['I do not know whether I can be saved','always lived deceitfully with everyone[j]','my lie appear true before all people','No one ever contradicted me' if doc is docs[1] else 'no one ever contradicted me']:self.assertIn(phrase,ps[2])
            for phrase in ['servant of God[k]','evil conscience','spirit of truth[l]','venerable and true spirit[c]','precisely[r]']:self.assertIn(phrase,ps[3])
            self.assertNotIn('holy and true Spirit',ps[3]);self.assertNotIn('slave of God',ps[3])
            for phrase in ['your dealings[m]','when these are found true[d]','those too can become credible','If you keep these','all truth','from now on','gain life for yourself[n]','hears this command and abstains from the most evil lie[o]','will live to God[f]']:self.assertIn(phrase,ps[4])
            self.assertEqual(ps[4].count('credible'),2)
            for added in ['perpetual','eternal','protected by truth','God’s deposit']:self.assertNotIn(added,doc['translation']['text'])
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(notes),set('abcdefghijklmnopqr'))
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]',doc['translation']['text'])),set(notes))
            for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1)
            for m,phrase in [('c','explicit reconsideration'),('d','genitive absolute'),('h','adapts the indwelling address'),('i','God’s deposit'),('j','45-line gap'),('k','current servant policy'),('n','protection by truth'),('o','Hilgenfeld’s conjecture')]:self.assertIn(phrase,notes[m])
            draft.validate_tool_input(dict(english_text=doc['translation']['text'],translation_philosophy=doc['translation']['philosophy'],lexical_decisions=doc['lexical_decisions'],footnotes=doc['translation']['footnotes'],theological_decisions=doc['theological_decisions']))
            self.assertEqual(doc['status'],'draft');self.assertFalse(doc['ai_draft']['independent_review'])

    def test_original_source_history_and_prior_accepted_inputs_preserved(self):
        a=json.loads((P/'third-mandate-alignment-20261105.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text())
        self.assertFalse(a['normalized_source_body_changed']);self.assertFalse(a['english_extent_changed']);self.assertFalse(a['contextual_397_policy_member'])
        self.assertEqual(hermas.load_normalized_unit('M.3').text,arc['normalized_before'])
        self.assertEqual(len(arc['nested_unchanged']),10)
        for p,row in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),row['file_sha256'])
        for row in arc['raw_unchanged'].values():self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])
        old=arc['standard_flat']['record']
        self.assertTrue(any('before all people' in r.get('rationale','') for r in old['revisions']))
        self.assertTrue(any('slave restored' in r.get('rationale','') for r in old['revisions']))
        r=json.loads((P/'model_reviews/legacy027-20261105-r2/receipt.json').read_text())
        for row in r['input_manifest']+[r['supplemental_evidence']]:self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])

if __name__=='__main__':unittest.main()
