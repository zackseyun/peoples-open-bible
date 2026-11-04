"""Earlier omissions need bounded sources, complete dialogue and intact history."""
import hashlib
import json
import unittest
from pathlib import Path

import yaml
from tools import draft_shepherd_of_hermas as drafting
from tools import shepherd_of_hermas as hermas

ROOT = Path(__file__).resolve().parents[1]
REPAIR = ROOT / 'sources/shepherd_of_hermas/repair'


class HermasEarlierDraftTests(unittest.TestCase):
    def test_four_baptism_compound_source_keeps_both_sections_and_reader_ids(self):
        audit = json.loads((REPAIR / 'four-baptism-repair-20261104.v1.json').read_text())
        row = audit['english_drafts'][0]
        assert not audit['source_body_changed'] and not audit['legacy_reader_ids_changed']
        assert not audit['complete'] and not audit['independent_review']
        assert row['reader_slot'] == 31 and row['additional_unit_ids'] == ['M.4.iv']
        expected = '\n\n'.join(hermas.load_normalized_unit(uid).text for uid in ['M.4.iii', 'M.4.iv'])
        for kind in ('standard', 'simplified'):
            doc = yaml.safe_load((ROOT / row[kind + '_path']).read_text())
            assert doc['id'] == 'HERM.M.4.iii' and doc['source']['text'] == expected
            paragraphs = doc['translation']['text'].split('\n\n')
            assert len(paragraphs) == 11
            assert [p.split('. ', 1)[0] for p in paragraphs] == ['III.' + str(i) for i in range(1, 8)] + ['IV.' + str(i) for i in range(1, 5)]
            for span in doc['source']['source_unit_spans']:
                text = expected[span['start']:span['start'] + span['length']]
                assert text == hermas.load_normalized_unit(span['unit_id']).text
                assert hashlib.sha256(text.encode()).hexdigest() == span['text_sha256']
            assert hashlib.sha256(doc['translation']['text'].encode()).hexdigest() == row[kind + '_text_sha256']
            assert doc['status'] == 'draft' and not doc['ai_draft']['independent_review']
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            assert 'sin and do not repent' in notes['d']
            assert 'cannot decide the negation' in notes['d']
            assert 'have no great sin' in notes['b']
            assert 'one repentance' in doc['translation']['text']
            assert 'if they keep' in doc['translation']['text']

    def test_four_baptism_preserves_old_nested_records_and_neighbor(self):
        audit = json.loads((REPAIR / 'four-baptism-repair-20261104.v1.json').read_text())
        archive = json.loads((REPAIR / audit['history_archive']).read_text())
        assert len(archive['nested_unchanged']) == 16
        for path, entry in archive['nested_unchanged'].items():
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == entry['file_sha256']
        neighbor = archive['unchanged_neighbor']
        assert hashlib.sha256((ROOT / neighbor['path']).read_bytes()).hexdigest() == neighbor['file_sha256']
        assert yaml.safe_load((ROOT / neighbor['path']).read_text())['id'] == 'HERM.M.5.i'

    def test_four_baptism_payload_and_simple_base_are_current(self):
        audit = json.loads((REPAIR / 'four-baptism-repair-20261104.v1.json').read_text())
        row = audit['english_drafts'][0]
        standard = yaml.safe_load((ROOT / row['standard_path']).read_text())
        simple = yaml.safe_load((ROOT / row['simplified_path']).read_text())
        payload = dict(english_text=standard['translation']['text'], translation_philosophy=standard['translation']['philosophy'], lexical_decisions=standard['lexical_decisions'], footnotes=standard['translation']['footnotes'], theological_decisions=standard['theological_decisions'])
        assert standard['ai_draft']['output_hash'] == drafting.sha256_hex(drafting.canonical_json(payload))
        assert simple['base_translation']['text'] == standard['translation']['text']
        assert simple['base_translation']['sha256'] == row['standard_text_sha256']
        assert simple['ai_draft']['output_hash'] == row['simplified_text_sha256']

    def test_mandate_eleven_restores_tests_and_both_upward_examples(self):
        audit = json.loads((REPAIR / 'mandate-eleven-repair-20261104.v1.json').read_text())
        assert not audit['complete'] and not audit['independent_review']
        assert not audit['source_body_changed'] and not audit['legacy_reader_ids_changed']
        row = audit['english_drafts'][0]
        source = hermas.load_normalized_unit('M.11').text
        assert hashlib.sha256(source.encode()).hexdigest() == audit['source_sha256']
        docs = {}
        for kind in ('standard', 'simplified'):
            doc = yaml.safe_load((ROOT / row[kind + '_path']).read_text())
            docs[kind] = doc
            text = doc['translation']['text']
            assert len(text.split('\n\n')) == 21
            assert doc['source']['text'] == source
            assert hashlib.sha256(text.encode()).hexdigest() == row[kind + '_text_sha256']
            assert doc['status'] == 'draft' and not doc['ai_draft']['independent_review']
            assert 'empty jar' in text and 'life and works' in text
            assert 'a stone' in text and 'water tube' in text and 'pierce heaven' in text
            assert 'earthly spirit flees' in text
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            assert 'The holy spirit flees' in notes['f']
            assert 'spiritus ille terrestris' in notes['f'] and 'spiritus terrenus' in notes['f']
            assert 'not preserved Athos Greek' in notes['f']
            assert 'angel of the prophet' in notes['e']
        assert docs['simplified']['base_translation']['text'] == docs['standard']['translation']['text']
        assert docs['simplified']['base_translation']['sha256'] == row['standard_text_sha256']

    def test_mandate_eleven_retains_original_reader_history_and_policy_paragraph(self):
        audit = json.loads((REPAIR / 'mandate-eleven-repair-20261104.v1.json').read_text())
        archive = json.loads((REPAIR / audit['history_archive']).read_text())
        assert len(archive['nested_unchanged']) == 34
        for path, entry in archive['nested_unchanged'].items():
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == entry['file_sha256']
        doc = yaml.safe_load((ROOT / audit['english_drafts'][0]['standard_path']).read_text())
        assert doc['translation']['text'].split('\n\n')[3] == archive['standard_flat']['translation']['text'].split('\n\n')[3]
        assert doc['lexical_decisions'][13] == archive['standard_flat']['lexical_decisions'][13]
        assert doc['terminology_revision'] == archive['standard_flat']['terminology_revision']
        assert archive['standard_flat']['translation']['text'].split('\n\n')[13].strip() == '14. [Heaven.]'

    def test_mandate_eleven_payload_and_simple_output_hashes_are_current(self):
        audit = json.loads((REPAIR / 'mandate-eleven-repair-20261104.v1.json').read_text())
        row = audit['english_drafts'][0]
        standard = yaml.safe_load((ROOT / row['standard_path']).read_text())
        simple = yaml.safe_load((ROOT / row['simplified_path']).read_text())
        payload = dict(english_text=standard['translation']['text'], translation_philosophy=standard['translation']['philosophy'], lexical_decisions=standard['lexical_decisions'], footnotes=standard['translation']['footnotes'], theological_decisions=standard['theological_decisions'])
        assert standard['ai_draft']['output_hash'] == drafting.sha256_hex(drafting.canonical_json(payload))
        assert simple['ai_draft']['output_hash'] == row['simplified_text_sha256']

    def test_vision_four_source_repairs_have_exact_history(self):
        audit = json.loads((REPAIR / 'vision-four-dialogue-20261104.v1.json').read_text())
        raw = audit['raw_correction']
        assert raw['before_text'].count(raw['old_clause']) == 1
        # Removing editorial notes leaves exactly the one declared body correction.
        before = raw['before_text'].split('[BODY]')[1].split('[MARGINALIA]')[0]
        after = raw['after_text'].split('[BODY]')[1].split('[MARGINALIA]')[0]
        assert after == before.replace(raw['old_clause'], raw['new_clause'])
        for phase in ('before', 'after'):
            assert hashlib.sha256(raw[phase + '_text'].encode()).hexdigest() == raw[phase + '_sha256']
        assert (ROOT / raw['path']).read_text() == raw['after_text']
        name = audit['selected_reading']
        assert name['source_before'].count(name['old_printed_clause']) == 1
        assert name['source_after'] == name['source_before'].replace(name['old_printed_clause'], name['new_selected_clause'])
        for phase in ('before', 'after'):
            assert hashlib.sha256(name['source_' + phase].encode()).hexdigest() == name[phase + '_source_sha256']
        assert hermas.load_normalized_unit('V.4.ii').text == name['source_after']

    def test_vision_four_drafts_restore_dialogue_conditions_and_source_variants(self):
        audit = json.loads((REPAIR / 'vision-four-dialogue-20261104.v1.json').read_text())
        row = audit['english_drafts'][0]
        assert not audit['complete'] and not audit['independent_review']
        assert not audit['legacy_reader_ids_changed']
        docs = {}
        for kind in ('standard', 'simplified'):
            doc = yaml.safe_load((ROOT / row[kind + '_path']).read_text())
            docs[kind] = doc
            text = doc['translation']['text']
            assert doc['id'] == 'HERM.V.4.ii'
            assert doc['source']['text'] == hermas.load_normalized_unit('V.4.ii').text
            assert len(text.split('\n\n')) == 6
            assert hashlib.sha256(text.encode()).hexdigest() == row[kind + '_text_sha256']
            assert doc['status'] == 'draft' and doc['cross_check']['status'] == 'needs_review'
            assert not doc['ai_draft']['independent_review']
            assert 'she was the church' in text.lower()
            assert 'oversees the beasts' in text and 'Thegri' in text
            assert 'repent toward the Lord with your whole heart' in text
            assert 'if your heart becomes pure and without blemish' in text
            assert 'I knew that I would escape' not in text
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            assert 'white hands' in notes['a']
            assert 'holy angel and glorious name' in notes['b']
            assert 'Segri' in notes['c'] and 'one manuscript' in notes['c']
            assert 'Cast your hearts' in notes['d']
        standard, simple = docs['standard'], docs['simplified']
        payload = dict(english_text=standard['translation']['text'], translation_philosophy=standard['translation']['philosophy'], lexical_decisions=standard['lexical_decisions'], footnotes=standard['translation']['footnotes'], theological_decisions=standard['theological_decisions'])
        assert standard['ai_draft']['output_hash'] == drafting.sha256_hex(drafting.canonical_json(payload))
        assert simple['base_translation']['text'] == standard['translation']['text']
        assert simple['base_translation']['sha256'] == row['standard_text_sha256']
        assert simple['ai_draft']['output_hash'] == row['simplified_text_sha256']

    def test_vision_four_nested_history_is_not_silently_reassigned(self):
        audit = json.loads((REPAIR / 'vision-four-dialogue-20261104.v1.json').read_text())
        archive = json.loads((REPAIR / audit['history_archive']).read_text())
        assert len(archive['nested_unchanged']) == 6
        for path, entry in archive['nested_unchanged'].items():
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == entry['file_sha256']
        assert 'I knew that I would escape' in archive['standard_flat']['translation']['text']
        assert archive['simplified_flat_before'] is None
        malformed = audit['paragraph_crosswalk'][1]
        assert malformed['old_reader'] == '023/002'
        assert malformed['new_flat_paragraphs'] == [2, 3, 4, 5]


if __name__ == '__main__':
    unittest.main()
