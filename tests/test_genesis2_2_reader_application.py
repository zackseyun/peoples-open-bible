"""Exact local English/disclosure application, not earliest-text or canon proof."""
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
BASE = 'a4a37ccad1cccdf05a9d330b221f31232c834e41'
TARGET = 'translation/ot/genesis/002/002.yaml'
CANDIDATE = 'sources/textual_restoration/candidates/genesis2_2_reader.2026-10-10.v1.json'
CONTRACT = 'sources/textual_restoration/comparisons/genesis2_2_reader_contract.2026-10-10.v1.json'
CONTRACT_SHA = '993e2038f84b85d8c5319a07ddecc845616a23a4f724db216b5190a96c78207b'
RECEIPT = 'sources/textual_restoration/applications/genesis2_2_reader.2026-10-10.v1.json'
ENGLISH_CONTRACT = 'sources/textual_restoration/comparisons/genesis2_2_english_contract.2026-10-10.v1.json'
ENGLISH_RESULT = 'sources/textual_restoration/comparisons/genesis2_2_english_result.2026-10-10.v1.json'
SOURCE_COMPARISON = 'sources/textual_restoration/comparisons/genesis2_2_sixth_seventh.2026-10-10.v1.json'
CANDIDATE_SHA = '6f143d248e18be69f62cea6b5f73e3552d5239d2804859afa7ae30770e1cd3f2'
YAML_SHA = 'bdeb4c9f5d6d7eaaf77b073b0bf58d61757ee13511facc0f52fbfad52a6c2e42'
ENGLISH_CONTRACT_SHA = '6bcb64f456e3d73e9766e4b8b9300b89d8af9245899cc9b492106a0c7fd64d8c'
ENGLISH_RESULT_SHA = 'f5a9b715a2cec0ed44bb44cd3ac5536a9684e6ba273b4e6d28beafdec6275c0c'
SOURCE_COMPARISON_SHA = '2562b3c17c13211db97dd9c8c2debd1596ba6409cee741cdfb7393448432bbfd'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


def clean(text):
    return re.sub(r'\[[a-z]\]', '', text)


