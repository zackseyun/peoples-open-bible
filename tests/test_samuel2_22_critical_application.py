"""Exact 1 Samuel 2:22 application; no original-wording or deployed-reader proof."""
import copy
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import unittest
from unittest.mock import patch

import yaml

from tools import draft
from tools import export_mobile_bible as exporter
from tools.textual_restoration import critical_verse

ROOT = Path(__file__).resolve().parents[1]
BASE = '032c4620d5e8d8faa1c5bf9cb56fa16327be47d5'
SOURCE_BASE = '7fe0843f2885ea54cf780739e6768bda4fb969b2'
BOOK = 'translation/ot/1_samuel'
TARGET = BOOK + '/002/022.yaml'
SOURCE = 'sources/ot/pob_critical/1_samuel/002/022.json'
APP = 'sources/textual_restoration/applications/samuel2_22_application_20261017/'
RESEARCH = 'sources/textual_restoration/applications/samuel2_22_full_source_20261017/'
CANDIDATE_SHA = 'b4b10874ff6eb133cfce5492f6ede7e0d5c94290bc23ad851048d756fdc26727'
TRUST = {
    'trusted_source_sha256': '63b3deb97a2c4c6209a780905a12f674d33a70596ce1d88fdb92693728e0a3dc',
    'trusted_review_sha256': 'aa6192b1c366e7332d757f7fba2948eacc4226d2a579e2c12f3954cffa8408d5',
    'trusted_composition_sha256': 'a832819617ad9c08ecb58d48951598f79c5f19fc09d149d1422006fccf8f0047',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':'), allow_nan=False).encode())


def index(book):
    return {(chapter['chapter'], verse['verse']): verse
            for chapter in book['chapters'] for verse in chapter['verses']}


