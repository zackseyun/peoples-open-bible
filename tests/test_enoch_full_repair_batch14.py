"""Exact paired2/6/7/8/9 partial repair, immutable history and no count grants."""
import copy
import json
from pathlib import Path
import re
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

P=t.APPLICATIONS/'enoch_full_repair_batch14_20261023'
EXPECTED=[(2,v)for v in(1,3)]+[(6,v)for v in(1,2,3,4,5,8)]+[(7,v)for v in(1,2,4,5,6)]+[(8,v)for v in(2,4)]+[(9,v)for v in(1,3,5,7,8,9)]
HOLDS=[(2,2),(3,1),(6,6),(6,7),(7,3),(8,1),(8,3),(9,2),(9,4),(9,6),(9,10),(9,11)]


def record(c,v):return yaml.load((t.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)


class FullRepairBatch14Test(unittest.TestCase):
    def test_exact21_scope_and_complete_historical_transaction(self):
        result=verify_current(P);m=t.load_manifest(P);r=json.loads((P/'application.json').read_text())
        self.assertEqual(result['references'],[f'1 Enoch {c}:{v}'for c,v in EXPECTED])
        self.assertEqual(result['candidate_files'],21);self.assertEqual(r['snapshot_file_count'],962)
        self.assertTrue(r['unrelated_canonical_files_unchanged_at_application'])
        expected=dict(m['canonical_baseline_sha256'])
        for c,v in EXPECTED:
            rel=f'{c:03d}/{v:03d}.yaml';digest=t.sha((P/f'{c:03d}-{v:03d}.candidate.yaml').read_bytes())
            expected[rel]=digest;self.assertEqual(t.corpus_hashes()[rel],digest)
        self.assertEqual(r['canonical_after_sha256'],expected)
        self.assertEqual(m['retirements'],[])
        self.assertEqual({r['reference']for r in m['not_applied']},{f'1 Enoch {c}:{v}'for c,v in HOLDS})
        for c,v in HOLDS:
            rel=f'{c:03d}/{v:03d}.yaml';self.assertEqual(t.sha((t.TRANSLATION/rel).read_bytes()),m['canonical_baseline_sha256'][rel])

    def test_full_count_scope_not_full_wording_approval(self):
        m=t.load_manifest(P);self.assertEqual(m['chapter_inventories'],[])
        self.assertEqual({r['chapter']:len(r['units'])for r in m['source_only_count_inventories']},{2:3,7:6,8:4,9:11})
        for c,v in EXPECTED:
            d=record(c,v)
            for k in ('selected_edition_chapter_reviewed','chapter_publication_approval','full_book_verified','graphic_publication_approved','manuscript_witness_certification'):
                self.assertFalse(d['source_correction'][k])

    def test_actual_source_repairs_and_retained_editorial_difficulties(self):
        one=record(2,1);self.assertIn('ይሠርቁ',one['source']['text']);self.assertIn('rise and set',one['translation']['text'])
        self.assertEqual(len(one['source']['additional_translation_input']),2)
        self.assertTrue(all(x['required_internal_explanation_marker']=='a'for x in one['source']['additional_translation_input']))
        self.assertIn('የዐርፍ',record(2,3)['source']['text']);self.assertIn('rest upon it',record(2,3)['translation']['text'])
        four=record(6,4);self.assertIn('ኢንመጠ',four['source']['text']);self.assertNotIn('ኢንምጠ',four['source']['text'])
        self.assertIn('[plan] deed',four['translation']['text']);self.assertIn('will not turn away',four['translation']['text'])
        self.assertEqual(four['source']['confidence'],'low');self.assertTrue(four['source']['transcription_uncertainties'])
        seven=record(7,1);self.assertEqual(seven['source']['text'].count('*'),4)
        self.assertIn('All four printed asterisks',seven['translation']['footnotes'][0]['text'])
        two=record(7,2);self.assertIn('፴፻',two['source']['text']);self.assertEqual(two['source']['text'].count('*'),1)
        clean=re.sub(r'\[([a-z])\]',lambda m:''if m[1]in{n['marker']for n in two['translation']['footnotes']}else m[0],two['translation']['text'])
        self.assertIn('three thousand cubits',clean)
        self.assertIn('[from it]',record(7,5)['translation']['text'])
        self.assertIn('ይስከዩ',record(9,3)['source']['text']);self.assertNotIn('ይስእዩ',record(9,3)['source']['text'])
        self.assertIn('bring their complaint',record(9,3)['translation']['text'])
        self.assertTrue(record(9,3)['translation']['text'].startswith('[And now'))

    def test_qualified_coda_preserves_h_vs_h_orthography_and_not_printed8(self):
        from tools.enoch.verse_parser import load_verse
        d=record(6,8);self.assertIn('*ሀበይተ',d['source']['text']);self.assertNotIn('ሐበይተ',d['source']['text'])
        self.assertEqual(d['source']['confidence'],'low')
        self.assertIn('unresolved_lexical_orthography_relation',{x['type']for x in d['source']['transcription_uncertainties']})
        note=d['translation']['footnotes'][0]['text']
        self.assertIn('ሐበይተ',note);self.assertIn('no numeral8',note);self.assertIn('remains unresolved',note)
        source,_=load_verse(6,8);self.assertIn('editorial',source.marker_raw.lower());self.assertIn('no printed numeral8',source.marker_raw.lower())
        original=json.loads((P/'history/ch06-language-exact-peer/independent-review.json').read_text())
        self.assertEqual(next(x for x in original['reviews']if x['reference']=='1 Enoch 6:8')['verdict'],'hold')
        new=json.loads((P/'final/ch06-8/independent-review.json').read_text())
        self.assertEqual(next(x for x in new['reviews']if x['reference']=='1 Enoch 6:8')['verdict'],'accept')
        self.assertNotEqual(original['input_sha256'],new['input_sha256'])

    def test_enum_delta_is_only_classification_not_new_full_pass(self):
        old=json.loads((P/'history/ch06-language-author/review-input.json').read_text())
        new=json.loads((P/'final/ch06/review-input.json').read_text())
        self.assertEqual(len(old),8);self.assertEqual(len(new),8)
        expected=['cultural_note','cultural_note','lexical_alternative','textual_variant','lexical_alternative','textual_variant','textual_variant','textual_variant']
        for a,b,reason in zip(old,new,expected):
            self.assertEqual(b['translation']['footnotes'][0]['reason'],reason)
            b['translation']['footnotes'][0]['reason']='source_explanation';self.assertEqual(a,b)
        peer=json.loads((P/'final/ch06/independent-provenance.json').read_text())
        self.assertEqual(peer['new_images_personally_viewed_for_this_enum_delta'],0)
        self.assertEqual(peer['inherited_own_full_review_sha256'],'67417d45bcc00bf348dd99246701a23541905eadecf303b9fc566352d2d99ac2')
        self.assertIn('no fresh',peer['image_scope'])

    def test_holds_rejected_and_exact_input_hash_drift_fails(self):
        m=t.load_manifest(P)
        for c,v in HOLDS:
            group='ch02-03'if c in(2,3)else'ch06'if c==6 else'ch07-08'if c in(7,8)else'ch09'
            ref=next(r for r in m['references']if m['review_bindings'][r][0]['input']==f'final/{group}/review-input.json')
            for b in m['review_bindings'][ref]:
                with self.assertRaisesRegex(ValueError,'not accepted'):t.review_row(P,b,f'1 Enoch {c}:{v}',m['files'])
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/P.name;shutil.copytree(P,p);f=p/'final/ch06-8/review-input.json';f.write_bytes(f.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'artifact changed'):t.load_manifest(p)

    def test_old_editorial_scope_zero_independent_passes_and_unique_fresh_successors(self):
        from tools.enoch import legacy_editorial_evidence as old,legacy6_evidence as six
        for name,n in zip(old.NAMES,(7,6)):
            proof=verify_current(t.APPLICATIONS/name);self.assertEqual(proof['historical_independent_review_passes_proven'],0)
            self.assertEqual(len([r for r in proof['reviewed_supersessions']if r['superseded_by']==P.name]),n);self.assertFalse(proof['chapter_publication_approval'])
        proof=verify_current(t.APPLICATIONS/six.NAME);self.assertEqual(proof['historical_independent_review_passes_proven'],0)
        self.assertTrue(proof['actual_parent_preimages_verified']);self.assertEqual(proof['reviewed_supersessions'],[{'reference':'1 Enoch 6:8','superseded_by':P.name}])
        for ref in ('1 Enoch 6:6','1 Enoch 6:7'):
            self.assertEqual(proof['historical_canonical_sha256'][ref],proof['current_canonical_sha256'][ref])
        from tools.textual_restoration.enoch_6_transaction import verify_applied
        with self.assertRaisesRegex(ValueError,'Applied source differs'):verify_applied()
        m=t.load_manifest(P);bad=copy.deepcopy(m);ref='1 Enoch 7:1';bad['supersedes_legacy_editorial'][ref]['historical_scope']='whole_chapter_independent_approval'
        with self.assertRaisesRegex(ValueError,'exact original scope'):old.validate_declared_successors(P,bad)

    def test_raw_legacy_artifact_drift_fails_without_mutating_original(self):
        from tools.enoch import legacy_editorial_evidence as old,legacy6_evidence as six
        for module in (old,six):
            index=module.read_index()
            with tempfile.TemporaryDirectory()as directory:
                root=Path(directory)
                for name in (module.INDEX,*index['files']):
                    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(t.ROOT/name,p)
                name=next(iter(index['files']));f=root/name;f.write_bytes(f.read_bytes()+b'\n')
                with patch.object(t,'ROOT',root):
                    with self.assertRaisesRegex(ValueError,'raw artifact differs|original artifact differs'):module.read_index()

    def test_exact_notes_controls_export_prompt_and_no_visible_note_marker_contract_change(self):
        exported={(c['chapter'],v['verse']):v for c in reader.export_extra_canonical_book('ENO')['chapters']for v in c['verses']}
        for c,v in EXPECTED:
            d=record(c,v);e=exported[(c,v)]
            if not d['translation']['footnotes']:
                self.assertNotIn('footnotes',e);self.assertNotIn('footnote_review',e)
                continue
            self.assertEqual(e['footnotes'],d['translation']['footnotes']);self.assertEqual(e['footnote_review'],'pob-enoch-paired-source-review-v1')
            for key in ('text','pages','note','confidence','transcription_uncertainties','additional_translation_input'):
                if key in d['source']:self.assertEqual(e['source_critical'][key],d['source'][key])
            prompt=build_enoch_prompt(c,v)
            for key in ('transcription_uncertainties','additional_translation_input'):
                if d['source'].get(key):self.assertEqual(prompt.source_payload[key],d['source'][key])
        self.assertEqual(t.sha((t.ROOT/'tools/export_mobile_bible.py').read_bytes()),'2258f72485099fe1014152eeb29394324415940467c2edd9d9da0d48a4a113c3')
        gate=json.loads((P/'explanation-delivery-gate.json').read_text());self.assertFalse(gate['candidate_public_delivery_verified']);self.assertFalse(gate['candidate_live_browser_verified'])

    def test_ci_pins_old_parent_objects_and_current_counterproof(self):
        workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        for commit in ('839ec57460182b422cd72fab65355c39726f7254','f436ae1f5e6f3b4764ccd3102a4d0828ad67ffe8','c77a1868d83428a0814c44b7922cb6096362df9e'):
            self.assertIn('git fetch --no-tags --depth=2 origin '+commit,workflow)
        for name in ('test_enoch_full_repair_batch14.py','test_enoch_canonical_address_maps.py','test_enoch_historical14_recovered.py'):
            self.assertIn(name,workflow)

    def test_partial_source_ingress_is_exact_reviewed_input_not_current_echo(self):
        from tools.enoch import selected_edition_sources as sources
        registry=sources.registry_data()
        for c,v in EXPECTED:
            self.assertNotIn(str(c),registry['chapters'])
            self.assertEqual(registry['units'][f'{c}:{v}'],P.name)
            rows={r['verse']:r for r in sources.load_unit_overrides(c)}
            self.assertEqual(rows[v]['source']['text'],record(c,v)['source']['text'])
            self.assertIn('/final/',rows[v]['evidence'])
        for c,v in HOLDS:self.assertNotIn(f'{c}:{v}',registry['units'])

    def test_no_new_reader_chapter_address_or_unrelated_export_change(self):
        m=t.load_manifest(P)
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);shutil.copytree(t.TRANSLATION,root/'1_enoch')
            for c,v in EXPECTED:
                rel=f'{c:03d}/{v:03d}.yaml';blob=m['baseline_git_blobs'][rel]['blob']
                (root/'1_enoch'/rel).write_bytes(subprocess.check_output(['git','cat-file','blob',blob],cwd=t.ROOT))
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):before=reader.export_extra_canonical_book('ENO')
        after=reader.export_extra_canonical_book('ENO');a={c['chapter']:c for c in before['chapters']};b={c['chapter']:c for c in after['chapters']}
        self.assertEqual(set(a),set(b));self.assertEqual({c for c in a if a[c]!=b[c]},{2,6,7,8,9})
        for c in a:self.assertEqual([v['verse']for v in a[c]['verses']],[v['verse']for v in b[c]['verses']])

    def test_current_progress_keeps_partial_chapters_and_all108_open(self):
        from tools.enoch.full_repair_progress import build
        report=build();self.assertEqual(report['evidence_inventory_warnings'],[])
        for c in (2,3,6,7,8,9):self.assertNotIn(c,report['chapters_with_complete_imported_selected_edition_review'])
        six=next(x for x in report['chapters']if x['chapter']==6)
        self.assertEqual(six['selected_printed_source_units'],list(range(1,8)))
        self.assertEqual(six['expected_units'],list(range(1,9)));self.assertFalse(six['canonical_source_unit_mapping_pending'])
        self.assertFalse(report['completion_proven']);self.assertFalse(report['artwork_publication_approval'])
