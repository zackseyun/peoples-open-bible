"""Preserve all source assertions and exact bounded Mandate ten repair history."""
import copy,hashlib,json,unittest
from pathlib import Path
from unittest.mock import patch
import yaml
from tools import shepherd_of_hermas as h,draft_shepherd_of_hermas as d,repentance_reassessment as policy,reorientation_policy as prior
ROOT=Path(__file__).resolve().parents[1]
REPAIR=ROOT/'sources/shepherd_of_hermas/repair'

class TenSorrowTests(unittest.TestCase):
    def test_historical_scope_and_source_choices(self):
        audit=json.loads((REPAIR/'ten-sorrow-alignment-20261104.v1.json').read_text())
        self.assertFalse(audit['english_extent_changed']);self.assertFalse(audit['normalized_source_body_changed'])
        self.assertEqual(audit['reader_paragraph_crosswalk_before']['038'],[[1,2,3,4,5,6]])
        self.assertEqual([r['paragraphs'] for r in audit['english_drafts']],[6,6,4])
        for row in audit['english_drafts']:
            for kind in ['standard','simplified']:
                doc=yaml.safe_load((ROOT/row[kind+'_path']).read_text());u=h.load_normalized_unit(row['unit_id'])
                self.assertEqual(doc['source']['text'],u.text)
                self.assertEqual(doc['id'],'HERM.'+u.unit_id)
                self.assertNotIn('manual unit override',doc['source']['edition'])
                ps=doc['translation']['text'].split('\n\n')
                self.assertEqual([x.split('. ',1)[0] for x in ps],[str(i) for i in range(1,row['paragraphs']+1)])
                notes={x['marker']:x['text'] for x in doc['translation']['footnotes']}
                for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1,(kind,row['unit_id'],m))
                if row['unit_id']=='M.10.i':
                    self.assertIn('saves',ps[1]);self.assertIn('understand nothing at all',ps[4]);self.assertIn('more quickly',ps[5]);self.assertIn('sir',ps[1].lower());self.assertIn('total allegiance',notes['c'])
                elif row['unit_id']=='M.10.ii':
                    self.assertIn('Listen now',ps[0]);self.assertIn('repents[g]',ps[2]);self.assertIn('seems to have salvation',ps[3]);self.assertIn('against you with God',ps[4]);self.assertIn('depart from you',ps[4]);self.assertIn('sorrow or anguish',ps[5]);self.assertIn('[κατὰ σοῦ]',doc['source']['text']);self.assertIn('without to God',notes['d']);self.assertIn('adds and again saves',notes['i'])
                else:
                    self.assertIn('neither praying nor confessing to God',ps[1]);self.assertIn('not have the same prayer',ps[2]);self.assertIn('all cheerfulness',ps[3]);self.assertIn('not obtaining/succeeding',notes['e']);self.assertIn('adds pure',notes['f'])
                self.assertEqual(d.sha256_hex(doc['translation']['text']),row[kind+'_text_sha256'])
                self.assertEqual(doc['status'],'draft');self.assertFalse(doc['ai_draft']['independent_review'])

    def test_archive_and_payloads(self):
        a=json.loads((REPAIR/'legacy37-39-before-sorrow-alignment-20261104.v1.json').read_text())
        self.assertEqual(len(a['nested_unchanged']),22)
        for path,x in a['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),x['file_sha256'])
        for n in [37,38,39]:
            s=yaml.safe_load((ROOT/f'translation/extra_canonical/shepherd_of_hermas/{n:03}.yaml').read_text());t=yaml.safe_load((ROOT/f'translation_simplified/extra_canonical/shepherd_of_hermas/{n:03}.yaml').read_text())
            payload=dict(english_text=s['translation']['text'],translation_philosophy=s['translation']['philosophy'],lexical_decisions=s['lexical_decisions'],footnotes=s['translation']['footnotes'],theological_decisions=s['theological_decisions'])
            self.assertEqual(s['ai_draft']['output_hash'],d.sha256_hex(d.canonical_json(payload)))
            self.assertEqual(t['base_translation']['text'],s['translation']['text']);self.assertEqual(t['base_translation']['sha256'],d.sha256_hex(s['translation']['text']))
            self.assertEqual(t['ai_draft']['output_hash'],d.sha256_hex(t['translation']['text']))

    def test_exact_contextual_followup_rejects_drift(self):
        path=ROOT/policy.HERMAS_TEN_II;doc=prior.load(path)
        self.assertEqual(policy.approved_errors(path,doc),[])
        self.assertEqual(policy.historical_view(path,doc)['translation']['text'],policy.plan_by_path()[policy.HERMAS_TEN_II]['after_text'])
        for field in ['source','translation']:
            bad=copy.deepcopy(doc);bad[field]['text']+=' changed';self.assertTrue(policy.approved_errors(path,bad))
        for key,value in [('text','omit warning'),('reason','wrong')]:
            bad=copy.deepcopy(doc);bad['translation']['footnotes'][3][key]=value;self.assertTrue(policy.approved_errors(path,bad))
        bad=copy.deepcopy(doc);bad['ai_draft']['independent_review']=True;self.assertTrue(policy.approved_errors(path,bad))
        with patch.object(Path,'read_bytes',return_value=b'{}'):
            with self.assertRaisesRegex(ValueError,'decision pin differs'):policy.historical_view(path,doc)

if __name__=='__main__':unittest.main()
