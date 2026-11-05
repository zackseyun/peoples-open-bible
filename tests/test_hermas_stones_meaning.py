"""Guard the interpretation's full service list, disputed negation and deadline."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/shepherd_of_hermas/repair'
PATHS=[ROOT/r/'extra_canonical/shepherd_of_hermas/013.yaml' for r in ['translation','translation_simplified']]


class StonesMeaningTests(unittest.TestCase):
    def test_complete_meaning_and_unharmonized_negation(self):
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            ps=doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ',1)[0] for p in ps],[f'V.{i}' for i in range(1,6)])
            for phrase in ['apostles','bishops[b]','teachers','deacons[c]','oversaw','taught','served','purity and reverence[e]','fallen asleep[f]','still alive','listened to each other[v]']:
                self.assertIn(phrase,ps[0])
            self.assertTrue(ps[0].endswith('”'))
            for phrase in ['deep[g]','name of the Lord[h]','suffered']:
                self.assertIn(phrase,ps[1])
            self.assertIn('accomplished his commandments[l]',ps[2])
            self.assertIn('new in the faith and faithful[m]',ps[3])
            self.assertIn('evil was found in them[u]',ps[3])
            self.assertNotIn('not found',ps[3])
            self.assertEqual(len(re.findall(r'\brepent\b',ps[4])),5)
            for phrase in ['have sinned','not','far away outside the tower','useful for the building[q]','strong in the faith','repent now','while the tower is being built[w]','no longer have a place','will be cast out[r]','only this: to lie beside the tower[s]']:
                self.assertIn(phrase,ps[4])
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(len(notes),23)
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]',doc['translation']['text'])),set(notes))
            for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1)
            for phrase in ['positively','not','Palatina','Athos','Vulgata']:
                self.assertIn(phrase,notes['u'])
            self.assertIn('Sinaiticus13.2 has God',notes['h'])
            self.assertIn('two unreadable-character gaps',notes['g'])
            self.assertIn('restorations are not unbroken visible Athos text',notes['w'])

    def test_print_only_change_and_complete_archival_history(self):
        a=json.loads((P/'stones-meaning-alignment-20261105.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertTrue(a['broader_source_collation_flag_retained'])
        self.assertEqual(hermas.load_normalized_unit('V.3.v').text,arc['normalized_before'].replace('ἔριττον','ἔριπτον'))
        self.assertEqual(arc['raw323_before'].count('ἔριττον'),1)
        raw=hermas.raw_page_path(323)
        self.assertEqual(raw.read_text(),arc['raw323_before'].replace('ἔριττον','ἔριπτον'))
        self.assertEqual(len(arc['nested_unchanged']),10)
        for p,row in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),row['file_sha256'])
        recovered=arc['recovered_historical_record']['record']
        self.assertEqual(len(recovered['translation']['footnotes']),20)
        self.assertEqual(len(recovered['lexical_decisions']),31)
        self.assertEqual(len(recovered['theological_decisions']),7)
        self.assertIn('doctrine_realignment',[r['category'] for r in arc['standard_flat']['record']['revisions']])
        for row in json.loads((P/'model_reviews/legacy012-20261105-r2/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])


if __name__=='__main__':unittest.main()
