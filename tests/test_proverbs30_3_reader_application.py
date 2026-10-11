"""Exact reader disclosure application, not proof of Hebrew original priority."""
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
BASE = 'aeab66f9dbff2fc4f18a50e6c8119c8fb2341bc1'
TARGET = 'translation/ot/proverbs/030/003.yaml'
CANDIDATE = 'sources/textual_restoration/candidates/proverbs30_3_reader.2026-10-10.v1.json'
CONTRACT = 'sources/textual_restoration/comparisons/proverbs30_3_reader_contract.2026-10-10.v1.json'
RECEIPT = 'sources/textual_restoration/applications/proverbs30_3_reader.2026-10-10.v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


def clean(text):
    return re.sub(r'\[[a-z]\]', '', text)


class Proverbs303ReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = subprocess.check_output(['git', 'show', f'{BASE}:{TARGET}'], cwd=ROOT)
        cls.before = yaml.safe_load(cls.raw)
        cls.candidate = json.loads((ROOT / CANDIDATE).read_text())
        cls.current = yaml.safe_load((ROOT / TARGET).read_text())
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        cls.receipt = json.loads((ROOT / RECEIPT).read_text())

    def test_complete_schema_record_and_preserved_source_generation_main_english(self):
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        validator.validate(self.candidate)
        validator.validate(self.current)
        self.assertEqual(self.current, self.candidate)
        self.assertEqual(self.current['id'], 'PRO.30.3')
        self.assertEqual(self.current['reference'], 'Proverbs 30:3')
        for field in ('source', 'ai_draft'):
            self.assertEqual(self.current[field], self.before[field])
        self.assertEqual(self.current['translation']['philosophy'],
                         self.before['translation']['philosophy'])
        self.assertEqual(clean(self.current['translation']['text']),
                         clean(self.before['translation']['text']))

    def test_two_notes_exact_old_note_and_true_polarity_anchors(self):
        tr = self.candidate['translation']
        self.assertEqual(tr['text'],
                         'And I have not learned wisdom, nor[a] do I know the knowledge of the Holy One[b].')
        self.assertEqual(re.findall(r'\[([a-z])\]', tr['text']), ['a', 'b'])
        self.assertEqual([n['marker'] for n in tr['footnotes']], ['a', 'b'])
        self.assertEqual(len(tr['footnotes']), 2)
        old_note = dict(self.before['translation']['footnotes'][0], marker='b')
        self.assertEqual(tr['footnotes'][1], old_note)
        new_note = tr['footnotes'][0]
        self.assertEqual(new_note['reason'], 'alternative_reading')
        for phrase in ('but I know the knowledge', 'no second negative',
                       'carries the first clause’s negative', 'possible Hebrew construction',
                       'Rahlfs–Hanhart Greek makes both claims positive', 'God teaching wisdom',
                       'Weber–Gryson Latin makes both negative',
                       'do not settle the Hebrew clause’s polarity'):
            self.assertIn(phrase, new_note['text'])
        self.assertIn('nor[a]', tr['text'])
        self.assertIn('Holy One[b]', tr['text'])

    def test_eight_archives_exact_and_old_approval_not_transferred(self):
        record = self.candidate
        fields = ['status', 'translation', 'lexical_decisions', 'theological_decisions',
                  'revision_pass', 'cross_check', 'ai_draft', 'source_audit']
        history = record['review_history']
        self.assertEqual([h['field'] for h in history], fields)
        self.assertEqual({h['field']: h['value'] for h in history},
                         {f: self.before[f] for f in fields})
        self.assertTrue(all(h['archived_from_baseline_sha256'] == sha(self.raw) and
                            h['certifies_this_candidate'] is False for h in history))
        self.assertEqual(record['revisions'][:-1], self.before['revisions'])
        self.assertEqual(len(self.before['revisions']), 1)
        revision = record['revisions'][-1]
        self.assertEqual(revision['from'], self.before['translation']['text'])
        self.assertEqual(revision['to'], record['translation']['text'])
        self.assertEqual(revision['category'], 'reader_disclosure')
        self.assertEqual(record['status'], 'draft')
        self.assertEqual(record['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', record)
        self.assertNotEqual(record['source_audit'], self.before['source_audit'])
        self.assertIs(record['source_audit']['human_or_scholar_review'], False)

    def test_only_knowledge_rationale_changed_and_no_source_priority_claim(self):
        old = self.before['lexical_decisions']
        new = self.candidate['lexical_decisions']
        self.assertEqual(len(old), len(new))
        changed = []
        for a, b in zip(old, new):
            if a != b:
                changed.append(a['source_word'])
                self.assertEqual(dict(a, rationale=b['rationale']), b)
        self.assertEqual(changed, ['אֵדָע'])
        rationale = next(d['rationale'] for d in new if d['source_word'] == 'אֵדָע')
        for phrase in ('first clause’s explicit negative', 'Hebrew does not repeat the negative',
                       'positive contrasting interpretation remains possible', 'note[a]',
                       'do not establish the intended Hebrew scope'):
            self.assertIn(phrase, rationale)
        self.assertEqual(self.candidate['theological_decisions'], self.before['theological_decisions'])
        audit = self.candidate['source_audit']
        for flag in ('source_changed', 'marker_free_english_changed', 'original_priority_settled',
                     'publication_approved'):
            self.assertIs(audit[flag], False)
        self.assertIs(audit['no_fresh_halot_consultation'], True)
        for flag in ('source_changed', 'marker_free_main_english_changed',
                     'existing_holy_one_note_content_changed', 'historical_approval_transferred',
                     'original_priority_settled', 'novel_reading_demonstrated', 'canon_changed',
                     'publication_approved'):
            self.assertIs(self.receipt['decision'][flag], False)
        self.assertIs(self.receipt['decision']['reader_disclosure_changed'], True)
        self.assertIs(self.receipt['decision']['new_polarity_note'], True)

    def test_current_full_proverbs_export_only_target_changes_and_two_notes_survive(self):
        # Compare today's book with only the target reverted, not a frozen whole-book hash.
        after = exporter.export_book('PRO')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
                          self.before if c == 'PRO' and (ch, v) == (30, 3) else loader(c, ch, v)):
            before = exporter.export_book('PRO')
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 31)
        self.assertEqual(len(a), 915)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[30, 3]])
        self.assertEqual(a[(30, 3)]['footnotes'], self.candidate['translation']['footnotes'])
        self.assertEqual(len(a[(30, 3)]['footnotes']), 2)
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)['status'], 'ok')

    def test_historical_git_archive_overlay_hashes_and_914_non_target_manifest(self):
        # Reproduce the immutable receipt snapshot independently of later Proverbs edits.
        archive = subprocess.check_output(['git', 'archive', BASE, 'translation/ot/proverbs'], cwd=ROOT)
        historical, manifest = {}, {}
        with tarfile.open(fileobj=io.BytesIO(archive)) as snapshot:
            for member in snapshot.getmembers():
                if member.isfile() and member.name.endswith('.yaml'):
                    raw = snapshot.extractfile(member).read()
                    p = Path(member.name)
                    historical[(int(p.parent.name), int(p.stem))] = yaml.safe_load(raw)
                    if member.name != TARGET:
                        manifest[member.name] = sha(raw)
        self.assertEqual(len(historical), 915)
        self.assertEqual(len(manifest), 914)
        loader = exporter.load_translation_record

        def snapshot_record(c, ch, v, candidate=False):
            if c != 'PRO':
                return loader(c, ch, v)
            if candidate and (ch, v) == (30, 3):
                return self.candidate
            return historical.get((ch, v))

        with patch.object(exporter, 'load_translation_record', side_effect=snapshot_record):
            before = exporter.export_book('PRO')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
                          snapshot_record(c, ch, v, candidate=True)):
            after = exporter.export_book('PRO')
        self.assertEqual(len(before['chapters']), 31)
        self.assertEqual(len(index(before)), 915)
        a, b = index(after), index(before)
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[30, 3]])
        for preflight in (self.contract['preflight'], self.receipt['preflight']):
            self.assertEqual(preflight['chapters'], 31)
            self.assertEqual(preflight['units'], 915)
            self.assertEqual(preflight['changed_units'], [[30, 3]])
            self.assertEqual(preflight['other_verse_files'], 914)
            self.assertEqual(preflight['exported_target_notes'], 2)
            self.assertEqual(compact_sha(before), preflight['export_before_sha256'])
            self.assertEqual(compact_sha(after), preflight['export_candidate_sha256'])
            self.assertEqual(compact_sha(manifest), preflight['other_verse_manifest_sha256'])
        if self.receipt['application']['status'] == 'applied-verified':
            self.assertEqual(compact_sha(after), self.receipt['application']['export_after_sha256'])
            self.assertEqual(compact_sha(manifest),
                             self.receipt['application']['other_verse_manifest_sha256'])

    def test_exact_candidate_contract_receipt_pins_and_applied_verified_flags(self):
        r, c = self.receipt, self.contract
        candidate_sha = sha((ROOT / CANDIDATE).read_bytes())
        contract_sha = sha((ROOT / CONTRACT).read_bytes())
        serialized = yaml.safe_dump(self.candidate, allow_unicode=True,
                                    sort_keys=False, width=1000).encode()
        yaml_sha = sha(serialized)
        self.assertEqual(candidate_sha, '9ea7afbc39c60c2253c761727f0ac34d65df3533571834aad30733b2e7b78da6')
        self.assertEqual(contract_sha, 'fc94b1a39fa20c19525c330b10ca31cf13d64a0db01fd0cacba99984938066e0')
        self.assertEqual((ROOT / TARGET).read_bytes(), serialized)
        for record in (r, c):
            self.assertEqual(record['baseline_revision'], BASE)
            self.assertEqual(record['target'], 'PRO.30.3')
            self.assertEqual(record['baseline_yaml_sha256'], sha(self.raw))
            self.assertEqual(record['candidate'], CANDIDATE)
            self.assertEqual(record['candidate_sha256'], candidate_sha)
            self.assertEqual(record['candidate_yaml_sha256'], yaml_sha)
            self.assertEqual(record['preflight']['candidate_sha256'], candidate_sha)
            self.assertEqual(record['preflight']['candidate_yaml_sha256'], yaml_sha)
            for flag in ('schema_valid', 'source_generation_preserved',
                         'marker_free_english_unchanged', 'eight_archives_exact'):
                self.assertIs(record['preflight'][flag], True)
            self.assertIs(record['preflight']['canonical_written'], False)
        self.assertEqual(r['canonical_target'], TARGET)
        self.assertEqual(r['reader_contract'], CONTRACT)
        self.assertEqual(r['reader_contract_sha256'], contract_sha)
        self.assertEqual(r['preflight']['pins'], c['pins'])
        self.assertEqual(c['preflight']['pins'], c['pins'])
        for path, digest in c['pins'].items():
            # The frozen review used the baseline method, not future edits.
            # All non-method evidence and current application stay live.
            raw = (subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
                   if path == 'docs/TEXTUAL_ADJUDICATION_METHOD.md'
                   else (ROOT / path).read_bytes())
            self.assertEqual(sha(raw), digest, path)
        self.assertEqual(c['source_record_sha256'], c['pins'][c['source_record']])
        for review in (r['review'], c['review']):
            self.assertIs(review['source_priority_reopened'], False)
            self.assertIs(review['repeat_until_agreement'], False)
        self.assertIs(c['review']['canonical_write_authorized_by_this_contract'], False)
        self.assertEqual(r['review']['status'], 'pass')
        self.assertEqual(r['review']['candidate_sha256'], candidate_sha)
        self.assertEqual(r['review']['candidate_yaml_sha256'], yaml_sha)
        self.assertEqual(r['review']['reader_contract_sha256'], contract_sha)
        self.assertEqual(r['application']['status'], 'applied-verified')
        self.assertIs(r['application']['canonical_written'], True)
        self.assertEqual(r['application']['changed_units'], [[30, 3]])
        self.assertEqual(r['application']['candidate_yaml_sha256'], yaml_sha)
        self.assertIs(r['application']['deployed_reader_verified'], False)


if __name__ == '__main__':
    unittest.main()
