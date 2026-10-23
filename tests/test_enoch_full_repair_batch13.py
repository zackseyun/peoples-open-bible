"""Current paired5/11/12/21 repairs, historical counterproof and held scope."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t, legacy21_evidence as legacy
from tools.enoch.current_evidence import verify_current
from tools.enoch.full_repair_progress import build
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader

P = t.APPLICATIONS/'enoch_full_repair_batch13_20261023'
EXPECTED = [(5,v) for v in (2,3,4,5,7,8,9)] + [(11,1),(11,2)] + \
           [(12,v) for v in (1,2,3,5,6)] + [(21,v) for v in (1,2,4,5,7,8,9,10)]
HOLDS = [(5,1),(5,6),(12,4),(21,3),(21,6)]


def record(c,v):
    return yaml.load((t.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)


class FullRepairBatch13Test(unittest.TestCase):
    def test_exact_scope_and_current_bytes_with_five_unchanged_holds(self):
        result=verify_current(P);m=t.load_manifest(P)
        self.assertEqual(result['references'],[f'1 Enoch {c}:{v}' for c,v in EXPECTED])
        self.assertEqual(result['candidate_files'],22)
        receipt=json.loads((P/'application.json').read_text())
        self.assertEqual(receipt['snapshot_file_count'],962)
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        self.assertEqual(m['retirements'],[])
        self.assertEqual({r['reference'] for r in m['not_applied']},{f'1 Enoch {c}:{v}'for c,v in HOLDS})
        self.assertTrue(all(r['verdicts']==['hold','hold']for r in m['not_applied']))
        for c,v in HOLDS:
            rel=f'{c:03d}/{v:03d}.yaml'
            self.assertEqual(t.sha((t.TRANSLATION/rel).read_bytes()),m['canonical_baseline_sha256'][rel])
        # Verify the complete historical transaction, not equality between a
        # dated snapshot and every future legitimate repair elsewhere.
        expected_after=dict(m['canonical_baseline_sha256'])
        current=t.corpus_hashes()
        for c,v in EXPECTED:
            rel=f'{c:03d}/{v:03d}.yaml'
            digest=t.sha((P/f'{c:03d}-{v:03d}.candidate.yaml').read_bytes())
            expected_after[rel]=digest
            self.assertEqual(current[rel],digest)
        self.assertEqual(receipt['canonical_after_sha256'],expected_after)

    def test_complete11_only_not_partial_count_approval(self):
        m=t.load_manifest(P)
        self.assertEqual([(r['chapter'],r['units'])for r in m['chapter_inventories']],[(11,[1,2])])
        self.assertEqual({r['chapter']:len(r['units'])for r in m['source_only_count_inventories']},{5:9,12:6,21:10})
        for c,v in EXPECTED:
            d=record(c,v)
            self.assertEqual(d['source_correction']['selected_edition_chapter_reviewed'],c==11)
            self.assertFalse(d['source_correction']['chapter_publication_approval'])
            self.assertFalse(d['source_correction']['graphic_publication_approved'])

    def test_complete_crosspage_units_not_truncated_or_misaddressed(self):
        d=record(5,9)
        self.assertEqual(d['source']['pages'],[48,50])
        self.assertIn('throughout all the days of their lives',d['translation']['text'])
        self.assertIn('everlasting peace',d['translation']['text'])
        d=record(21,9)
        self.assertEqual(d['source']['pages'],[92,94])
        self.assertIn('painful torment',d['translation']['text'])
        self.assertIn('I answered[a]',d['translation']['text'])
        self.assertIn('editorial restoration',d['translation']['footnotes'][0]['text'])
        self.assertNotIn('heaven-like',d['translation']['text'])
        proof=json.loads((P/'history/ch21-exact-peer/provenance.json').read_text())
        self.assertIn('pain/torment',proof['ledger_correction'])

    def test_selected_critical_constitution_not_silent_normalization(self):
        one=record(11,1);two=record(11,2)
        self.assertEqual(one['source']['text'].count('*'),2)
        self.assertNotIn('*',two['source']['text'])
        self.assertIn('uprightness',two['translation']['text'])
        self.assertIn('had been hidden',record(12,1)['translation']['text'])
        self.assertNotIn('taken up',record(12,1)['translation']['text'])
        d=record(12,2)
        self.assertIn('*†ኵሉ፡†',d['source']['text'])
        self.assertEqual(d['source']['confidence'],'low')
        self.assertEqual(d['source']['transcription_uncertainties'][0]['type'],'intrinsic_editorial_corruption')
        self.assertEqual(d['source']['additional_translation_input'],[])
        self.assertIn('intrinsically uncertain',d['translation']['footnotes'][0]['text'])
        self.assertIn('was blessing',record(12,3)['translation']['text'])
        self.assertNotIn('standing',record(12,3)['translation']['text'])
        self.assertIn('neither peace nor forgiveness',record(12,5)['translation']['text'])
        self.assertIn('because',record(12,6)['translation']['text'])
        self.assertIn('neither mercy[b] nor peace',record(12,6)['translation']['text'])
        self.assertIn('[ነጽሮ፡]',record(21,7)['source']['text'])

    def test_metadata_delta_and_serializer_do_not_invent_full_passes(self):
        original=json.loads((P/'history/ch11-12-author-resume/v2/review-input.json').read_text())
        revised=json.loads((P/'final/ch11-12/review-input.json').read_text())
        self.assertEqual(revised[3]['reference'],'1 Enoch 12:2')
        revised[3]['source']['transcription_uncertainties']=[]
        self.assertEqual(original,revised)
        author=json.loads((P/'final/ch11-12/author-provenance.json').read_text())
        peer=json.loads((P/'final/ch11-12/independent-provenance.json').read_text())
        self.assertEqual(author['reviewer_id'],'/root')
        self.assertFalse(author['fresh_full_source_or_English_review_claimed'])
        self.assertEqual(peer['reviewer_id'],'/root/enoch11_12_exact_peer')
        self.assertEqual(len(peer['scan_image_sha256']),39)
        self.assertIn('No fresh',peer['identity_and_exposure'])
        raw=json.loads((P/'history/ch21-author-resume/v2/author-review.json').read_text())
        wrapper=json.loads((P/'final/ch21/author-review.json').read_text())
        self.assertEqual(raw['rows'],wrapper['reviews'])
        self.assertEqual(wrapper['original_review_sha256'],t.sha((P/'history/ch21-author-resume/v2/author-review.json').read_bytes()))
        self.assertEqual(len(json.loads((P/'final/ch21/author-provenance.json').read_text())['scan_image_sha256']),59)

    def test_legacy21_exact_original_payload_and_count_flag_not_chapter_approval(self):
        result=verify_current(t.APPLICATIONS/legacy.NAME)
        self.assertEqual(result['historical_accepted_individual_review_passes'],2)
        self.assertEqual(len(result['reviewed_supersessions']),1)
        self.assertNotEqual(result['historical_canonical_sha256'],result['current_canonical_sha256'])
        self.assertFalse(result['chapter_publication_approval'])
        old=legacy.historical_record();current=record(21,10)
        self.assertEqual(old['source']['text'],current['source']['text'])
        self.assertIn('and here',old['translation']['text'])
        self.assertIn('and there',current['translation']['text'])
        for n in (1,2):
            raw=json.loads((t.APPLICATIONS/legacy.REVIEW/f'pass{n}/review.json').read_text())
            self.assertTrue(raw['chapter_complete'])
            self.assertEqual(raw['reviews'][5]['verdict'],'hold')
        receipt=json.loads((t.APPLICATIONS/legacy.NAME/'application.json').read_text())
        self.assertFalse(receipt['chapter_editorially_accepted'])
        self.assertEqual(receipt['clipped_existing_reference'],'1 Enoch 21:9')

    def test_legacy5_explicit_exact_preimage_chain_and_unchanged_shared_exporter(self):
        m=t.load_manifest(P);prior=m['supersedes']['1 Enoch 5:9']
        old=t.APPLICATIONS/prior['package']
        self.assertEqual(prior['manifest_sha256'],t.sha((old/'manifest.json').read_bytes()))
        self.assertEqual(prior['candidate_sha256'],m['canonical_baseline_sha256']['005/009.yaml'])
        self.assertNotEqual(prior['candidate_sha256'],t.sha((t.TRANSLATION/'005/009.yaml').read_bytes()))
        self.assertEqual(t.sha((t.ROOT/'tools/export_mobile_bible.py').read_bytes()),'2258f72485099fe1014152eeb29394324415940467c2edd9d9da0d48a4a113c3')

    def test_exact_holds_and_source_drift_fail_closed(self):
        m=t.load_manifest(P)
        for c,v in HOLDS:
            group='ch05'if c==5 else 'ch21'if c==21 else 'ch11-12'
            representative=next(ref for ref in m['references']if any(b['input']==f'final/{group}/review-input.json'for b in m['review_bindings'][ref]))
            for binding in m['review_bindings'][representative]:
                with self.assertRaisesRegex(ValueError,'not accepted'):
                    t.review_row(P,binding,f'1 Enoch {c}:{v}',m['files'])
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/P.name;shutil.copytree(P,p)
            f=p/'final/ch21/review-input.json';f.write_bytes(f.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'artifact changed'):
                t.load_manifest(p)

    def test_legacy_artifact_drift_and_scope_laundering_fail_closed(self):
        index=legacy.read_index()
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory)
            for name in [legacy.INDEX,*index['files']]:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(t.ROOT/name,target)
            name=next(n for n in index['files']if n.endswith('pass1/review.json'))
            (root/name).write_bytes((root/name).read_bytes()+b'\n')
            with patch.object(t,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'original artifact differs'):
                    legacy.read_index()
        m=t.load_manifest(P);bad=copy.deepcopy(m)
        bad['supersedes_legacy21'][legacy.REF]['historical_scope']='whole_chapter_approved'
        with self.assertRaisesRegex(ValueError,'scope differs'):
            legacy.validate_declared_successor(P,bad)

    def test_page_map_only_adds_independently_confirmed_continuation(self):
        p=t.ROOT/'sources/enoch/ethiopic/page_map.json'
        current=json.loads(p.read_text())
        before=json.loads(subprocess.check_output(['git','show','7c290e9d069ccabdb91eeccfd82ab592c80aef31:'+str(p.relative_to(t.ROOT))],cwd=t.ROOT))
        self.assertEqual(current['editions']['charles_1906']['chapters']['005']['pages'],[46,48,50])
        current['editions']['charles_1906']['chapters']['005']['pages']=[46,48]
        self.assertEqual(before,current)
        proof=json.loads((t.ROOT/'sources/enoch/coverage/page-map5-continuation-20261023.json').read_text())
        self.assertFalse(proof['wording_approval'])
        self.assertEqual(proof['after_sha256'],t.sha(p.read_bytes()))
        for rel,digest in proof['source_first_input_hashes'].items():
            self.assertEqual(t.sha((P/'history'/rel).read_bytes()),digest)

    def test_exact_reviewed_explanations_and_controls_survive_export_and_prompt(self):
        book=reader.export_extra_canonical_book('ENO')
        published={(c['chapter'],v['verse']):v for c in book['chapters']for v in c['verses']}
        for c,v in EXPECTED:
            d=record(c,v);notes=d['translation'].get('footnotes',[])
            if not notes:continue
            exported=published[(c,v)]
            self.assertEqual(exported['footnote_review'],'pob-enoch-paired-source-review-v1')
            self.assertEqual(exported['footnotes'],notes)
            for k in ('text','pages','note','confidence','transcription_uncertainties','additional_translation_input'):
                if k in d['source']:self.assertEqual(exported['source_critical'][k],d['source'][k])
            bundle=build_enoch_prompt(c,v)
            for k in ('transcription_uncertainties','additional_translation_input'):
                if d['source'].get(k):self.assertEqual(bundle.source_payload[k],d['source'][k])

    def test_export_has_no_new_chapters_and_no_unrelated_delta(self):
        m=t.load_manifest(P)
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);shutil.copytree(t.TRANSLATION,root/'1_enoch')
            for c,v in EXPECTED:
                rel=f'{c:03d}/{v:03d}.yaml';blob=m['baseline_git_blobs'][rel]['blob']
                (root/'1_enoch'/rel).write_bytes(subprocess.check_output(['git','cat-file','blob',blob],cwd=t.ROOT))
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):before=reader.export_extra_canonical_book('ENO')
        after=reader.export_extra_canonical_book('ENO')
        a={c['chapter']:c for c in before['chapters']};b={c['chapter']:c for c in after['chapters']}
        self.assertEqual(set(a),set(b))
        changed={c for c in a if a[c]!=b[c]}
        self.assertEqual(changed,{5,11,12,21})
        for c in changed:self.assertEqual([v['verse']for v in a[c]['verses']],[v['verse']for v in b[c]['verses']])

    def test_source_registry_uses_exact_accepted_inputs_not_canonical_echo(self):
        from tools.enoch.selected_edition_sources import registry_data,load_chapter,load_unit_overrides
        registry=registry_data()
        self.assertEqual(registry['chapters']['11'],P.name)
        self.assertEqual([r['verse'] for r in load_chapter(11)],[1,2])
        for c in (5,12,21):
            self.assertNotIn(str(c),registry['chapters'])
            overrides={r['verse']:r for r in load_unit_overrides(c)}
            for cc,v in EXPECTED:
                if cc==c:
                    self.assertEqual(registry['units'][f'{c}:{v}'],P.name)
                    self.assertEqual(overrides[v]['source']['text'],record(c,v)['source']['text'])
            for cc,v in HOLDS:
                if cc==c:self.assertNotIn(f'{c}:{v}',registry['units'])

    def test_legacy12_parent_record_is_not_upgraded_to_independent_approval(self):
        from tools.enoch import legacy12_evidence as old
        from tools.textual_restoration import enoch_12_transaction as strict
        result=verify_current(t.APPLICATIONS/old.NAME)
        self.assertEqual(result['historical_independent_review_passes_proven'],0)
        self.assertEqual(result['original_parent_editorial_decisions_preserved'],6)
        self.assertEqual(len(result['reviewed_supersessions']),5)
        self.assertTrue(result['held_preimage_unchanged'])
        self.assertEqual(result['historical_canonical_sha256']['012/004.yaml'],result['current_canonical_sha256']['012/004.yaml'])
        for v in (1,2,3,5,6):
            self.assertNotEqual(result['historical_canonical_sha256'][f'012/{v:03d}.yaml'],result['current_canonical_sha256'][f'012/{v:03d}.yaml'])
        with self.assertRaisesRegex(ValueError,'Applied source differs'):
            strict.verify_applied()
        declaration=old.read_declaration()
        self.assertEqual(declaration['successor_manifest_sha256'],t.sha((P/'manifest.json').read_bytes()))
        self.assertTrue(declaration['no_historical_receipt_or_current_application_rewritten'])

    def test_current_unregistered_fallback_stays_raw_while_exact5_overrides_remain_separate(self):
        from tools.enoch import selected_edition_sources as sources,verse_parser as parser
        registry=copy.deepcopy(sources.registry_data())
        self.assertNotIn('5',registry['chapters'])
        registry['units']={key:value for key,value in registry['units'].items()if not key.startswith('5:')}
        with patch.object(sources,'registry_data',return_value=registry):
            self.assertIsNone(sources.load_chapter(5))
            self.assertEqual(sources.load_unit_overrides(5),[])
            self.assertEqual(parser.parse_chapter(5),parser.parse_ocr_chapter(5))
        self.assertEqual([r['verse']for r in sources.load_unit_overrides(5)],[2,3,4,5,7,8,9])
        self.assertNotEqual(parser.parse_chapter(5),parser.parse_ocr_chapter(5))

    def test_ci_fetches_actual_original_and_replay_tree_and_runs_current_counterproof(self):
        workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        for sha in ('f59737b6fe9071b9f98c2a1b75375518d508debf','0eba75255fa8d6ebefcf4fc79ef1e4b405ab442e','7c290e9d069ccabdb91eeccfd82ab592c80aef31'):
            self.assertIn('git fetch --no-tags --depth=1 origin '+sha,workflow)
        for name in ('test_enoch_full_repair_batch13.py','test_enoch21_10_application.py','test_enoch_low_risk_transaction.py','test_enoch_12_transaction.py','test_enoch_reviewed_sources.py'):
            self.assertIn(name,workflow)

    def test_progress_does_not_close_the_book_or_partial_chapters(self):
        report=build()
        self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertEqual(report['canonical_file_count'],962)
        self.assertIn(11,report['chapters_with_complete_imported_selected_edition_review'])
        for c in (5,12,21):self.assertNotIn(c,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertFalse(report['completion_proven'])
        self.assertFalse(report['artwork_publication_approval'])
