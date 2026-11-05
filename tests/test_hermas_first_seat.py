"""Guard the complete scene, transcription corrections, and distinct witness layers."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / r / 'extra_canonical/shepherd_of_hermas/009.yaml' for r in ['translation', 'translation_simplified']]


class FirstSeatTests(unittest.TestCase):
    def test_complete_scene_conditions_and_witness_disclosures(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'I.{i}' for i in range(1, 10)])
            self.assertIn('fifth hour[1]', ps[1])
            for phrase in ['ivory seat[3]', 'linen cushion[e]', 'fine linen[4]']:
                self.assertIn(phrase, ps[3])
            for phrase in ['six young men[g]', 'stood near me[h]', 'listened closely', 'sins[c]', 'righteousness[5]', 'household[6]']:
                self.assertIn(phrase, ps[5])
            self.assertIn('Go and build', ps[6])
            self.assertIn('elders[7] sit first', ps[7])
            for phrase in ['left side[j]', 'the Name[8]', 'lack many things[b]', 'simplicity, remain[k]', 'you will sit with them', 'do their works and bear what they also bore']:
                self.assertIn(phrase, ps[8])
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]', doc['translation']['text'])), set(notes))
            for marker in notes:
                self.assertEqual(doc['translation']['text'].count('[' + marker + ']'), 1)
            self.assertIn('sixth', notes['1'])
            self.assertIn('editorial supplement', notes['3'])
            self.assertIn('Hilgenfeld’s conjecture', notes['h'])
            self.assertIn('start with touching', notes['g'])
            self.assertIn('first hand lacks', notes['j'])
            self.assertIn('my Name', notes['8'])

    def test_exact_print_changes_and_unmodified_history_neighbors(self):
        a = json.loads((P / 'first-seat-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertTrue(a['broader_source_collation_flag_retained'])
        expected = arc['normalized_before']
        for row in a['printed_transcription_corrections']:
            expected = expected.replace(row['before'], row['after'])
        self.assertEqual(hermas.load_normalized_unit('V.3.i').text, expected)
        self.assertIn('κερβικάριον λινοῦν', expected)
        self.assertIn('μεῖνον', expected)
        for n, before in arc['raw_before'].items():
            after = before
            for row in a['printed_transcription_corrections']:
                if row['physical_page'] == int(n):
                    self.assertEqual(before.count(row['before']), row['count'])
                    after = after.replace(row['before'], row['after'])
            raw = ROOT / f'sources/shepherd_of_hermas/transcribed/raw/hermas_lightfoot1891_p{int(n):04d}.txt'
            self.assertEqual(raw.read_text(), after)
        self.assertEqual(len(arc['nested_unchanged']), 18)
        for path, row in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), row['file_sha256'])
        for row in json.loads((P / 'model_reviews/legacy008-20261104-r3/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest(), row['file_sha256'])


if __name__ == '__main__':
    unittest.main()
