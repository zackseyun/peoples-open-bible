"""Check the research proposal's provenance/composition, not historical truth.

Read the immutable baseline so later approved translations do not falsify this
historical proposal. Private UBS input re-extraction is a separate local check.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest

import yaml

from tools.textual_restoration.verify_source_composition import compose, normalized

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / 'sources/textual_restoration/decisions/samuel1_24_research_source.2026-10-15.v1.json'


class SamuelSourceProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text())
        cls.inputs = {}
        pins = [cls.record['base'], *cls.record['context_pins'], *cls.record['evidence_pins']]
        for pin in pins:
            raw = subprocess.check_output([
                'git', '-C', str(ROOT), 'show',
                f"{cls.record['base_revision']}:{pin['path']}",
            ])
            cls.inputs[pin['path']] = raw
        cls.base = yaml.safe_load(cls.inputs[cls.record['base']['path']])

    def test_exact_historical_inputs(self):
        for pin in [self.record['base'], *self.record['context_pins'], *self.record['evidence_pins']]:
            with self.subTest(path=pin['path']):
                self.assertEqual(hashlib.sha256(self.inputs[pin['path']]).hexdigest(), pin['sha256'])

    def test_only_declared_animal_source_unit_changes(self):
        proposed = compose(normalized(self.base['source']['text']), self.record['patches'], len(self.record['evidence_pins']))
        self.assertEqual(proposed, self.record['source']['text'])
        self.assertEqual(hashlib.sha256(proposed.encode()).hexdigest(), self.record['source']['text_sha256_utf8_no_newline'])
        self.assertEqual(self.record['patches'], [{'start': 22, 'before': 'בפרים שלשה', 'after': 'בפר משלש', 'evidence': [0]}])
        self.assertNotIn('ולחם', proposed)

    def test_incorrect_offset_or_changed_letters_rejected(self):
        for field, value in [('start', 21), ('before', 'בפרים שלש')]:
            patches = copy.deepcopy(self.record['patches'])
            patches[0][field] = value
            # A valid prefix alone could be a real patch, so require the exact
            # resulting candidate as well as the general composition contract.
            try:
                result = compose(normalized(self.base['source']['text']), patches, len(self.record['evidence_pins']))
            except ValueError:
                continue
            self.assertNotEqual(result, self.record['source']['text'])

    def test_complete_english_context_changes_only_animal(self):
        records = [yaml.safe_load(self.inputs[f'translation/ot/1_samuel/001/{n:03}.yaml']) for n in (22, 23, 24, 25)]
        expected = [re.sub(r'\[[a-z]+\]', '', r['translation']['text']) for r in records]
        expected[2] = expected[2].replace('three bulls', 'a three-year-old bull')
        self.assertEqual(expected, self.record['prospective_english']['context_1_22_to_25'])
        self.assertEqual(expected[2], self.record['prospective_english']['verse24'])

    def test_committee_scope_and_reconstruction_not_erased(self):
        animal, bread = self.record['committee']['entries']
        self.assertEqual((animal['id'], animal['preferred'], animal['rating'], animal['alternative_factors']), ('00985', '[בפר משלש]', 'B', [12]))
        self.assertEqual((bread['id'], bread['preferred'], bread['rating'], bread['alternative_factors']), ('00986', 'ואיפה', 'C', [13]))
        self.assertEqual(animal['remark'], '')
        self.assertEqual(bread['remark'], '')
        self.assertEqual(self.record['committee']['verse25_xml_entries'], [])
        for key in ('ratings_are_probabilities', 'full_apparatus_consulted', 'modern_versions_are_ancient_votes'):
            self.assertFalse(self.record['committee'][key])
        self.assertFalse(self.record['source']['entire_phrase_directly_attested'])
        self.assertFalse(self.record['source']['entire_verse_attested_in_4q51'])
        self.assertIn('surviving בקר', self.record['judgments']['exact_short_phrase'])

    def test_proposal_does_not_claim_approval_or_restore_ink(self):
        for key in ('canonical_source_change_applied', 'canonical_english_change_applied',
                    'canonical_application_approved', 'whole_verse_optimality_certified',
                    'generated_images_used_as_evidence', 'canon_inference'):
            self.assertFalse(self.record[key])
        self.assertEqual(self.record['gates']['canonical_application'], 'not-approved')
        self.assertFalse(self.record['judgments']['word_division_only_sufficient'])
        self.assertFalse(self.record['judgments']['hypothetical_intermediate_attested'])
        self.assertNotEqual(self.record['source']['edition'], 'WLC')


if __name__ == '__main__':
    unittest.main()
