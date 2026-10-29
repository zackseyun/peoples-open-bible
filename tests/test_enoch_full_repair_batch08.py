"""47 exact units:35 newly imported reviews and12metadata-only successors."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools import export_reader_bible as reader
from tools.enoch import bounded_application as t,verse_parser,selected_edition_sources,multi_witness
from tools.enoch.current_evidence import verify_current
from tools.enoch.full_repair_progress import build
from tools.enoch.build_translation_prompt import build_enoch_prompt
P=t.APPLICATIONS/'enoch_full_repair_batch08_20261022'
FULL={22:14,57:3,84:6}
PARTIAL={52:9,53:7,54:10,55:4,56:8}

def record(c,v):return yaml.load((t.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)

class FullRepairBatch08Test(unittest.TestCase):
    def assert_later53_6_restoration(self):
        # B08's original fourteen holds remain historical holds. Only this
        # explicit later exact paired application may add the absent sixth unit.
        successor=t.APPLICATIONS/'enoch_full_repair_batch30_20261025'
        self.assertEqual(t.sha((successor/'manifest.json').read_bytes()),'c71ce5a3d18960cc6ac785bee2be9afd52247aa5faacf4c6539b5129e6fff978')
        m=t.load_manifest(successor);self.assertEqual(m['references'],['1 Enoch 53:6'])
        self.assertEqual(verify_current(successor)['references'],['1 Enoch 53:6'])
        self.assertNotIn('053/006.yaml',m['canonical_baseline_sha256'])
        prior=json.loads((t.APPLICATIONS/'enoch_full_repair_batch29_20261024/application.json').read_text())
        self.assertEqual(m['canonical_baseline_sha256'],prior['canonical_after_sha256'])
        bindings=m['review_bindings']['1 Enoch 53:6'];self.assertEqual(len({b['reviewer_id']for b in bindings}),2)
        rows=t.reviewed_rows(successor,bindings,'1 Enoch 53:6',m['files']);self.assertEqual(rows[0],rows[1])
        self.assertEqual(record(53,6),yaml.load((successor/'053-006.candidate.yaml').read_bytes(),Loader=t.LOADER))
        self.assertEqual(selected_edition_sources.registry_data()['units']['53:6'],successor.name)
        self.assertFalse(record(53,6)['source_correction']['selected_edition_chapter_reviewed'])
        return 6

    def assert_later55_2_review(self):
        # Exactly B31's new whole pair, not B08 or source-count approval.
        from test_enoch_full_repair_batch31 import assert_current_batch31,P as successor
        m,_=assert_current_batch31(self);ref='1 Enoch 55:2'
        rows=t.reviewed_rows(successor,m['review_bindings'][ref],ref,m['files']);self.assertEqual(rows[0],rows[1])
        self.assertEqual(selected_edition_sources.registry_data()['units']['55:2'],successor.name)
        self.assertEqual(record(55,2),yaml.load((successor/'055-002.candidate.yaml').read_bytes(),Loader=t.LOADER))
        self.assertFalse(record(55,2)['source_correction']['selected_edition_chapter_reviewed']);return 2

    def assert_later54_8_review(self):
        # B08's HOLD is preserved. Only the new exact whole B32 pair may replace it.
        from test_enoch_full_repair_batch32 import assert_current_batch32,P as successor
        m,_=assert_current_batch32(self);ref='1 Enoch 54:8'
        rows=t.reviewed_rows(successor,m['review_bindings'][ref],ref,m['files']);self.assertEqual(rows[0],rows[1])
        self.assertEqual(selected_edition_sources.registry_data()['units']['54:8'],successor.name)
        self.assertEqual(record(54,8),yaml.load((successor/'054-008.candidate.yaml').read_bytes(),Loader=t.LOADER))
        self.assertFalse(record(54,8)['source_correction']['selected_edition_chapter_reviewed']);return 8

    def test_exact_application_and_metadata_successors_preserve_unrelated_and_held_bytes(self):
        result=verify_current(P);self.assertEqual(result['candidate_files'],47)
        self.assertFalse(result['full_book_verified'])
        m=t.load_manifest(P);receipt=json.loads((P/'application.json').read_text())
        self.assertEqual(len(receipt['canonical_after_sha256']),946)
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        self.assertEqual(len(m['supersedes']),12)
        self.assertEqual(len(m['references'])-len(m['supersedes']),35)
        additions=[r for r in m['references'] if '%03d/%03d.yaml'%t.parse_ref(r) not in m['canonical_baseline_sha256']]
        self.assertEqual(additions,['1 Enoch 22:14','1 Enoch 52:9','1 Enoch 53:5','1 Enoch 54:9','1 Enoch 84:6'])
        for row in m['not_applied']:
            c,v=t.parse_ref(row['reference']);rel=f'{c:03d}/{v:03d}.yaml'
            self.assertEqual(receipt['canonical_after_sha256'].get(rel),m['canonical_baseline_sha256'].get(rel))
        self.assertEqual(len(m['not_applied']),14)
        prior=t.APPLICATIONS/'enoch_full_repair_batch07_20261021'
        for ref in m['supersedes']:
            c,v=t.parse_ref(ref);old=yaml.load((prior/f'{c:03d}-{v:03d}.candidate.yaml').read_bytes(),Loader=t.LOADER);new=record(c,v)
            self.assertEqual(old['translation'],new['translation'])
            for key in ('edition','language','text','pages','additional_translation_input','transcription_uncertainties'):
                self.assertEqual(old['source'].get(key),new['source'].get(key))
        self.assertEqual(len(verify_current(prior)['reviewed_supersessions']),12)

    def test_actual_complete_scopes_and_individually_named_sources(self):
        m=t.load_manifest(P)
        self.assertEqual({r['chapter']:len(r['units']) for r in m['chapter_inventories']},FULL)
        self.assertEqual({r['chapter']:len(r['units']) for r in m['source_only_count_inventories']},PARTIAL)
        for c,n in FULL.items():
            rows,_=verse_parser.parse_chapter(c)
            self.assertEqual([r.verse for r in rows],list(range(1,n+1)))
        for c in PARTIAL:
            refs=sorted(t.parse_ref(r)[1] for r in m['references'] if t.parse_ref(r)[0]==c)
            if c==53:refs=sorted([*refs,self.assert_later53_6_restoration()])
            if c==55:refs=sorted([*refs,self.assert_later55_2_review()])
            if c==54:refs=sorted([*refs,self.assert_later54_8_review()])
            self.assertEqual([r['verse'] for r in selected_edition_sources.load_unit_overrides(c)],refs)
            self.assertTrue(all(not record(c,v)['source_correction']['selected_edition_chapter_reviewed'] for v in refs))

    def test_later53_6_exception_is_one_exact_paired_addition_not_a_general_hold_waiver(self):
        self.assertEqual(self.assert_later53_6_restoration(),6)
        original=t.load_manifest(P)
        self.assertIn('1 Enoch 53:6',[r['reference']for r in original['not_applied']])
        self.assertEqual(len(original['not_applied']),14)
        registry=selected_edition_sources.registry_data()
        for v in(2,3,4,7):self.assertNotIn(f'53:{v}',registry['units'])

    def test_later53_6_canonical_drift_cannot_use_the_historical_hold_exception(self):
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);target=root/'053/006.yaml';target.parent.mkdir(parents=True)
            raw=(t.TRANSLATION/'053/006.yaml').read_bytes();self.assertIn('መንፈስት'.encode(),raw)
            target.write_bytes(raw.replace('መንፈስት'.encode(),'መንፈሳት'.encode()))
            with patch.object(t,'TRANSLATION',root):
                with self.assertRaises(ValueError):self.assert_later53_6_restoration()

    def test_historical84_unknown_span_requires_exact_whole_B32_successor(self):
        historical=yaml.load((P/'084-002.candidate.yaml').read_bytes(),Loader=t.LOADER)
        self.assertIn('መ⟦?⟧ትከ',historical['source']['text']);self.assertEqual(historical['source']['confidence'],'low')
        self.assertIn('not a mark printed by Charles',historical['translation']['footnotes'][1]['text'])
        from test_enoch_full_repair_batch32 import assert_current_batch32
        assert_current_batch32(self);d=record(84,2);bundle=build_enoch_prompt(84,2);api=verse_parser.build_jsonable(84)
        self.assertEqual([r.verse for r in verse_parser.parse_chapter(84)[0]],list(range(1,7)))
        self.assertEqual(bundle.source_payload['text'],d['source']['text']);self.assertEqual(bundle.source_payload['confidence'],'low');self.assertNotIn('⟦?⟧',d['source']['text'])
        self.assertEqual(api['verses'][1]['text'],d['source']['text']);self.assertEqual(api['verses'][1]['transcription_uncertainties'],d['source']['transcription_uncertainties'])
        self.assertFalse(json.loads((P/'uncertainty-policy.json').read_text())['application_approved'])
        gate=json.loads((P/'explanation-delivery-gate.json').read_text());self.assertFalse(gate['candidate_public_delivery_verified']);self.assertFalse(gate['physical_device_verified'])

    def test_complete_current_export_contains_exact_source_metadata_and_linked_explanations(self):
        output={c['chapter']:c for c in reader.export_extra_canonical_book('ENO')['chapters']}
        for c,n in FULL.items():
            self.assertEqual([v['verse'] for v in output[c]['verses']],list(range(1,n+1)))
            for v in output[c]['verses']:
                d=record(c,v['verse']);notes=d['translation'].get('footnotes',[])
                self.assertEqual(v.get('footnotes',[]),notes)
                if not notes:
                    self.assertNotIn('footnote_review',v)
                    continue
                for key in ('text','note','confidence','transcription_uncertainties','additional_translation_input'):
                    if key in d['source']:self.assertEqual(v['source_critical'][key],d['source'][key])
        self.assertEqual(output[84]['verses'][1]['source_critical']['confidence'],'low')
        for ref in t.load_manifest(P)['references']:
            c,v=t.parse_ref(ref);d=record(c,v)
            for note in d['translation'].get('footnotes',[]):self.assertIn('['+note['marker']+']',d['translation']['text'])

    def test_additional22_2_supply_does_not_claim_fresh_greek_manuscripts(self):
        d=record(22,2);extra=d['source']['additional_translation_input']
        self.assertTrue(extra);self.assertTrue(all(not x['independent_manuscript_collation'] for x in extra))
        bundle=build_enoch_prompt(22,2)
        self.assertEqual(bundle.source_payload['additional_translation_input'],extra)
        self.assertEqual(d['enoch_witnesses']['loaded_witnesses_by_language'],{'geez':['charles_1906']})

    def test_structural_only_scope_does_not_promote_held_neighbors_or_release_counts(self):
        from tools.enoch.audit_pob_source_coverage import EXPECTED_VERSES
        self.assertFalse(set(PARTIAL)&set(EXPECTED_VERSES))
        for row in t.load_manifest(P)['not_applied']:
            c,v=t.parse_ref(row['reference'])
            if (c,v)==(53,6):
                self.assert_later53_6_restoration()
                historical=json.loads((P/'application.json').read_text())
                self.assertNotIn('053/006.yaml',historical['canonical_after_sha256'])
                self.assertNotIn(row['reference'],t.load_manifest(P)['references'])
                continue  # Not B08 approval or count-based promotion.
            if (c,v)==(55,2):
                self.assert_later55_2_review()
                historical=json.loads((P/'application.json').read_text())
                self.assertEqual(historical['canonical_after_sha256']['055/002.yaml'],t.load_manifest(P)['canonical_baseline_sha256']['055/002.yaml'])
                self.assertNotIn(row['reference'],t.load_manifest(P)['references'])
                continue  # Explicit later whole pair, never B08/count approval.
            if (c,v)==(54,8):
                self.assert_later54_8_review();historical=json.loads((P/'application.json').read_text())
                self.assertEqual(historical['canonical_after_sha256']['054/008.yaml'],t.load_manifest(P)['canonical_baseline_sha256']['054/008.yaml'])
                self.assertNotIn(row['reference'],t.load_manifest(P)['references']);continue
            if (t.TRANSLATION/f'{c:03d}/{v:03d}.yaml').exists():
                self.assertFalse(record(c,v).get('source_correction',{}).get('individual_unit_application_approved',False))
            else:
                self.assertNotIn(f'{c:03d}/{v:03d}.yaml',json.loads((P/'application.json').read_text())['canonical_after_sha256'])
        self.assertIn('drink offerings',record(53,1)['translation']['text'])
        self.assertFalse(record(55,3)['source_correction']['selected_edition_chapter_reviewed'])

    def test_progress_adds35_reviews_and3full_scopes_not_a_whole_book_certificate(self):
        if (t.APPLICATIONS/'enoch_full_repair_batch10_20261022/application.json').exists():
            from tools.enoch.replay_18_pre_complete_gate import replay
            result=replay('progress18')
            self.assertEqual((result['tests_run'],result['skipped'],result['expected_failures']), (1,0,0))
            self.assertFalse(result['current_corpus_validated'])
            return
        report=build();self.assertGreaterEqual(report['current_units_with_imported_review_evidence'],258)
        self.assertTrue(set(FULL)<=set(report['chapters_with_complete_imported_selected_edition_review']))
        self.assertEqual(report['evidence_inventory_warnings'],[]);self.assertFalse(report['completion_proven'])
        self.assertNotIn(18,report['chapters_with_complete_imported_selected_edition_review'])

    def test_complete_inventory_still_does_not_make_mechanical_audit_a_translation_approval(self):
        from tools.enoch.audit_pob_source_coverage import audit
        row=audit([84])['chapters'][0]
        self.assertTrue(row['inventory_complete'])
        self.assertEqual(row['expected_verses'],6)
        self.assertFalse(row['translation_verified_by_this_audit'])

    def test_serialization_addenda_are_explicit_not_new_source_votes(self):
        m=t.load_manifest(P)
        for sub in ('ch52-54','ch22-2-metadata'):
            raw=json.loads((P/f'final/{sub}/author-provenance.json').read_text())
            adapted=json.loads((P/f'final/{sub}/author-integration-provenance.json').read_text())
            self.assertEqual(adapted['reviewer_id'],raw['reviewer_id'])
            self.assertEqual(adapted['original_provenance_sha256'],t.sha((P/f'final/{sub}/author-provenance.json').read_bytes()))
            self.assertFalse(adapted['new_source_review_vote'])
            self.assertEqual(adapted['receipt_creator'],'/root')
            self.assertTrue(adapted['scan_image_sha256'])


    def test_later55_2_exception_rejects_source_drift(self):
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);import shutil;shutil.copytree(t.TRANSLATION,root/'corpus');target=root/'corpus/055/002.yaml';target.write_bytes(target.read_bytes().replace('በሰማያት'.encode(),'በሰማይ'.encode()))
            with patch.object(t,'TRANSLATION',root/'corpus'):
                with self.assertRaises((AssertionError,ValueError)):self.assert_later55_2_review()

if __name__=='__main__':unittest.main()
