"""Guard disputed dwelling, direct purification, full purity and conditional clauses."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import draft_shepherd_of_hermas as draft
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/shepherd_of_hermas/repair'
PATHS=[ROOT/r/'extra_canonical/shepherd_of_hermas/024.yaml' for r in ['translation','translation_simplified']]

class FourColorsTests(unittest.TestCase):
    def test_recovered_bodmer_images_do_not_become_unrelated_passage_votes(self):
        e=json.loads((P/'four-colors-witness-extracts-20261105.v1.json').read_text())
        link=e['availability_followup'];path=P/link['record']
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),link['sha256'])
        self.assertTrue(link['does_not_cover_current_unit'])
        b=json.loads(path.read_text())
        self.assertEqual(b['witness_id'],'G-BODMER38');self.assertFalse(b['complete'])
        labels={row['canvas']:row for row in b['caption_observations']}
        self.assertEqual(labels[23]['global_range'],'20.1-21.4')
        self.assertEqual(labels[24]['work'],'Dorotheus')
        self.assertEqual(b['bounded_comparison']['unit_ids'],['V.3.xii','V.3.xiii'])
        self.assertIn('not independently certified',b['bounded_comparison']['finding'])
        self.assertIn('/by-nc/4.0/',b['rights']['license'])
        self.assertTrue(all(len(row['sha256'])==64 for row in b['images']))

    def test_seven_complete_paragraphs_and_localized_notes(self):
        docs,_=review.load_pair(*PATHS)
        for doc in docs:
            ps=doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ',1)[0] for p in ps],[f'III.{i}' for i in range(1,8)])
            expected={0:['four colors','beast[a]','upon its head','Again you are curious','my Lady[b]'],1:['Listen','black is this world','in which you dwell'],2:['fiery and blood-red[c]','world must be destroyed by blood and fire'],3:['you who have escaped this world[p]','tested by fire and becomes useful','you [who dwell][d] are being tested among them[e]','you who have remained','fired by it[f] will be purified[g]','gold casts off its dross','every grief and distress','you will be purified','will be useful','tower[h]'],4:['age that is coming[i]','elect of God will dwell','because those chosen by God for eternal life will be spotless and pure[q]'],5:['speaking in the ears of the holy ones[j]','also have the pattern[k]','great tribulation that is coming[l]','if you are willing, it will be nothing[m]','Remember the things written beforehand[n]'],6:['she went away','did not see to what place she went[r]','for a noise occurred[o]','turned around in fear','thinking','beast was coming']}
            for i,phrases in expected.items():
                for phrase in phrases:self.assertIn(phrase.lower(),ps[i].lower())
            self.assertTrue('do not cease' in ps[5] or 'do not stop' in ps[5])
            for p in ps:self.assertEqual(p.count('“'),p.count('”'))
            notes={n['marker']:n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(notes),set('abcdefghijklmnopqr'))
            self.assertEqual(set(re.findall(r'\[([a-z])\]',doc['translation']['text'])),set(notes))
            for m in notes:self.assertEqual(doc['translation']['text'].count('['+m+']'),1)
            self.assertIn('not marked as a gap',notes['q'])
            self.assertIn('first-hand en autē',notes['e']);self.assertIn('by them',notes['f'])
            self.assertIn('nephos, cloud',notes['o']);self.assertIn('nebula',notes['o'])
            self.assertIn('marked supplied in the modern XML',notes['r'])
            self.assertIn('second-person plural future',notes['g'])
            self.assertIn('nothing will happen',notes['m']);self.assertIn('does not settle',notes['m'])
            draft.validate_tool_input(dict(english_text=doc['translation']['text'],translation_philosophy=doc['translation']['philosophy'],lexical_decisions=doc['lexical_decisions'],footnotes=doc['translation']['footnotes'],theological_decisions=doc['theological_decisions']))
            self.assertEqual(doc['status'],'draft');self.assertFalse(doc['ai_draft']['independent_review'])

    def test_full_source_history_and_preceding_accepted_inputs_preserved(self):
        a=json.loads((P/'four-colors-alignment-20261105.v1.json').read_text());arc=json.loads((P/a['history_archive']).read_text())
        self.assertFalse(a['normalized_source_body_changed']);self.assertTrue(a['english_extent_changed'])
        self.assertEqual(hermas.load_normalized_unit('V.4.iii').text,arc['normalized_before'])
        for row in arc['raw_unchanged'].values():
            path=Path(row['path']);self.assertFalse(path.is_absolute());self.assertNotIn('..',path.parts)
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),row['file_sha256'])
        self.assertEqual(len(arc['nested_unchanged']),10)
        for p,row in arc['nested_unchanged'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),row['file_sha256'])
        self.assertTrue(any(r['category']=='doctrine_realignment' and "'fired'" in r['rationale'] for r in arc['standard_flat']['record']['revisions']))
        r=json.loads((P/'model_reviews/legacy022-20261105-r3/receipt.json').read_text())
        for row in r['input_manifest']+[r['supplemental_evidence']]:
            self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['file_sha256'])

if __name__=='__main__':unittest.main()
