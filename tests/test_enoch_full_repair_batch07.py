"""Exact repaired units; source-critical explanations remain available on click."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import yaml
from tools import export_mobile_bible as mobile
from tools.enoch import bounded_application as t, verse_parser
from tools.enoch.current_evidence import verify_current
from tools.enoch.full_repair_progress import build
from tools.enoch.build_translation_prompt import build_enoch_prompt

P=t.APPLICATIONS/'enoch_full_repair_batch07_20261021'
FULL={19:3,46:8,49:4}
def record(c,v):return yaml.load((t.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)

class FullRepairBatch07Test(unittest.TestCase):
    def test_exact_scope_preserves_all_unrelated_and_held_bytes(self):
        result=verify_current(P);self.assertEqual(result['candidate_files'],50)
        self.assertFalse(result['full_book_verified'])
        m=t.load_manifest(P);receipt=json.loads((P/'application.json').read_text())
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        self.assertEqual(len(receipt['canonical_after_sha256']),941)
        self.assertEqual(sum(f'{c:03d}/{v:03d}.yaml' not in m['canonical_baseline_sha256'] for c,v in map(t.parse_ref,m['references'])),2)
        for row in m['not_applied']:
            self.assertNotIn(row['reference'],m['references'])
            c,v=t.parse_ref(row['reference']);rel=f'{c:03d}/{v:03d}.yaml'
            self.assertEqual(receipt['canonical_after_sha256'].get(rel),m['canonical_baseline_sha256'].get(rel))
        for ref in ['1 Enoch 41:8','1 Enoch 80:5','1 Enoch 97:10']:
            self.assertNotIn(ref,m['references'])
        self.assertEqual({x['chapter'] for x in m['chapter_inventories']},set(FULL))

    def test_material_negative_direction_and_lexical_controls(self):
        # Immutable applied choices; later explicitly reviewed successors may improve them.
        def record(c,v):return yaml.load((P/f'{c:03d}-{v:03d}.candidate.yaml').read_bytes(),Loader=t.LOADER)
        self.assertIn('will raise kings',record(46,4)['translation']['text'])
        self.assertIn('†ያነሥኦሙ',record(46,4)['source']['text'])
        self.assertIn('does not remain',record(49,2)['translation']['text'])
        self.assertNotIn('no opponent',record(49,2)['translation']['text'])
        self.assertIn('different derived forms',record(49,2)['translation']['footnotes'][0]['text'])
        self.assertIn('ብርህት',record(22,9)['source']['text'])
        self.assertNotIn('ብርሃን',record(22,9)['source']['text'])

    def test_internal_explanations_are_linked_and_metadata_survives_export(self):
        m=t.load_manifest(P)
        for ref in m['references']:
            c,v=t.parse_ref(ref);d=record(c,v);out=mobile._export_record_verse(v,d)
            if d['translation'].get('footnotes'):
                self.assertEqual(out['footnote_review'],'pob-enoch-paired-source-review-v1')
                self.assertEqual(out['source_critical']['text'],d['source']['text'])
            else:
                self.assertNotIn('footnote_review',out)
            self.assertEqual(out.get('footnotes',[]),d['translation'].get('footnotes',[]))
            for note in d['translation'].get('footnotes',[]):
                self.assertIn('['+note['marker']+']',d['translation']['text'],ref)
        gate=json.loads((P/'explanation-delivery-gate.json').read_text())
        self.assertTrue(gate['ancestry_verified'])
        self.assertFalse(gate['candidate_public_delivery_verified'])
        self.assertFalse(gate['physical_device_verified'])

    def test_reported_variants_are_exact_separate_controls_not_loaded_manuscripts(self):
        for c,v in [(48,8),(49,1)]:
            d=record(c,v);bundle=build_enoch_prompt(c,v)
            self.assertEqual(bundle.source_payload['additional_translation_input'],d['source']['additional_translation_input'])
            self.assertEqual(bundle.source_payload['text'],d['source']['text'])
            self.assertIn('not newly inspected manuscripts',bundle.prompt)
            self.assertEqual(d['enoch_witnesses']['loaded_witnesses_by_language'],{'geez':['charles_1906']})

    def test_current_complete_reviewed_chapters_export_exact_details(self):
        out={c['chapter']:c for c in mobile.export_extra_canonical_book('ENO')['chapters']}
        for c,n in FULL.items():
            self.assertEqual([v['verse'] for v in out[c]['verses']],list(range(1,n+1)))
            self.assertEqual([r.verse for r in verse_parser.parse_chapter(c)[0]],list(range(1,n+1)))
        # Negative application scope is checked against the immutable receipt in
        # test_exact_scope... above, not a permanent ban on future reviewed repairs.
        row=next(r for r in out[49]['verses'] if r['verse']==2)
        self.assertEqual(row['footnote_review'],'pob-enoch-paired-source-review-v1')
        self.assertEqual(row['source_critical']['text'],record(49,2)['source']['text'])
        self.assertEqual(row['footnotes'],record(49,2)['translation']['footnotes'])
        progress=build();self.assertGreaterEqual(progress['current_units_with_imported_review_evidence'],215)
        self.assertTrue(set(FULL)<=set(progress['chapters_with_complete_imported_selected_edition_review']))
        self.assertEqual(progress['evidence_inventory_warnings'],[])
        self.assertFalse(progress['completion_proven'])

    def test_critical_metadata_cannot_be_added_after_review_even_when_candidate_repinned(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/P.name;shutil.copytree(P,p)
            f=p/'049-002.candidate.yaml';d=yaml.load(f.read_bytes(),Loader=t.LOADER)
            d['source']['transcription_uncertainties']=[{'text':'unreviewed unknown span'}]
            f.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False))
            m=json.loads((p/'manifest.json').read_text());m['files'][f.name]=t.sha(f.read_bytes());(p/'manifest.json').write_text(json.dumps(m))
            with self.assertRaisesRegex(ValueError,'Candidate differs from accepted source/English/notes'):t.verify(p,evidence_only=True)

    def test_source_only_count_never_promotes_held_neighbors_or_reader_policy(self):
        from tools.enoch import audit_pob_source_coverage as coverage
        m=t.load_manifest(P)
        self.assertEqual({r['chapter'] for r in m['source_only_count_inventories']},{47,48})
        self.assertNotIn(47,coverage.EXPECTED_VERSES)
        self.assertNotIn(48,coverage.EXPECTED_VERSES)
        for flag in ['wording_approval','reader_release_policy_changed']:
            with tempfile.TemporaryDirectory() as directory:
                p=Path(directory)/P.name;shutil.copytree(P,p)
                f=p/'source-only-count-inventory.json';data=json.loads(f.read_text());data[flag]=True
                f.write_text(json.dumps(data));index=json.loads((p/'manifest.json').read_text())
                index['files'][f.name]=t.sha(f.read_bytes());(p/'manifest.json').write_text(json.dumps(index))
                with self.assertRaisesRegex(ValueError,'Source-only count artifact or release limit differs'):t.load_manifest(p)

    def test_exact_receipt_serializer_alias_is_not_acceptance_inference(self):
        row={'reference':'1 Enoch 49:2','verdict':'hold'}
        self.assertEqual(t.review_entries({'results':[row]}),[row])
        for bad in [{'results':[row],'reviews':[row]}, {}, {'results':[dict(row,verdict='probably fine')]}, {'results':[row,row]}]:
            with self.assertRaises(ValueError):t.review_entries(bad)

if __name__=='__main__':unittest.main()
