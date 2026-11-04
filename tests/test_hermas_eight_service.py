"""Keep the complete service list and the edited source's witness distinctions."""
import hashlib,json,re,unittest
from pathlib import Path
import yaml
from tools import shepherd_of_hermas as hermas
from tools import draft_shepherd_of_hermas as drafting

ROOT=Path(__file__).resolve().parents[1]
REPAIR=ROOT/'sources/shepherd_of_hermas/repair'


class EightServiceTests(unittest.TestCase):
    def test_continuous_source_replaces_retired_override_without_claiming_new_extent(self):
        audit=json.loads((REPAIR/'eight-service-alignment-20261104.v1.json').read_text())
        assert not audit['english_extent_changed'] and not audit['normalized_source_body_changed']
        assert not audit['complete'] and not audit['independent_review']
        row=audit['english_drafts'][0]
        source=hermas.load_normalized_unit('M.8')
        assert hashlib.sha256(source.text.encode()).hexdigest()==audit['source_sha256']
        for kind in ['standard','simplified']:
            doc=yaml.safe_load((ROOT/row[kind+'_path']).read_text())
            assert doc['source']['text']==source.text
            assert doc['source']['edition']=='Lightfoot & Harmer 1891 (normalized OCR)'
            assert doc['id']=='HERM.M.8' and 'manual unit override' not in doc['source']['edition']
            assert '|' in doc['source']['text'] and '[φησί,]' in doc['source']['text']
            paragraphs=doc['translation']['text'].split('\n\n')
            assert [p.split('. ',1)[0] for p in paragraphs]==[str(n) for n in range(1,13)]
            assert 'I say' not in paragraphs[5] and 'he says' in paragraphs[5].lower()
            assert 'needy debtors' in paragraphs[9] and 'debtors and the needy' not in paragraphs[9]
            assert 'stumbled away from the faith' in paragraphs[9]
            assert 'good' in paragraphs[11] and 'evil' in paragraphs[11]
            assert 'God’s slaves' not in doc['translation']['text']
            assert hashlib.sha256(doc['translation']['text'].encode()).hexdigest()==row[kind+'_text_sha256']
            assert doc['status']=='draft' and not doc['ai_draft']['independent_review']

    def test_variants_and_each_kind_of_service_remain_explicit(self):
        audit=json.loads((REPAIR/'eight-service-alignment-20261104.v1.json').read_text())
        for kind in ['standard','simplified']:
            doc=yaml.safe_load((ROOT/audit['english_drafts'][0][kind+'_path']).read_text())
            text=doc['translation']['text'].split('\n\n')[9].lower()
            for word in ['widows','orphans','distress','hospit','quiet','less','elderly','righteousness','brotherhood','insult','resentment','weary','stumbled','turn','cheer','admonish','debtors']:
                assert word in text,word
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            assert 'vertical bars' in notes['b'] and 'absent in Athos' in notes['b']
            assert 'printed52–53 were not read' in notes['c']
            assert 'Hermas’s reply' in notes['d'] and 'one question' in notes['d']
            assert 'fear of God' in notes['e']
            assert 'debtors and the needy' in notes['f']
            assert 'preserve goodness' in notes['h'] and 'fraternitatem custodire' in notes['h']
            for marker in notes:assert doc['translation']['text'].count('['+marker+']')==1

    def test_nested_history_and_new_payloads_are_consistent(self):
        audit=json.loads((REPAIR/'eight-service-alignment-20261104.v1.json').read_text())
        archive=json.loads((REPAIR/audit['history_archive']).read_text())
        assert len(archive['nested_unchanged'])==24
        assert 'manual unit override' in archive['standard_flat']['source']['edition']
        assert len(archive['standard_flat']['translation']['text'].split('\n\n'))==12
        for path,entry in archive['nested_unchanged'].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==entry['file_sha256']
        row=audit['english_drafts'][0];s=yaml.safe_load((ROOT/row['standard_path']).read_text());t=yaml.safe_load((ROOT/row['simplified_path']).read_text())
        payload=dict(english_text=s['translation']['text'],translation_philosophy=s['translation']['philosophy'],lexical_decisions=s['lexical_decisions'],footnotes=s['translation']['footnotes'],theological_decisions=s['theological_decisions'])
        assert s['ai_draft']['output_hash']==drafting.sha256_hex(drafting.canonical_json(payload))
        assert t['base_translation']['text']==s['translation']['text']
        assert t['base_translation']['sha256']==row['standard_text_sha256']
        assert t['ai_draft']['output_hash']==row['simplified_text_sha256']
        assert 'not to press needy debtors' in s['translation']['text']
        assert 'make yourself one who has less' in s['translation']['text']
        assert 'boastful pretension' in s['translation']['text']
        assert 'servant (of God)' in [x['chosen'] for x in s['lexical_decisions']]


if __name__=='__main__':unittest.main()
