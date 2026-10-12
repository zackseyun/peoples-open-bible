"""Scoped same-source English application, not original-pointing certification."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes
from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
BASE = 'b2f0cd87b78333613b2bc099c6bf62834746aef6'
CONTRACT = 'sources/textual_restoration/comparisons/nahum1_5_earth_reader_contract.2026-10-11.v1.json'
RECEIPT = 'sources/textual_restoration/applications/nahum1_5_earth_reader.2026-10-11.v1.json'
TARGET = (1, 5)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def plain(text):
    return re.sub(r'\[[a-z]\]', '', text)


def digest(obj):
    return sha(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


class NahumEarthApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        cls.candidate = json.loads((ROOT / cls.contract['candidate']).read_text())
        cls.historical = {}
        for pin in cls.contract['book_baseline_pins']:
            raw = subprocess.check_output(['git', 'show', f"{BASE}:{pin['path']}"], cwd=ROOT)
            assert sha(raw) == pin['sha256']
            p = Path(pin['path'])
            cls.historical[(int(p.parent.name), int(p.stem))] = yaml.safe_load(raw)
        cls.before = cls.historical[TARGET]

    def test_complete_candidate_and_six_appended_archives(self):
        c, b, contract = self.candidate, self.before, self.contract
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(c)
        self.assertEqual(contract['baseline_commit'], BASE)
        self.assertEqual(sha((ROOT / contract['candidate']).read_bytes()), contract['candidate_sha256'])
        self.assertEqual(sha(yaml.safe_dump(c, allow_unicode=True, sort_keys=False,
                                          width=1000).encode()), contract['candidate_yaml_sha256'])
        for field in ('id', 'reference', 'source', 'ai_draft', 'theological_decisions'):
            self.assertEqual(c[field], b[field], field)
        self.assertEqual(c['translation']['philosophy'], b['translation']['philosophy'])
        original_history = b['review_history']
        self.assertEqual(c['review_history'][:len(original_history)], original_history)
        archives = c['review_history'][len(original_history):]
        expected = {'status', 'cross_check', 'translation.text', 'translation.footnotes',
                    'lexical_decisions', 'theological_decisions'}
        self.assertEqual(len(archives), 6)
        self.assertEqual({h['field'] for h in archives}, expected)
        for h in archives:
            old = b
            for part in h['field'].split('.'):
                old = old[part]
            self.assertEqual(h['value'], old)
            self.assertEqual(h['archived_from_baseline_sha256'], contract['baseline_yaml_sha256'])
            self.assertIs(h['historical_review_inputs_verified'], False)
            self.assertIs(h['certifies_this_candidate'], False)
        self.assertEqual(c['status'], 'draft')
        self.assertEqual(c['cross_check'], {'status': 'needs_review'})
        self.assertEqual(c['revisions'][:-1], b['revisions'])
        self.assertEqual(c['revisions'][-1]['from'], b['translation']['text'])
        self.assertEqual(c['revisions'][-1]['to'], c['translation']['text'])
        self.assertEqual(c['revisions'][-1]['baseline_sha256'], contract['baseline_yaml_sha256'])
        allowed = {'translation', 'lexical_decisions', 'revisions', 'review_history',
                   'source_audit', 'textual_comparison'}
        self.assertLessEqual({k for k in set(b) | set(c) if b.get(k) != c.get(k)}, allowed)

    def test_only_three_dependent_lexical_entries_change(self):
        c, b = self.candidate['lexical_decisions'], self.before['lexical_decisions']
        self.assertEqual(len(c), len(b))
        for i, entry in enumerate(c):
            changed = {k for k in set(entry) | set(b[i]) if entry.get(k) != b[i].get(k)}
            self.assertEqual(changed, {'rationale'} if i == 0 else
                             {'chosen', 'alternatives', 'rationale'} if i in (5, 7) else set())
            self.assertEqual(entry['source_word'], b[i]['source_word'])
            self.assertEqual(entry['lexicon'], b[i]['lexicon'])
        self.assertIn('without a prefixed definite article', c[0]['rationale'])
        self.assertIn('initial he belongs to the noun', c[0]['rationale'])
        self.assertIn('Mur88', c[0]['rationale'])
        self.assertEqual(c[5]['chosen'], 'heaves')
        self.assertEqual(c[7]['chosen'], 'before him')
        for phrase in ('unusual intransitive', 'not a proven exclusive lexical sense',
                       'unadopted hypothesis', 'do not select original Hebrew pointing'):
            self.assertIn(phrase, c[5]['rationale'])
        self.assertIn('explicit face image is a real main-text tradeoff', c[7]['rationale'])

    def test_clause_notes_and_retained_source_interpretation(self):
        text = self.candidate['translation']['text']
        self.assertEqual(text, 'The mountains quake before him, and the hills melt away; '
                         'the earth heaves[a] before him[b], the world and all who dwell in it.')
        self.assertEqual(plain(text), plain(self.before['translation']['text']).replace(
            'the earth rises up before his face', 'the earth heaves before him'))
        notes = self.candidate['translation']['footnotes']
        self.assertEqual([n['marker'] for n in notes], ['a', 'b'])
        self.assertEqual(re.findall(r'\[([a-z])\]', text), ['a', 'b'])
        for phrase in ('rises up', 'is upheaved', 'retained Hebrew pointing', 'unusual',
                       'same consonants', 'is devastated', 'not adopted',
                       'partly reconstructed Greek', 'does not settle'):
            self.assertIn(phrase, notes[0]['text'])
        self.assertEqual(notes[0]['reason'], 'textual_variant')
        self.assertIn('from/before his face', notes[1]['text'])
        self.assertEqual(audit_footnotes.audit_one(ROOT / self.contract['candidate'])['status'], 'ok')
        audit = self.candidate['source_audit']
        self.assertIs(audit['source_consonants_pointing_segmentation_retained'], True)
        self.assertIs(audit['fresh_halot_consultation'], False)
        self.assertIs(audit['generated_images_used_as_evidence'], False)
        self.assertIn('HOLD', audit['historical_priority'])
        self.assertIs(self.candidate['textual_comparison']['whole_verse_optimality_certified'], False)

    def test_identity_masked_assessment_and_exact_context(self):
        comparison = self.candidate['textual_comparison']
        packet = json.loads((ROOT / comparison['english_contract']).read_text())
        result = json.loads((ROOT / comparison['english_result']).read_text())
        self.assertEqual(sha((ROOT / result['contract']).read_bytes()), result['contract_sha256'])
        self.assertEqual(packet['source_text'], self.before['source']['text'])
        self.assertEqual(packet['context_before'], plain(self.historical[(1, 4)]['translation']['text']))
        self.assertEqual(packet['context_after'], plain(self.historical[(1, 6)]['translation']['text']))
        self.assertEqual(packet['candidates']['K'], plain(self.candidate['translation']['text']))
        self.assertEqual(packet['candidates']['R'], plain(self.before['translation']['text']))
        self.assertEqual(packet['presentation_orders'], [['K', 'R'], ['R', 'K']])
        self.assertEqual(result['working_preference'], 'K')
        self.assertIn('Context makes “heaves” plausible; it does not demonstrate it',
                      result['actual_assessment'])
        self.assertIn('HOLD would be appropriate', result['actual_assessment'])
        self.assertIs(result['repeat_until_agreement'], False)
        self.assertIs(packet['blinding']['full_main_english_blind_vote_claimed'], False)
        self.assertIs(packet['blinding']['order_check_is_not_an_independent_vote'], True)

    def test_historical_input_pins_do_not_freeze_future_documents(self):
        new_inputs = {self.candidate['textual_comparison']['english_contract'],
                      self.candidate['textual_comparison']['english_result']}
        for path, expected in self.contract['input_pins'].items():
            raw = ((ROOT / path).read_bytes() if path in new_inputs else
                   subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))
            self.assertEqual(sha(raw), expected, path)

    def test_complete_pinned_historical_proposed_export(self):
        self.assertEqual(len(self.contract['book_baseline_pins']), 47)
        self.assertEqual(len(self.historical), 47)
        loader = exporter.load_translation_record
        def load(code, ch, v, candidate=False):
            if code != 'NAM':
                return loader(code, ch, v)
            return self.candidate if candidate and (ch, v) == TARGET else self.historical[(ch, v)]
        with patch.object(exporter, 'load_translation_record', side_effect=load):
            before = exporter.export_book('NAM')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v: load(c, ch, v, True)):
            after = exporter.export_book('NAM')
        a, b = index(after), index(before)
        self.assertEqual((len(after['chapters']), len(a)), (3, 47))
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[1, 5]])
        self.assertEqual(sum(a[k] == b[k] for k in a), 46)
        self.assertEqual(a[TARGET]['footnotes'], self.candidate['translation']['footnotes'])
        self.assertEqual(len(a[TARGET]['footnotes']), 2)
        preflight = self.contract['preflight']
        self.assertEqual(digest(before), preflight['before_export_sha256'])
        self.assertEqual(digest(after), preflight['candidate_export_sha256'])
        self.assertIs(preflight['canonical_written'], False)

    def test_exact_applied_bytes_complete_current_export_and_non_targets(self):
        raw = (ROOT / self.contract['canonical_target']).read_bytes()
        self.assertEqual(sha(raw), self.contract['candidate_yaml_sha256'])
        self.assertEqual(yaml.safe_load(raw), self.candidate)
        for pin in self.contract['book_baseline_pins']:
            if pin['path'] != self.contract['canonical_target']:
                self.assertEqual(sha((ROOT / pin['path']).read_bytes()), pin['sha256'])
        after = exporter.export_book('NAM')
        self.assertEqual(digest(after), self.contract['preflight']['candidate_export_sha256'])
        self.assertEqual(index(after)[TARGET]['footnotes'], self.candidate['translation']['footnotes'])
        for target, name in [((2, 9), 'nahum2_9_reader'), ((3, 18), 'nahum3_18_reader')]:
            old = json.loads((ROOT / f'sources/textual_restoration/candidates/{name}.2026-10-10.v1.json').read_text())
            self.assertEqual(self.historical[target], old)
        self.assertEqual(audit_footnotes.audit_one(ROOT / self.contract['canonical_target'])['status'], 'ok')

    def test_receipt_keeps_english_and_source_judgments_separate(self):
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(receipt['contract'], CONTRACT)
        self.assertEqual(receipt['contract_sha256'], sha((ROOT / CONTRACT).read_bytes()))
        self.assertEqual(receipt['candidate_sha256'], self.contract['candidate_sha256'])
        self.assertEqual(receipt['candidate_yaml_sha256'], self.contract['candidate_yaml_sha256'])
        self.assertEqual(receipt['review']['status'], 'pass')
        self.assertEqual(receipt['review']['reviewed_candidate_sha256'], self.contract['candidate_sha256'])
        self.assertEqual(receipt['review']['reviewed_contract_sha256'], receipt['contract_sha256'])
        self.assertEqual(receipt['application']['status'], 'applied-local-verified')
        self.assertEqual(receipt['application']['after_export_sha256'],
                         self.contract['preflight']['candidate_export_sha256'])
        self.assertEqual(receipt['application']['changed_export_ids'], [[1, 5]])
        self.assertEqual(receipt['application']['other_units_unchanged'], 46)
        self.assertIs(receipt['decisions']['marker_free_main_english_changed'], True)
        for flag in ('source_changed', 'source_pointing_changed', 'source_priority_settled',
                     'canon_changed', 'fresh_manuscript_transcription', 'imagegen_evidence',
                     'whole_verse_optimality_certified', 'historical_approval_transferred',
                     'deployed_reader_verified'):
            self.assertIs(receipt['decisions'][flag], False)


if __name__ == '__main__':
    unittest.main()
