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
TEN_RECORD = ROOT / 'sources/shepherd_of_hermas/repair/amherst190-ten-drafts-20261103.v2.json'
MOUNTAIN_RECORD = ROOT / 'sources/shepherd_of_hermas/repair/white-mountain-drafts-20261103.v1.json'
SERVICE_RECORD = ROOT / 'sources/shepherd_of_hermas/repair/service-mountain-drafts-20261103.v1.json'
FORGIVENESS_RECORD = ROOT / 'sources/shepherd_of_hermas/repair/forgiveness-mountain-drafts-20261103.v1.json'
ACCOUNTABILITY_RECORD = ROOT / 'sources/shepherd_of_hermas/repair/accountability-drafts-20261103.v1.json'


class HermasEndingDraftTests(unittest.TestCase):
    def test_ending_drafts_have_current_sources_and_explicit_review_limits(self):
        for record, slots in [(RECORD, {113, 114}), (TEN_RECORD, {108, 109, 110, 111, 112}), (MOUNTAIN_RECORD, {105, 106, 107}), (SERVICE_RECORD, {102, 103, 104}), (FORGIVENESS_RECORD, {99, 100, 101}), (ACCOUNTABILITY_RECORD, {95, 96, 97, 98})]:
            audit = json.loads(record.read_text())
            assert not audit['complete']
            assert not audit['independent_review']
            assert not audit['legacy_reader_ids_changed']
            assert not audit['source_body_changed']
            assert {r['reader_slot'] for r in audit['english_drafts']} == slots
            for row in audit['english_drafts']:
                source = hermas.load_normalized_unit(row['unit_id'])
                standard = yaml.safe_load((ROOT / row['standard_path']).read_text())
                simplified = yaml.safe_load((ROOT / row['simplified_path']).read_text())
                for kind, doc in [('standard', standard), ('simplified', simplified)]:
                    text = doc['translation']['text']
                    assert doc['id'] == 'HERM.' + row['unit_id']
                    assert doc['source']['text'] == source.text
                    assert doc['source']['language'] == row.get('source_language', 'Latin')
                    assert doc['status'] == 'draft'
                    assert not doc['ai_draft']['independent_review']
                    assert doc['cross_check']['status'] == 'needs_review'
                    assert doc['source_grounding']['reserved_reader_slot'] == row['reader_slot']
                    assert len(text.split('\n\n')) == row['paragraphs']
                    assert hashlib.sha256(text.encode()).hexdigest() == row[kind + '_text_sha256']
                    markers = re.findall(r'\[([a-z])\]', text)
                    assert sorted(markers) == sorted(n['marker'] for n in doc['translation'].get('footnotes', []))
                assert simplified['base_translation']['text'] == standard['translation']['text']
                assert simplified['base_translation']['sha256'] == row['standard_text_sha256']

    def test_supplied_negation_and_conditions_do_not_gain_fragment_certification(self):
        audit = json.loads(ACCOUNTABILITY_RECORD.read_text())
        decisions = {r['case_id']: r for r in audit['decisions']}
        assert len(decisions['S.9.xviii.1-God-Christ-Lord']['full_English_alternatives']) == 3
        for root in ('translation', 'translation_simplified'):
            rich = yaml.safe_load((ROOT / root / 'extra_canonical/shepherd_of_hermas/097.yaml').read_text())
            assert 'do not[a]' in rich['translation']['text']
            assert 'with difficulty' in rich['translation']['text']
            notes = {n['marker']: n['text'] for n in rich['translation']['footnotes']}
            assert 'without “not,”' in notes['a']
            assert 'not the complete inserted condition' in notes['d']
            divided = yaml.safe_load((ROOT / root / 'extra_canonical/shepherd_of_hermas/098.yaml').read_text())
            assert any('Without it:' in n['text'] for n in divided['translation']['footnotes'])

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

    def test_amherst_evidence_is_not_assigned_to_uncovered_chapters(self):
        audit = json.loads(TEN_RECORD.read_text())
        assert not audit['source_body_changed']
        assert 309 in audit['physical_pages_visually_read']
        h = next(row for row in audit['checked_edition_ranges'] if row['fragment'] == 'h')
        assert h['range'] == 'S.9.xxx.1–4; recto1–2, verso3–4'
        for slot in (111, 112):
            doc = yaml.safe_load((ROOT / f'translation/extra_canonical/shepherd_of_hermas/{slot}.yaml').read_text())
            assert 'not a Greek witness' in doc['source']['drafting_basis']
        second = yaml.safe_load((ROOT / 'translation/extra_canonical/shepherd_of_hermas/112.yaml').read_text())
        assert any('here they' in n['text'] for n in second['translation']['footnotes'])
        assert any('direct collation' in n['text'] for n in second['translation']['footnotes'])

    def test_supplied_death_penalty_is_exposed_in_both_editions(self):
        for root in ('translation', 'translation_simplified'):
            doc = yaml.safe_load((ROOT / root / 'extra_canonical/shepherd_of_hermas/109.yaml').read_text())
            assert '[morte te]' in doc['source']['text']
            assert 'death' in doc['translation']['text']
            note = doc['translation']['footnotes'][0]['text']
            assert 'editorial supply absent' in note
            assert 'conjectural' in note

    def test_mixed_source_and_crux_remain_explicit(self):
        doc = yaml.safe_load((ROOT / 'translation/extra_canonical/shepherd_of_hermas/107.yaml').read_text())
        assert doc['source']['language'] == 'Greek and Latin'
        assert '3. quodsi' in doc['source']['text']
        assert '†posse eos veritati favere,†' in doc['source']['text']
        assert 'favor the truth[c]' in doc['translation']['text']
        audit = json.loads(MOUNTAIN_RECORD.read_text())
        crux = next(row for row in audit['decisions'] if row['case_id'] == 'S.9.xxx.5-crux')
        assert crux['status'] == 'unresolved_translate_printed_words_provisionally'
        assert 'Amherst h stops' in crux['evidence']
        found = next(row for row in audit['decisions'] if row['case_id'] == 'S.9.xxx.3-found')
        assert any('young' in text for text in found['full_English_alternatives'])

    def test_excerpt_selection_keeps_latin_alternative_and_historical_hash(self):
        old = json.loads((ROOT / 'sources/shepherd_of_hermas/repair/amherst190-ten-drafts-20261103.v1.json').read_text())
        current = json.loads(TEN_RECORD.read_text())
        prior = next(row for row in old['english_drafts'] if row['reader_slot'] == 110)
        revised = next(row for row in current['english_drafts'] if row['reader_slot'] == 110)
        assert prior['standard_text_sha256'] != revised['standard_text_sha256']
        doc = yaml.safe_load((ROOT / revised['standard_path']).read_text())
        assert 'Dei servis' in doc['source']['text']
        assert 'God’s servant[b]' in doc['translation']['text']
        assert any('God’s servants' in n['text'] for n in doc['translation']['footnotes'])
        assert not doc['ai_draft']['independent_review']

    def test_service_draft_retains_conditional_and_uncertain_source_claims(self):
        doc = yaml.safe_load((ROOT / 'translation/extra_canonical/shepherd_of_hermas/103.yaml').read_text())
        text = doc['translation']['text']
        assert 'I do not know' in text
        assert 'impossible' in text
        assert 'seems to be available' in text
        office = yaml.safe_load((ROOT / 'translation/extra_canonical/shepherd_of_hermas/104.yaml').read_text())
        assert any('overseers and hospitable people' in n['text'] for n in office['translation']['footnotes'])

    def test_legacy57_repair_preserves_id_and_archives_truncated_records(self):
        audit = json.loads((ROOT / 'sources/shepherd_of_hermas/repair/six-four-repair-20261103.v1.json').read_text())
        archive = json.loads((ROOT / 'sources/shepherd_of_hermas/repair' / audit['history_archive']).read_text())
        source = hermas.load_normalized_unit('S.6.iv')
        assert source.sequence == 64
        assert archive['standard_flat']['source']['text'] != source.text
        assert archive['simplified_flat_before'] is None
        assert yaml.safe_load((ROOT / 'translation_simplified/extra_canonical/shepherd_of_hermas/057/001.yaml').read_text()) == archive['simplified_nested_unchanged']
        row = audit['english_drafts'][0]
        standard = yaml.safe_load((ROOT / row['standard_path']).read_text())
        simple = yaml.safe_load((ROOT / row['simplified_path']).read_text())
        for kind, doc in [('standard', standard), ('simplified', simple)]:
            assert doc['id'] == 'HERM.S.6.iv'
            assert doc['source']['text'] == source.text
            assert doc['source_grounding']['reserved_reader_slot'] == 57
            assert doc['source_grounding']['current_historical_source_sequence'] == 64
            assert len(doc['translation']['text'].split('\n\n')) == 4
            assert 'seven times as much' in doc['translation']['text']
            assert hashlib.sha256(doc['translation']['text'].encode()).hexdigest() == row[kind + '_text_sha256']
            assert not doc['ai_draft']['independent_review']
        assert simple['base_translation']['text'] == standard['translation']['text']
        assert source.text == audit['source_after']

    def test_spirit_seed_conjecture_is_exposed_without_changing_source(self):
        doc = yaml.safe_load((ROOT / 'translation/extra_canonical/shepherd_of_hermas/101.yaml').read_text())
        assert 'τοῦ πνεύματος αὐτοῦ' in doc['source']['text']
        assert 'his spirit.[c]' in doc['translation']['text']
        assert any('his seed' in n['text'] for n in doc['translation']['footnotes'])
        audit = json.loads(FORGIVENESS_RECORD.read_text())
        case = next(row for row in audit['decisions'] if row['case_id'] == 'S.9.xxiv.4-spirit-seed')
        assert case['status'] == 'provisionally_follow_printed_conjecture'
