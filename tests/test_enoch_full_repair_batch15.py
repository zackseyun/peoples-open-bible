"""Complete14 paired chapter10 treatments, metadata26 and exact page windows."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t, legacy_editorial_evidence as legacy
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader

P=t.APPLICATIONS/'enoch_full_repair_batch15_20261023'
EXPECTED=[2,4,5,6,8,11,12,13,16,17,19,20,21,22]
HOLDS=[1,3,7,9,10,14,15,18]
WINDOW=t.ROOT/'sources/enoch/coverage/page-map13-14-20261023'


def record(v):return yaml.load((t.TRANSLATION/f'010/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)


class FullRepairBatch15Test(unittest.TestCase):
    def test_exact14_current_units_complete_historical_postmap_and_eight_holds(self):
        result=verify_current(P);m=t.load_manifest(P);receipt=json.loads((P/'application.json').read_text())
        self.assertEqual(result['references'],[f'1 Enoch 10:{v}'for v in EXPECTED])
        self.assertEqual(result['candidate_files'],14);self.assertEqual(receipt['snapshot_file_count'],962)
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        expected=dict(m['canonical_baseline_sha256'])
        for v in EXPECTED:
            rel=f'010/{v:03d}.yaml';expected[rel]=t.sha((P/f'010-{v:03d}.candidate.yaml').read_bytes())
            self.assertEqual(t.sha((t.TRANSLATION/rel).read_bytes()),expected[rel])
        self.assertEqual(expected,receipt['canonical_after_sha256'])
        self.assertEqual({r['reference']for r in m['not_applied']},{f'1 Enoch 10:{v}'for v in HOLDS})
        self.assertEqual(m['retirements'],[])
        for v in HOLDS:self.assertEqual(t.sha((t.TRANSLATION/f'010/{v:03d}.yaml').read_bytes()),m['canonical_baseline_sha256'][f'010/{v:03d}.yaml'])

    def test_critical19_is_new_exact_treatment_not_promotion_of_adverse_v2(self):
        old=json.loads((P/'final/ch10/independent-review.json').read_text())
        new=json.loads((P/'final/ch10-19/independent-review.json').read_text())
        self.assertEqual(next(r for r in old['reviews']if r['reference']=='1 Enoch 10:19')['verdict'],'hold')
        self.assertEqual(next(r for r in new['reviews']if r['reference']=='1 Enoch 10:19')['verdict'],'accept')
        self.assertNotEqual(old['input_sha256'],new['input_sha256'])
        d=record(19);self.assertIn('one measure will produce a thousand;[a]',d['translation']['text'])
        self.assertNotIn('ten thousand',d['translation']['text'])
        self.assertIn('ten press-measures of oil',d['translation']['text']);self.assertIn('፲ምክያደ',d['source']['text'])
        self.assertEqual(d['source']['confidence'],'low')
        self.assertEqual(d['source']['transcription_uncertainties'][0]['status'],'retained_lexical_quantity_ambiguity')
        self.assertIn('subsection1',d['translation']['footnotes'][0]['text'])
        self.assertIn('subsection2',d['translation']['footnotes'][0]['text'])
        self.assertIn('rather than',d['translation']['footnotes'][0]['text'])
        raw=json.loads((P/'history/ch10-language-exact-peer/numeric19-adverse-observation.json').read_text())
        self.assertTrue(raw)
        historical=next(r for r in json.loads((t.APPLICATIONS/legacy.NAMES[1]).read_text())['applications']if r['reference']=='1 Enoch 10:19')
        self.assertIn('ten thousand',historical['english'])

    def test_negative_hills_rest_full_crosspage_and_parenthetical_text_retained(self):
        self.assertEqual(record(4)['source']['pages'],[62,64]);self.assertIn('cast him there',record(4)['translation']['text'])
        self.assertTrue(record(2)['translation']['text'].startswith('[Go to Noah and]'))
        # The integration-instructions.txt retained typo calls the light
        # negative6; the exact reviewed/canonical unit is5, not6. No raw edit.
        self.assertIn('may not see light',record(5)['translation']['text'])
        self.assertIn('great day of judgment',record(6)['translation']['text'])
        self.assertIn('beneath the hills of the earth',record(12)['translation']['text'])
        self.assertNotIn('valleys',record(12)['translation']['text'])
        self.assertIn('seventy generations',record(12)['translation']['text'])
        self.assertEqual(record(16)['source']['pages'],[66,68]);self.assertIn('forever in joy',record(16)['translation']['text'])
        self.assertIn('youth and their rest in peace',record(17)['translation']['text'])
        self.assertNotIn('old age',record(17)['translation']['text'])
        self.assertIn('Never again will I send',record(22)['translation']['text'])

    def test_count_and_individual_registration_never_claim_whole10_or_all108(self):
        m=t.load_manifest(P);self.assertEqual(m['chapter_inventories'],[])
        self.assertEqual([(r['chapter'],r['units'])for r in m['source_only_count_inventories']],[(10,list(range(1,23)))])
        from tools.enoch import selected_edition_sources as source
        registry=source.registry_data();self.assertNotIn('10',registry['chapters'])
        overrides={r['verse']:r for r in source.load_unit_overrides(10)}
        for v in EXPECTED:
            self.assertEqual(registry['units'][f'10:{v}'],P.name)
            self.assertEqual(overrides[v]['source']['text'],record(v)['source']['text'])
            self.assertIn('/final/',overrides[v]['evidence'])
            for k in('selected_edition_chapter_reviewed','chapter_publication_approval','full_book_verified','graphic_publication_approved'):
                self.assertFalse(record(v)['source_correction'][k])
        for v in HOLDS:self.assertNotIn(f'10:{v}',registry['units'])
        from tools.enoch.full_repair_progress import build
        report=build();self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertNotIn(10,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertFalse(report['completion_proven']);self.assertFalse(report['artwork_publication_approval'])

    def test_full_original_editorial_history_and_exact6_plus14_successors(self):
        proof=verify_current(t.APPLICATIONS/legacy.NAMES[1])
        self.assertEqual(proof['historical_independent_review_passes_proven'],0)
        ours=[r for r in proof['reviewed_supersessions']if r['superseded_by']==P.name]
        self.assertEqual([r['reference']for r in ours],[f'1 Enoch 10:{v}'for v in EXPECTED])
        earlier=[r for r in proof['reviewed_supersessions']if r['superseded_by']=='enoch_full_repair_batch14_20261023']
        self.assertEqual(len(earlier),6);self.assertEqual(len(proof['references']),33)
        m=t.load_manifest(P)
        for ref,old in m['supersedes_legacy_editorial'].items():
            self.assertEqual(old,legacy.descriptor(ref));self.assertEqual(old['historical_scope'],'parent_editorial_application_no_imported_exact_independent_review_passes')

    def test_metadata26_precedes_runtime_snapshot_but_does_not_supply_language_votes(self):
        from tools.enoch import metadata26_evidence as metadata
        d=metadata.read_index();m=t.load_manifest(P)
        for ref,case in d['cases'].items():
            c,v=t.parse_ref(ref);rel=f'{c:03d}/{v:03d}.yaml'
            self.assertEqual(m['canonical_baseline_sha256'][rel],d['files'][case['candidate']])
        proof=metadata.verify(applied=True)
        self.assertEqual(proof['new_full_source_English_reviews'],0)
        self.assertEqual(proof['historical_payloads']['1 Enoch 26:6']['historical_full_final_payload_accepting_passes'],[2])

    def test_exact_notes_controls_prompts_and_empty_note_contract(self):
        book=reader.export_extra_canonical_book('ENO');exported={v['verse']:v for c in book['chapters']if c['chapter']==10 for v in c['verses']}
        for v in EXPECTED:
            d=record(v);notes=d['translation']['footnotes'];e=exported[v]
            if not notes:
                self.assertNotIn('footnotes',e);self.assertNotIn('footnote_review',e);continue
            self.assertEqual(e['footnotes'],notes);self.assertEqual(e['footnote_review'],'pob-enoch-paired-source-review-v1')
            for k in('text','pages','note','confidence','transcription_uncertainties','additional_translation_input'):
                if k in d['source']:self.assertEqual(e['source_critical'][k],d['source'][k])
            bundle=build_enoch_prompt(10,v)
            for k in('transcription_uncertainties','additional_translation_input'):
                if d['source'].get(k):self.assertEqual(bundle.source_payload[k],d['source'][k])
        gate=json.loads((P/'explanation-delivery-gate.json').read_text())
        self.assertFalse(gate['candidate_public_delivery_verified']);self.assertFalse(gate['candidate_live_browser_verified'])

    def test_page_windows_only_two_arrays_change_and_actual_pair_is_bound(self):
        p=t.ROOT/'sources/enoch/ethiopic/page_map.json';proof=json.loads((WINDOW/'application-proof.json').read_text())
        baseline=subprocess.check_output(['git','show',proof['source_baseline_git_commit']+':'+str(p.relative_to(t.ROOT))],cwd=t.ROOT)
        self.assertEqual(t.sha(baseline),proof['before_sha256']);self.assertEqual(t.sha(p.read_bytes()),proof['after_sha256'])
        self.assertEqual(proof['after_sha256'],'3767ebc1bb19abf174afe21aa7c992af551853cbefa358ee12f1cc18a4a19800')
        old=json.loads(baseline);new=json.loads(p.read_text())
        self.assertEqual(new['editions']['charles_1906']['chapters']['013']['pages'],[70,72])
        self.assertEqual(new['editions']['charles_1906']['chapters']['014']['pages'],[72,74,76,78])
        new['editions']['charles_1906']['chapters']['013']['pages']=[70]
        new['editions']['charles_1906']['chapters']['014']['pages']=[72,74,76]
        self.assertEqual(new,old)
        for name,digest in proof['files'].items():self.assertEqual(t.sha((WINDOW/name).read_bytes()),digest)
        a=json.loads((WINDOW/'author-ledger.json').read_text());b=json.loads((WINDOW/'independent-ledger.json').read_text());pair=json.loads((WINDOW/'paired-comparison.json').read_text())
        self.assertNotEqual(a['reviewer_id'],b['reviewer_id'])
        self.assertEqual(pair['author_ledger']['sha256'],proof['files']['author-ledger.json'])
        self.assertEqual(pair['independent_ledger']['sha256'],proof['files']['independent-ledger.json'])
        for c,n in((13,10),(14,25)):
            self.assertEqual(a['counts'][str(c)],n);self.assertEqual(b['actual_count_and_spans'][str(c)]['count'],n)
            self.assertEqual(a['source_spans'][str(c)],b['actual_count_and_spans'][str(c)]['unit_pdf_pages'])
            self.assertEqual(sorted(map(int,a['source_spans'][str(c)])),list(range(1,n+1)))
        self.assertEqual(pair['crosspage_unit_spans'],{'13:4':[70,72],'14:3':[72,74],'14:8':[74,76],'14:19':[76,78]})
        self.assertFalse(pair['wording_approval']);self.assertFalse(pair['release_approval']);self.assertEqual(pair['new_language_vote_count'],0)

    def test_no_new_reader_addresses_chapters_or_unrelated_export_deltas(self):
        m=t.load_manifest(P)
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);shutil.copytree(t.TRANSLATION,root/'1_enoch')
            for v in EXPECTED:
                rel=f'010/{v:03d}.yaml';blob=m['baseline_git_blobs'][rel]['blob']
                (root/'1_enoch'/rel).write_bytes(subprocess.check_output(['git','cat-file','blob',blob],cwd=t.ROOT))
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):before=reader.export_extra_canonical_book('ENO')
        after=reader.export_extra_canonical_book('ENO');a={c['chapter']:c for c in before['chapters']};b={c['chapter']:c for c in after['chapters']}
        self.assertEqual(set(a),set(b));self.assertEqual({c for c in a if a[c]!=b[c]},{10})
        for c in a:self.assertEqual([v['verse']for v in a[c]['verses']],[v['verse']for v in b[c]['verses']])

    def test_held_and_drifted_exact_inputs_fail_closed(self):
        m=t.load_manifest(P);bindings=m['review_bindings']['1 Enoch 10:2']
        for v in HOLDS:
            for binding in bindings:
                with self.assertRaisesRegex(ValueError,'not accepted'):t.review_row(P,binding,f'1 Enoch 10:{v}',m['files'])
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/P.name;shutil.copytree(P,p);f=p/'final/ch10-19/review-input.json';f.write_bytes(f.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'artifact changed'):t.load_manifest(p)
        self.assertEqual(t.sha((t.ROOT/'tools/export_mobile_bible.py').read_bytes()),'2258f72485099fe1014152eeb29394324415940467c2edd9d9da0d48a4a113c3')
