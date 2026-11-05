"""Guard the distinct builders, complete reply, and fragment/corrector limits."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / r / 'extra_canonical/shepherd_of_hermas/012.yaml'
         for r in ['translation', 'translation_simplified']]


class BuildersRevelationTests(unittest.TestCase):
    def test_complete_dialogue_and_local_notes(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], ['IV.1', 'IV.2', 'IV.3'])
            for phrase in ['six young men[1]', 'all his creation', 'make it grow', 'build it up[3]', 'rule over all creation', 'tower[4]']:
                self.assertIn(phrase, ps[0])
            for phrase in ['holy angels of God[a]', 'six are superior to them[6]', 'rejoice', 'glorify God', 'has been completed[7]']:
                self.assertIn(phrase, ps[1])
            for phrase in ['outcome[8]', 'power', 'not because you are more worthy', 'better than you', 'visions', 'has been revealed to you and will be revealed[b]', 'double-minded[9]', 'whether these things are so or not[c]', 'nothing is outside the truth' if doc is docs[0] else 'Nothing is outside the truth', 'well-founded[10]']:
                self.assertIn(phrase, ps[2])
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]', doc['translation']['text'])), set(notes))
            for m in notes:
                self.assertEqual(doc['translation']['text'].count('[' + m + ']'), 1)
            self.assertIn('sixty', notes['1'])
            self.assertIn('S1 removes', notes['6'])
            self.assertIn('not a supplied numeral', notes['6'])
            self.assertIn('without an explicit soi', notes['b'])
            self.assertIn('Those restored words are not counted', notes['b'])
            self.assertIn('editorial inference', notes['9'])
            self.assertIn('entire verb is not extant', notes['c'])

    def test_history_and_fragment_scope_remain_explicit(self):
        a = json.loads((P / 'builders-revelation-alignment-20261105.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['normalized_source_body_changed'])
        self.assertFalse(a['english_extent_changed'])
        self.assertTrue(a['broader_source_collation_flag_retained'])
        self.assertEqual(hermas.load_normalized_unit('V.3.iv').text, arc['normalized_before'])
        self.assertEqual(len(arc['nested_unchanged']), 12)
        self.assertEqual(len(arc['standard_flat']['record']['revisions']), 2)
        self.assertIn('doctrine_realignment', [r['category'] for r in arc['standard_flat']['record']['revisions']])
        for path, row in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), row['file_sha256'])
        ev = json.loads((P / a['evidence_record']).read_text())
        self.assertEqual(ev['sources']['Oxford4706']['dclp_tm'], 69384)
        self.assertTrue(ev['sources']['Oxford4706']['dclp_edition_empty'])
        self.assertEqual(len(ev['sources']['Oxford4706']['images']), 4)
        self.assertIn('not a complete independent', ev['sources']['Oxford4706']['method'])
        papyrus = next(e for e in ev['excerpts'] if e['edition'] == 'Gonis2005')
        self.assertIn('not a continuous copy', papyrus['finding'])
        self.assertIn('inferred from spacing', papyrus['finding'])
        self.assertEqual(a['bounded_manuscript_selections']['new_loci'], 0)


if __name__ == '__main__':
    unittest.main()
