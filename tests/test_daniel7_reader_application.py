"""Exact reader application checks; not proof of original source priority."""
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
BASE = '9e4ca5ad3da4ae569e5042fe462c7ac10998440b'
RECEIPT = ROOT / 'sources/textual_restoration/applications/daniel7_13_14_reader.2026-10-10.v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


class Daniel7ReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(RECEIPT.read_text())
        cls.units = cls.receipt['units']
        cls.raw = {v: subprocess.check_output(['git', 'show', f"{BASE}:{u['target']}"],
                                              cwd=ROOT) for v, u in cls.units.items()}
        cls.before = {v: yaml.safe_load(raw) for v, raw in cls.raw.items()}
        cls.candidates = {v: json.loads((ROOT / u['candidate']).read_text())
                          for v, u in cls.units.items()}
        cls.current = {v: yaml.safe_load((ROOT / u['target']).read_text())
                       for v, u in cls.units.items()}
        cls.contract = json.loads((ROOT / cls.receipt['reader_contract']).read_text())

    def test_complete_records_schema_source_generation_and_exact_main_change(self):
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        clean = lambda text: re.sub(r'\[[a-z]\]', '', text)
        self.assertEqual(set(self.units), {'13', '14'})
        for v, record in self.current.items():
            validator.validate(record)
            self.assertEqual(record, self.candidates[v])
            self.assertEqual(record['id'], f'DAN.7.{v}')
            for field in ('source', 'ai_draft'):
                self.assertEqual(record[field], self.before[v][field])
            self.assertEqual(record['translation']['philosophy'],
                             self.before[v]['translation']['philosophy'])
        old13 = clean(self.before['13']['translation']['text'])
        old14 = clean(self.before['14']['translation']['text'])
        new14 = clean(self.current['14']['translation']['text'])
        self.assertEqual(clean(self.current['13']['translation']['text']), old13)
        old_clause = 'that all peoples, nations, and languages should serve him'
        new_clause = 'and all peoples, nations, and languages will serve him'
        self.assertEqual(old14.count(old_clause), 1)
        self.assertEqual(new14, old14.replace(old_clause, new_clause))
        self.assertEqual(old14, self.contract['english14_candidates']['B'])
        self.assertEqual(new14, self.contract['english14_candidates']['A'])

    def test_seven_notes_have_true_anchors_and_qualified_alternatives(self):
        markers = {'13': list('abcd'), '14': list('abc')}
        anchors = {'13': ['clouds of heaven[a]', 'one like a son of man[b]',
                          'to the Ancient of Days[c]', 'they brought him near before him[d]'],
                   '14': ['languages[a]', 'will serve him[b][c]']}
        self.assertEqual(sum(len(r['translation']['footnotes']) for r in self.current.values()), 7)
        for v, record in self.current.items():
            tr = record['translation']
            self.assertEqual(re.findall(r'\[([a-z])\]', tr['text']), markers[v])
            self.assertEqual([n['marker'] for n in tr['footnotes']], markers[v])
            self.assertEqual(audit_footnotes.audit_one(ROOT / self.units[v]['target'])['status'], 'ok')
            for anchor in anchors[v]:
                self.assertIn(anchor, tr['text'])
        a = self.current['13']['translation']['footnotes']
        b = self.current['14']['translation']['footnotes']
        for phrase in ('Aramaic', 'with the clouds', 'selected Rahlfs–Hanhart2006 Old Greek',
                       'upon the clouds', 'versional contrast'):
            self.assertIn(phrase, a[0]['text'])
        for phrase in ('one like a human being', 'comparative', 'does not by itself name'):
            self.assertIn(phrase, a[1]['text'])
        for phrase in ('selected Rahlfs–Hanhart2006 Old Greek', 'as/like',
                       'subject and relation', 'uncertain', "NETS's Old Greek", 'destination',
                       'not a uniform reading', 'earliest wording remains unresolved'):
            self.assertIn(phrase, a[2]['text'])
        for phrase in ('unnamed plural agents', 'they brought him near', 'Theodotion',
                       'passive presentation', 'Old Greek', 'attendants present'):
            self.assertIn(phrase, a[3]['text'])
        for phrase in ('Literally', 'languages', 'people who speak them'):
            self.assertIn(phrase, b[0]['text'])
        for phrase in ('should serve him', 'purpose or intended result', 'and',
                       'contextual rendering', "not the verb's only possible force"):
            self.assertIn(phrase, b[1]['text'])
        for phrase in ('worship him', 'Daniel 3 and 6', 'God or gods',
                       'religious resonance', 'ordinary service', "recipient's identity"):
            self.assertIn(phrase, b[2]['text'])
        self.assertNotIn("Daniel's other uses", b[2]['text'])

    def test_seven_archives_exact_old_revisions_preserved_and_approval_not_transferred(self):
        fields = ['status', 'translation', 'lexical_decisions', 'theological_decisions',
                  'revision_pass', 'cross_check', 'ai_draft']
        for v, record in self.current.items():
            old = self.before[v]
            history = record['review_history']
            self.assertEqual([h['field'] for h in history], fields)
            self.assertEqual({h['field']: h['value'] for h in history}, {f: old[f] for f in fields})
            self.assertTrue(all(h['archived_from_baseline_sha256'] == sha(self.raw[v]) and
                                h['certifies_this_candidate'] is False for h in history))
            self.assertEqual(record['revisions'][:-1], old.get('revisions', []))
            self.assertEqual(len(old.get('revisions', [])), 0)
            self.assertEqual(record['revisions'][-1]['from'], old['translation']['text'])
            self.assertEqual(record['revisions'][-1]['to'], record['translation']['text'])
            self.assertEqual(record['status'], 'draft')
            self.assertEqual(record['cross_check'], {'status': 'needs_review'})
            self.assertNotIn('revision_pass', record)

    def test_rationale_matches_aramaic_and_bounded_application_scope(self):
        lex = {v: {d['source_word']: d for d in r['lexical_decisions']}
               for v, r in self.current.items()}
        for phrase in ('participle', 'Aramaic הוה auxiliary', 'ongoing past observation',
                       'not the Hebrew היה construction'):
            self.assertIn(phrase, lex['13']['חָזֵה הֲוֵית']['rationale'])
        self.assertEqual(lex['13']['הַקְרְבוּהִי']['chosen'], 'they brought him near')
        for phrase in ('plural masculine agents', 'singular masculine object'):
            self.assertIn(phrase, lex['13']['הַקְרְבוּהִי']['rationale'])
        self.assertEqual(lex['14']['יִפְלְחוּן']['chosen'], 'will serve him')
        self.assertIn('should serve him', lex['14']['יִפְלְחוּן']['alternatives'])
        for phrase in ('future, durative and modal', 'preferred moderately', '7:27',
                       'coordinating conjunction', 'remains defensible', 'religious resonance',
                       'Daniel 3 and 6 plh uses'):
            self.assertIn(phrase, lex['14']['יִפְלְחוּן']['rationale'])
        self.assertNotIn("Daniel's other plh uses", lex['14']['יִפְלְחוּן']['rationale'])
        theology = self.current['14']['theological_decisions'][0]['rationale']
        self.assertIn('supported by Daniel 3 and 6', theology)
        self.assertNotIn("Daniel's other uses", theology)
        changed = {'13': {'חָזֵה הֲוֵית', 'עִם עֲנָנֵי שְׁמַיָּא', 'כְּבַר אֱנָשׁ',
                           'וְעַד עַתִּיק יוֹמַיָּא', 'הַקְרְבוּהִי'},
                   '14': {'שָׁלְטָן', 'יִפְלְחוּן'}}
        for v, record in self.current.items():
            for old in self.before[v]['lexical_decisions']:
                if old['source_word'] not in changed[v]:
                    self.assertEqual(lex[v][old['source_word']], old)
            self.assertIn('unresolved', record['textual_comparison']['historical_priority'])
            for flag in ('fresh_image_reading', 'novel_reading_demonstrated', 'canon_changed',
                         'publication_approved'):
                self.assertIs(record['textual_comparison'][flag], False)
            for flag in ('source_changed', 'original_meaning_settled', 'publication_approved'):
                self.assertIs(record['source_audit'][flag], False)
            self.assertIs(record['source_audit']['marker_free_english_changed'], v == '14')
            self.assertIs(record['source_audit']['no_fresh_halot_consultation'], True)

    def test_current_full_reader_export_isolates_two_units_and_keeps_seven_notes(self):
        after = exporter.export_book('DAN')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
            self.before[str(v)] if c == 'DAN' and ch == 7 and str(v) in self.before else loader(c, ch, v)):
            before = exporter.export_book('DAN')
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 12)
        self.assertEqual(len(a), 357)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[7, 13], [7, 14]])
        for v in self.current:
            self.assertEqual(a[(7, int(v))]['footnotes'], self.current[v]['translation']['footnotes'])
        self.assertEqual(sum(len(a[(7, int(v))]['footnotes']) for v in self.current), 7)

    def test_historical_export_digests_and_non_target_manifest(self):
        # Validate the receipt's immutable snapshot separately from today's book.
        archive = subprocess.check_output(['git', 'archive', BASE, 'translation/ot/daniel'], cwd=ROOT)
        historical, manifest = {}, {}
        targets = {u['target'] for u in self.units.values()}
        with tarfile.open(fileobj=io.BytesIO(archive)) as snapshot:
            for member in snapshot.getmembers():
                if member.isfile() and member.name.endswith('.yaml'):
                    raw = snapshot.extractfile(member).read()
                    p = Path(member.name)
                    historical[(int(p.parent.name), int(p.stem))] = yaml.safe_load(raw)
                    if member.name not in targets:
                        manifest[member.name] = sha(raw)
        self.assertEqual(len(historical), 357)
        self.assertEqual(len(manifest), 355)
        manifest_sha = compact_sha(manifest)
        for section in ('preflight', 'review', 'application'):
            self.assertEqual(manifest_sha, self.receipt[section]['other_verse_manifest_sha256'])
        loader = exporter.load_translation_record

        def snapshot_record(c, ch, v, candidate=False):
            if c != 'DAN':
                return loader(c, ch, v)
            if candidate and ch == 7 and str(v) in self.candidates:
                return self.candidates[str(v)]
            return historical.get((ch, v))

        with patch.object(exporter, 'load_translation_record', side_effect=snapshot_record):
            before = exporter.export_book('DAN')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
            snapshot_record(c, ch, v, candidate=True)):
            after = exporter.export_book('DAN')
        self.assertEqual(len(before['chapters']), 12)
        self.assertEqual(len(index(before)), 357)
        for section in ('preflight', 'review'):
            self.assertEqual(compact_sha(before), self.receipt[section]['export_before_sha256'])
            self.assertEqual(compact_sha(after), self.receipt[section]['export_candidate_sha256'])
        self.assertEqual(compact_sha(after), self.receipt['application']['export_after_sha256'])
        prior = self.receipt['review_history'][0]
        original14 = json.loads((ROOT / prior['candidate14']).read_text())
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
            original14 if c == 'DAN' and ch == 7 and v == 14 else
            snapshot_record(c, ch, v, candidate=True)):
            original_export = exporter.export_book('DAN')
        self.assertEqual(compact_sha(before), prior['preflight']['export_before_sha256'])
        self.assertEqual(compact_sha(original_export), prior['preflight']['export_candidate_sha256'])
        self.assertEqual(manifest_sha, prior['preflight']['other_verse_manifest_sha256'])

    def test_receipt_pins_exact_json_yaml_contracts_and_narrow_approval(self):
        r = self.receipt
        self.assertEqual(r['baseline_revision'], BASE)
        self.assertEqual(self.contract['baseline_revision'], BASE)
        for v, u in self.units.items():
            self.assertEqual(u['target'], f'translation/ot/daniel/007/0{v}.yaml')
            version = 'v1' if v == '13' else 'v2'
            self.assertEqual(u['candidate'],
                             f'sources/textual_restoration/candidates/daniel7_{v}_reader.2026-10-10.{version}.json')
            self.assertEqual(sha(self.raw[v]), u['baseline_sha256'])
            self.assertEqual(u['baseline_sha256'], self.contract['baseline_yaml_sha256s'][v])
            self.assertEqual(sha((ROOT / u['candidate']).read_bytes()), u['candidate_sha256'])
            serialized = yaml.safe_dump(self.candidates[v], allow_unicode=True,
                                        sort_keys=False, width=1000).encode()
            self.assertEqual(sha(serialized), u['candidate_yaml_sha256'])
            self.assertEqual((ROOT / u['target']).read_bytes(), serialized)
            self.assertEqual(r['review']['candidate_sha256s'][v], u['candidate_sha256'])
            self.assertEqual(r['review']['candidate_yaml_sha256s'][v], u['candidate_yaml_sha256'])
            self.assertEqual(r['application']['yaml_sha256s'][v], u['candidate_yaml_sha256'])
        for field in ('reader_contract', 'source_contract', 'source_assessment', 'english_assessment'):
            self.assertEqual(sha((ROOT / r[field]).read_bytes()), r[field + '_sha256'])
        for field in ('source_contract', 'source_assessment'):
            self.assertEqual(r[field], self.contract[field])
            self.assertEqual(r[field + '_sha256'], self.contract[field + '_sha256'])
        for path, field in (('schema/verse.schema.json', 'schema_sha256'),
                            ('sources/ot/wlc/Dan.xml', 'source_xml_sha256'),
                            ('docs/TEXTUAL_ADJUDICATION_METHOD.md', 'method_sha256'),
                            ('DOCTRINE.md', 'doctrine_sha256')):
            self.assertEqual(sha((ROOT / path).read_bytes()), self.contract[field])
        self.assertEqual(r['schema_sha256'], self.contract['schema_sha256'])
        english = json.loads((ROOT / r['english_assessment']).read_text())
        self.assertEqual(english['reader_contract_sha256'], r['reader_contract_sha256'])
        self.assertEqual(r['review']['reader_contract_sha256'], r['reader_contract_sha256'])
        self.assertEqual(r['review']['baseline_revision'], BASE)
        self.assertEqual(r['review']['status'], 'pass')
        self.assertIs(r['review']['source_priority_reopened'], False)
        self.assertIs(r['review']['repeat_until_agreement'], False)
        self.assertEqual(r['application']['status'], 'applied-verified')
        self.assertIs(r['application']['canonical_written'], True)
        self.assertEqual(r['application']['changed_units'], [[7, 13], [7, 14]])
        self.assertEqual(r['preflight']['changed_units'], [[7, 13], [7, 14]])
        self.assertEqual(r['preflight']['other_verse_files'], 355)
        self.assertIs(r['application']['deployed_reader_verified'], False)
        self.assertIs(r['decision']['marker_free_main_english_changed'], True)
        self.assertEqual(r['decision']['english_changed_verses'], [14])
        for flag in ('source_changed', 'original_priority_settled', 'original_meaning_settled',
                     'novel_reading_demonstrated', 'canon_changed', 'publication_approved'):
            self.assertIs(r['decision'][flag], False)
        self.assertEqual(len(r['review_history']), 1)
        prior = r['review_history'][0]
        self.assertEqual(prior['status'], 'needs-correction')
        for flag in ('canonical_applied', 'source_priority_reopened', 'repeat_until_agreement'):
            self.assertIs(prior[flag], False)
        self.assertEqual(prior['candidate14'],
                         'sources/textual_restoration/candidates/daniel7_14_reader.2026-10-10.v1.json')
        old_raw = (ROOT / prior['candidate14']).read_bytes()
        self.assertEqual(sha(old_raw),
                         '7b386edf75b37d21bf3c5d8c9aeacb756e3db0dcbb6a0205651d35344c93e2d2')
        original14 = json.loads(old_raw)
        old_yaml = yaml.safe_dump(original14, allow_unicode=True, sort_keys=False, width=1000).encode()
        self.assertEqual(prior['candidate_sha256s']['14'], sha(old_raw))
        self.assertEqual(prior['candidate_yaml_sha256s']['14'], sha(old_yaml))
        self.assertEqual(prior['candidate_sha256s']['13'], self.units['13']['candidate_sha256'])
        self.assertEqual(prior['candidate_yaml_sha256s']['13'], self.units['13']['candidate_yaml_sha256'])
        self.assertIn('ambiguous7:27 recipient', prior['issue'])
        self.assertIn('Daniel3/6', prior['correction'])
        self.assertIn("Daniel's other uses", original14['translation']['footnotes'][2]['text'])
        # The defect repair changes only the three overbroad evidence summaries.
        repaired = json.loads(old_raw)
        repaired['translation']['footnotes'][2]['text'] = self.candidates['14']['translation']['footnotes'][2]['text']
        repaired['lexical_decisions'][7]['rationale'] = self.candidates['14']['lexical_decisions'][7]['rationale']
        repaired['theological_decisions'][0]['rationale'] = self.candidates['14']['theological_decisions'][0]['rationale']
        self.assertEqual(repaired, self.candidates['14'])


if __name__ == '__main__':
    unittest.main()
