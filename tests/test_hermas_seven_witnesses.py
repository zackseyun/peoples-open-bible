"""The fear comparison must not invent omissions or manuscript consensus."""
import hashlib,json,re,unittest
from pathlib import Path
import yaml
from tools import shepherd_of_hermas as hermas
from tools import draft_shepherd_of_hermas as drafting

ROOT=Path(__file__).resolve().parents[1]
REPAIR=ROOT/'sources/shepherd_of_hermas/repair'


class SevenWitnessTests(unittest.TestCase):
    def test_complete_existing_words_preserved_and_notes_bound_to_passages(self):
        audit=json.loads((REPAIR/'seven-fear-witness-comparison-20261104.v1.json').read_text())
        archive=json.loads((REPAIR/audit['history_archive']).read_text())
        assert not audit['english_wording_changed'] and not audit['normalized_source_body_changed']
        assert not audit['complete'] and not audit['independent_review']
        row=audit['english_drafts'][0]
        standard=yaml.safe_load((ROOT/row['standard_path']).read_text())
        assert re.sub(r'\[[a-e]\]','',standard['translation']['text'])==archive['standard_flat']['translation']['text']
        for kind in ['standard','simplified']:
            doc=yaml.safe_load((ROOT/row[kind+'_path']).read_text())
            assert doc['source']['text']==hermas.load_normalized_unit('M.7').text
            assert len(doc['translation']['text'].split('\n\n'))==5
            assert hashlib.sha256(doc['translation']['text'].encode()).hexdigest()==row[kind+'_text_sha256']
            assert doc['status']=='draft' and not doc['ai_draft']['independent_review']
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            assert 'indirect quotation evidence' in notes['c']
            assert 'supplied from Greek' in notes['d'] and 'Palatina' in notes['d']
            assert 'singular' in notes['e'] and 'in illis' in notes['e'] and 'will not be in life' in notes['e']
            for m in notes:assert doc['translation']['text'].count('['+m+']')==1
            if kind=='simplified':
                assert 'if you' in doc['translation']['text'].lower()
                assert 'do good' in doc['translation']['text']

    def test_history_payloads_and_indirect_witness_limits(self):
        audit=json.loads((REPAIR/'seven-fear-witness-comparison-20261104.v1.json').read_text())
        archive=json.loads((REPAIR/audit['history_archive']).read_text())
        assert len(archive['nested_unchanged'])==10
        for path,entry in archive['nested_unchanged'].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==entry['file_sha256']
        row=audit['english_drafts'][0]
        s=yaml.safe_load((ROOT/row['standard_path']).read_text());t=yaml.safe_load((ROOT/row['simplified_path']).read_text())
        payload=dict(english_text=s['translation']['text'],translation_philosophy=s['translation']['philosophy'],lexical_decisions=s['lexical_decisions'],footnotes=s['translation']['footnotes'],theological_decisions=s['theological_decisions'])
        assert s['ai_draft']['output_hash']==drafting.sha256_hex(drafting.canonical_json(payload))
        assert t['base_translation']['text']==s['translation']['text']
        assert t['base_translation']['sha256']==row['standard_text_sha256']
        assert t['ai_draft']['output_hash']==row['simplified_text_sha256']
        assert any('not a direct vote' in x['observation'] for x in audit['additional_indirect_evidence'])
        coverage=json.loads((REPAIR/'coverage.v1.json').read_text())
        row=next(x for x in coverage['units'] if x['unit_id']=='M.7')
        assert row['translation_status']=='requires_source_collation'
        assert row['manuscript_collation_status']=='not_completed'


if __name__=='__main__':unittest.main()
