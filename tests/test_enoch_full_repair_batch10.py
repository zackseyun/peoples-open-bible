"""41 exact reviewed units; no all-glyph, held-neighbor or complete-book claim."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools import export_reader_bible as reader
from tools.enoch import bounded_application as t, verse_parser, selected_edition_sources
from tools.enoch.current_evidence import verify_current
from tools.enoch.full_repair_progress import build
from tools.enoch.build_translation_prompt import build_enoch_prompt

P=t.APPLICATIONS/'enoch_full_repair_batch10_20261022'
FULL={18:16}
PARTIAL={65:12,66:3,67:13,68:5,69:29}

def record(c,v):return yaml.load((t.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)

class FullRepairBatch10Test(unittest.TestCase):
    def test_exact_scope_and37_held_preimages_are_preserved(self):
        result=verify_current(P);m=t.load_manifest(P)
        self.assertEqual(result['candidate_files'],41);self.assertFalse(result['full_book_verified'])
        self.assertEqual(len(m['supersedes']),12);self.assertEqual(len(m['references'])-len(m['supersedes']),29)
        receipt=json.loads((P/'application.json').read_text())
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        self.assertEqual(len(receipt['canonical_after_sha256']),958)
        self.assertEqual(len(m['not_applied']),37)
        for row in m['not_applied']:
            c,v=t.parse_ref(row['reference']);rel=f'{c:03d}/{v:03d}.yaml'
            self.assertEqual(receipt['canonical_after_sha256'].get(rel),m['canonical_baseline_sha256'].get(rel))
        additions=[r for r in m['references'] if '%03d/%03d.yaml'%t.parse_ref(r) not in m['canonical_baseline_sha256']]
        self.assertEqual(additions,['1 Enoch 18:13','1 Enoch 18:16','1 Enoch 65:7','1 Enoch 65:9','1 Enoch 66:3'])
        for rel in ('069/028.yaml','069/029.yaml','097/010.yaml'):
            self.assertNotIn(rel,receipt['canonical_after_sha256'])
        for rel,digest in m['canonical_baseline_sha256'].items():
            if rel.startswith('097/'):self.assertEqual(receipt['canonical_after_sha256'][rel],digest)

    def test_all16_18_source_count_and_prior_negative_printing_survive(self):
        self.assertEqual([r.verse for r in verse_parser.parse_chapter(18)[0]],list(range(1,17)))
        d=record(18,12)
        self.assertIn('*ኢጽገበ',d['source']['text']);self.assertIn('ወኢማን',d['source']['text'])
        self.assertIn('no heaven',d['translation']['text']);self.assertIn('nun-shaped',d['translation']['footnotes'][2]['text'])
        self.assertTrue(d['source']['additional_translation_input'])
        self.assertTrue(record(18,6)['source']['additional_translation_input'])
        for v in range(1,17):
            d=record(18,v);self.assertEqual(d['status'],'draft')
            if v==8:
                from test_enoch_full_repair_batch32 import assert_current_batch32
                assert_current_batch32(self);self.assertFalse(d['source_correction']['selected_edition_chapter_reviewed'])
            else:self.assertTrue(d['source_correction']['selected_edition_chapter_reviewed'])
            self.assertFalse(d['source_correction']['manuscript_witness_certification'])
            self.assertFalse(d['source_correction']['graphic_publication_approved'])
        prior=verify_current(t.APPLICATIONS/'enoch_source_repairs_20261020')
        self.assertEqual(len([r for r in prior['reviewed_supersessions'] if t.parse_ref(r['reference'])[0]==18]),11)
        self.assertIn('1 Enoch 18:12',[r['reference'] for r in verify_current(
            t.APPLICATIONS/'enoch_full_repair_batch04_20261020')['reviewed_supersessions']])

    def test_historical_unclear18_8_requires_exact_whole_B32_successor(self):
        d=yaml.load((P/'018-008.candidate.yaml').read_bytes(),Loader=t.LOADER);s=d['source'];self.assertIn('ወ⟦?⟧ማሑ',s['text']);self.assertEqual(s['confidence'],'low')
        u=s['transcription_uncertainties'][0];self.assertFalse(u['selected_glyph_resolved'])
        self.assertIn('POB',u['marker_owner']);self.assertIn('not Charles',u['marker_owner'])
        extra=s['additional_translation_input'][0]
        self.assertFalse(extra['adopted_into_diplomatic_source']);self.assertFalse(extra['selected_glyph_certified'])
        note=d['translation']['footnotes'][1];self.assertEqual(note['reason'],'textual_variant')
        self.assertIn('provisional',note['text']);self.assertIn('did not print',note['text'])
        from test_enoch_full_repair_batch32 import assert_current_batch32
        assert_current_batch32(self);current=record(18,8);bundle=build_enoch_prompt(18,8)
        self.assertEqual(bundle.source_payload['text'],current['source']['text']);self.assertNotIn('⟦?⟧',bundle.source_payload['text'])
        self.assertEqual(bundle.source_payload['confidence'],'low')
        self.assertEqual(bundle.source_payload['transcription_uncertainties'],current['source']['transcription_uncertainties'])

    def test12_successors_preserve_all_english_bodies_and11_exact_note_sets(self):
        for ref,b in t.load_manifest(P)['supersedes'].items():
            c,v=t.parse_ref(ref);old=yaml.load((t.APPLICATIONS/b['package']/f'{c:03d}-{v:03d}.candidate.yaml').read_bytes(),Loader=t.LOADER);new=record(c,v)
            if (c,v)==(18,8):
                from test_enoch_full_repair_batch32 import assert_current_batch32
                assert_current_batch32(self);new=yaml.load((P/'018-008.candidate.yaml').read_bytes(),Loader=t.LOADER)  # Preserve B10's exact historical claims, not its old glyph forever.
            self.assertEqual(old['translation']['text'],new['translation']['text'])
            for k in ('edition','language','pages'):self.assertEqual(old['source'].get(k),new['source'].get(k))
            if v==8:
                self.assertEqual(old['translation']['footnotes'][0]['text'],new['translation']['footnotes'][0]['text'])
                self.assertNotEqual(old['source']['text'],new['source']['text'])
            else:
                self.assertEqual(old['source']['text'],new['source']['text'])
                self.assertEqual([n['text'] for n in old['translation'].get('footnotes',[])],[n['text'] for n in new['translation'].get('footnotes',[])])

    def test_mist_revision_and_outer_bracket_source_context_are_distinct_exact_reviews(self):
        d=record(69,23);self.assertIn('storehouses of mist',d['translation']['text'])
        self.assertIn('storehouses of snow',d['translation']['text'])
        self.assertNotIn('storehouses of frost',d['translation']['text'])
        self.assertTrue(d['source']['additional_translation_input'])
        context=d['source']['additional_translation_input'][0]
        self.assertEqual(context['enclosing_reference_range'],['1 Enoch 69:22','1 Enoch 69:24'])
        self.assertFalse(context['additional_reading_adopted']);self.assertFalse(context['unit_contains_its_own_delimiters'])
        self.assertNotIn('[',d['source']['text']);self.assertIn('outer square brackets',d['source']['note'])
        row=verse_parser.load_verse(69,23)[0];self.assertEqual(row.additional_translation_input,d['source']['additional_translation_input'])
        bundle=build_enoch_prompt(69,23);self.assertEqual(bundle.source_payload['additional_translation_input'],d['source']['additional_translation_input'])
        self.assertIn('outer square brackets',bundle.source_payload['note'])
        m=t.load_manifest(P);b=m['review_bindings']['1 Enoch 69:23']
        self.assertEqual({v['reviewer_id'] for v in b},{'/root','/root/enoch52_54_resume/ch69_23_context_independent'})
        self.assertTrue(all('ch69-23-context' in v['input'] for v in b))

    def test_counts_for65_69_do_not_approve_held_wording_or_change_release_policy(self):
        m=t.load_manifest(P)
        self.assertEqual({x['chapter']:len(x['units']) for x in m['chapter_inventories']},FULL)
        self.assertEqual({x['chapter']:len(x['units']) for x in m['source_only_count_inventories']},PARTIAL)
        for c in PARTIAL:
            refs=sorted(t.parse_ref(r)[1] for r in m['references'] if t.parse_ref(r)[0]==c)
            self.assertEqual([r['verse'] for r in selected_edition_sources.load_unit_overrides(c) if '/'+P.name+'/' in r['evidence']],refs)
            self.assertTrue(all(not record(c,v)['source_correction']['selected_edition_chapter_reviewed'] for v in refs))
        self.assertIn('without the earth',record(65,7)['translation']['text'])
        self.assertIn('እምብለ',record(65,7)['source']['text'])
        self.assertNotIn('dust',record(65,7)['translation']['text'])

    def test_all41_actual_records_preserve_exact_explanations_and_source_controls_in_reader(self):
        for ref in t.load_manifest(P)['references']:
            c,v=t.parse_ref(ref);d=record(c,v);out=reader._export_record_verse(v,d)
            notes=d['translation'].get('footnotes',[]);self.assertEqual(out.get('footnotes',[]),notes)
            if not notes:continue
            self.assertEqual(out['footnote_review'],reader.PROTOCOL)
            for k in ('edition','language','text','pages','note','confidence','transcription_uncertainties','additional_translation_input'):
                if k in d['source']:self.assertEqual(out['source_critical'][k],d['source'][k])
            for n in notes:self.assertIn('['+n['marker']+']',d['translation']['text'])

    def test_only18_is_newly_released_and_no_unrelated_chapter_changes(self):
        m=t.load_manifest(P)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);old=root/'1_enoch';shutil.copytree(t.TRANSLATION,old)
            for ref in m['references']:
                c,v=t.parse_ref(ref);rel=f'{c:03d}/{v:03d}.yaml';target=old/rel
                if rel in m['baseline_git_blobs']:target.write_bytes(subprocess.check_output(['git','cat-file','blob',m['baseline_git_blobs'][rel]['blob']],cwd=t.ROOT))
                else:target.unlink()
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):before=reader.export_extra_canonical_book('ENO')
            after=reader.export_extra_canonical_book('ENO')
        before={c['chapter']:c for c in before['chapters']};after={c['chapter']:c for c in after['chapters']}
        self.assertEqual(sorted(set(after)-set(before)),[18]);self.assertFalse(set(before)-set(after))
        self.assertEqual({c:d for c,d in after.items() if c not in {*FULL,*PARTIAL}},{c:d for c,d in before.items() if c not in {*FULL,*PARTIAL}})
        self.assertEqual([v['verse'] for v in after[18]['verses']],list(range(1,17)))

    def test_progress_is_not_a_whole_book_or_all_glyph_or_live_ui_certificate(self):
        report=build();self.assertGreaterEqual(report['current_units_with_imported_review_evidence'],339)
        self.assertIn(18,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertFalse(report['completion_proven']);self.assertEqual(report['evidence_inventory_warnings'],[])
        gate=json.loads((P/'explanation-delivery-gate.json').read_text())
        self.assertFalse(gate['candidate_public_delivery_verified']);self.assertFalse(gate['candidate_live_browser_verified'])
        self.assertFalse(gate['physical_device_verified'])

if __name__=='__main__':unittest.main()
