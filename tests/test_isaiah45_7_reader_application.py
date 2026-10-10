"""Exact reviewed English/disclosure application, not original-text or canon proof."""
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
BASE = '151161c934519009ab3d51e73d027c4c6734fb96'
TARGET = 'translation/ot/isaiah/045/007.yaml'
CANDIDATE = 'sources/textual_restoration/candidates/isaiah45_7_reader.2026-10-10.v1.json'
CONTRACT = 'sources/textual_restoration/comparisons/isaiah45_7_reader_contract.2026-10-10.v1.json'
CONTRACT_SHA = '5eedc1442b572f6c4bd69a68cc83c16221f1803c80bf58fdb3962fd0abe6e947'
RECEIPT = 'sources/textual_restoration/applications/isaiah45_7_reader.2026-10-10.v1.json'
ENGLISH_CONTRACT = 'sources/textual_restoration/comparisons/isaiah45_7_english_contract.2026-10-10.v1.json'
ENGLISH_RESULT = 'sources/textual_restoration/comparisons/isaiah45_7_english_result.2026-10-10.v1.json'
CANDIDATE_SHA = 'd095bb6be06e938cfa31bb74ff9366f46c60db1361b3152f3a6ede0d347c8bc7'
YAML_SHA = 'f31998fe7aefeca55560480bbe1b2a1bc96881ac13ac56f8efa86a22814f2b4f'
ENGLISH_CONTRACT_SHA = '61e48c641d6bd638924c303df74e56269288941865ebb975f80895631ab7e9c5'
ENGLISH_RESULT_SHA = '253072d3eb43da3e567ae7f568017fd10d4433e31d676a6a75fd7e26aa381597'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


def clean(text):
    return re.sub(r'\[[a-z]\]', '', text)


