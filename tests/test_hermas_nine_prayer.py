"""Guard prayer assertions, repaired source identity and bounded witness claims."""
import copy,hashlib,json,unittest
from pathlib import Path
from unittest.mock import patch
import yaml
from tools import shepherd_of_hermas as h, draft_shepherd_of_hermas as d
from tools import repentance_reassessment as policy,reorientation_policy as prior
ROOT=Path(__file__).resolve().parents[1]
REPAIR=ROOT/'sources/shepherd_of_hermas/repair'

class NinePrayerTests(unittest.TestCase):
    def test_complete_scope_source_and_difficult_assertions(self):
        audit=json.loads((REPAIR/'nine-prayer-alignment-20261104.v1.json').read_text())
        source=h.load_normalized_unit('M.9')
        self.assertEqual(source.sequence,39)
        self.assertFalse(audit['normalized_source_body_changed'])
        self.assertFalse(audit['english_extent_changed'])
        row=audit['english_drafts'][0]
        for kind in ['standard','simplified']:
            doc=yaml.safe_load((ROOT/row[kind+'_path']).read_text())
            self.assertEqual(doc['id'],'HERM.M.9')
            self.assertEqual(doc['source']['text'],source.text)
            self.assertNotIn('manual unit override',doc['source']['edition'])
            ps=doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ',1)[0] for p in ps],[str(i) for i in range(1,13)])
            self.assertIn('unless he repents',ps[5])
            self.assertIn('saved with difficulty',ps[5])
            self.assertTrue('surely' in ps[6] or 'certainly' in ps[6])
            self.assertNotIn('perhaps',ps[6])
            self.assertIn('daughter of the devil',ps[8])
            self.assertIn('faithful and strong',ps[8])
            self.assertIn('does not trust itself',ps[9])
            self.assertIn('think these things',ps[11])
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1,m)
            self.assertIn('sister (adelphē)',notes['n'])
            self.assertIn('does not quote the same wording',notes['n'])
            self.assertIn('observe the preceding words',notes['d'])
            self.assertIn('will live to God with difficulty',notes['m'])
            self.assertIn('perhaps',notes['f'])
            self.assertIn('total allegiance',notes['g'])
            self.assertEqual(hashlib.sha256(doc['translation']['text'].encode()).hexdigest(),row[kind+'_text_sha256'])
            self.assertEqual(doc['status'],'draft')
            self.assertFalse(doc['ai_draft']['independent_review'])

    def test_preserved_history_and_current_payloads(self):
        a=json.loads((REPAIR/'legacy36-before-prayer-alignment-20261104.v1.json').read_text())
        self.assertEqual(len(a['nested_unchanged']),24)
        for path,x in a['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),x['file_sha256'])
        s=yaml.safe_load((ROOT/policy.HERMAS_NINE).read_text())
        t=yaml.safe_load((ROOT/'translation_simplified/extra_canonical/shepherd_of_hermas/036.yaml').read_text())
        payload=dict(english_text=s['translation']['text'],translation_philosophy=s['translation']['philosophy'],lexical_decisions=s['lexical_decisions'],footnotes=s['translation']['footnotes'],theological_decisions=s['theological_decisions'])
        self.assertEqual(s['ai_draft']['output_hash'],d.sha256_hex(d.canonical_json(payload)))
        self.assertEqual(t['base_translation']['text'],s['translation']['text'])
        self.assertEqual(t['base_translation']['sha256'],d.sha256_hex(s['translation']['text']))
        self.assertEqual(t['ai_draft']['output_hash'],d.sha256_hex(t['translation']['text']))
        self.assertEqual(s['lexical_decisions'][10],a['standard_flat']['lexical_decisions'][10])

    def test_exact_policy_followup_preserves_history_and_rejects_drift(self):
        path=ROOT/policy.HERMAS_NINE;doc=prior.load(path);old=policy.historical_view(path,doc)
        self.assertEqual(policy.approved_errors(path,doc),[])
        self.assertEqual(old['translation']['text'],policy.plan_by_path()[policy.HERMAS_NINE]['after_text'])
        for field in ['source','translation']:
            bad=copy.deepcopy(doc);bad[field]['text']+=' altered'
            self.assertTrue(policy.approved_errors(path,bad))
        bad=copy.deepcopy(doc);bad['translation']['footnotes'][-1]['text']='all witnesses agree'
        self.assertTrue(policy.approved_errors(path,bad))
        bad=copy.deepcopy(doc);bad['ai_draft']['independent_review']=True
        self.assertTrue(policy.approved_errors(path,bad))
        with patch.object(Path,'read_bytes',return_value=b'{}'):
            with self.assertRaisesRegex(ValueError,'decision pin differs'):policy.historical_view(path,doc)

if __name__=='__main__':unittest.main()
