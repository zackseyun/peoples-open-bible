"""Guard the restored road/angel dialogue, source corrections and witness limits."""
import hashlib
import json
from pathlib import Path
import unittest
import yaml
from tools import shepherd_of_hermas as hermas
from tools import draft_shepherd_of_hermas as drafting
from tools import reorientation_policy as prior

ROOT=Path(__file__).resolve().parents[1]
REPAIR=ROOT/'sources/shepherd_of_hermas/repair'


class SixTwoAngelsTests(unittest.TestCase):
    def test_complete_source_and_both_dialogue_sections(self):
        audit=json.loads((REPAIR/'six-two-angels-repair-20261104.v1.json').read_text())
        row=audit['english_drafts'][0]
        expected='\n\n'.join(hermas.load_normalized_unit(u).text for u in ['M.6.i','M.6.ii'])
        assert not audit['complete'] and not audit['independent_review']
        assert not audit['legacy_reader_ids_changed'] and row['reader_slot']==33
        for kind in ['standard','simplified']:
            doc=yaml.safe_load((ROOT/row[kind+'_path']).read_text())
            assert doc['source']['text']==expected and doc['id']=='HERM.M.6.i'
            paragraphs=doc['translation']['text'].split('\n\n')
            assert [p.split('. ',1)[0] for p in paragraphs]==['I.'+str(n) for n in range(1,6)]+['II.'+str(n) for n in range(1,11)]
            assert 'neither rough nor thorny' in paragraphs[3]
            assert 'turns to the Lord with their whole heart' in paragraphs[4]
            assert 'two angels' in paragraphs[5].lower()
            assert 'righteousness, purity, dignity, contentment' in paragraphs[7]
            assert '[These' in paragraphs[7] and 'righteousness.]' in paragraphs[7]
            assert 'things that are not fitting' in paragraphs[9]
            assert 'must commit some sin' in paragraphs[11] and 'must' in paragraphs[12]
            assert 'not doing them' in paragraphs[14]
            for span in doc['source']['source_unit_spans']:
                body=expected[span['start']:span['start']+span['length']]
                assert body==hermas.load_normalized_unit(span['unit_id']).text
                assert hashlib.sha256(body.encode()).hexdigest()==span['text_sha256']
            assert hashlib.sha256(doc['translation']['text'].encode()).hexdigest()==row[kind+'_text_sha256']
            assert doc['status']=='draft' and doc['cross_check']['status']=='needs_review'
            assert not doc['ai_draft']['independent_review']
            assert doc['translation']['text'].count('God’s servants')==2
            assert 'God’s slaves' not in doc['translation']['text']
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            assert 'believes in the Lord' in notes['c']
            assert 'omits that intervening description' in notes['d']
            assert 'different expanded list' in notes['d'] and 'marked corrupt' in notes['d']
            assert 'therefore' in notes['e'] and 'cannot decide Mandate6' in notes['h']
            assert 'bonded-status' in notes['e'] and 'total-allegiance' in notes['e']

    def test_two_transcription_changes_match_scan_receipt_and_parser(self):
        audit=json.loads((REPAIR/'six-source-corrections-20261104.v1.json').read_text())
        before=audit['before_raw']
        expected=before.replace('προσπέσῃ ἡ πικρία','προσπέσῃ ἢ πικρία').replace('ἀγαθον τι','ἀγαθόν τι')
        path=ROOT/'sources/shepherd_of_hermas/transcribed/raw/hermas_lightfoot1891_g31_p0343.txt'
        assert path.read_text()==expected
        assert hashlib.sha256(before.encode()).hexdigest()==audit['before_sha256']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==audit['after_sha256']
        current=hermas.load_normalized_unit('M.6.ii')
        parsed=next(u for u in hermas.parse_units() if u.key.unit_id=='M.6.ii')
        assert current.text==parsed.text
        assert 'προσπέσῃ ἢ πικρία' in current.text and 'ἀγαθόν τι' in current.text

    def test_old_nested_records_neighbor_and_draft_provenance(self):
        audit=json.loads((REPAIR/'six-two-angels-repair-20261104.v1.json').read_text())
        archive=json.loads((REPAIR/audit['history_archive']).read_text())
        assert len(archive['nested_unchanged'])==6
        for path,entry in archive['nested_unchanged'].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==entry['file_sha256']
        neighbor=archive['unchanged_neighbor']
        later=json.loads((REPAIR/'legacy34-before-fear-review-20261104.v1.json').read_text())
        assert later['standard_flat_before_file_sha256']==neighbor['file_sha256']
        assert prior.digest(later['standard_flat'])=='23d6ce23f208da6515d9befda430fcb573324713b6128e41eb1996964453d71c'
        assert yaml.safe_load((ROOT/neighbor['path']).read_text())['source']['unit_id']=='M.7'
        row=audit['english_drafts'][0]
        standard=yaml.safe_load((ROOT/row['standard_path']).read_text())
        simple=yaml.safe_load((ROOT/row['simplified_path']).read_text())
        payload=dict(english_text=standard['translation']['text'],translation_philosophy=standard['translation']['philosophy'],lexical_decisions=standard['lexical_decisions'],footnotes=standard['translation']['footnotes'],theological_decisions=standard['theological_decisions'])
        assert standard['ai_draft']['output_hash']==drafting.sha256_hex(drafting.canonical_json(payload))
        assert simple['base_translation']['text']==standard['translation']['text']
        assert simple['base_translation']['sha256']==row['standard_text_sha256']
        assert simple['ai_draft']['output_hash']==row['simplified_text_sha256']
        assert 'no separate provider API call' in standard['ai_draft']['method']


if __name__=='__main__':unittest.main()
