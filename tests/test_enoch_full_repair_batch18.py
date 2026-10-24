"""Three whole critical treatments, no retrospective vision/source-unknown pass."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader

P=t.APPLICATIONS/'enoch_full_repair_batch18_20261023'
REFS=['1 Enoch 14:2','1 Enoch 14:6','1 Enoch 14:18']
MANIFEST='18d8a4a1460e6b80b3b5e161438ec6cdefe2667c8a434c90d4f54c2ed5f17ebc'


def record(v):return yaml.load((t.TRANSLATION/f'014/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)


class FullRepairBatch18Test(unittest.TestCase):
    def test_exact_three_full_payloads_and_complete_historical_application_map(self):
        self.assertEqual(t.sha((P/'manifest.json').read_bytes()),MANIFEST)
        proof=verify_current(P);m=t.load_manifest(P);r=json.loads((P/'application.json').read_text())
        self.assertEqual(proof['references'],REFS);self.assertEqual(proof['candidate_files'],3)
        self.assertEqual(r['snapshot_file_count'],962);self.assertTrue(r['unrelated_canonical_files_unchanged_at_application'])
        expected=dict(m['canonical_baseline_sha256'])
        for v in(2,6,18):
            rel=f'014/{v:03d}.yaml';expected[rel]=t.sha((P/f'014-{v:03d}.candidate.yaml').read_bytes())
            self.assertEqual(t.sha((t.TRANSLATION/rel).read_bytes()),expected[rel])
        self.assertEqual(r['canonical_after_sha256'],expected)
        self.assertEqual(m['retirements'],[]);self.assertEqual(m['supersedes'],{})
        self.assertEqual(m['chapter_inventories'],[]);self.assertEqual(m['source_only_count_inventories'],[])

    def test_two_scoped_edited_greek_relations_not_silent_geez_normalization(self):
        a=record(2);b=record(6)
        self.assertIn('with the breath of my mouth',a['translation']['text'])
        self.assertIn('†ወበመንፈስየ',a['source']['text'])
        self.assertIn('you have seen',b['translation']['text']);self.assertNotIn('you may see',b['translation']['text'])
        self.assertIn('you will have no benefit from them',b['translation']['text'])
        for d,page in((a,73),(b,75)):
            control=d['source']['additional_translation_input'];self.assertEqual(len(control),1)
            self.assertEqual(control[0]['language'],'Greek');self.assertEqual(control[0]['pdf_pages'],[page])
            self.assertEqual(control[0]['pdf_sha256'],t.PRIMARY_SHA)
            self.assertFalse(control[0]['independent_manuscript_collation']);self.assertFalse(control[0]['fresh_manuscript_transcription'])
            self.assertEqual(control[0]['selected_print_unchanged'],d['source']['text'])
            self.assertIn(control[0]['required_internal_explanation_marker'],[n['marker']for n in d['translation']['footnotes']])
            self.assertEqual(d['source']['confidence'],'low');self.assertTrue(d['source']['transcription_uncertainties'])

    def test_voice_is_primary_and_all_three_copulas_remain_visible(self):
        d=record(18);text=d['translation']['text']
        self.assertIn('ወቃለ፡ ኪሩቤን',d['source']['text'])
        self.assertIn('the voice of the cherubim',text);self.assertEqual(text.count('[was]'),2)
        self.assertIn('[there was]',text)
        for unprinted in('I heard','vision','wheel'):self.assertNotIn(unprinted,text)
        self.assertFalse(d['source'].get('additional_translation_input'))
        self.assertEqual(d['source']['confidence'],'low');self.assertTrue(d['source']['transcription_uncertainties'])
        self.assertIn('copula',d['translation']['footnotes'][0]['text'].lower())

    def test_original_vision_rejection_and_only_new_voice_acceptance_are_separate(self):
        m=t.load_manifest(P);old=m['review_bindings']['1 Enoch 14:2'];new=m['review_bindings']['1 Enoch 14:18']
        self.assertNotEqual(old,new)
        for b in old:
            if b['reviewer_id']=='/root/enoch09_language_author':
                with self.assertRaisesRegex(ValueError,'not accepted'):t.review_row(P,b,'1 Enoch 14:18',m['files'])
        for b in new:t.review_row(P,b,'1 Enoch 14:18',m['files'])
        rejected=json.loads((P/'unapplied-proposals.json').read_text())
        self.assertEqual(next(r['verdicts']for r in rejected['proposals']if r['reference']=='1 Enoch 14:18'),['accept','hold'])
        old_input=json.loads((P/'final/ch14-critical/review-input.json').read_text())
        self.assertIn('a vision of the cherubim',next(r for r in old_input if r['reference']=='1 Enoch 14:18')['translation']['text'])
        self.assertNotIn('a vision of the cherubim',record(18)['translation']['text'])
        self.assertEqual(t.sha((P/'final/ch14-critical/review-input.json').read_bytes()),'ce101b1cb000018580b63d495e160128d442b2e695fd06ee89c36b303411f2cd')
        self.assertEqual(t.sha((P/'final/ch14-18-voice/review-input.json').read_bytes()),'5d46a05dbc343e2bdbe47361ff76202df3c9c117e6b8d6c86d21347832f28dd8')

    def test_real_primary_unknown8_is_not_replaced_by_a_greek_whole_unit(self):
        m=t.load_manifest(P);self.assertEqual([r['reference']for r in m['not_applied']],['1 Enoch 14:8'])
        self.assertEqual(t.sha((t.TRANSLATION/'014/008.yaml').read_bytes()),m['canonical_baseline_sha256']['014/008.yaml'])
        original=json.loads((P/'final/ch14-critical/review-input.json').read_text());held=next(r for r in original if r['reference']=='1 Enoch 14:8')
        self.assertIn('⟦?⟧',held['source']['text'])
        for b in m['review_bindings']['1 Enoch 14:2']:
            with self.assertRaisesRegex(ValueError,'not accepted'):t.review_row(P,b,'1 Enoch 14:8',m['files'])

    def test_partial_critical_reviews_do_not_become_full_chapter_or_book_certification(self):
        from tools.enoch.full_repair_progress import build
        report=build();self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertNotIn(14,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertFalse(report['completion_proven']);self.assertFalse(report['artwork_publication_approval'])
        for v in(2,6,18):
            d=record(v)
            for key in('selected_edition_chapter_reviewed','chapter_publication_approval','full_book_verified','human_specialist_certification','manuscript_witness_certification','graphic_publication_approved'):self.assertFalse(d['source_correction'][key])
            self.assertEqual(d['ai_draft']['model_id'],'not_reported');self.assertEqual(d['cross_check']['status'],'needs_review')
        self.assertEqual(t.sha((P/'final/ch14-critical/independent-review.json').read_bytes()),'1d34eef19b69d036872f725933150d0c655b8bb8b075eaacda471d879f8ce0b2')
        self.assertEqual(t.sha((P/'final/ch14-18-voice/independent-review.json').read_bytes()),'0f199e4f8fdecf2243813c1cf2e8f8a010ed243addd689a8b9cbed31db1840f7')

    def test_independent_source_ingress_uses_only_exact_accepted_new_units(self):
        from tools.enoch import selected_edition_sources as s
        registry=s.registry_data();self.assertNotIn('14',registry['chapters'])
        rows={r['verse']:r for r in s.load_unit_overrides(14)}
        for v in(2,6,18):
            self.assertEqual(registry['units'][f'14:{v}'],P.name)
            self.assertEqual(rows[v]['source']['text'],record(v)['source']['text'])
            self.assertIn('/final/',rows[v]['evidence'])
        self.assertNotIn('14:8',registry['units'])

    def test_exact_explanations_and_controls_export_without_losing_editorial_brackets(self):
        book=reader.export_extra_canonical_book('ENO');chapter=next(c for c in book['chapters']if c['chapter']==14);verses={v['verse']:v for v in chapter['verses']}
        for v in(2,6,18):
            d=record(v);e=verses[v]
            self.assertEqual(e['footnotes'],d['translation']['footnotes']);self.assertEqual(e['footnote_review'],'pob-enoch-paired-source-review-v1')
            for key in('text','pages','note','confidence','additional_translation_input','transcription_uncertainties'):
                if key in d['source']:self.assertEqual(e['source_critical'][key],d['source'][key])
                else:self.assertNotIn(key,e['source_critical'])
            prompt=build_enoch_prompt(14,v)
            for key in('additional_translation_input','transcription_uncertainties'):
                if key in d['source']:self.assertEqual(prompt.source_payload[key],d['source'][key])
                else:self.assertFalse(prompt.source_payload.get(key))
        self.assertEqual(verses[18]['text'].count('[was]'),2);self.assertIn('[there was]',verses[18]['text'])
        self.assertFalse(json.loads((P/'explanation-delivery-gate.json').read_text())['candidate_public_delivery_verified'])

    def test_no_new_addresses_or_chapters_and_only_owned_chapter_export_delta(self):
        m=t.load_manifest(P)
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);shutil.copytree(t.TRANSLATION,root/'1_enoch')
            for v in(2,6,18):
                rel=f'014/{v:03d}.yaml';blob=m['baseline_git_blobs'][rel]['blob']
                (root/'1_enoch'/rel).write_bytes(subprocess.check_output(['git','cat-file','blob',blob],cwd=t.ROOT))
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):before=reader.export_extra_canonical_book('ENO')
        after=reader.export_extra_canonical_book('ENO');a={c['chapter']:c for c in before['chapters']};b={c['chapter']:c for c in after['chapters']}
        self.assertEqual(set(a),set(b));self.assertEqual({c for c in a if a[c]!=b[c]},{14})
        for c in a:self.assertEqual([v['verse']for v in a[c]['verses']],[v['verse']for v in b[c]['verses']])

    def test_artifact_drift_and_missing_actual_baseline_are_not_ignored(self):
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/P.name;shutil.copytree(P,p);f=p/'final/ch14-18-voice/review-input.json';f.write_bytes(f.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'artifact changed'):t.load_manifest(p)
        workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn('git fetch --no-tags --depth=1 origin d88fd4a9a8e020b4cd6c69c6ab496da51a75a294',workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_enoch_full_repair_batch18.py'",workflow)