class Isaiah457ReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = subprocess.check_output(['git', 'show', f'{BASE}:{TARGET}'], cwd=ROOT)
        cls.before = yaml.safe_load(cls.raw)
        cls.candidate = json.loads((ROOT / CANDIDATE).read_text())

    def contract(self):
        return json.loads((ROOT / CONTRACT).read_text())

    def receipt(self):
        return json.loads((ROOT / RECEIPT).read_text())

    def test_complete_schema_preserved_source_generation_and_only_positive_english_change(self):
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        validator.validate(self.candidate)
        self.assertEqual(sha((ROOT / CANDIDATE).read_bytes()), CANDIDATE_SHA)
        self.assertEqual(sha(yaml.safe_dump(self.candidate, allow_unicode=True,
                                          sort_keys=False, width=1000).encode()), YAML_SHA)
        self.assertEqual(self.candidate['id'], 'ISA.45.7')
        self.assertEqual(self.candidate['reference'], 'Isaiah 45:7')
        for field in ('source', 'ai_draft'):
            self.assertEqual(self.candidate[field], self.before[field])
        self.assertEqual(self.candidate['translation']['philosophy'],
                         self.before['translation']['philosophy'])
        old = clean(self.before['translation']['text'])
        self.assertEqual(old.count('making peace'), 1)
        self.assertEqual(clean(self.candidate['translation']['text']),
                         old.replace('making peace', 'making well-being'))
        self.assertEqual(set(self.candidate) - set(self.before),
                         {'review_history', 'revisions', 'source_audit', 'textual_comparison'})
        self.assertEqual(set(self.before) - set(self.candidate), {'revision_pass'})

    def test_two_notes_actual_wellbeing_calamity_anchors_and_qualified_source_disclosure(self):
        tr = self.candidate['translation']
        self.assertEqual(tr['text'],
                         'forming light and creating darkness, making well-being[a] and creating calamity[b]; I am Yahweh, who does all these things.')
        self.assertEqual(re.findall(r'\[([a-z])\]', tr['text']), ['a', 'b'])
        self.assertEqual([n['marker'] for n in tr['footnotes']], ['a', 'b'])
        self.assertEqual(len(tr['footnotes']), 2)
        self.assertNotIn('darkness[a]', tr['text'])
        a, b = tr['footnotes']
        self.assertEqual(a['reason'], 'textual_variant')
        for phrase in ('Or ‘peace’ or ‘welfare.’', 'Masoretic Hebrew has שָׁלוֹם',
                       'Great Isaiah Scroll (1QIsaᵃ)', '‘good,’', '‘making good.’',
                       'different Hebrew reading', 'historical priority remains unresolved'):
            self.assertIn(phrase, a['text'])
        self.assertEqual(b['reason'], 'lexical_alternative')
        for phrase in ('Or ‘disaster’ or ‘evil.’', 'harm or adversity as well as moral evil',
                       'contextual rendering', 'not a theological exclusion'):
            self.assertIn(phrase, b['text'])

    def test_seven_archives_exact_new_revision_and_no_transferred_approval(self):
        fields = ['status', 'translation', 'lexical_decisions', 'theological_decisions',
                  'revision_pass', 'cross_check', 'ai_draft']
        history = self.candidate['review_history']
        self.assertEqual([h['field'] for h in history], fields)
        self.assertEqual({h['field']: h['value'] for h in history},
                         {field: self.before[field] for field in fields})
        self.assertTrue(all(h['archived_from_baseline_sha256'] == sha(self.raw) and
                            h['certifies_this_candidate'] is False for h in history))
        self.assertNotIn('revisions', self.before)
        self.assertEqual(len(self.candidate['revisions']), 1)
        revision = self.candidate['revisions'][0]
        self.assertEqual(revision['from'], self.before['translation']['text'])
        self.assertEqual(revision['to'], self.candidate['translation']['text'])
        self.assertEqual(revision['category'], 'english_source_rendering')
        self.assertEqual(self.candidate['status'], 'draft')
        self.assertEqual(self.candidate['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', self.candidate)
        audit = self.candidate['source_audit']
        for flag in ('source_changed', 'original_priority_settled',
                     'human_or_scholar_review', 'publication_approved'):
            self.assertIs(audit[flag], False)
        self.assertIs(audit['marker_free_english_changed'], True)
        self.assertIs(audit['no_fresh_halot_consultation'], True)
        self.assertIn('remaining verbs and whole verse not newly certified', audit['scope'])
        self.assertIn('full-record review is recorded separately', audit['review_summary'])
        comparison = self.candidate['textual_comparison']
        for flag in ('source_changed', 'fresh_image_reading', 'novel_reading_demonstrated',
                     'canon_changed', 'publication_approved'):
            self.assertIs(comparison[flag], False)
        self.assertIs(comparison['marker_free_english_changed'], True)
        self.assertIn('Unresolved', comparison['historical_priority'])
        self.assertIn('1Q8/4Q57 is supplied', comparison['good_alternative'])

    def test_three_lexical_changes_qualified_theology_and_one_limited_english_vote(self):
        old, new = self.before['lexical_decisions'], self.candidate['lexical_decisions']
        self.assertEqual(len(old), len(new))
        changed = [(a, b) for a, b in zip(old, new) if a != b]
        self.assertEqual([a['source_word'] for a, _ in changed],
                         ['שָׁלוֹם', 'רָע', 'אֲנִי יְהוָה'])
        shalom, adverse, name = [b for _, b in changed]
        self.assertEqual(shalom['chosen'], 'well-being')
        self.assertEqual(shalom['alternatives'], ['peace', 'welfare', 'wholeness', 'prosperity'])
        self.assertEqual(adverse['chosen'], 'calamity')
        self.assertEqual(adverse['alternatives'], ['disaster', 'evil'])
        self.assertEqual(name['chosen'], 'I am Yahweh')
        self.assertEqual(name['alternatives'], ['I, Yahweh'])
        self.assertEqual([shalom['lexicon'], adverse['lexicon']], ['BDB (hosted entry)'] * 2)
        for entry in (shalom, adverse, name):
            self.assertIn('No fresh HALOT consultation is claimed', entry['rationale'])
        self.assertIn('not a global replacement of peace elsewhere', shalom['rationale'])
        self.assertIn('neither theological preference', adverse['rationale'])
        self.assertIn('not a new historical origin or etymology claim', name['rationale'])
        for a, b in zip(self.before['theological_decisions'], self.candidate['theological_decisions']):
            self.assertEqual(dict(a, rationale=b['rationale']), b)
        theology = self.candidate['theological_decisions']
        self.assertIn('does not resolve a doctrine of divine causation', theology[0]['rationale'])
        self.assertIn('no etymological or historical-origin decision', theology[1]['rationale'])
        ec = json.loads((ROOT / ENGLISH_CONTRACT).read_text())
        er = json.loads((ROOT / ENGLISH_RESULT).read_text())
        self.assertEqual(sha((ROOT / ENGLISH_CONTRACT).read_bytes()), ENGLISH_CONTRACT_SHA)
        self.assertEqual(sha((ROOT / ENGLISH_RESULT).read_bytes()), ENGLISH_RESULT_SHA)
        self.assertEqual(er['contract'], ENGLISH_CONTRACT)
        self.assertEqual(er['contract_sha256'], ENGLISH_CONTRACT_SHA)
        self.assertEqual(er['independent_votes'], 1)
        self.assertEqual(er['preference'], 'K')
        self.assertIn('M viable', er['confidence'])
        self.assertEqual([o['order'] for o in er['orders_assessed']], ec['presentation_orders'])
        self.assertEqual([o['preference'] for o in er['orders_assessed']], ['K', 'K'])
        self.assertIs(er['assessment_frozen_before_origin_reveal'], True)
        self.assertTrue(any('not controlled first-exposure randomization' in s
                            for s in er['blinding_limits']))
        for record in (ec, er):
            self.assertIs(record['canonical_application_approved'], False)
            self.assertIs(record['repeat_until_agreement'], False)
        self.assertIs(ec['source_priority_vote'], False)
        self.assertIs(er['source_priority_approved'], False)
        self.assertIs(er['publication_approved'], False)

    def test_current_full_isaiah_export_only_target_changes_and_notes_survive(self):
        # Future-safe: today's book versus today's book with only this target reverted.
        after = exporter.export_book('ISA')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
                          self.before if c == 'ISA' and (ch, v) == (45, 7) else loader(c, ch, v)):
            before = exporter.export_book('ISA')
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 66)
        self.assertEqual(len(a), 1291)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[45, 7]])
        self.assertEqual(a[(45, 7)]['footnotes'], self.candidate['translation']['footnotes'])
        self.assertEqual(len(a[(45, 7)]['footnotes']), 2)
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)['status'], 'ok')

    def test_historical_git_archive_overlay_and_1290_non_target_manifest(self):
        # Frozen historical exports are independent of future unrelated Isaiah changes.
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
            if candidate and (ch, v) == (45, 7):
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
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[45, 7]])
        contract, receipt = self.contract(), self.receipt()
        for preflight in (contract['preflight'], receipt['preflight']):
            self.assertEqual(preflight['chapters'], 66)
            self.assertEqual(preflight['units'], 1291)
            self.assertEqual(preflight['changed_units'], [[45, 7]])
            self.assertEqual(preflight['other_verse_files'], 1290)
            self.assertEqual(preflight['exported_target_notes'], 2)
            self.assertEqual(compact_sha(before), preflight['export_before_sha256'])
            self.assertEqual(compact_sha(after), preflight['export_candidate_sha256'])
            self.assertEqual(compact_sha(manifest), preflight['other_verse_manifest_sha256'])
        self.assertEqual(compact_sha(after), receipt['application']['export_after_sha256'])
        self.assertEqual(compact_sha(manifest), receipt['application']['other_verse_manifest_sha256'])

    def test_exact_candidate_contract_current_yaml_and_applied_verified_receipt(self):
        r, c = self.receipt(), self.contract()
        contract_sha = sha((ROOT / CONTRACT).read_bytes())
        self.assertEqual(contract_sha, CONTRACT_SHA)
        serialized = yaml.safe_dump(self.candidate, allow_unicode=True,
                                    sort_keys=False, width=1000).encode()
        self.assertEqual((ROOT / TARGET).read_bytes(), serialized)
        current = yaml.safe_load((ROOT / TARGET).read_text())
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(current)
        self.assertEqual(current, self.candidate)
        for record in (r, c):
            self.assertEqual(record['baseline_revision'], BASE)
            self.assertEqual(record['target'], 'ISA.45.7')
            self.assertEqual(record['canonical_target'], TARGET)
            self.assertEqual(record['baseline_yaml_sha256'], sha(self.raw))
            self.assertEqual(record['candidate'], CANDIDATE)
            self.assertEqual(record['candidate_sha256'], CANDIDATE_SHA)
            self.assertEqual(record['candidate_yaml_sha256'], YAML_SHA)
            preflight = record['preflight']
            self.assertEqual(preflight['candidate_sha256'], CANDIDATE_SHA)
            self.assertEqual(preflight['candidate_yaml_sha256'], YAML_SHA)
            for flag in ('schema_valid', 'source_generation_preserved',
                         'marker_free_english_change_only_peace_to_well_being', 'seven_archives_exact'):
                self.assertIs(preflight[flag], True)
            self.assertIs(preflight['canonical_written'], False)
        self.assertEqual(r['reader_contract'], CONTRACT)
        self.assertEqual(r['reader_contract_sha256'], contract_sha)
        self.assertEqual(r['preflight']['pins'], c['preflight']['pins'])
        for path, digest in c['preflight']['pins'].items():
            self.assertEqual(sha((ROOT / path).read_bytes()), digest)
        for path, digest in ((ENGLISH_CONTRACT, ENGLISH_CONTRACT_SHA), (ENGLISH_RESULT, ENGLISH_RESULT_SHA)):
            self.assertEqual(c['preflight']['pins'][path], digest)
        self.assertEqual(r['review']['status'], 'pass')
        self.assertEqual(r['review']['candidate_sha256'], CANDIDATE_SHA)
        self.assertEqual(r['review']['candidate_yaml_sha256'], YAML_SHA)
        self.assertEqual(r['review']['reader_contract_sha256'], contract_sha)
        self.assertIs(r['review']['repeat_until_agreement'], False)
        self.assertEqual(r['application']['status'], 'applied-verified')
        self.assertIs(r['application']['canonical_written'], True)
        self.assertEqual(r['application']['candidate_yaml_sha256'], YAML_SHA)
        self.assertEqual(r['application']['changed_units'], [[45, 7]])
        self.assertIs(r['application']['deployed_reader_verified'], False)
        for flag in ('source_changed', 'historical_approval_transferred',
                     'original_priority_settled', 'novel_reading_demonstrated',
                     'canon_changed', 'publication_approved', 'fresh_image_reading'):
            self.assertIs(r['decision'][flag], False)
        self.assertIs(r['decision']['marker_free_main_english_changed'], True)
        self.assertIs(r['decision']['reader_disclosure_changed'], True)
        self.assertIs(c['blind_main_english_vote_claimed'], False)
        self.assertIs(c['identity_masked_positive_phrase_comparison_recorded'], True)
        self.assertIs(c['repeat_until_agreement'], False)


if __name__ == '__main__':
    unittest.main()
