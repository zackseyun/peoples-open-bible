"""Scoped disclosure checks; not historical priority or canon certification."""
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
BASE = '330d06e9eed7c301dde580f51338e786daa5ffac'
TARGET = 'translation/ot/zephaniah/003/017.yaml'
CANDIDATE = 'sources/textual_restoration/candidates/zephaniah3_17_reader.2026-10-10.v1.json'
CONTRACT = 'sources/textual_restoration/comparisons/zephaniah3_17_reader_contract.2026-10-10.v1.json'
CONTRACT_SHA = 'd84dba0cd4932feb2097365bfee4ef54761e41393b4ae2abcfcce365eaf6092f'
RECEIPT = 'sources/textual_restoration/applications/zephaniah3_17_reader.2026-10-10.v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


class Zephaniah317ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = subprocess.check_output(['git', 'show', f'{BASE}:{TARGET}'], cwd=ROOT)
        cls.before = yaml.safe_load(cls.raw)
        cls.candidate = json.loads((ROOT / CANDIDATE).read_text())
        cls.contract = json.loads((ROOT / CONTRACT).read_text())

    def test_complete_schema_exact_source_and_marker_free_english(self):
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.candidate)
        self.assertEqual(sha((ROOT / CONTRACT).read_bytes()), CONTRACT_SHA)
        self.assertEqual(sha(self.raw), self.contract['baseline_yaml_sha256'])
        self.assertEqual(sha((ROOT / CANDIDATE).read_bytes()), self.contract['candidate_sha256'])
        self.assertEqual(sha(yaml.safe_dump(self.candidate, allow_unicode=True,
                                          sort_keys=False, width=1000).encode()),
                         self.contract['candidate_yaml_sha256'])
        for field in ('source', 'ai_draft'):
            self.assertEqual(self.candidate[field], self.before[field])
        clean = lambda t: re.sub(r'\[[a-z]\]', '', t)
        self.assertEqual(clean(self.candidate['translation']['text']),
                         clean(self.before['translation']['text']))
        self.assertEqual(self.candidate['translation']['philosophy'],
                         self.before['translation']['philosophy'])
        self.assertEqual(set(self.candidate) - set(self.before),
                         {'review_history', 'revisions', 'source_audit', 'textual_comparison'})
        self.assertEqual(set(self.before) - set(self.candidate), {'revision_pass'})

    def test_correct_anchors_and_two_different_evidence_types(self):
        tr = self.candidate['translation']
        self.assertIn('in his love[a][b];', tr['text'])
        self.assertNotIn('midst[a]', tr['text'])
        self.assertEqual(re.findall(r'\[([a-z])\]', tr['text']), ['a', 'b'])
        a, b = tr['footnotes']
        self.assertEqual([a['marker'], b['marker']], ['a', 'b'])
        self.assertEqual(a['reason'], 'alternative_reading')
        self.assertEqual(b['reason'], 'textual_variant')
        for phrase in ('quiet you', 'unexpressed', 'possible', 'provisionally'):
            self.assertIn(phrase, a['text'])
        for phrase in ('Selected Greek editions', 'renew you', 'versional alternative',
                       'not an ordinary gloss', 'published Murabbaʿat',
                       'historical priority remains unresolved'):
            self.assertIn(phrase, b['text'])

    def test_exact_archives_one_lexical_entry_and_qualified_audit(self):
        fields = ['status', 'translation', 'lexical_decisions', 'theological_decisions',
                  'revision_pass', 'cross_check', 'ai_draft']
        history = self.candidate['review_history']
        self.assertEqual([h['field'] for h in history], fields)
        self.assertEqual({h['field']: h['value'] for h in history},
                         {k: self.before[k] for k in fields})
        self.assertTrue(all(h['archived_from_baseline_sha256'] == sha(self.raw)
                            and h['certifies_this_candidate'] is False for h in history))
        old, new = self.before['lexical_decisions'], self.candidate['lexical_decisions']
        self.assertEqual(len(old), len(new))
        self.assertEqual([i for i, (a, b) in enumerate(zip(old, new)) if a != b], [7])
        for phrase in ('Job11:3', 'not grammatically forbidden', 'not the whole pointed phrase',
                       'No fresh HALOT consultation'):
            self.assertIn(phrase, new[7]['rationale'])
        self.assertEqual(len(self.candidate['theological_decisions']), 1)
        self.assertIn('without selecting by pastoral desirability',
                      self.candidate['theological_decisions'][0]['rationale'])
        self.assertEqual(self.candidate['status'], 'draft')
        self.assertEqual(self.candidate['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', self.candidate)
        self.assertEqual(self.candidate['revisions'][0]['category'], 'reader_disclosure')
        for flag in ('source_changed', 'marker_free_english_changed', 'original_priority_settled',
                     'human_or_scholar_review', 'publication_approved'):
            self.assertIs(self.candidate['source_audit'][flag], False)
        self.assertIs(self.candidate['source_audit']['no_fresh_halot_consultation'], True)

    def test_pinned_source_comparison_limits_not_manuscript_votes(self):
        for p, expected in self.contract['preflight']['pins'].items():
            # Method history is immutable; source evidence stays live.
            raw = (subprocess.check_output(['git', 'show', f'{BASE}:{p}'], cwd=ROOT)
                   if p == 'docs/TEXTUAL_ADJUDICATION_METHOD.md'
                   else (ROOT / p).read_bytes())
            self.assertEqual(sha(raw), expected, p)
        p = 'sources/textual_restoration/comparisons/zephaniah3_17_silence_renewal.2026-10-10.v1.json'
        comparison = json.loads((ROOT / p).read_text())
        for flag in ('source_changed', 'marker_free_english_changed', 'fresh_image_reading',
                     'novel_reading_demonstrated', 'canon_changed', 'publication_approved'):
            self.assertIs(comparison[flag], False)
        mur = comparison['controls'][1]
        self.assertEqual(mur['preserved_published_word'], 'יחריש')
        self.assertIs(mur['whole_phrase_preserved'], False)
        self.assertIs(mur['pointing_attested'], False)
        greek = comparison['controls'][5]
        self.assertIn('εὐφροσύνη', greek['apparatus_contrary_control'])
        self.assertIs(greek['unanimity_inferred'], False)
        latin = comparison['controls'][6]
        self.assertEqual(latin['excerpt'], 'silebit in dilectione tua')
        self.assertIs(latin['full_phrase_agreement_with_mt'], False)
        self.assertEqual(comparison['morphological_screen']['wordforms'], 39)
        self.assertEqual(comparison['morphological_screen']['verses'], 35)
        self.assertIs(comparison['morphological_screen']['quiet_you_impossible'], False)
        self.assertIs(self.contract['repeat_until_agreement'], False)

    def test_historical_full_book_overlay_and_non_target_manifest(self):
        archive = subprocess.check_output(['git', 'archive', BASE, 'translation/ot/zephaniah'], cwd=ROOT)
        records, manifest = {}, {}
        with tarfile.open(fileobj=io.BytesIO(archive)) as snapshot:
            for m in snapshot.getmembers():
                if m.isfile() and m.name.endswith('.yaml'):
                    raw = snapshot.extractfile(m).read()
                    p = Path(m.name)
                    records[(int(p.parent.name), int(p.stem))] = yaml.safe_load(raw)
                    if m.name != TARGET:
                        manifest[m.name] = sha(raw)
        loader = exporter.load_translation_record

        def historical(c, ch, v, overlay=False):
            if c == 'ZEP':
                return self.candidate if overlay and (ch, v) == (3, 17) else records.get((ch, v))
            return loader(c, ch, v)

        with patch.object(exporter, 'load_translation_record', side_effect=historical):
            before = exporter.export_book('ZEP')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda *args:
                          historical(*args, overlay=True)):
            after = exporter.export_book('ZEP')
        a, b = index(before), index(after)
        self.assertEqual(len(before['chapters']), 3)
        self.assertEqual(len(a), 53)
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[3, 17]])
        preflight = self.contract['preflight']
        self.assertEqual(compact_sha(before), preflight['export_before_sha256'])
        self.assertEqual(compact_sha(after), preflight['export_candidate_sha256'])
        self.assertEqual(len(manifest), 52)
        self.assertEqual(compact_sha(manifest), preflight['other_verse_manifest_sha256'])
        self.assertEqual(b[(3, 17)]['footnotes'], self.candidate['translation']['footnotes'])

    def test_exact_application_current_export_and_review_receipt(self):
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(sha((ROOT / TARGET).read_bytes()), self.contract['candidate_yaml_sha256'])
        self.assertEqual(yaml.safe_load((ROOT / TARGET).read_text()), self.candidate)
        self.assertEqual(receipt['reader_contract_sha256'], CONTRACT_SHA)
        self.assertEqual(receipt['review']['status'], 'pass')
        self.assertIs(receipt['review']['source_priority_approved'], False)
        self.assertIs(receipt['review']['additional_english_preference_vote'], False)
        self.assertIs(receipt['application']['deployed_reader_verified'], False)
        after = exporter.export_book('ZEP')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
                          self.before if c == 'ZEP' and (ch, v) == (3, 17) else loader(c, ch, v)):
            before = exporter.export_book('ZEP')
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 3)
        self.assertEqual(len(a), 53)
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[3, 17]])
        self.assertEqual(a[(3, 17)]['footnotes'], self.candidate['translation']['footnotes'])
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)['status'], 'ok')


if __name__ == '__main__':
    unittest.main()
