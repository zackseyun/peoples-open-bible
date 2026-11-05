"""Guard opposite repentance directions, this/other place, and transfer conditions."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/shepherd_of_hermas/repair'
PATHS=[ROOT/r/'extra_canonical/shepherd_of_hermas/015.yaml' for r in ['translation','translation_simplified']]


class RepentanceTransferTests(unittest.TestCase):
    def test_opposite_directions_and_full_conditions_remain(self):
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            ps=doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ',1)[0] for p in ps],[f'VII.{i}' for i in range(1,7)])
            for phrase in ['pathless places[h]','double-mindedness[l]','true road','better road','suffer misery']:
                self.assertIn(phrase,ps[0])
            for phrase in ['fire','burned','living God[m]','no longer came up into their heart to repent[a]','cravings','lewdness[b]','evils they have done']:
                self.assertIn(phrase,ps[1])
            self.assertNotIn('change their mind',ps[1])
            for phrase in ['the water','want to be baptized into the name of the Lord[j]','purity of the truth[c]','change their mind[d]','evil desires']:
                self.assertIn(phrase,ps[2])
            self.assertNotIn('repent',ps[2])
            self.assertIn('finished',ps[3])
            self.assertNotIn('question',ps[3])
            for phrase in ['plucking up my courage[n]' if doc is docs[0] else 'Plucking up my courage[n]','all these stones','repentance[k]','They have repentance','cannot fit into this tower[o]']:
                self.assertIn(phrase,ps[4])
            for phrase in ['another place, much smaller[e]','have been tormented[p]','completed the days of their sins[i]','shared in the righteous word[f]','transferred from their torments[r]','if the evil deeds they have done come up into their heart[g]','if they do not come up into their heart','not saved because of their hardness of heart[s]']:
                self.assertIn(phrase,ps[5])
            self.assertNotIn('may be transferred',ps[5])
            for p in ps:self.assertEqual(p.count('“'),p.count('”'))
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(len(notes),19)
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]',doc['translation']['text'])),set(notes))
            for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1)
            self.assertIn('because of the evil works',notes['r'])
            self.assertIn('not counted as preserved',notes['s'])
            self.assertIn('ca adds',notes['s'])
            self.assertIn('a uniquely named referent',notes['f'])

    def test_only_two_print_corrections_and_complete_history(self):
        a=json.loads((P/'repentance-transfer-alignment-20261105.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertTrue(a['broader_source_collation_flag_retained'])
        self.assertEqual(arc['raw325_before'].count('οὐτοί εἰσιν'),2)
        self.assertEqual(hermas.raw_page_path(325).read_text(),arc['raw325_before'].replace('οὐτοί εἰσιν','οὗτοί εἰσιν'))
        self.assertEqual(hermas.load_normalized_unit('V.3.vii').text,arc['normalized_before'].replace('οὐτοί εἰσιν','οὗτοί εἰσιν'))
        self.assertEqual(len(arc['nested_unchanged']),10)
        for p,row in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),row['file_sha256'])
        self.assertIn('doctrine_realignment',[r['category'] for r in arc['standard_flat']['record']['revisions']])
        for row in json.loads((P/'model_reviews/legacy014-20261105-r2/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])


if __name__=='__main__':unittest.main()
