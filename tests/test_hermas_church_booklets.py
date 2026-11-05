"""Protect recovered history and the vision's speakers and distinct commissions."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / r / 'extra_canonical/shepherd_of_hermas/008.yaml' for r in ['translation', 'translation_simplified']]


class ChurchBookletsTests(unittest.TestCase):
    def test_complete_vision_speakers_commissions_and_notes(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'IV.{i}' for i in range(1, 4)])
            for phrase in ['while I was asleep[k]', 'very handsome young man', 'The Sibyl[b]', 'The Church', 'created first of all[g]', 'for her sake the world was set in order[d]']:
                self.assertIn(phrase, ps[0])
            for phrase in ['in my house', 'I denied having given it', 'I complete all the words[l]', 'through you[m]', 'all the elect']:
                self.assertIn(phrase, ps[1])
            for phrase in ['two little booklets', 'one to Clement[h]', 'one to Grapte[i]', 'cities outside[e]', 'entrusted to him', 'widows and the orphans', 'read it aloud[f]', 'elders[j] who preside over the church']:
                self.assertIn(phrase, ps[2])
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]', doc['translation']['text'])), set(notes))
            for marker in notes:
                self.assertEqual(doc['translation']['text'].count('[' + marker + ']'), 1)
            self.assertIn('first hand lacks', notes['c'])
            self.assertIn('S1 adds', notes['c'])
            self.assertIn('Angero’s conjecture', notes['m'])
            self.assertIn('not counted as preserved Latin agreement', notes['m'])
            self.assertIn('do not separately name Grapte', notes['i'])
            self.assertIn('not direct Geʿez', notes['j'])

    def test_both_flat_histories_and_unchanged_source_reader_are_preserved(self):
        a = json.loads((P / 'church-booklets-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertFalse(a['normalized_source_body_changed'])
        self.assertTrue(a['broader_source_collation_flag_retained'])
        self.assertEqual(hermas.load_normalized_unit('V.2.iv').text, arc['normalized_before'])
        self.assertNotIn('footnotes', arc['standard_flat']['record']['translation'])
        history = arc['recovered_prior_record']
        self.assertEqual(history['provenance']['commit'], '286c9666699e4062546f8ce60358d0d59667aa4a')
        self.assertEqual(len(history['record']['lexical_decisions']), 23)
        self.assertEqual(len(history['record']['translation']['footnotes']), 11)
        self.assertEqual(len(arc['nested_unchanged']), 6)
        for path, row in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), row['file_sha256'])
        for row in json.loads((P / 'model_reviews/legacy007-20261104-r1/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest(), row['file_sha256'])


if __name__ == '__main__':
    unittest.main()