class Genesis22ReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = subprocess.check_output(['git', 'show', f'{BASE}:{TARGET}'], cwd=ROOT)
        cls.before = yaml.safe_load(cls.raw)
        cls.candidate = json.loads((ROOT / CANDIDATE).read_text())

    def contract(self):
        return json.loads((ROOT / CONTRACT).read_text())

    def receipt(self):
        return json.loads((ROOT / RECEIPT).read_text())

    def test_complete_schema_preserved_source_generation_and_precise_english_change(self):
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        validator.validate(self.candidate)
        self.assertEqual(sha((ROOT / CANDIDATE).read_bytes()), CANDIDATE_SHA)
        self.assertEqual(sha(yaml.safe_dump(self.candidate, allow_unicode=True,
                                          sort_keys=False, width=1000).encode()), YAML_SHA)
        self.assertEqual(self.candidate['id'], 'GEN.2.2')
        self.assertEqual(self.candidate['reference'], 'Genesis 2:2')
        for field in ('source', 'ai_draft'):
            self.assertEqual(self.candidate[field], self.before[field])
        self.assertEqual(self.candidate['translation']['philosophy'],
                         self.before['translation']['philosophy'])
        old = clean(self.before['translation']['text'])
        old_prefix = 'By the seventh day God had finished'
        self.assertTrue(old.startswith(old_prefix))
        self.assertEqual(clean(self.candidate['translation']['text']),
                         'On the seventh day God finished' + old[len(old_prefix):])
        self.assertEqual(set(self.candidate) - set(self.before),
                         {'review_history', 'revisions', 'source_audit', 'textual_comparison'})
        self.assertEqual(set(self.before) - set(self.candidate), {'revision_pass'})

    def test_two_notes_separate_source_variant_and_same_source_english_alternative(self):
        tr = self.candidate['translation']
        self.assertEqual(tr['text'],
                         'On the seventh day[a] God finished his work that he had done[b], and he rested on the seventh day from all his work that he had done.')
        self.assertEqual(re.findall(r'\[([a-z])\]', tr['text']), ['a', 'b'])
        self.assertEqual([n['marker'] for n in tr['footnotes']], ['a', 'b'])
        self.assertEqual(len(tr['footnotes']), 2)
        a, b = tr['footnotes']
        self.assertEqual(a['reason'], 'textual_variant')
        for phrase in ('edited Samaritan Hebrew digital text',
                       'Rahlfs–Hanhart’s selected Greek text', '‘sixth’ for completion',
                       'both retain ‘seventh’ for cessation',
                       'Masoretic base used here has ‘seventh’ in both clauses',
                       'both day numerals are supplied, not surviving ink',
                       'Historical priority remains unresolved'):
            self.assertIn(phrase, a['text'])
        self.assertEqual(b['reason'], 'alternative_reading')
        for phrase in ('‘By the seventh day God had finished his work.’',
                       'completion retrospectively in light of 2:1',
                       'retains the repeated day phrase',
                       'does not itself imply additional creative work or work throughout'):
            self.assertIn(phrase, b['text'])

    def test_seven_exact_archives_qualified_audit_and_no_transferred_approval(self):
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
        self.assertIn('remaining five lexical entries and rest of verse not newly certified', audit['scope'])
        self.assertIn('exact full-record review recorded separately', audit['review_summary'])
        comparison = self.candidate['textual_comparison']
        for flag in ('source_changed', 'fresh_image_reading', 'novel_reading_demonstrated',
                     'canon_changed', 'publication_approved'):
            self.assertIs(comparison[flag], False)
        self.assertIs(comparison['marker_free_english_changed'], True)
        self.assertIn('Unresolved', comparison['historical_priority'])
        self.assertIn('both published4Q10 numerals supplied, not surviving support',
                      comparison['sixth_alternative'])
        self.assertEqual(sha((ROOT / SOURCE_COMPARISON).read_bytes()), SOURCE_COMPARISON_SHA)

    def test_only_two_lexical_entries_qualified_theology_and_one_limited_english_vote(self):
        old, new = self.before['lexical_decisions'], self.candidate['lexical_decisions']
        self.assertEqual(len(old), len(new))
        changed = [(i, a, b) for i, (a, b) in enumerate(zip(old, new)) if a != b]
        self.assertEqual([i for i, _, _ in changed], [0, 2])
        self.assertEqual([a['source_word'] for _, a, _ in changed],
                         ['וַיְכַל', 'בַּיּוֹם הַשְּׁבִיעִי'])
        completion, day = [b for _, _, b in changed]
        self.assertEqual(completion['chosen'], 'finished')
        self.assertEqual(completion['alternatives'], ['had finished', 'completed'])
        self.assertEqual(completion['lexicon'], 'GKC §111 (grammar controls)')
        self.assertEqual(day['chosen'], 'On the seventh day')
        self.assertEqual(day['alternatives'], ['By the seventh day'])
        self.assertEqual(day['lexicon'], 'GKC §119h (temporal-preposition control)')
        for entry in (completion, day):
            self.assertIn('No fresh HALOT consultation is claimed', entry['rationale'])
        self.assertIn('not a rule that wayyiqtol always maps to English simple past', completion['rationale'])
        self.assertIn('not an exclusive gloss dictated by ב', day['rationale'])
        self.assertEqual(len(self.candidate['theological_decisions']), 1)
        theology = self.candidate['theological_decisions'][0]
        self.assertIn('not resolved by a theological contradiction veto', theology['chosen_reading'])
        self.assertIn('historical priority remains unresolved', theology['rationale'])
        self.assertEqual(theology['alternative_readings'],
                         ['By the seventh day God had finished his work as a retrospective interpretation'])
        ec = json.loads((ROOT / ENGLISH_CONTRACT).read_text())
        er = json.loads((ROOT / ENGLISH_RESULT).read_text())
        self.assertEqual(sha((ROOT / ENGLISH_CONTRACT).read_bytes()), ENGLISH_CONTRACT_SHA)
        self.assertEqual(sha((ROOT / ENGLISH_RESULT).read_bytes()), ENGLISH_RESULT_SHA)
        self.assertEqual(er['contract'], ENGLISH_CONTRACT)
        self.assertEqual(er['contract_sha256'], ENGLISH_CONTRACT_SHA)
        self.assertEqual(er['independent_votes'], 1)
        self.assertEqual(er['preference'], 'M')
        self.assertEqual(er['strength'], 'modest')
        self.assertEqual(er['reverse_order_preference'], 'M')
        self.assertIs(er['order_changed_preference'], False)
        self.assertEqual([r['order'] for r in ec['presentation_rounds']],
                         [er['first_order'], er['reverse_order']])
        self.assertEqual(er['identity_mapping_after_assessment'],
                         {'K': 'current POB', 'M': 'proposed on/finished'})
        self.assertIn('not impossible or wholly unsupported', er['actual_assessment']['strongest_contrary_case'])
        self.assertIs(er['root_assessment']['not_independent_vote'], True)
        self.assertIs(ec['origin_labels_hidden_from_reviewer'], True)
        self.assertTrue(any('not randomized first-exposure replication' in s for s in er['limits']))
        for record in (ec, er):
            self.assertIs(record['canonical_application_approved'], False)
            self.assertIs(record['repeat_until_agreement'], False)
        self.assertIs(ec['source_priority_vote'], False)
        self.assertIs(er['source_priority_approved'], False)
        self.assertIs(er['publication_approved'], False)

    def test_current_full_genesis_export_only_target_changes_and_actual_notes_survive(self):
        # Future-safe: today's book versus today's book with only this target reverted.
        after = exporter.export_book('GEN')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
                          self.before if c == 'GEN' and (ch, v) == (2, 2) else loader(c, ch, v)):
            before = exporter.export_book('GEN')
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 50)
        self.assertEqual(len(a), 1533)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[2, 2]])
        self.assertEqual(a[(2, 2)]['footnotes'], self.candidate['translation']['footnotes'])
        self.assertEqual(len(a[(2, 2)]['footnotes']), 2)
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)['status'], 'ok')

    def test_historical_git_archive_overlay_and_1532_non_target_manifest(self):
        # Historical exports do not depend on future unrelated Genesis changes.
        archive = subprocess.check_output(['git', 'archive', BASE, 'translation/ot/genesis'], cwd=ROOT)
        historical, manifest = {}, {}
        with tarfile.open(fileobj=io.BytesIO(archive)) as snapshot:
            for member in snapshot.getmembers():
                if member.isfile() and member.name.endswith('.yaml'):
                    raw = snapshot.extractfile(member).read()
                    p = Path(member.name)
                    historical[(int(p.parent.name), int(p.stem))] = yaml.safe_load(raw)
                    if member.name != TARGET:
                        manifest[member.name] = sha(raw)
        self.assertEqual(len(historical), 1533)
        self.assertEqual(len(manifest), 1532)
        loader = exporter.load_translation_record

        def snapshot_record(c, ch, v, candidate=False):
            if c != 'GEN':
                return loader(c, ch, v)
            if candidate and (ch, v) == (2, 2):
                return self.candidate
            return historical.get((ch, v))

        with patch.object(exporter, 'load_translation_record', side_effect=snapshot_record):
            before = exporter.export_book('GEN')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
                          snapshot_record(c, ch, v, candidate=True)):
            after = exporter.export_book('GEN')
        self.assertEqual(len(before['chapters']), 50)
        self.assertEqual(len(index(before)), 1533)
        a, b = index(after), index(before)
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[2, 2]])
        self.assertEqual(a[(2, 2)]['footnotes'], self.candidate['translation']['footnotes'])
        contract, receipt = self.contract(), self.receipt()
        for preflight in (contract['preflight'], receipt['preflight']):
            self.assertEqual(preflight['chapters'], 50)
            self.assertEqual(preflight['units'], 1533)
            self.assertEqual(preflight['changed_units'], [[2, 2]])
            self.assertEqual(preflight['other_verse_files'], 1532)
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
            self.assertEqual(record['target'], 'GEN.2.2')
            self.assertEqual(record['canonical_target'], TARGET)
            self.assertEqual(record['baseline_yaml_sha256'], sha(self.raw))
            self.assertEqual(record['candidate'], CANDIDATE)
            self.assertEqual(record['candidate_sha256'], CANDIDATE_SHA)
            self.assertEqual(record['candidate_yaml_sha256'], YAML_SHA)
            preflight = record['preflight']
            self.assertEqual(preflight['candidate_sha256'], CANDIDATE_SHA)
            self.assertEqual(preflight['candidate_yaml_sha256'], YAML_SHA)
            for flag in ('schema_valid', 'source_generation_preserved',
                         'marker_free_english_change_only_completion_clause', 'seven_archives_exact'):
                self.assertIs(preflight[flag], True)
            self.assertIs(preflight['canonical_written'], False)
        self.assertEqual(r['reader_contract'], CONTRACT)
        self.assertEqual(r['reader_contract_sha256'], contract_sha)
        self.assertEqual(r['preflight']['pins'], c['preflight']['pins'])
        for path, digest in c['preflight']['pins'].items():
            # Preserve historical method bytes without freezing future docs.
            # All non-method evidence and current application stay live.
            raw = (subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
                   if path == 'docs/TEXTUAL_ADJUDICATION_METHOD.md'
                   else (ROOT / path).read_bytes())
            self.assertEqual(sha(raw), digest, path)
        for path, digest in ((ENGLISH_CONTRACT, ENGLISH_CONTRACT_SHA),
                             (ENGLISH_RESULT, ENGLISH_RESULT_SHA),
                             (SOURCE_COMPARISON, SOURCE_COMPARISON_SHA)):
            self.assertEqual(c['preflight']['pins'][path], digest)
        self.assertEqual(r['review']['status'], 'pass')
        self.assertEqual(r['review']['candidate_sha256'], CANDIDATE_SHA)
        self.assertEqual(r['review']['candidate_yaml_sha256'], YAML_SHA)
        self.assertEqual(r['review']['reader_contract_sha256'], contract_sha)
        self.assertIs(r['review']['repeat_until_agreement'], False)
        self.assertEqual(r['application']['status'], 'applied-verified')
        self.assertIs(r['application']['canonical_written'], True)
        self.assertEqual(r['application']['candidate_yaml_sha256'], YAML_SHA)
        self.assertEqual(r['application']['changed_units'], [[2, 2]])
        self.assertIs(r['application']['deployed_reader_verified'], False)
        for flag in ('source_changed', 'historical_approval_transferred',
                     'original_priority_settled', 'novel_reading_demonstrated',
                     'canon_changed', 'publication_approved', 'fresh_image_reading'):
            self.assertIs(r['decision'][flag], False)
        self.assertIs(r['decision']['marker_free_main_english_changed'], True)
        self.assertIs(r['decision']['reader_disclosure_changed'], True)
        self.assertIs(c['blind_main_english_vote_claimed'], False)
        self.assertIs(c['identity_masked_completion_clause_comparison_recorded'], True)
        self.assertIs(c['repeat_until_agreement'], False)


if __name__ == '__main__':
    unittest.main()
