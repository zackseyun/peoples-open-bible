"""Prevent recurrence of the recorded-source gap and detached footnotes."""
import copy
import json
from pathlib import Path
import re
import unittest
from unittest.mock import patch

from tools import reorientation_policy as prior
from tools import repentance_reassessment as policy

ROOT = Path(__file__).resolve().parents[1]
REPAIR = ROOT / 'sources/shepherd_of_hermas/repair'


class FourSourceAlignmentTests(unittest.TestCase):
    def test_source_extent_and_unchanged_english_words(self):
        audit = json.loads((REPAIR / 'four-source-alignment-20261104.v1.json').read_text())
        archive = json.loads((REPAIR / 'legacy29-30-before-source-alignment-20261104.v1.json').read_text())
        originals = {r['path']: r['record'] for r in archive['records']}
        for row in audit['records']:
            doc = prior.load(ROOT / row['path'])
            if (row['unit_id'] == 'M.4.i' and
                    doc.get('source_grounding', {}).get('history_archive') ==
                    'sources/shepherd_of_hermas/repair/legacy29-before-reception-alignment-20261104.v1.json'):
                later = json.loads((REPAIR / 'legacy29-before-reception-alignment-20261104.v1.json').read_text())
                self.assertEqual(later['standard_flat']['record_sha256'], row['record_sha256'])
                doc = later['standard_flat']['record']
                self.assertEqual(prior.digest(doc), row['record_sha256'])
            body = '\n'.join(l for l in (ROOT / row['normalized_path']).read_text().splitlines()
                             if not l.startswith('#')).strip()
            self.assertEqual(doc['source']['text'], body)
            self.assertEqual(policy.SHA(body), row['source_text_sha256'])
            self.assertEqual(prior.digest(doc), row['record_sha256'])
            strip = lambda s: re.sub(r'\[(?:[0-9]+|a|b)\]', '', s)
            self.assertEqual(strip(doc['translation']['text']), strip(originals[row['path']]['translation']['text']))
            mapping = row['reader_paragraph_source_paragraphs']
            self.assertEqual(len(mapping), len(doc['translation']['text'].split('\n\n')))
            expected = 11 if row['unit_id'] == 'M.4.i' else 4
            self.assertEqual([n for group in mapping for n in group], list(range(1, expected + 1)))
            self.assertFalse(doc['source_alignment']['independent_review'])
            self.assertEqual(doc['cross_check']['status'], 'needs_review')

    def test_annotations_attach_to_their_actual_lemmas(self):
        first = prior.load(ROOT / policy.HERMAS_FOUR_I)
        second = prior.load(ROOT / policy.HERMAS_FOUR_II)
        for phrase in ['another man’s wife[1]', 'rise up upon your heart[2]',
                       'brings death upon himself[3]', 'not repeatedly[5]',
                       'repentance is one[6]', 'remain by yourselves[7]',
                       'makes images as the nations do[8]', 'give healing[9]']:
            self.assertIn(phrase, first['translation']['text'])
        for phrase in ['am over repentance[a][1]', 'comes up upon his heart[2]',
                       'the man who has sinned[3]', 'lavishly[4]', 'will live to God[6]']:
            self.assertIn(phrase, second['translation']['text'])
        for doc in [first, second]:
            markers = [n['marker'] for n in doc['translation']['footnotes']]
            self.assertEqual(len(markers), len(set(markers)))
            for marker in markers:
                self.assertEqual(doc['translation']['text'].count('[' + marker + ']'), 1)
        self.assertNotIn('[a]', first['translation']['text'])
        note = next(n for n in first['translation']['footnotes'] if n['marker'] == '9')
        self.assertIn('first-hand', note['text'])
        self.assertIn('corrections ca and d', note['text'])

    def test_historical_policy_survives_without_mutation_exemptions(self):
        for name in [policy.HERMAS_FOUR_I, policy.HERMAS_FOUR_II]:
            path = ROOT / name
            doc = prior.load(path)
            self.assertEqual(policy.approved_errors(path, doc), [])
            old = policy.historical_view(path, doc)
            decisions = doc['lexical_decisions']
            if name == policy.HERMAS_FOUR_I and doc.get('source_grounding', {}).get('history_archive') == 'sources/shepherd_of_hermas/repair/legacy29-before-reception-alignment-20261104.v1.json':
                archived = json.loads((REPAIR / 'legacy29-before-reception-alignment-20261104.v1.json').read_text())
                decisions = archived['standard_flat']['record']['lexical_decisions']
                self.assertEqual(doc['lexical_decisions'][10]['chosen'], 'servant')
            self.assertEqual(old['lexical_decisions'], decisions)
            self.assertEqual(old['translation']['text'], policy.plan_by_path()[name]['after_text'])
            for field in ['source', 'translation']:
                bad = copy.deepcopy(doc)
                bad[field]['text'] += ' changed'
                self.assertTrue(policy.approved_errors(path, bad))
            bad = copy.deepcopy(doc)
            bad['translation']['footnotes'][0]['text'] = 'All witnesses agree'
            self.assertTrue(policy.approved_errors(path, bad))
            bad = copy.deepcopy(doc)
            bad['source_alignment']['independent_review'] = True
            self.assertTrue(policy.approved_errors(path, bad))
            with patch.object(Path, 'read_bytes', return_value=b'{}'):
                with self.assertRaisesRegex(ValueError, 'decision pin differs'):
                    policy.historical_view(path, doc)


if __name__ == '__main__':
    unittest.main()
