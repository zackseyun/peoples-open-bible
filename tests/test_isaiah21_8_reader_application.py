"""Exact lion/lookout disclosure and anchors, not proof of original-text priority."""
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
from jsonschema import Draft202012Validator
from tools import audit_footnotes
from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
BASE = '61c8af3011b9501ab05ff6a0ffa829e980ffd6f7'
TARGET = 'translation/ot/isaiah/021/008.yaml'
CANDIDATE = 'sources/textual_restoration/candidates/isaiah21_8_reader.2026-10-10.v1.json'
CONTRACT = 'sources/textual_restoration/comparisons/isaiah21_8_reader_contract.2026-10-10.v1.json'
RECEIPT = 'sources/textual_restoration/applications/isaiah21_8_reader.2026-10-10.v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


def clean(text):
    return re.sub(r'\[[a-z]\]', '', text)


class Isaiah218ReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = subprocess.check_output(['git', 'show', f'{BASE}:{TARGET}'], cwd=ROOT)
        cls.before = yaml.safe_load(cls.raw)
        cls.candidate = json.loads((ROOT / CANDIDATE).read_text())
        cls.contract = json.loads((ROOT / CONTRACT).read_text())

    def receipt(self):
        # Candidate-only tests remain runnable before the application receipt exists.
        return json.loads((ROOT / RECEIPT).read_text())

    def test_complete_schema_candidate_and_preserved_source_generation_main_english(self):
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        validator.validate(self.candidate)
        self.assertEqual(self.candidate['id'], 'ISA.21.8')
        self.assertEqual(self.candidate['reference'], 'Isaiah 21:8')
        for field in ('source', 'ai_draft'):
            self.assertEqual(self.candidate[field], self.before[field])
        self.assertEqual(self.candidate['translation']['philosophy'],
                         self.before['translation']['philosophy'])
        self.assertEqual(clean(self.candidate['translation']['text']),
                         clean(self.before['translation']['text']))

    def test_two_notes_exact_night_note_and_true_lion_nights_anchors(self):
        tr = self.candidate['translation']
        self.assertEqual(tr['text'],
                         'Then he cried, “A lion![a] On the watchtower, my lord, I stand continually by day, and at my post I am stationed all the nights[b].”')
        self.assertEqual(re.findall(r'\[([a-z])\]', tr['text']), ['a', 'b'])
        self.assertEqual([n['marker'] for n in tr['footnotes']], ['a', 'b'])
        self.assertEqual(len(tr['footnotes']), 2)
        self.assertEqual(tr['footnotes'][1], self.before['translation']['footnotes'][1])
        self.assertIn('A lion![a]', tr['text'])
        self.assertIn('all the nights[b]', tr['text'])
        self.assertNotIn('cried[a]', tr['text'])
        self.assertNotIn('by day[b]', tr['text'])
        note = tr['footnotes'][0]
        self.assertEqual(note['reason'], 'textual_variant')
        for phrase in ('Masoretic Hebrew has ‘lion,’', 'a difficult expression here',
                       'Great Isaiah Scroll (1QIsaᵃ)', '‘the one who sees,’',
                       '‘Then the lookout cried.’', '‘Like a lion’ interprets',
                       'comparison word is not written'):
            self.assertIn(phrase, note['text'])

    def test_six_archives_exact_prior_revisions_and_no_transferred_approval(self):
        fields = ['status', 'translation', 'lexical_decisions', 'revision_pass',
                  'cross_check', 'ai_draft']
        history = self.candidate['review_history']
        self.assertEqual([h['field'] for h in history], fields)
        self.assertEqual({h['field']: h['value'] for h in history},
                         {field: self.before[field] for field in fields})
        self.assertTrue(all(h['archived_from_baseline_sha256'] == sha(self.raw) and
                            h['certifies_this_candidate'] is False for h in history))
        self.assertEqual(self.candidate['revisions'][:-1], self.before['revisions'])
        self.assertEqual(len(self.before['revisions']), 2)
        revision = self.candidate['revisions'][-1]
        self.assertEqual(revision['from'], self.before['translation']['text'])
        self.assertEqual(revision['to'], self.candidate['translation']['text'])
        self.assertEqual(revision['category'], 'reader_disclosure')
        self.assertEqual(self.candidate['status'], 'draft')
        self.assertEqual(self.candidate['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', self.candidate)
        self.assertIs(self.candidate['source_audit']['human_or_scholar_review'], False)

    def test_only_lion_lexical_entry_changes_and_scope_is_not_whole_verse_approval(self):
        old, new = self.before['lexical_decisions'], self.candidate['lexical_decisions']
        self.assertEqual(len(old), len(new))
        changed = [(a, b) for a, b in zip(old, new) if a != b]
        self.assertEqual([a['source_word'] for a, _ in changed], ['אַרְיֵה'])
        a, b = changed[0]
        self.assertEqual(b['chosen'], 'A lion!')
        self.assertEqual(a['alternatives'], ['A lion!', 'Lion!'])
        self.assertEqual(b['alternatives'], ['Like a lion!', 'Lion!'])
        self.assertEqual(dict(a, chosen=b['chosen'], alternatives=b['alternatives'],
                              rationale=b['rationale']), b)
        for phrase in ('current provisional main text', 'supplies a comparison',
                       'Published 1QIsaᵃ instead has הראה', 'note[a]',
                       'Historical priority remains unresolved',
                       'No fresh HALOT consultation is claimed'):
            self.assertIn(phrase, b['rationale'])
        audit = self.candidate['source_audit']
        for flag in ('source_changed', 'marker_free_english_changed',
                     'original_priority_settled', 'publication_approved'):
            self.assertIs(audit[flag], False)
        self.assertIs(audit['no_fresh_halot_consultation'], True)
        self.assertIn('divine address and other lexical choices not adjudicated', audit['scope'])
        self.assertIn('no fresh image reading or whole-verse approval', audit['review_summary'])
        comparison = self.candidate['textual_comparison']
        for flag in ('source_changed', 'marker_free_english_changed', 'fresh_image_reading',
                     'novel_reading_demonstrated', 'canon_changed', 'publication_approved'):
            self.assertIs(comparison[flag], False)
        self.assertIn('Unresolved', comparison['historical_priority'])
        self.assertIs(self.contract['blind_main_english_vote_claimed'], False)
        self.assertIs(self.contract['repeat_until_agreement'], False)

    def test_current_full_isaiah_export_only_target_changes_and_notes_survive(self):
        # Future-safe isolation: compare today's book against only its target reverted.
        after = exporter.export_book('ISA')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
                          self.before if c == 'ISA' and (ch, v) == (21, 8) else loader(c, ch, v)):
            before = exporter.export_book('ISA')
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 66)
        self.assertEqual(len(a), 1291)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[21, 8]])
        self.assertEqual(a[(21, 8)]['footnotes'], self.candidate['translation']['footnotes'])
        self.assertEqual(len(a[(21, 8)]['footnotes']), 2)
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)['status'], 'ok')

    def test_historical_git_archive_overlay_and_1290_non_target_manifest(self):
        # Historical receipt hashes do not depend on future unrelated Isaiah revisions.
        archive = subprocess.check_output(['git', 'archive', BASE, 'translation/ot/isaiah'], cwd=ROOT)
        historical, manifest = {}, {}
        with tarfile.open(fileobj=io.BytesIO(archive)) as snapshot:
            for member in snapshot.getmembers():
                if member.isfile() and member.name.endswith('.yaml'):
                    raw = snapshot.extractfile(member).read()
                    p = Path(member.name)
                    historical[(int(p.parent.name), int(p.stem))] = yaml.safe_load(raw)
                    if member.name != TARGET:
                        manifest[member.name] = sha(raw)
        self.assertEqual(len(historical), 1291)
        self.assertEqual(len(manifest), 1290)
        loader = exporter.load_translation_record

        def snapshot_record(c, ch, v, candidate=False):
            if c != 'ISA':
                return loader(c, ch, v)
            if candidate and (ch, v) == (21, 8):
                return self.candidate
            return historical.get((ch, v))

        with patch.object(exporter, 'load_translation_record', side_effect=snapshot_record):
            before = exporter.export_book('ISA')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
                          snapshot_record(c, ch, v, candidate=True)):
            after = exporter.export_book('ISA')
        self.assertEqual(len(before['chapters']), 66)
        self.assertEqual(len(index(before)), 1291)
        a, b = index(after), index(before)
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[21, 8]])
        receipt = self.receipt()
        for preflight in (self.contract['preflight'], receipt['preflight']):
            self.assertEqual(preflight['chapters'], 66)
            self.assertEqual(preflight['units'], 1291)
            self.assertEqual(preflight['changed_units'], [[21, 8]])
            self.assertEqual(preflight['other_verse_files'], 1290)
            self.assertEqual(preflight['exported_target_notes'], 2)
            self.assertEqual(compact_sha(before), preflight['export_before_sha256'])
            self.assertEqual(compact_sha(after), preflight['export_candidate_sha256'])
            self.assertEqual(compact_sha(manifest), preflight['other_verse_manifest_sha256'])
        self.assertEqual(compact_sha(after), receipt['application']['export_after_sha256'])
        self.assertEqual(compact_sha(manifest),
                         receipt['application']['other_verse_manifest_sha256'])

    def test_exact_candidate_contract_current_yaml_and_applied_verified_receipt(self):
        r, c = self.receipt(), self.contract
        candidate_sha = sha((ROOT / CANDIDATE).read_bytes())
        contract_sha = sha((ROOT / CONTRACT).read_bytes())
        serialized = yaml.safe_dump(self.candidate, allow_unicode=True,
                                    sort_keys=False, width=1000).encode()
        yaml_sha = sha(serialized)
        self.assertEqual(candidate_sha, '1e0b251a402ca93c5b70e047eefe01a3e8e4f73c74316256828b96f81ba79ad6')
        self.assertEqual(contract_sha, '1b1ee22063d0f90a6ad5e5219f74061260a93a46328618914a369151e3ee0a3e')
        self.assertEqual((ROOT / TARGET).read_bytes(), serialized)
        current = yaml.safe_load((ROOT / TARGET).read_text())
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(current)
        self.assertEqual(current, self.candidate)
        for record in (r, c):
            self.assertEqual(record['baseline_revision'], BASE)
            self.assertEqual(record['target'], 'ISA.21.8')
            self.assertEqual(record['canonical_target'], TARGET)
            self.assertEqual(record['baseline_yaml_sha256'], sha(self.raw))
            self.assertEqual(record['candidate'], CANDIDATE)
            self.assertEqual(record['candidate_sha256'], candidate_sha)
            self.assertEqual(record['candidate_yaml_sha256'], yaml_sha)
            preflight = record['preflight']
            self.assertEqual(preflight['candidate_sha256'], candidate_sha)
            self.assertEqual(preflight['candidate_yaml_sha256'], yaml_sha)
            for flag in ('schema_valid', 'source_generation_preserved',
                         'marker_free_english_unchanged', 'six_archives_exact'):
                self.assertIs(preflight[flag], True)
            self.assertIs(preflight['canonical_written'], False)
        self.assertEqual(r['reader_contract'], CONTRACT)
        self.assertEqual(r['reader_contract_sha256'], contract_sha)
        self.assertEqual(r['preflight']['pins'], c['preflight']['pins'])
        for path, digest in c['preflight']['pins'].items():
            self.assertEqual(sha((ROOT / path).read_bytes()), digest)
        self.assertEqual(r['review']['status'], 'pass')
        self.assertEqual(r['review']['candidate_sha256'], candidate_sha)
        self.assertEqual(r['review']['candidate_yaml_sha256'], yaml_sha)
        self.assertEqual(r['review']['reader_contract_sha256'], contract_sha)
        self.assertIs(r['review']['repeat_until_agreement'], False)
        self.assertEqual(r['application']['status'], 'applied-verified')
        self.assertIs(r['application']['canonical_written'], True)
        self.assertEqual(r['application']['candidate_yaml_sha256'], yaml_sha)
        self.assertEqual(r['application']['changed_units'], [[21, 8]])
        self.assertIs(r['application']['deployed_reader_verified'], False)
        for flag in ('source_changed', 'marker_free_main_english_changed',
                     'historical_approval_transferred', 'original_priority_settled',
                     'novel_reading_demonstrated', 'canon_changed', 'publication_approved',
                     'existing_night_note_content_changed', 'fresh_image_reading',
                     'divine_address_adjudicated'):
            self.assertIs(r['decision'][flag], False)
        self.assertIs(r['decision']['reader_disclosure_changed'], True)


if __name__ == '__main__':
    unittest.main()