class Samuel222CriticalApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Read immutable Git objects in memory; never substitute the live corpus
        # wrapper for the source-stage record that existed at application base.
        raw = subprocess.check_output([
            'git', '-C', str(ROOT), 'archive', BASE, BOOK, RESEARCH, SOURCE,
            APP + 'preparation.v1.json', APP + 'candidate.v1.yaml'])
        cls.frozen = {}
        with tarfile.open(fileobj=io.BytesIO(raw), mode='r:') as archive:
            for member in archive:
                if member.isdir():
                    continue
                if not member.isfile():
                    raise AssertionError('Non-regular historical input: ' + member.name)
                cls.frozen[member.name] = archive.extractfile(member).read()
        cls.book_raw = {name: data for name, data in cls.frozen.items()
                        if name.startswith(BOOK + '/') and name.endswith('.yaml')}
        cls.baseline = yaml.safe_load(cls.book_raw[TARGET])
        cls.current_raw = (ROOT / TARGET).read_bytes()
        cls.current = yaml.safe_load(cls.current_raw)
        cls.plan = json.loads((ROOT / APP / 'application_plan.v1.json').read_bytes())

    def test_exact_candidate_and_full_record_have_separate_application_approval(self):
        self.assertEqual(sha(self.current_raw), CANDIDATE_SHA)
        self.assertEqual(self.current_raw, (ROOT / APP / 'candidate.v2.yaml').read_bytes())
        self.assertEqual(sha((ROOT / APP / 'application_plan.v1.json').read_bytes()),
                         'a101b9344f18d9760baf90226b9a196d2fee3e67e97359915199b89b02621c75')
        self.assertEqual(sha((ROOT / APP / 'source_candidate.v2.json').read_bytes()),
                         'd118bf1030a27a4ede50f9623840a840e64c876aec5ffc1891647c0d8bf7fe72')
        result = critical_verse.validate(self.current, **TRUST)
        self.assertIs(result['full_critical_verse_verified'], True)
        for field in ('canonical_application_approved', 'publication_approved'):
            self.assertIs(result[field], False)
        source = json.loads((ROOT / SOURCE).read_bytes())
        self.assertEqual(sha((ROOT / SOURCE).read_bytes()), TRUST['trusted_source_sha256'])
        self.assertEqual(source['provenance']['base_revision'], SOURCE_BASE)
        for field in ('canonical_application_approved', 'publication_approved'):
            self.assertIs(source['provenance'][field], False)
        review_raw = (ROOT / APP / 'editorial_review.v2.json').read_bytes()
        self.assertEqual(sha(review_raw), TRUST['trusted_review_sha256'])
        review = json.loads(review_raw)
        for field in ('source_selection_approved', 'full_record_editorially_approved',
                      'canonical_application_approved', 'repository_publication_ready'):
            self.assertIs(review[field], True)
        self.assertIs(review['deployed_reader_verified'], False)

    def test_frozen_research_and_preparation_keep_their_historical_false_flags(self):
        frozen_names = {name for name in self.frozen if name.startswith(RESEARCH)}
        live_names = {str(path.relative_to(ROOT)) for path in (ROOT / RESEARCH).rglob('*')
                      if path.is_file() or path.is_symlink()}
        self.assertEqual(live_names, frozen_names)
        for name in sorted(frozen_names | {APP + 'preparation.v1.json', APP + 'candidate.v1.yaml'}):
            with self.subTest(path=name):
                self.assertFalse((ROOT / name).is_symlink())
                self.assertEqual((ROOT / name).read_bytes(), self.frozen[name])
        preparation = json.loads(self.frozen[APP + 'preparation.v1.json'])
        self.assertEqual(preparation['source']['path'], SOURCE)
        self.assertEqual(preparation['source']['sha256'],
                         '7519a03697690664f6f115b03d8d7e7a5e84a47c4aa048324aadb3a70ac4f8df')
        self.assertEqual(sha(self.frozen[SOURCE]), preparation['source']['sha256'])
        self.assertNotEqual(sha((ROOT / SOURCE).read_bytes()), preparation['source']['sha256'])
        review = json.loads(self.frozen[RESEARCH + 'full_record_review.v1.json'])
        for record in (preparation, preparation['validation'], review):
            for field in ('canonical_application_approved', 'publication_approved'):
                self.assertIs(record[field], False)
        self.assertIs(self.plan['canonical_application_approved'], False)
        self.assertIs(self.plan['publication_approved'], False)

    def test_v2_only_corrects_declared_metadata_and_source_binding(self):
        first = yaml.safe_load(self.frozen[APP + 'candidate.v1.yaml'])
        second = yaml.safe_load((ROOT / APP / 'candidate.v2.yaml').read_bytes())
        delta = self.plan['metadata_only_v2_delta']
        self.assertEqual(delta['path'], 'theological_decisions[0].alternative_readings[0]')
        self.assertEqual(first['theological_decisions'][0]['alternative_readings'][0], delta['before'])
        self.assertEqual(second['theological_decisions'][0]['alternative_readings'][0], delta['after'])
        for field in ('source', 'translation'):
            self.assertEqual(first[field], second[field])
        self.assertIs(self.plan['hebrew_english_notes_changed_from_v1'], False)
        first['theological_decisions'][0]['alternative_readings'][0] = delta['after']
        first['critical_source_integration']['record']['sha256'] = TRUST['trusted_source_sha256']
        self.assertEqual(digest(first), digest(second))

    def test_old_scores_do_not_transfer_and_generation_and_revisions_are_preserved(self):
        self.assertEqual(self.current['ai_draft'], self.baseline['ai_draft'])
        self.assertEqual(self.current['revisions'], self.baseline['revisions'])
        self.assertEqual(self.current['status'], 'draft')
        self.assertEqual(self.current['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', self.current)
        historical = self.baseline.get('review_history', [])
        self.assertEqual(self.current['review_history'][:len(historical)], historical)
        added = self.current['review_history'][len(historical):]
        self.assertEqual({entry['field'] for entry in added},
                         {'cross_check', 'revision_pass', 'lexical_decisions',
                          'theological_decisions', 'translation'})
        for entry in added:
            with self.subTest(field=entry['field']):
                self.assertEqual(entry['value'], self.baseline[entry['field']])
                self.assertEqual(entry['archived_from_baseline_sha256'], sha(self.book_raw[TARGET]))
                self.assertEqual(entry['historical_review_input_binding'], 'not-verified')
                self.assertIs(entry['certifies_this_candidate'], False)
        for field in ('approved', 'canonical_change_applied', 'publication_ready',
                      'entire_verse_attested_in_one_manuscript'):
            self.assertIs(self.current['restoration_draft'][field], False)

    def test_selected_hebrew_english_and_both_disclosure_anchors(self):
        self.assertEqual(self.current['source']['edition'], 'POB-critical')
        self.assertEqual(self.current['source']['text'],
                         'ועלי זקן מאד וישמע את אשר עושים בניו לבני ישראל׃')
        self.assertEqual(self.current['translation']['text'],
                         'Eli was very old[a], and he heard what his sons were doing to the people of Israel[b].')
        self.assertNotEqual(self.current['source'], self.baseline['source'])
        self.assertNotEqual(self.current['translation'], self.baseline['translation'])
        text = self.current['translation']['text']
        self.assertEqual(re.findall(r'\[([a-z])\]', text), ['a', 'b'])
        notes = self.current['translation']['footnotes']
        self.assertEqual([note['marker'] for note in notes], ['a', 'b'])
        self.assertTrue(all(note['reason'] == 'textual_variant' for note in notes))
        for phrase in ('ninety years', 'following words are missing', 'Ninety-eight',
                       'one editorial reconstruction', 'Masoretic and Greek forms give no age'):
            self.assertIn(phrase, notes[0]['text'])
        for phrase in ('sons of Israel', 'collective designation', 'all that his sons',
                       'lying with the women', 'entrance to the tent of meeting',
                       'assembled', 'surviving text and space', 'other Greek witnesses have longer forms',
                       'earliest wording remains uncertain'):
            self.assertIn(phrase, notes[1]['text'])

    def test_source_english_note_score_and_false_to_zero_drift_are_rejected(self):
        for field in ('source', 'english', 'note', 'score', 'archival_false', 'preparation_false'):
            record = copy.deepcopy(self.current)
            if field == 'source':
                record['source']['text'] = record['source']['text'].replace('לבני ישראל', 'לכל ישראל')
            elif field == 'english':
                record['translation']['text'] += ' Certain original.'
            elif field == 'note':
                record['translation']['footnotes'][1]['text'] = 'Certain original.'
            elif field == 'score':
                record['cross_check']['agreement'] = 1
            elif field == 'archival_false':
                record['review_history'][0]['certifies_this_candidate'] = 0
            else:
                record['restoration_draft']['approved'] = 0
            with self.subTest(field=field), self.assertRaises(ValueError):
                critical_verse.validate(record, **TRUST)
        original = Path.read_bytes
        for name in (SOURCE, APP + 'editorial_review.v2.json'):
            def corrupt(path):
                raw = original(path)
                return raw + b'corrupt' if path == ROOT / name else raw
            with self.subTest(pinned_file=name), patch.object(Path, 'read_bytes', new=corrupt):
                with self.assertRaisesRegex(ValueError, 'Pinned file drift'):
                    critical_verse.validate(self.current, **TRUST)

    def test_all_811_raw_book_paths_match_baseline_except_exact_target(self):
        self.assertEqual(self.plan['application_base_revision'], BASE)
        self.assertEqual(self.plan['original_source_base_revision'], SOURCE_BASE)
        expected = {name: sha(raw) for name, raw in self.book_raw.items()}
        self.assertEqual(len(expected), 811)
        self.assertEqual(digest(expected), self.plan['book_baseline']['raw_path_sha256_map_digest'])
        self.assertEqual(sha(self.book_raw[TARGET]), self.plan['before_sha256'])
        self.assertFalse((ROOT / BOOK).is_symlink())
        live = {}
        for path in (ROOT / BOOK).rglob('*'):
            self.assertFalse(path.is_symlink(), str(path))
            if path.is_file() and path.suffix == '.yaml':
                live[str(path.relative_to(ROOT))] = sha(path.read_bytes())
        self.assertEqual(set(live), set(expected))
        self.assertEqual({name for name in expected if live[name] != expected[name]}, {TARGET})
        expected[TARGET] = CANDIDATE_SHA
        self.assertEqual(live, expected)
        goliath = BOOK + '/017/004.yaml'
        self.assertEqual((ROOT / goliath).read_bytes(), self.book_raw[goliath])

    def test_actual_full_export_only_changes_2_22_and_preserves_notes_not_deployment_proof(self):
        after = exporter.export_book('1SA')
        loader = exporter.load_translation_record

        def overlay(book, chapter, verse):
            if (book, chapter, verse) == ('1SA', 2, 22):
                return copy.deepcopy(self.baseline)
            return loader(book, chapter, verse)

        with patch.object(exporter, 'load_translation_record', side_effect=overlay):
            before = exporter.export_book('1SA')
        old, new = index(before), index(after)
        self.assertEqual((len(before['chapters']), len(old)), (31, 811))
        self.assertEqual((len(after['chapters']), len(new)), (31, 811))
        self.assertEqual(set(old), set(new))
        self.assertEqual({key for key in old if old[key] != new[key]}, {(2, 22)})
        self.assertEqual(sum(old[key] == new[key] for key in old), 810)
        self.assertEqual(digest(before), 'c970260b4451b82bdcfb157259090a6e796736236bc00425c39f9e1c07ea9e45')
        self.assertEqual(digest(after), '6ff7ff81e6070d89d055458ddc152ff5638a69e8ae63912d8899491124c48113')
        self.assertEqual(digest(before), self.plan['actual_preflight']['before_export_sha256'])
        self.assertEqual(digest(after), self.plan['actual_preflight']['candidate_export_sha256'])
        self.assertEqual(new[2, 22]['text'], self.current['translation']['text'])
        self.assertEqual(new[2, 22]['footnotes'], self.current['translation']['footnotes'])
        self.assertNotIn('source', new[2, 22])
        # This is a local exporter assertion. It cannot certify the CDN payload,
        # actual provenance navigation, mobile/offline UI, or a deployed release.
        review = json.loads((ROOT / APP / 'editorial_review.v2.json').read_bytes())
        self.assertIs(review['deployed_reader_verified'], False)

    def test_raw_wlc_redraft_refuses_selected_critical_source_before_model(self):
        verse = draft.load_source_verse('1SA', 2, 22)
        self.assertEqual(draft.translation_path_for_verse(verse), ROOT / TARGET)
        self.assertNotEqual(draft.source_text_for_verse(verse), self.current['source']['text'])
        with patch.object(draft, 'call_model') as model:
            with self.assertRaisesRegex(ValueError, 'Selected-source regeneration required'):
                draft.assert_raw_ot_draft_source_safe(verse)
            with self.assertRaisesRegex(ValueError, 'Selected-source regeneration required'):
                draft.draft_verse(verse, write=True)
            model.assert_not_called()
        self.assertEqual((ROOT / TARGET).read_bytes(), self.current_raw)


if __name__ == '__main__':
    unittest.main()
