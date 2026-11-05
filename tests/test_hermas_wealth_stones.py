"""Guard the complete judgments, wealth conditions and bounded papyrus evidence."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/shepherd_of_hermas/repair'
PATHS=[ROOT/r/'extra_canonical/shepherd_of_hermas/014.yaml' for r in ['translation','translation_simplified']]


class WealthStonesTests(unittest.TestCase):
    def test_all_groups_negatives_and_both_wealth_conditions_remain(self):
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            ps=doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ',1)[0] for p in ps],[f'VI.{i}' for i in range(1,8)])
            for phrase in ['sons of lawlessness[a]','no salvation[i]','not','anger','provoked him[j]']:
                self.assertIn(phrase,ps[0])
            for phrase in ['scabbed ones[h]','not going into the building','did not remain','holy ones[k]','useless']:
                self.assertIn(phrase,ps[1])
            self.assertIn('among these' if doc is docs[0] else 'Among them',ps[1])
            self.assertIn('scabbed ones[h] are',ps[1])
            for phrase in ['cracks[g]','not at peace','face of peace[l]','remain in their hearts']:
                self.assertIn(phrase,ps[2])
            self.assertIn('?” “',ps[2])
            for phrase in ['greater part in righteousness[m]','parts of lawlessness','truncated and not whole']:
                self.assertIn(phrase,ps[3])
            for phrase in ['faith','wealth of this age[n]','affliction','wealth','business dealings','deny their Lord']:
                self.assertIn(phrase,ps[4])
            for phrase in ['captivates their souls[f]','cut back[s]','useful to God[o]','round stone[p]','square[e]','unless','trimmed and sheds something','cannot','Lord']:
                self.assertIn(phrase,ps[5])
            self.assertEqual(ps[5].count('unless'),2)
            for phrase in ['[But][d]','when you were rich[r]','useless','useful','beneficial for life','God','[b]','same stones[c]']:
                self.assertIn(phrase,ps[6])
            self.assertIn('all of you',ps[6].lower())
            for p in ps:self.assertEqual(p.count('“'),p.count('”'))
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(len(notes),19)
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]',doc['translation']['text'])),set(notes))
            for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1)
            self.assertIn('active alternative',notes['c'])
            self.assertIn('not itself unambiguous proof',notes['c'])
            self.assertIn('Sinaiticus14.7 omits it',notes['c'])
            self.assertIn('not active-use corroboration',notes['c'])
            self.assertIn('supplemented from Palatina',notes['m'])
            self.assertIn('does not reach',notes['p'])
            self.assertIn('Christ',notes['o'])

    def test_footer_removal_and_exact_previous_repair_are_chained(self):
        a=json.loads((P/'wealth-stones-alignment-20261105.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertTrue(a['broader_source_collation_flag_retained'])
        self.assertEqual(arc['normalized_before'].count('20—2'),1)
        self.assertEqual(hermas.load_normalized_unit('V.3.vi').text,arc['normalized_before'].replace('20—2 ',''))
        self.assertEqual(arc['raw323_before'].count('\n20—2\n'),1)
        self.assertEqual(hermas.raw_page_path(323).read_text(),arc['raw323_before'].replace('\n20—2\n','\n'))
        self.assertEqual(len(arc['nested_unchanged']),14)
        for p,row in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),row['file_sha256'])
        for row in json.loads((P/'model_reviews/legacy013-20261105-r2/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])
        ev=json.loads((P/a['evidence_record']).read_text())
        self.assertEqual(ev['sources']['Oxford4706']['dclp_tm'],69384)
        papyrus=next(e for e in ev['excerpts'] if e['edition']=='Gonis2005')
        self.assertIn('Fragment does not reach',papyrus['finding'])
        self.assertIn('not certain surviving variants',papyrus['finding'])


if __name__=='__main__':unittest.main()
