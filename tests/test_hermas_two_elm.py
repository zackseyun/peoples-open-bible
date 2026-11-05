"""Guard S2 complete scope, reversal of a wrong scan claim and papyrus bounds."""
import hashlib,json,unittest
from pathlib import Path
import yaml
from tools import shepherd_of_hermas as h,draft_shepherd_of_hermas as d
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'sources/shepherd_of_hermas/repair'
class TwoElmTests(unittest.TestCase):
    def test_exact_source_repair_and_bounded_selection(self):
        a=json.loads((P/'two-elm-vine-restoration-20261104.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text());sel=a['bounded_manuscript_selection'];u=h.load_normalized_unit('S.2')
        self.assertEqual(sel['before_selected_body'],arc['normalized_s02_before'].replace('τὰς εὐχὰς','τὰς ψυχὰς'))
        self.assertEqual(u.text,sel['before_selected_body'].replace(sel['base_printed_clause'],sel['selected_clause']))
        self.assertIn('συν[ίω]ν',sel['selected_clause']);self.assertIn('δια[κ]ονῆσαί τ[ι ἀ]γαθόν',sel['selected_clause']);self.assertFalse(sel['independent_photograph_collation'])
        raw=(ROOT/'sources/shepherd_of_hermas/transcribed/raw/hermas_lightfoot1891_g31_p0361.txt').read_text();self.assertIn('τὰς ψυχὰς',raw);self.assertIn('δυνήσονται ἀγαθόν',raw);self.assertIn('τὰς εὐχὰς',arc['raw361_before'])
        row=a['english_drafts'][0]
        for kind in ['standard','simplified']:
            doc=yaml.safe_load((ROOT/row[kind+'_path']).read_text());ps=doc['translation']['text'].split('\n\n');self.assertEqual(len(ps),10);self.assertEqual(doc['source']['text'],u.text)
            self.assertIn('shepherd appears',ps[0]);self.assertIn('rotten',ps[2]);self.assertIn('more',ps[3]);self.assertIn('wage',ps[4]);self.assertIn('power above',ps[4]);self.assertNotIn('go up above',ps[4]);self.assertIn('without doubting',ps[4]);self.assertIn('abundant with God',ps[5]);self.assertIn('double fruit',ps[7]);self.assertIn('souls complete',ps[7]);self.assertIn('books of the living',ps[8]);self.assertIn('the one who understands',ps[9]);self.assertIn('some good service',ps[9]);self.assertNotIn('luxury',doc['translation']['text']);self.assertNotIn('winter',doc['translation']['text'])
            for note in doc['translation']['footnotes']:self.assertEqual(doc['translation']['text'].count('['+note['marker']+']'),1)
            self.assertEqual(d.sha256_hex(doc['translation']['text']),row[kind+'_text_sha256']);self.assertFalse(doc['ai_draft']['independent_review'])
    def test_exact_archives_donor_and_prior_acceptance_preserved(self):
        a=json.loads((P/'legacy48-49-before-elm-restoration-20261104.v1.json').read_text());self.assertEqual(len(a['nested_unchanged']),28)
        for path,item in a['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),item['file_sha256'])
        donor='translation/extra_canonical/shepherd_of_hermas/049.yaml';self.assertEqual(hashlib.sha256((ROOT/donor).read_bytes()).hexdigest(),a['flats'][donor]['file_sha256'])
        receipt=json.loads((P/'model_reviews/legacy047-20261104-r1/receipt.json').read_text())
        for x in receipt['input_manifest']:self.assertEqual(hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest(),x['file_sha256'])
        std=yaml.safe_load((ROOT/'translation/extra_canonical/shepherd_of_hermas/048.yaml').read_text());simple=yaml.safe_load((ROOT/'translation_simplified/extra_canonical/shepherd_of_hermas/048.yaml').read_text());payload=dict(english_text=std['translation']['text'],translation_philosophy=std['translation']['philosophy'],lexical_decisions=std['lexical_decisions'],footnotes=std['translation']['footnotes'],theological_decisions=std['theological_decisions'])
        self.assertEqual(std['ai_draft']['output_hash'],d.sha256_hex(d.canonical_json(payload)));self.assertEqual(simple['base_translation']['text'],std['translation']['text']);self.assertEqual(simple['base_translation']['sha256'],d.sha256_hex(std['translation']['text']));self.assertEqual(simple['ai_draft']['output_hash'],d.sha256_hex(simple['translation']['text']))
if __name__=='__main__':unittest.main()
