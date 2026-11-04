"""New ending drafts must keep source limits and simplified bases auditable."""
import hashlib
import json
import re
import unittest
from pathlib import Path

import yaml
from tools import shepherd_of_hermas as hermas

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / 'sources/shepherd_of_hermas/repair/oxy404-ending-20261103.v1.json'


class HermasEndingDraftTests(unittest.TestCase):
    def test_both_ending_drafts_have_current_sources_and_explicit_review_limits(self):
        audit = json.loads(RECORD.read_text())
        assert not audit['complete']
        assert not audit['independent_review']
        assert not audit['legacy_reader_ids_changed']
        assert not audit['source_body_changed']
        assert {r['reader_slot'] for r in audit['english_drafts']} == {113, 114}
        for row in audit['english_drafts']:
            source = hermas.load_normalized_unit(row['unit_id'])
            standard = yaml.safe_load((ROOT / row['standard_path']).read_text())
            simplified = yaml.safe_load((ROOT / row['simplified_path']).read_text())
            for kind, doc in [('standard', standard), ('simplified', simplified)]:
                text = doc['translation']['text']
                assert doc['id'] == 'HERM.' + row['unit_id']
                assert doc['source']['text'] == source.text
                assert doc['source']['language'] == 'Latin'
                assert doc['status'] == 'draft'
                assert not doc['ai_draft']['independent_review']
                assert doc['cross_check']['status'] == 'needs_review'
                assert doc['source_grounding']['reserved_reader_slot'] == row['reader_slot']
                assert len(text.split('\n\n')) == row['paragraphs'] == 5
                assert hashlib.sha256(text.encode()).hexdigest() == row[kind + '_text_sha256']
                markers = re.findall(r'\[([a-z])\]', text)
                assert sorted(markers) == sorted(n['marker'] for n in doc['translation']['footnotes'])
            assert simplified['base_translation']['text'] == standard['translation']['text']
            assert simplified['base_translation']['sha256'] == row['standard_text_sha256']

    def test_greek_selection_is_bounded_and_latin_is_not_silently_rewritten(self):
        standard = yaml.safe_load((ROOT / 'translation/extra_canonical/shepherd_of_hermas/113.yaml').read_text())
        assert 'Video, inquit' in standard['source']['text']
        assert 'I know[a]' in standard['translation']['text']
        assert 'a clean dwelling.[b]' in standard['translation']['text']
        assert 'correction' in standard['translation']['footnotes'][0]['text']
        audit = json.loads(RECORD.read_text())
        decisions = {d['case_id']: d for d in audit['decisions']}
        know = decisions['S.10.iii.4-know-see']
        assert any('I see' in r['text'] for r in know['full_English_alternatives'])
        assert any('I know' in r['text'] for r in know['full_English_alternatives'])
        plural = decisions['S.10.iv.3-guilty-plural']
        assert plural['status'] == 'retain_Latin_pending_fragment_adjudication'
        assert 'not reconstructed' in plural['full_English_alternatives'][1]['text']
        final = yaml.safe_load((ROOT / 'translation/extra_canonical/shepherd_of_hermas/114.yaml').read_text())
        assert 'becomes guilty of that person’s blood.[b]' in final['translation']['text']
        assert 'his house' not in final['translation']['text'].split('\n\n')[-1]
        assert 'back to my house' in final['translation']['text'].split('\n\n')[-1]
