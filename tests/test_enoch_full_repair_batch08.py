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
            self.assertEqual([r['verse'] for r in selected_edition_sources.load_unit_overrides(c)],refs)
            self.assertTrue(all(not record(c,v)['source_correction']['selected_edition_chapter_reviewed'] for v in refs))

    def test_all6_84_unknown_span_source_note_low_confidence_and_explanations_survive(self):
        self.assertEqual([r.verse for r in verse_parser.parse_chapter(84)[0]],list(range(1,7)))
        d=record(84,2);self.assertIn('መ⟦?⟧ትከ',d['source']['text']);self.assertEqual(d['source']['confidence'],'low')
        bundle=build_enoch_prompt(84,2);row=verse_parser.load_verse(84,2)[0];api=verse_parser.build_jsonable(84)
        self.assertEqual(row.source_confidence,'low');self.assertEqual(bundle.source_payload['confidence'],'low')
        self.assertIn('⟦?⟧',bundle.prompt);self.assertIn('መ⟦?⟧ትከ',api['verses'][1]['text'])
        self.assertEqual(api['verses'][1]['transcription_uncertainties'],d['source']['transcription_uncertainties'])
        self.assertIn('not a mark printed by Charles',d['translation']['footnotes'][1]['text'])
        self.assertIn('provisional',d['translation']['footnotes'][1]['text'].lower())
        self.assertFalse(json.loads((P/'uncertainty-policy.json').read_text())['application_approved'])
        gate=json.loads((P/'explanation-delivery-gate.json').read_text())
        self.assertFalse(gate['candidate_public_delivery_verified']);self.assertFalse(gate['physical_device_verified'])

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
            if (t.TRANSLATION/f'{c:03d}/{v:03d}.yaml').exists():
                self.assertFalse(record(c,v).get('source_correction',{}).get('individual_unit_application_approved',False))
            else:
                self.assertNotIn(f'{c:03d}/{v:03d}.yaml',json.loads((P/'application.json').read_text())['canonical_after_sha256'])
        self.assertIn('drink offerings',record(53,1)['translation']['text'])
        self.assertFalse(record(55,3)['source_correction']['selected_edition_chapter_reviewed'])

    def test_progress_adds35_reviews_and3full_scopes_not_a_whole_book_certificate(self):
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

if __name__=='__main__':unittest.main()
