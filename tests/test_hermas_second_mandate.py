"""Guard responsibility, giving scope and disclosed limits of manuscript support."""
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
PATHS=[ROOT/r/'extra_canonical/shepherd_of_hermas/027.yaml' for r in ['translation','translation_simplified']]

class SecondMandateTests(unittest.TestCase):
    def test_all_paragraphs_preserve_conditions_and_responsibilities(self):
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            ps=doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ',1)[0] for p in ps],[f'II.{i}' for i in range(1,8)])
            for phrase in ['if you believe the slander you hear','will have something against your brother[g]','will be guilty of the slanderer’s sin']:
                self.assertIn(phrase,ps[1])
            self.assertEqual(ps[1].count('guilty of the slanderer’s sin'),2)
            for phrase in ['restless demon[c]','never at peace','divisions','well-being with all[a]']:self.assertIn(phrase,ps[2])
            for phrase in ['all things are smooth and cheerful[r]','God gives you','give simply to all who are in need[e]','Give to all[j]','God wants all to be given from his own gifts[o]']:self.assertIn(phrase,ps[3])
            for phrase in ['will not be judged','in hypocrisy will pay the penalty[k]']:self.assertIn(phrase,ps[4])
            for phrase in ['innocent[p]','from the Lord the ministry to carry out[h]','glorious before God[i]','to God will live[n]']:self.assertIn(phrase,ps[5])
            for phrase in ['your repentance[b] and that of your household','found in simplicity[m]','[your] heart clean and unstained[l]']:self.assertIn(phrase,ps[6])
            self.assertNotIn('eternal',doc['translation']['text'])
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(notes),set('abcdefghijklmnopqr'))
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]',doc['translation']['text'])),set(notes))
            for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1)
            for m,phrase in [('j','absence as apparent'),('k','proposed negative is editorial correction'),('l','conjectural restoration'),('m','immediately before its verse element'),('n','service-to-God attachment'),('o','not surviving papyrus ink')]:self.assertIn(phrase,notes[m])
            draft.validate_tool_input(dict(english_text=doc['translation']['text'],translation_philosophy=doc['translation']['philosophy'],lexical_decisions=doc['lexical_decisions'],footnotes=doc['translation']['footnotes'],theological_decisions=doc['theological_decisions']))
            self.assertEqual(doc['status'],'draft');self.assertFalse(doc['ai_draft']['independent_review'])

    def test_source_history_policy_note_and_previous_review_inputs_preserved(self):
        a=json.loads((P/'second-mandate-alignment-20261105.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text())
        self.assertFalse(a['normalized_source_body_changed']);self.assertFalse(a['english_extent_changed'])
        self.assertTrue(a['contextual_397_policy_member'])
        self.assertEqual(hermas.load_normalized_unit('M.2').text,arc['normalized_before'])
        self.assertEqual(len(arc['nested_unchanged']),14)
        for p,row in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),row['file_sha256'])
        for row in arc['raw_unchanged'].values():self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])
        old=arc['standard_flat']['record'];docs,_=review.load_pair(*PATHS)
        for doc in docs:self.assertEqual(next(n for n in old['translation']['footnotes'] if n['marker']=='b'),next(n for n in doc['translation']['footnotes'] if n['marker']=='b'))
        self.assertTrue(any(r['category']=='consistency' for r in old['revisions']))
        for receipt in ['legacy025-20261105-r1','legacy026-20261105-r1']:
            r=json.loads((P/'model_reviews'/receipt/'receipt.json').read_text())
            for row in r['input_manifest']+[r['supplemental_evidence']]:self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])

if __name__=='__main__':unittest.main()
