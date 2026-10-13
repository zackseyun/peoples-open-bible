"""Six unchanged-source numeral/anchor corrections, not source-priority proof."""
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
from tools import export_mobile_bible as ex

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = 'sources/textual_restoration/comparisons/eleven_compound_reader_contract.2026-10-12.v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(obj):
    return sha(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def plain(text):
    return re.sub(r'\[[a-z]+\]', '', text)


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


def field(record, name):
    for key in name.split('.'):
        record = record[key]
    return record


class ElevenCompoundReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.k = json.loads((ROOT / CONTRACT).read_text())
        cls.before, cls.candidates, cls.pins = {}, {}, {}
        for row in cls.k['targets']:
            raw = subprocess.check_output(['git', 'show', f"{cls.k['baseline_commit']}:{row['canonical_target']}"], cwd=ROOT)
            assert sha(raw) == row['baseline_yaml_sha256']
            cls.before[row['id']] = yaml.safe_load(raw)
            cls.candidates[row['id']] = json.loads((ROOT / row['candidate']).read_text())
            cls.pins[row['id']] = row
        h = cls.k['historical_ezekiel']
        raw = subprocess.check_output(['git', 'show', f"{h['commit']}:{h['path']}"], cwd=ROOT)
        assert sha(raw) == h['sha256']
        cls.historical = yaml.safe_load(raw)
        # Receipt hashes describe this transaction's immutable baseline, not
        # every later legitimate application to an unrelated verse.
        raw = subprocess.check_output([
            'git', 'archive', cls.k['baseline_commit'],
            *(book['folder'] for book in cls.k['books'])
        ], cwd=ROOT)
        cls.book_records = {book['code']: {} for book in cls.k['books']}
        cls.non_target_pins = {book['code']: [] for book in cls.k['books']}
        targets = {row['canonical_target'] for row in cls.k['targets']}
        with tarfile.open(fileobj=io.BytesIO(raw)) as snapshot:
            for member in snapshot.getmembers():
                if not member.isfile() or not member.name.endswith('.yaml'):
                    continue
                for book in cls.k['books']:
                    if member.name.startswith(book['folder'] + '/'):
                        code, p = book['code'], Path(member.name)
                        content = snapshot.extractfile(member).read()
                        cls.book_records[code][(int(p.parent.name), int(p.stem))] = yaml.safe_load(content)
                        if member.name not in targets:
                            cls.non_target_pins[code].append({'path': member.name, 'sha256': sha(content)})
                        break
        for pins in cls.non_target_pins.values():
            pins.sort(key=lambda pin: pin['path'])
        cls.exports, cls.current_before = {}, {}
        loader = ex.load_translation_record

        def load(code, ch, verse, proposed=False, current=False):
            key = f'{code}.{ch}.{verse}'
            if key in cls.candidates:
                return cls.candidates[key] if proposed else cls.before[key]
            if not current and code in cls.book_records:
                return cls.book_records[code].get((ch, verse))
            return loader(code, ch, verse)

        for book in cls.k['books']:
            code = book['code']
            current = ex.export_book(code)
            with patch.object(ex, 'load_translation_record', side_effect=lambda c, ch, v: load(c, ch, v, current=True)):
                cls.current_before[code] = ex.export_book(code)
            with patch.object(ex, 'load_translation_record', side_effect=load):
                before = ex.export_book(code)
            with patch.object(ex, 'load_translation_record', side_effect=lambda c, ch, v: load(c, ch, v, True)):
                proposed = ex.export_book(code)
            cls.exports[code] = current, before, proposed

    def test_candidate_bytes_schema_and_source_preservation(self):
        schema = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        self.assertEqual(len(self.candidates), 6)
        for key, c in self.candidates.items():
            b, pin = self.before[key], self.pins[key]
            self.assertEqual(sha((ROOT / pin['candidate']).read_bytes()), pin['candidate_sha256'])
            self.assertEqual(sha(yaml.safe_dump(c, allow_unicode=True, sort_keys=False, width=1000).encode()), pin['candidate_yaml_sha256'])
            schema.validate(c)
            for name in ('id', 'reference', 'source'):
                self.assertEqual(c[name], b[name])
            self.assertEqual(sha(c['source']['text'].encode()), pin['source_text_sha256'])
            self.assertEqual(c['ai_draft'], self.historical['ai_draft'] if key.startswith('EZK') else b['ai_draft'])
            self.assertEqual(c['translation']['philosophy'], self.historical['translation']['philosophy'] if key.startswith('EZK') else b['translation']['philosophy'])
            self.assertEqual(c['status'], 'draft')
            self.assertEqual(c['cross_check'], {'status': 'needs_review'})
            self.assertNotIn('revision_pass', c)
            changed = {name for name in set(b) | set(c) if b.get(name) != c.get(name)}
            expected = {'translation', 'status', 'revision_pass', 'cross_check', 'revisions', 'review_history', 'source_audit', 'textual_comparison'}
            if key in ('1CH.25.18', '1CH.27.14', 'EZK.40.49'):
                expected.add('lexical_decisions')
            if key == 'EZK.40.49':
                expected.add('ai_draft')
            self.assertEqual(changed, expected)

    def test_exact_current_archives_and_revision_history(self):
        for key, c in self.candidates.items():
            b, pin = self.before[key], self.pins[key]
            old = b.get('review_history', [])
            self.assertEqual(c['review_history'][:len(old)], old)
            archives = [r for r in c['review_history'][len(old):] if not r.get('historical_record')]
            expected = {'translation.text', 'revision_pass'}
            if 'status' in b:
                expected.add('status')
            if 'cross_check' in b:
                expected.add('cross_check')
            if key in ('1CH.25.18', '1CH.27.14'):
                expected.add('lexical_decisions')
            if key == '1CH.27.15':
                expected.add('translation.footnotes')
            self.assertEqual({r['field'] for r in archives}, expected)
            for r in archives:
                self.assertEqual(r['value'], field(b, r['field']))
                self.assertEqual(r['archived_from_baseline_commit'], self.k['baseline_commit'])
                self.assertEqual(r['archived_from_baseline_sha256'], pin['baseline_yaml_sha256'])
                self.assertIs(r['historical_review_inputs_verified'], False)
                self.assertIs(r['certifies_this_candidate'], False)
            self.assertEqual(c['revisions'][:-1], b.get('revisions', []))
            self.assertEqual(c['revisions'][-1]['from'], b['translation']['text'])
            self.assertEqual(c['revisions'][-1]['to'], c['translation']['text'])

    def test_ezekiel_recovered_history_without_bad_current_metadata(self):
        c, h = self.candidates['EZK.40.49'], self.historical
        archived = [r for r in c['review_history'] if r.get('historical_record')]
        self.assertEqual({r['field'] for r in archived}, {'translation.footnotes', 'lexical_decisions', 'revisions', 'status', 'revision_pass', 'cross_check'})
        for r in archived:
            self.assertEqual(r['value'], field(h, r['field']))
            self.assertEqual(r['archived_from_baseline_commit'], self.k['historical_ezekiel']['commit'])
            self.assertEqual(r['archived_from_baseline_sha256'], self.k['historical_ezekiel']['sha256'])
            self.assertIs(r['certifies_this_candidate'], False)
        self.assertEqual(len(c['lexical_decisions']), 1)
        self.assertEqual(c['lexical_decisions'][0]['chosen'], 'eleven')
        self.assertIn('BDB07732', c['lexical_decisions'][0]['entry'])
        self.assertNotIn('Straightforward cardinal', c['lexical_decisions'][0]['rationale'])
        b = self.before['EZK.40.49']['translation']['text']
        self.assertEqual(plain(c['translation']['text']), b.replace('width was twelve cubits', 'width was eleven cubits'))
        self.assertIn('width was eleven cubits[a]', c['translation']['text'])
        self.assertEqual(c['revisions'][0], self.before['EZK.40.49']['revisions'][0])

    def test_numerals_and_only_dependent_lexical_changes(self):
        c25, c27, c12 = (self.candidates[k] for k in ('1CH.25.18', '1CH.27.14', '1CH.12.14'))
        self.assertEqual(c25['translation']['text'], 'the eleventh, Azarel[a]; his sons and his brothers, twelve.')
        self.assertEqual(c27['translation']['text'], 'The eleventh, for the eleventh month, was Benaiah the Pirathonite, from the sons of Ephraim[a]; and over his division were twenty-four thousand.')
        for key in ('1CH.25.18', '1CH.27.14'):
            c, b = self.candidates[key], self.before[key]
            self.assertEqual(c['lexical_decisions'][1:], b['lexical_decisions'][1:])
            self.assertEqual(c['lexical_decisions'][0]['source_word'], b['lexical_decisions'][0]['source_word'])
            self.assertNotIn('twelfth', c['lexical_decisions'][0]['chosen'])
            self.assertIn('No fresh HALOT', c['lexical_decisions'][0]['rationale'])
        self.assertEqual(c12['lexical_decisions'], self.before['1CH.12.14']['lexical_decisions'])
        self.assertEqual(plain(c12['translation']['text']), plain(self.before['1CH.12.14']['translation']['text']))
        for key in ('1CH.27.13', '1CH.27.15'):
            c, b = self.candidates[key], self.before[key]
            self.assertEqual(c['lexical_decisions'], b['lexical_decisions'])
            self.assertEqual(plain(c['translation']['text']), plain(b['translation']['text']))
            self.assertIn('twenty-four thousand', c['translation']['text'])
        self.assertEqual(plain(self.candidates['1CH.27.15']['translation']['text']).count('twelfth'), 2)
        self.assertIn('was supplies the Hebrew zero-copula', c27['lexical_decisions'][0]['rationale'])
        self.assertIn('paragraph-marker', c12['textual_comparison']['scope'])
        self.assertIn('not adjudicate', c12['source_audit']['paragraph_marker_issue'])

    def test_actual_note_anchors_and_exported_notes(self):
        anchors = {'1CH.12.14': 'eleventh[a]', '1CH.25.18': 'Azarel[a]', '1CH.27.13': 'Zerahites[a]', '1CH.27.14': 'Ephraim[a]', '1CH.27.15': 'Othniel[a]', 'EZK.40.49': 'eleven cubits[a]'}
        for key, c in self.candidates.items():
            text, notes = c['translation']['text'], c['translation']['footnotes']
            self.assertEqual(re.findall(r'\[([a-z]+)\]', text), ['b', 'a'] if key == '1CH.27.15' else ['a'])
            self.assertIn(anchors[key], text)
            self.assertEqual([n['marker'] for n in notes], ['a', 'b'] if key == '1CH.27.15' else ['a'])
            self.assertEqual(audit_footnotes.audit_one(ROOT / self.pins[key]['candidate'])['status'], 'ok')
            if key.startswith('1CH') and key != '1CH.27.15':
                self.assertEqual(notes, self.before[key]['translation']['footnotes'])
            code, ch, v = key.split('.')
            self.assertEqual(index(self.exports[code][2])[(int(ch), int(v))]['footnotes'], notes)
        note = self.candidates['EZK.40.49']['translation']['footnotes'][0]['text']
        self.assertIn('Heldai[b]', self.candidates['1CH.27.15']['translation']['text'])
        c15, b15 = self.candidates['1CH.27.15'], self.before['1CH.27.15']
        self.assertEqual(c15['translation']['footnotes'][0], b15['translation']['footnotes'][0])
        self.assertEqual(c15['translation']['footnotes'][1]['reason'], 'cross_reference')
        self.assertEqual(c15['translation']['footnotes'][1]['text'], 'Compare Heled in the parallel warrior roster at 1 Chronicles 11:30. This cross-reference does not establish a manuscript variant at this verse or prove that the two names identify the same person.')
        self.assertIn('translation/ot/1_chronicles/011/030.yaml', self.k['input_pins'])
        self.assertIn('selected Greek text reads twelve', note)
        self.assertIn('earlier remains unresolved', note)

    def test_input_pins_and_untransferred_judgments(self):
        for path, expected in self.k['input_pins'].items():
            raw = ((ROOT / path).read_bytes() if path in self.k['new_input_paths'] else subprocess.check_output(['git', 'show', f"{self.k['baseline_commit']}:{path}"], cwd=ROOT))
            self.assertEqual(sha(raw), expected, path)
        self.assertIs(self.k['canonical_change_applied_at_contract_freeze'], False)
        self.assertIs(self.k['independent_application_critique_passed_at_contract_freeze'], False)
        for c in self.candidates.values():
            self.assertEqual(c['source_audit']['historical_priority'], 'HOLD')
            self.assertIs(c['source_audit']['generated_images_used_as_evidence'], False)
            self.assertIs(c['textual_comparison']['whole_verse_optimality_certified'], False)
            self.assertIs(c['textual_comparison']['source_replacement_authorized'], False)

    def test_complete_real_exports_and_exact_six_changed_loci(self):
        changed_count = 0
        for book in self.k['books']:
            _, before, after = self.exports[book['code']]
            spec, bi, ai = book['export'], index(before), index(after)
            self.assertEqual(digest(before), spec['before_sha256'])
            self.assertEqual(digest(after), spec['proposed_sha256'])
            self.assertEqual(len(before['chapters']), spec['chapter_count'])
            self.assertEqual(len(after['chapters']), spec['chapter_count'])
            self.assertEqual(len(bi), spec['unit_count'])
            self.assertEqual(len(ai), spec['unit_count'])
            changed = [list(k) for k in bi if bi[k] != ai[k]]
            self.assertEqual(changed, spec['changed_loci'])
            changed_count += len(changed)
        self.assertEqual(changed_count, 6)

    def test_current_application_state_and_historical_non_target_aggregates(self):
        receipt = json.loads((ROOT / self.k['application_receipt']).read_text())
        self.assertEqual(receipt['contract'], CONTRACT)
        self.assertEqual(receipt['contract_sha256'], sha((ROOT / CONTRACT).read_bytes()))
        for book in self.k['books']:
            pins = self.non_target_pins[book['code']]
            self.assertEqual(len(pins), book['non_target_file_count'])
            self.assertEqual(digest(pins), book['non_target_path_and_sha256_aggregate'])
            # The proposed historical export remains pinned, while current
            # target bytes are independently checked below.
            key = 'proposed_sha256' if receipt['canonical_change_applied'] else 'before_sha256'
            historical_export = self.exports[book['code']][2 if receipt['canonical_change_applied'] else 1]
            self.assertEqual(digest(historical_export), book['export'][key])
        for key, pin in self.pins.items():
            raw = (ROOT / pin['canonical_target']).read_bytes()
            expected = pin['candidate_yaml_sha256'] if receipt['canonical_change_applied'] else pin['baseline_yaml_sha256']
            self.assertEqual(sha(raw), expected)
            if receipt['canonical_change_applied']:
                self.assertEqual(yaml.safe_load(raw), self.candidates[key])
        if receipt['canonical_change_applied']:
            self.assertIs(receipt['independent_application_critique']['passed'], True)

    def test_current_reader_isolates_six_targets_without_freezing_other_verses(self):
        receipt = json.loads((ROOT / self.k['application_receipt']).read_text())
        current = {code: exports[0] for code, exports in self.exports.items()}
        self._assert_current_reader_scope(receipt['canonical_change_applied'], current)

    def test_unapplied_reader_scope_accepts_baseline_without_ezekiel_notes(self):
        # Preflight has no six-record application yet; EZK40:49's baseline
        # has no footnotes key. Exercise the same assertions without exports
        # or disk writes, using the real baseline-target reader payloads.
        self.assertNotIn('footnotes', self.before['EZK.40.49']['translation'])
        self._assert_current_reader_scope(False, self.current_before)

    def _assert_current_reader_scope(self, applied, current_exports):
        changed_count = 0
        for book in self.k['books']:
            code, spec = book['code'], book['export']
            before = self.current_before[code]
            current = current_exports[code]
            bi, ci = index(before), index(current)
            self.assertEqual(bi.keys(), ci.keys())
            self.assertEqual(len(current['chapters']), spec['chapter_count'])
            self.assertEqual(len(ci), spec['unit_count'])
            changed = [list(key) for key in bi if bi[key] != ci[key]]
            self.assertEqual(changed, spec['changed_loci'] if applied else [])
            changed_count += len(changed)
            for key, candidate in self.candidates.items():
                target_code, ch, verse = key.split('.')
                if target_code == code:
                    unit = ci[(int(ch), int(verse))]
                    expected = candidate if applied else self.before[key]
                    self.assertEqual(unit['text'], expected['translation']['text'])
                    self.assertEqual(unit.get('footnotes', []), expected['translation'].get('footnotes', []))
        self.assertEqual(changed_count, 6 if applied else 0)


if __name__ == '__main__':
    unittest.main()
