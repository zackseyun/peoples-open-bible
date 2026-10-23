"""Fresh17 source treatments; historical14context units are not new votes."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t, historical_evidence
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader

P=t.APPLICATIONS/'enoch_full_repair_batch17_20261023'
EXPECTED=[(13,v)for v in(1,2,3)]+[(14,v)for v in(1,3,4,5,7,9,10,11,12,13,14,15,16,17)]
HOLDS=[(14,v)for v in(2,6,8,18)]
CONTEXT=[(13,v)for v in range(4,11)]+[(14,v)for v in range(19,26)]


def record(c,v):return yaml.load((t.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)


class FullRepairBatch17Test(unittest.TestCase):
    def test_exact17_historical_postmap_and_unchanged_holds_and_context(self):
        result=verify_current(P);m=t.load_manifest(P);receipt=json.loads((P/'application.json').read_text())
        self.assertEqual(result['references'],[f'1 Enoch {c}:{v}'for c,v in EXPECTED])
        self.assertEqual(result['candidate_files'],17);self.assertEqual(receipt['snapshot_file_count'],962)
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        expected=dict(m['canonical_baseline_sha256'])
        for c,v in EXPECTED:
            rel=f'{c:03d}/{v:03d}.yaml';expected[rel]=t.sha((P/f'{c:03d}-{v:03d}.candidate.yaml').read_bytes())
            self.assertEqual(t.sha((t.TRANSLATION/rel).read_bytes()),expected[rel])
        self.assertEqual(expected,receipt['canonical_after_sha256']);self.assertEqual(m['retirements'],[])
        self.assertEqual({r['reference']for r in m['not_applied']},{f'1 Enoch {c}:{v}'for c,v in HOLDS})
        for c,v in HOLDS+CONTEXT:
            rel=f'{c:03d}/{v:03d}.yaml';self.assertEqual(receipt['canonical_after_sha256'][rel],m['canonical_baseline_sha256'][rel])
            self.assertEqual(t.sha((t.TRANSLATION/rel).read_bytes()),m['canonical_baseline_sha256'][rel])

    def test_actual_walls_doorway_judgment_subject_and_negatives(self):
        self.assertIn('The walls of that house',record(14,10)['translation']['text'])
        self.assertNotIn('roof',record(14,10)['translation']['text'])
        self.assertIn('its doorway blazed',record(14,12)['translation']['text'])
        self.assertNotIn('beneath',record(14,12)['translation']['text'])
        self.assertIn('Judgment is complete against you',record(14,4)['translation']['text'])
        self.assertNotIn('I am complete',record(14,4)['translation']['text'])
        self.assertIn('You will have no peace',record(13,1)['translation']['text'])
        self.assertIn('No respite or petition will be granted',record(13,2)['translation']['text'])
        self.assertIn('you will not ascend',record(14,5)['translation']['text'])
        self.assertIn('will not be granted, nor on your own behalf',record(14,7)['translation']['text'])
        self.assertIn('no delight of life',record(14,13)['translation']['text'])

    def test_real_crosspage_source_not_clipped_and_false_apparatus_stars_removed(self):
        d=record(14,3);self.assertEqual(d['source']['pages'],[72,74])
        self.assertIn('children of heaven',d['translation']['text'])
        self.assertEqual(record(13,1)['source']['text'].count('*'),1)
        self.assertEqual(record(13,3)['source']['text'].count('*'),3)
        self.assertEqual(record(13,3)['source']['pages'],[70])
        self.assertIn('fear and trembling seized them',record(13,3)['translation']['text'])
        for c,v in EXPECTED:
            self.assertFalse(record(c,v)['source'].get('additional_translation_input'))
            self.assertFalse(record(c,v)['source_correction']['graphic_publication_approved'])
            self.assertFalse(record(c,v)['source_correction']['manuscript_witness_certification'])

    def test_historical_context_stays_historical_and13_completion_not_fresh35_votes(self):
        m=t.load_manifest(P);self.assertEqual(m['chapter_inventories'],[]);self.assertEqual(m['source_only_count_inventories'],[])
        self.assertFalse({f'1 Enoch {c}:{v}'for c,v in CONTEXT}&set(m['references']))
        old=historical_evidence.load_all_current()
        for key in CONTEXT:self.assertIn(key,old)
        from tools.enoch.full_repair_progress import build
        report=build();self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertIn(13,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertNotIn(14,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertFalse(report['completion_proven'])
        for c,v in EXPECTED:self.assertFalse(record(c,v)['source_correction']['selected_edition_chapter_reviewed'])
        author=json.loads((P/'final/ch13-14/author-provenance.json').read_text());peer=json.loads((P/'final/ch13-14/independent-provenance.json').read_text())
        self.assertEqual(author['reviewer_id'],'/root/enoch09_language_author')
        self.assertEqual(peer['reviewer_id'],'/root/historical_evidence_candidates')
        self.assertEqual(len(author['scan_image_sha256']),67);self.assertEqual(len(peer['scan_image_sha256']),68)

    def test_source_ingress_is_exact_accepted_new_input_only(self):
        from tools.enoch import selected_edition_sources as s
        registry=s.registry_data()
        for c in(13,14):
            self.assertNotIn(str(c),registry['chapters']);rows={r['verse']:r for r in s.load_unit_overrides(c)}
            for cc,v in EXPECTED:
                if cc==c:
                    self.assertEqual(registry['units'][f'{c}:{v}'],P.name)
                    self.assertEqual(rows[v]['source']['text'],record(c,v)['source']['text'])
                    self.assertIn('/final/',rows[v]['evidence'])
        for c,v in HOLDS:self.assertNotIn(f'{c}:{v}',registry['units'])

    def test_exact_explanations_controls_export_and_prompt(self):
        book=reader.export_extra_canonical_book('ENO');rows={(c['chapter'],v['verse']):v for c in book['chapters']for v in c['verses']}
        for c,v in EXPECTED:
            d=record(c,v);e=rows[c,v];notes=d['translation']['footnotes']
            if not notes:
                self.assertNotIn('footnotes',e);continue
            self.assertEqual(e['footnotes'],notes);self.assertEqual(e['footnote_review'],'pob-enoch-paired-source-review-v1')
            for k in('text','pages','note','confidence','additional_translation_input','transcription_uncertainties'):
                if k in d['source']:self.assertEqual(e['source_critical'][k],d['source'][k])
            prompt=build_enoch_prompt(c,v)
            for k in('additional_translation_input','transcription_uncertainties'):
                if d['source'].get(k):self.assertEqual(prompt.source_payload[k],d['source'][k])
        self.assertFalse(json.loads((P/'explanation-delivery-gate.json').read_text())['candidate_public_delivery_verified'])

    def test_no_new_reader_chapter_or_address_and_only13_14_export_changes(self):
        m=t.load_manifest(P)
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);shutil.copytree(t.TRANSLATION,root/'1_enoch')
            for c,v in EXPECTED:
                rel=f'{c:03d}/{v:03d}.yaml';blob=m['baseline_git_blobs'][rel]['blob']
                (root/'1_enoch'/rel).write_bytes(subprocess.check_output(['git','cat-file','blob',blob],cwd=t.ROOT))
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):before=reader.export_extra_canonical_book('ENO')
        after=reader.export_extra_canonical_book('ENO');a={c['chapter']:c for c in before['chapters']};b={c['chapter']:c for c in after['chapters']}
        self.assertEqual(set(a),set(b));self.assertEqual({c for c in a if a[c]!=b[c]},{13,14})
        for c in a:self.assertEqual([v['verse']for v in a[c]['verses']],[v['verse']for v in b[c]['verses']])

    def test_held_or_drifted_inputs_cannot_pass(self):
        m=t.load_manifest(P);bindings=m['review_bindings']['1 Enoch 13:1']
        for c,v in HOLDS:
            for b in bindings:
                with self.assertRaisesRegex(ValueError,'not accepted'):t.review_row(P,b,f'1 Enoch {c}:{v}',m['files'])
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/P.name;shutil.copytree(P,p);f=p/'final/ch13-14/review-input.json';f.write_bytes(f.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'artifact changed'):t.load_manifest(p)
        workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn('git fetch --no-tags --depth=1 origin e05937eff24f125aa4b18fb3f5ee9fd0c23270d0',workflow)

    def test_original13_first3_receipt_is_historical_not_new_source_votes(self):
        from tools.enoch import legacy13_parent_evidence as old
        proof=old.verify_current(t.APPLICATIONS/old.NAME)
        self.assertEqual(proof['historical_independent_source_review_passes_proven'],0)
        self.assertTrue(proof['actual_parent_and_baseline_preimages_verified'])
        self.assertFalse(proof['full_chapter_approval'])
        self.assertEqual({r['reference']for r in proof['reviewed_supersessions']},{f'1 Enoch 13:{v}'for v in(1,2,3)})
        self.assertEqual(t.sha((P/'manifest.json').read_bytes()),'85b6a9a55f206a568e3986ceb679076b499101629cbd340ae5f25316bfc7b81f')
        for v in(1,2,3):
            d=record(13,v);self.assertNotIn('lexical_decisions',d)
            self.assertEqual(d['ai_draft']['model_id'],'not_reported')
            self.assertEqual(d['cross_check']['status'],'needs_review')
            self.assertFalse(d['review_history'][0]['certifies_this_candidate'])
            self.assertEqual(d['review_history'][0]['sha256'],proof['historical_canonical_sha256'][f'1 Enoch 13:{v}'])
            self.assertEqual(d, yaml.load((P/f'013-{v:03d}.candidate.yaml').read_bytes(),Loader=t.LOADER))
        d=record(13,2)
        self.assertIn('No respite or petition will be granted',d['translation']['text'])
        self.assertNotIn('mercy',d['translation']['text'])
        self.assertIn('actual cols1330 and1213',d['translation']['footnotes'][0]['text'])
        self.assertIn('col250',d['translation']['footnotes'][0]['text'])
        self.assertIn('col376',d['translation']['footnotes'][0]['text'])

    def test_legacy13_detached_index_and_raw_editorial_drift_rejected(self):
        from tools.enoch import legacy13_parent_evidence as old
        index=old.read_index();raw=t.artifact
        with patch.object(old.t,'artifact',side_effect=lambda root,path:Path('/dev/null')if path==old.INDEX else raw(root,path)):
            with self.assertRaisesRegex(ValueError,'fixed detached index differs'):old.read_index()
        path=next(k for k in index['legacy_files']if k.endswith('editorial-review.json'))
        with patch.object(old.t,'artifact',side_effect=lambda root,p:Path('/dev/null')if p==path else raw(root,p)):
            with self.assertRaisesRegex(ValueError,'original artifact differs'):old.read_index()
        self.assertIn('git fetch --no-tags --depth=2 origin 053a1b8f175d6b047bdb20a0fa95f7ab2ba0dd41',(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text())
