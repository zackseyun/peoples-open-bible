"""Guard complete Mandate twelve, displaced sections and witness independence."""
import copy,hashlib,json,unittest
from pathlib import Path
from unittest.mock import patch
import yaml
from tools import shepherd_of_hermas as h,draft_shepherd_of_hermas as d,repentance_reassessment as policy,reorientation_policy as prior
ROOT=Path(__file__).resolve().parents[1];REPAIR=ROOT/'sources/shepherd_of_hermas/repair'

class TwelveDialogueTests(unittest.TestCase):
    def test_complete_scope_and_restored_assertions(self):
        a=json.loads((REPAIR/'twelve-dialogue-restoration-20261104.v1.json').read_text())
        self.assertTrue(a['english_extent_changed']);self.assertFalse(a['normalized_source_body_changed'])
        self.assertEqual([r['paragraphs'] for r in a['english_drafts']],[3,5,6,7,4,5])
        self.assertIn('NOTindependentPalatina',a['primary_sources'][3]['limitation'])
        for row in a['english_drafts']:
            for kind in ['standard','simplified']:
                doc=yaml.safe_load((ROOT/row[kind+'_path']).read_text());u=h.load_normalized_unit(row['unit_id']);ps=doc['translation']['text'].split('\n\n')
                self.assertEqual(doc['source']['text'],u.text);self.assertEqual(doc['id'],'HERM.'+u.unit_id)
                self.assertEqual([p.split('. ',1)[0] for p in ps],[str(n) for n in range(1,row['paragraphs']+1)])
                notes={x['marker']:x['text'] for x in doc['translation']['footnotes']}
                for marker in notes:self.assertEqual(doc['translation']['text'].count('['+marker+']'),1,(row['unit_id'],kind,marker))
                if row['unit_id']=='M.12.iii':
                    for word in ['righteousness','virtue','truth','faith','gentleness']:self.assertIn(word,ps[0])
                    self.assertIn('repentance',ps[1]);self.assertIn('compel',ps[2]);self.assertIn('not have salvation',ps[5]);self.assertIn('children',ps[5]);self.assertIn('household',ps[5])
                    self.assertIn('not independent Palatina',notes['a'])
                if row['unit_id']=='M.12.iv':
                    self.assertIn('appearance changed',ps[0]);self.assertIn('more cheerfully',ps[1]);self.assertIn('on their lips',ps[3]);self.assertIn('Turn back',ps[5]);self.assertIn('angel of repentance',ps[6]);self.assertIn('only fear',ps[6])
                    self.assertIn('additional creation passage',notes['b'])
                if row['unit_id']=='M.12.v':self.assertIn('half-full',notes['b'])
                if row['unit_id']=='M.12.vi':
                    self.assertIn('strengthen them',ps[0]);self.assertIn('righteousness',ps[1]);self.assertIn('save',ps[2]);self.assertIn('destroy',ps[2]);self.assertIn('hope',ps[3]);self.assertIn('pure toward the Lord',ps[4]);self.assertIn('vain desires',ps[4]);self.assertNotIn('city',doc['translation']['text'])
                self.assertEqual(d.sha256_hex(doc['translation']['text']),row[kind+'_text_sha256'])
                self.assertEqual(doc['status'],'draft');self.assertFalse(doc['ai_draft']['independent_review'])

    def test_preserved_donor_nested_history_and_payloads(self):
        a=json.loads((REPAIR/'legacy41-47-before-twelve-restoration-20261104.v1.json').read_text())
        self.assertEqual(len(a['nested_unchanged']),48)
        for path,x in a['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),x['file_sha256'])
        donor=a['standard_flats']['47']
        later=json.loads((REPAIR/'legacy47-48-before-city-restoration-20261104.v1.json').read_text())
        self.assertEqual(later['flats'][donor['path']],{'file_sha256':donor['file_sha256'],'record':donor['record']})
        current=yaml.safe_load((ROOT/donor['path']).read_text())
        self.assertEqual(current['source_grounding']['evidence_record'],'sources/shepherd_of_hermas/repair/one-city-restoration-20261104.v1.json')
        self.assertEqual(current['source']['unit_id'],'S.1')
        self.assertEqual(len(current['translation']['text'].split('\n\n')),11)
        self.assertIn('if the turning is toward your own city',donor['record']['translation']['text'])
        self.assertIn('desire…',a['standard_flats']['43']['record']['translation']['text'])
        for n in range(41,47):
            s=yaml.safe_load((ROOT/f'translation/extra_canonical/shepherd_of_hermas/{n:03}.yaml').read_text());t=yaml.safe_load((ROOT/f'translation_simplified/extra_canonical/shepherd_of_hermas/{n:03}.yaml').read_text())
            payload=dict(english_text=s['translation']['text'],translation_philosophy=s['translation']['philosophy'],lexical_decisions=s['lexical_decisions'],footnotes=s['translation']['footnotes'],theological_decisions=s['theological_decisions'])
            self.assertEqual(s['ai_draft']['output_hash'],d.sha256_hex(d.canonical_json(payload)));self.assertEqual(t['base_translation']['text'],s['translation']['text']);self.assertEqual(t['base_translation']['sha256'],d.sha256_hex(s['translation']['text']));self.assertEqual(t['ai_draft']['output_hash'],d.sha256_hex(t['translation']['text']))

    def test_exact_policy_followups_reject_changes(self):
        for rel in [policy.HERMAS_TWELVE_IV,policy.HERMAS_TWELVE_VI]:
            path=ROOT/rel;doc=prior.load(path);self.assertEqual(policy.approved_errors(path,doc),[])
            self.assertEqual(policy.historical_view(path,doc)['translation']['text'],policy.plan_by_path()[rel]['after_text'])
            for field in ['source','translation']:
                bad=copy.deepcopy(doc);bad[field]['text']+=' changed';self.assertTrue(policy.approved_errors(path,bad))
            bad=copy.deepcopy(doc);bad['translation']['footnotes'][-1]['text']='unanimous source';self.assertTrue(policy.approved_errors(path,bad))
            bad=copy.deepcopy(doc);bad['ai_draft']['independent_review']=True;self.assertTrue(policy.approved_errors(path,bad))
            with patch.object(Path,'read_bytes',return_value=b'{}'):
                with self.assertRaisesRegex(ValueError,'decision pin differs'):policy.historical_view(path,doc)

if __name__=='__main__':unittest.main()
