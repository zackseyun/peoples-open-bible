"""Current Psalm145 source/English binding; not historical-priority proof."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator, ValidationError

from tools import export_mobile_bible as exporter
from tools.textual_restoration import critical_verse
from tools.textual_restoration import reviewed_critical_source
from tools.textual_restoration.verify_source_composition import normalized

ROOT = Path(__file__).resolve().parents[1]
BASE = '6b9337f796dedecd4794b09451f712b9cfb3f6f8'
PREFIX = 'sources/textual_restoration/applications/'
PATH13 = 'translation/ot/psalms/145/013.yaml'
PATH17 = 'translation/ot/psalms/145/017.yaml'
TRUST = {
    'trusted_source_sha256': '2f27ded084a69914c12d65ced77e656d89bf8382e73dabb6501dc5ce3e48077d',
    'trusted_review_sha256': 'd3ce234ad5bf82e4e37679146461a5912776a63afd6ba82cf20afd7b76433e27',
    'trusted_composition_sha256': '21910b84761fc5e5bd3fe771eb5001dd066b4f1cb30e09488cb6ddd22e6aee21',
}


def old_record(path):
    raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{BASE}:{path}'])
    return yaml.safe_load(raw), hashlib.sha256(raw).hexdigest()


class Psalm145CriticalApplicationTests(unittest.TestCase):
    def setUp(self):
        self.thirteen = yaml.safe_load((ROOT / PATH13).read_text())
        self.seventeen = yaml.safe_load((ROOT / PATH17).read_text())

    def test_full_critical_record_matches_externally_reviewed_candidate(self):
        result = critical_verse.validate(self.thirteen, **TRUST)
        self.assertTrue(result['full_critical_verse_verified'])
        self.assertFalse(result['publication_approved'])
        self.assertEqual(self.thirteen['source']['edition'], 'POB-critical')

    def test_original_review_policies_are_historical_not_live(self):
        original = Path.read_bytes

        def reject_live_policy(path):
            if path in {ROOT / 'docs/TEXTUAL_ADJUDICATION_METHOD.md', ROOT / 'DOCTRINE.md'}:
                raise AssertionError('Must use the original Git review policy')
            return original(path)

        with patch.object(Path, 'read_bytes', new=reject_live_policy):
            self.assertTrue(critical_verse.validate(self.thirteen, **TRUST)
                            ['full_critical_verse_verified'])

    def test_corrupt_either_historical_policy_cannot_satisfy_original_review(self):
        original = subprocess.run

        for name in ('docs/TEXTUAL_ADJUDICATION_METHOD.md', 'DOCTRINE.md'):
            def corrupt_policy(args, **kwargs):
                result = original(args, **kwargs)
                if args[-1] == f'{BASE}:{name}':
                    return subprocess.CompletedProcess(
                        result.args, result.returncode, result.stdout + b'corrupt', result.stderr)
                return result

            with self.subTest(path=name), patch.object(subprocess, 'run', side_effect=corrupt_policy):
                with self.assertRaisesRegex(ValueError, 'Historical review policy drift'):
                    critical_verse.validate(self.thirteen, **TRUST)

    def test_current_source_schema_is_still_enforced(self):
        original = Path.read_text

        def changed_schema(path, *args, **kwargs):
            raw = original(path, *args, **kwargs)
            if path == ROOT / reviewed_critical_source.SCHEMA:
                schema = json.loads(raw)
                schema['required'].append('new_live_schema_requirement')
                return json.dumps(schema)
            return raw

        with patch.object(Path, 'read_text', new=changed_schema):
            with self.assertRaises(ValidationError):
                critical_verse.validate(self.thirteen, **TRUST)

    def test_changed_live_review_candidate_and_evidence_still_fail(self):
        source_pin = self.thirteen['critical_source_integration']['record']
        source = json.loads((ROOT / source_pin['path']).read_text())
        provenance = source['provenance']
        review = json.loads((ROOT / provenance['editorial_review']['path']).read_text())
        composition = json.loads((ROOT / provenance['composition']['path']).read_text())
        live_paths = {source_pin['path'], provenance['editorial_review']['path'],
                      provenance['candidate']['path'], provenance['composition']['path']}
        live_paths.update(name for name in review['input_pins']
                          if name not in {PATH13, 'docs/TEXTUAL_ADJUDICATION_METHOD.md', 'DOCTRINE.md'})
        live_paths.update(pin['path'] for pin in composition['entries'][0]['evidence'])
        original = Path.read_bytes

        for name in sorted(live_paths):
            def corrupt_live(path):
                raw = original(path)
                return raw + b'corrupt' if path == ROOT / name else raw

            with self.subTest(path=name), patch.object(Path, 'read_bytes', new=corrupt_live):
                with self.assertRaisesRegex(ValueError, 'Pinned file drift'):
                    critical_verse.validate(self.thirteen, **TRUST)

    def test_exact_attested_line_and_explicit_punctuation_patch(self):
        baseline, _ = old_record(PATH13)
        mem, nun = self.thirteen['source']['text'].split('\n')
        self.assertEqual(mem, normalized(baseline['source']['text']).replace('־־׃', '׃'))
        self.assertEqual(nun, 'נאמן אלוהים בדבריו וחסיד בכול מעשיו׃')
        self.assertNotIn('יהוה', nun)
        self.assertNotIn('בכול דבריו', nun)
        self.assertNotIn('ברוך', nun)
        bundle = json.loads((ROOT / (PREFIX + 'psalm145_composition.2026-10-04.v1.json')).read_text())
        patch = bundle['entries'][0]['patches'][0]
        self.assertEqual(patch['before'], '־־׃')
        self.assertEqual(patch['after'], '׃\n' + nun)

    def test_generation_history_and_old_review_objects_are_preserved(self):
        for path, record in [(PATH13, self.thirteen), (PATH17, self.seventeen)]:
            baseline, digest = old_record(path)
            with self.subTest(path=path):
                self.assertEqual(record['ai_draft'], baseline['ai_draft'])
                history = baseline.get('revisions', [])
                self.assertEqual(record['revisions'][:len(history)], history)
                self.assertEqual(record['cross_check'], {'status': 'needs_review'})
                self.assertEqual(record['status'], 'draft')
                for key in ('cross_check', 'revision_pass', 'source_audit'):
                    archive = record['legacy_' + key]
                    self.assertEqual(archive['archived_from_baseline_sha256'], digest)
                    for field, value in baseline[key].items():
                        self.assertEqual(archive[field], value)

    def test_seventeen_keeps_hebrew_and_matches_reviewed_english(self):
        baseline, _ = old_record(PATH17)
        self.assertEqual(self.seventeen['source'], baseline['source'])
        candidate = json.loads((ROOT / (PREFIX + 'psalm145_17_candidate.2026-10-04.v1.json')).read_text())
        self.assertEqual(self.seventeen, candidate)
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.seventeen)
        self.assertIn('loyal in all his deeds', self.seventeen['translation']['text'])
        note = self.seventeen['translation']['footnotes'][0]['text']
        self.assertIn('does not establish a different Hebrew reading', note)

    def test_reader_retains_added_assertion_and_scoped_notes(self):
        for verse, record in [(13, self.thirteen), (17, self.seventeen)]:
            with self.subTest(verse=verse):
                out = exporter._export_record_verse(verse, record)
                self.assertEqual(out['text'], record['translation']['text'])
                self.assertEqual(out['footnotes'], record['translation']['footnotes'])
        text = self.thirteen['translation']['text']
        self.assertIn('God is faithful in his words and loyal[c] in all his deeds[b]', text)
        note = next(n['text'] for n in self.thirteen['translation']['footnotes'] if n['marker'] == 'b')
        for caution in ('provisionally', 'Masoretic Text lacks', 'acrostic repair', 'earliest wording is unresolved', 'blessings are not included'):
            self.assertIn(caution, note)

    def test_unreviewed_source_or_english_cannot_use_approval(self):
        for field in ('source', 'english'):
            record = copy.deepcopy(self.thirteen)
            if field == 'source':
                record['source']['text'] = record['source']['text'].replace('אלוהים', 'יהוה')
            else:
                record['translation']['text'] = record['translation']['text'].replace('in his words', 'in all his promises')
            with self.subTest(field=field), self.assertRaises(ValueError):
                critical_verse.validate(record, **TRUST)


if __name__ == '__main__':
    unittest.main()
