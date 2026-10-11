"""One attested qere application; not proof of original wording or publication."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes, wlc
from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
BASE = '0dd2177731960ad1e4fa324865b91c4366204807'
TARGET = 'translation/ot/psalms/073/010.yaml'
CANDIDATE = 'sources/textual_restoration/candidates/psalm73_10_written_read.2026-10-10.v1.json'
CONTRACT = 'sources/textual_restoration/comparisons/psalm73_10_application_contract.2026-10-10.v1.json'
CONTRACT_SHA = '795bed705ff88f3b7ffe0b1c9d724128b7d002bc26012b2be74dd7f54165ca6c'
RECEIPT = 'sources/textual_restoration/applications/psalm73_10_written_read.2026-10-10.v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


class Psalm7310ApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = subprocess.check_output(['git', 'show', f'{BASE}:{TARGET}'], cwd=ROOT)
        cls.before = yaml.safe_load(cls.raw)
        cls.candidate = json.loads((ROOT / CANDIDATE).read_text())
        cls.contract = json.loads((ROOT / CONTRACT).read_text())

    def test_exact_candidate_schema_and_one_actual_adjacent_qere(self):
        c, contract = self.candidate, self.contract
        self.assertEqual(sha((ROOT / CONTRACT).read_bytes()), CONTRACT_SHA)
        self.assertEqual(sha(self.raw), contract['baseline_yaml_sha256'])
        self.assertEqual(sha((ROOT / CANDIDATE).read_bytes()), contract['candidate_sha256'])
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(c)
        raw = (ROOT / 'sources/ot/wlc/Ps.xml').read_bytes()
        self.assertEqual(sha(raw), contract['preflight']['pins']['sources/ot/wlc/Ps.xml'])
        node = ET.fromstring(raw).find(".//o:verse[@osisID='Ps.73.10']", wlc.OSIS_NS)
        words = list(node)
        written = node.find("o:w[@id='19T6R']", wlc.OSIS_NS)
        qere = words[words.index(written) + 1].find("o:rdg[@type='x-qere']/o:w", wlc.OSIS_NS)
        self.assertEqual((written.text, written.attrib['morph']), ('ישיב', 'HVhi3ms'))
        self.assertEqual((qere.text, qere.attrib['id'], qere.attrib['lemma'], qere.attrib['morph']),
                         ('יָשׁ֣וּב', '19h5B', '7725', 'HVqi3ms'))
        self.assertEqual(c['source']['text'], self.before['source']['text'].replace(' ישיב ', ' יָשׁ֣וּב ', 1))
        self.assertEqual(c['source']['edition'], 'WLC')
        self.assertIn('selected Masoretic reading form', c['source']['note'])
        self.assertIn('not newly deciphered', c['source']['note'])

    def test_scoped_english_notes_and_exact_noncertifying_history(self):
        c, old = self.candidate, self.before
        self.assertEqual(c['translation']['text'],
                         'Therefore his people return here[a], and abundant waters are drained for them[b].')
        self.assertEqual(c['translation']['footnotes'][1], old['translation']['footnotes'][1])
        note = c['translation']['footnotes'][0]
        self.assertEqual(note['reason'], 'textual_variant')
        for phrase in ('reading form', 'written form', 'he brings', 'uncertain', 'Earliest wording remains unresolved'):
            self.assertIn(phrase, note['text'])
        self.assertEqual(c['ai_draft'], old['ai_draft'])
        self.assertEqual(c['revisions'][:-1], old['revisions'])
        archives = c['review_history']
        self.assertEqual([h['field'] for h in archives], self.contract['archive_fields'])
        self.assertEqual({h['field']: h['value'] for h in archives},
                         {f: old[f] for f in self.contract['archive_fields']})
        self.assertTrue(all(h['certifies_this_candidate'] is False
                            and h['archived_from_baseline_sha256'] == sha(self.raw) for h in archives))
        self.assertEqual(c['status'], 'draft')
        self.assertEqual(c['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', c)
        self.assertEqual(c['theological_decisions'], old['theological_decisions'])
        self.assertEqual([i for i, (a, b) in enumerate(zip(old['lexical_decisions'], c['lexical_decisions'])) if a != b], [1])

    def test_evidence_limits_and_frozen_inputs(self):
        for path, expected in self.contract['preflight']['pins'].items():
            if path.endswith('genizah_genesis_b7_14_followup.v1.json'):
                continue  # User-owned untracked local file is deliberately not shipped.
            # This is the method used at review time, not a claim that the
            # evolving live method has never changed. Evidence stays live.
            raw = (subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
                   if path == 'docs/TEXTUAL_ADJUDICATION_METHOD.md'
                   else (ROOT / path).read_bytes())
            self.assertEqual(sha(raw), expected, path)
        comparison = json.loads((ROOT / 'sources/textual_restoration/comparisons/psalm73_10_written_read.2026-10-10.v1.json').read_text())
        self.assertEqual(comparison['DSS_screen']['target_hits'], 0)
        self.assertIn('not attested omission', comparison['DSS_screen']['inference'])
        self.assertFalse(comparison['acquisition_design']['repeat_until_agreement'])
        for flag in ('source_interpretation_settled', 'novel_reading_demonstrated', 'canon_changed', 'publication_approved'):
            self.assertFalse(comparison['decision'][flag])
        self.assertFalse(comparison['decision']['second_clause_changed'])
        self.assertIn('regularize', comparison['arguments']['qere_objection'])

    def test_corrupt_historical_method_cannot_satisfy_frozen_pin(self):
        original = subprocess.check_output

        def corrupt_method(args, **kwargs):
            raw = original(args, **kwargs)
            return raw + b'corrupt' if args[-1] == f'{BASE}:docs/TEXTUAL_ADJUDICATION_METHOD.md' else raw

        with patch.object(subprocess, 'check_output', side_effect=corrupt_method):
            with self.assertRaisesRegex(AssertionError, 'docs/TEXTUAL_ADJUDICATION_METHOD.md'):
                self.test_evidence_limits_and_frozen_inputs()

    def test_changed_live_evidence_cannot_hide_behind_historical_method(self):
        original = Path.read_bytes

        def corrupt_source(path):
            raw = original(path)
            return raw + b'corrupt' if path == ROOT / 'sources/ot/wlc/Ps.xml' else raw

        with patch.object(Path, 'read_bytes', new=corrupt_source):
            with self.assertRaisesRegex(AssertionError, 'sources/ot/wlc/Ps.xml'):
                self.test_evidence_limits_and_frozen_inputs()

    def test_historical_complete_normalized_psalms_export(self):
        archive = subprocess.check_output(['git', 'archive', BASE, 'translation/ot/psalms'], cwd=ROOT)
        files, manifest = {}, {}
        with tarfile.open(fileobj=io.BytesIO(archive)) as snapshot:
            for member in snapshot.getmembers():
                if member.isfile() and member.name.endswith('.yaml'):
                    raw = snapshot.extractfile(member).read()
                    files[(ROOT / member.name).resolve()] = raw.decode()
                    if member.name != TARGET:
                        manifest[member.name] = sha(raw)
        read_text = Path.read_text

        def historical(path, *args, overlay=False, **kwargs):
            if overlay and path.resolve() == (ROOT / TARGET).resolve():
                return yaml.safe_dump(self.candidate, allow_unicode=True, sort_keys=False, width=100000)
            return files.get(path.resolve()) if path.resolve() in files else read_text(path, *args, **kwargs)

        with patch.object(Path, 'read_text', new=historical):
            before = exporter.export_book('PSA')
        with patch.object(Path, 'read_text', new=lambda path, *a, **kw: historical(path, *a, overlay=True, **kw)):
            after = exporter.export_book('PSA')
        index = lambda b: {(c['chapter'], v['verse']): v for c in b['chapters'] for v in c['verses']}
        a, b = index(before), index(after)
        self.assertEqual(len(before['chapters']), 150)
        self.assertEqual(len(a), 2578)
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[73, 10]])
        self.assertEqual(compact_sha(before), self.contract['preflight']['export_before_sha256'])
        self.assertEqual(compact_sha(after), self.contract['preflight']['export_candidate_sha256'])
        self.assertEqual(len(manifest), 2577)
        self.assertEqual(compact_sha(manifest), self.contract['preflight']['other_verse_manifest_sha256'])
        self.assertTrue(a[(73, 0)]['is_superscription'])
        self.assertEqual(a[(73, 0)], b[(73, 0)])
        self.assertEqual(a[(145, 13)], b[(145, 13)])
        self.assertEqual(b[(73, 10)]['footnotes'], self.candidate['translation']['footnotes'])

    def test_exact_application_and_qualified_receipt(self):
        actual = (ROOT / TARGET).read_bytes()
        self.assertEqual(sha(actual), self.contract['candidate_yaml_sha256'])
        self.assertEqual(yaml.safe_load(actual), self.candidate)
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)['status'], 'ok')
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(receipt['candidate_sha256'], self.contract['candidate_sha256'])
        self.assertEqual(receipt['contract_sha256'], CONTRACT_SHA)
        self.assertEqual(receipt['review']['candidate_sha256'], self.contract['candidate_sha256'])
        self.assertTrue(receipt['review']['verdict'].startswith('PASS for exact full-record provisional'))
        self.assertTrue(receipt['application']['candidate_matches'])
        self.assertFalse(receipt['application']['deployed_reader_verified'])
        self.assertFalse(receipt['decision']['source_interpretation_settled'])
        self.assertFalse(receipt['decision']['publication_approved'])
        exported = exporter._export_record_verse(10, self.candidate)
        self.assertEqual(exported['text'], self.candidate['translation']['text'])
        self.assertEqual(exported['footnotes'], self.candidate['translation']['footnotes'])


if __name__ == '__main__':
    unittest.main()
