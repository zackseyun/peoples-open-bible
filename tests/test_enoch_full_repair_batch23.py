"""One exact language pair plus a separately approved confidence-only qualifier."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t,confidence27_evidence as confidence
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader

P=t.APPLICATIONS/'enoch_full_repair_batch23_20261024'
REF='1 Enoch 27:4'
MANIFEST='64cf47676c58ca676b126475bf9ba0753509402d474b94dad21e8e32ec6e5793'


def record():return yaml.load((t.TRANSLATION/'027/004.yaml').read_bytes(),Loader=t.LOADER)


class FullRepairBatch23Test(unittest.TestCase):
    def test_single_existing_unit_and_complete964_postmap(self):
        self.assertEqual(t.sha((P/'manifest.json').read_bytes()),MANIFEST)
        m=t.load_manifest(P);r=json.loads((P/'application.json').read_text())
        self.assertEqual(verify_current(P)['references'],[REF])
        prior=json.loads((t.APPLICATIONS/'enoch_full_repair_batch22_20261024/application.json').read_text())
        self.assertEqual(m['canonical_baseline_sha256'],prior['canonical_after_sha256'])
        expected=dict(m['canonical_baseline_sha256']);expected['027/004.yaml']=t.sha((P/'027-004.candidate.yaml').read_bytes())
        self.assertEqual(r['canonical_after_sha256'],expected);self.assertEqual(r['snapshot_file_count'],964)
        self.assertEqual(t.sha((t.TRANSLATION/'027/004.yaml').read_bytes()),expected['027/004.yaml'])
        self.assertEqual(m['retirements'],[]);self.assertEqual(m['supersedes'],{})

    def test_actual_baseline_is_existing_unreviewed_unit_not_fictitious_restore(self):
        m=t.load_manifest(P);self.assertEqual(m['source_baseline_git_commit'],'a2a44ea4dddfc6c4e0976c3b14825260cf1d9a13')
        t.verify_git_preimage(m,'027/004.yaml',m['canonical_baseline_sha256']['027/004.yaml'])
        self.assertEqual(record()['review_history'][0]['sha256'],m['canonical_baseline_sha256']['027/004.yaml'])

    def test_original_exact_full_language_pair_remains_primary(self):
        m=t.load_manifest(P);d=json.loads((P/m['confidence_metadata_evidence']).read_text())
        self.assertEqual(d['language_bindings'],m['review_bindings'][REF])
        self.assertEqual(t.sha((P/d['old_input']).read_bytes()),confidence.OLD)
        self.assertEqual({m['files'][b['review']]for b in d['language_bindings']},confidence.LANGUAGE_REVIEWS)
        self.assertEqual({b['reviewer_id']for b in d['language_bindings']},{'/root/enoch27_author','/root/enoch09_language_author'})
        for b in d['language_bindings']:
            row=t.review_row(P,b,REF,m['files']);self.assertEqual(row['source']['confidence'],0.91)
            self.assertTrue(json.loads((P/b['provenance']).read_text())['scan_image_sha256'])

    def test_only_confidence_changes_no_extra_English_or_source_views(self):
        m=t.load_manifest(P);d=json.loads((P/m['confidence_metadata_evidence']).read_text());old=json.loads((P/d['old_input']).read_text());new=json.loads((P/d['new_input']).read_text())
        expected=copy.deepcopy(old);expected[0]['source']['confidence']='medium';self.assertEqual(new,expected)
        self.assertEqual(t.sha((P/d['new_input']).read_bytes()),confidence.NEW)
        self.assertEqual(confidence.validate(P,m),new[0]['source'])
        self.assertEqual(record()['translation'],old[0]['translation'])
        for key in('extra_English_language_passes','extra_provider_calls','extra_photo_views'):self.assertEqual(d[key],0)
        self.assertFalse(d['derived_adapter_used_as_primary'])

    def test_empty_metadata_photo_map_is_honest_and_not_a_language_approval(self):
        m=t.load_manifest(P);d=json.loads((P/m['confidence_metadata_evidence']).read_text())
        peer=next(b for b in d['metadata_bindings']if b['role']=='independent_reviewer')
        self.assertEqual(json.loads((P/peer['provenance']).read_text())['scan_image_sha256'],{})
        with self.assertRaisesRegex(ValueError,'lacks pinned primary scan evidence'):t.review_row(P,peer,REF,m['files'])
        self.assertTrue(confidence.validate(P,m))
        self.assertEqual({m['files'][b['review']]for b in d['metadata_bindings']},confidence.METADATA_REVIEWS)

    def test_metadata_pair_cannot_replace_original_language_binding(self):
        with tempfile.TemporaryDirectory()as directory:
            q=Path(directory)/'package';shutil.copytree(P,q);m=json.loads((q/'manifest.json').read_text());p=q/m['confidence_metadata_evidence'];d=json.loads(p.read_text())
            m['review_bindings'][REF]=d['metadata_bindings'];d['language_bindings']=d['metadata_bindings'];p.write_text(json.dumps(d));m['files'][p.name]=t.sha(p.read_bytes());(q/'manifest.json').write_text(json.dumps(m))
            with self.assertRaises(ValueError):t.verify(q,evidence_only=True)

    def test_source_days_judgment_mercy_and_apportionment_retain_no_extra_object(self):
        d=record();s=d['source'];text=d['translation']['text']
        self.assertEqual(s['text'],'በመዋዕል፡ ኵነኔዮሙ፡ ይባርክዎ፡ በምሕረቱ፡ በከመ፡ ከፈለዮሙ።')
        self.assertEqual(s['confidence'],'medium')
        for phrase in('days of their judgment','his mercy','what he apportioned to them'):self.assertIn(phrase,text)
        self.assertNotIn('inheritance',text);self.assertFalse(text.startswith('And'))
        self.assertEqual([n['marker']for n in d['translation']['footnotes']],['a','b'])

    def test_count_is_external_structural_not_fabricated_fullfive_input(self):
        m=t.load_manifest(P);self.assertEqual(m['chapter_inventories'],[]);self.assertEqual(m['source_only_count_inventories'],[])
        from tools.enoch import selected_edition_sources as source,count26_27_33_evidence as counts
        self.assertEqual(counts.load()[27]['units'],list(range(1,6)))
        rows=source.load_unit_overrides(27);self.assertEqual([r['verse']for r in rows],[4])
        self.assertEqual(rows[0]['source']['confidence'],'medium')
        self.assertIn('confidence-delta-evidence.json',rows[0]['evidence'])
        from tools.enoch import audit_pob_source_coverage as coverage
        self.assertEqual(coverage.EXPECTED_VERSES[27],5)
        undeclared={c:n for c,n in coverage.EXPECTED_VERSES.items()if c!=27}
        with patch.object(coverage,'EXPECTED_VERSES',undeclared):
            with self.assertRaisesRegex(ValueError,'declared printed count/address'):source.load_unit_overrides(27)
        registry=source.registry_data();self.assertNotIn('27',registry['chapters'])
        self.assertEqual(registry['units']['27:4'],P.name)
        for v in(1,2,3,5):self.assertNotIn(f'27:{v}',registry['units'])

    def test_exact_source_notes_and_qualified_confidence_survive_prompt_and_export(self):
        d=record();out=reader._export_record_verse(4,d);prompt=build_enoch_prompt(27,4)
        self.assertEqual(out['text'],d['translation']['text']);self.assertEqual(out['footnotes'],d['translation']['footnotes']);self.assertEqual(out['footnote_review'],reader.PROTOCOL)
        for key in('text','pages','confidence','transcription_uncertainties','additional_translation_input'):
            if key in d['source']:self.assertEqual(out['source_critical'][key],d['source'][key]);self.assertEqual(prompt.source_payload[key],d['source'][key])
        self.assertFalse(json.loads((P/'explanation-delivery-gate.json').read_text())['candidate_live_browser_verified'])

    def test_unreviewed_English_or_confidence_only_bypass_is_rejected(self):
        for target in('English','unapproved-confidence'):
            with self.subTest(target=target),tempfile.TemporaryDirectory()as directory:
                q=Path(directory)/'package';shutil.copytree(P,q);p=q/'027-004.candidate.yaml';d=yaml.load(p.read_bytes(),Loader=t.LOADER)
                if target=='English':d['translation']['text']+=' an inheritance'
                else:d['source']['confidence']='low'
                p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m=json.loads((q/'manifest.json').read_text());m['files'][p.name]=t.sha(p.read_bytes());(q/'manifest.json').write_text(json.dumps(m))
                with self.assertRaises(ValueError):t.verify(q,evidence_only=True)

    def test_no_newreader_chapter_or_unrelated_export_change(self):
        m=t.load_manifest(P)
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);before=root/'1_enoch';shutil.copytree(t.TRANSLATION,before);blob=m['baseline_git_blobs']['027/004.yaml']['blob'];(before/'027/004.yaml').write_bytes(subprocess.check_output(['git','cat-file','blob',blob],cwd=t.ROOT))
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):old=reader.export_extra_canonical_book('ENO')
            new=reader.export_extra_canonical_book('ENO')
        a={c['chapter']:c for c in old['chapters']};b={c['chapter']:c for c in new['chapters']};self.assertEqual(set(a),set(b))
        self.assertEqual({c:v for c,v in a.items()if c!=27},{c:v for c,v in b.items()if c!=27})

    def test_book_and_neighbor_language_scope_not_inflated(self):
        from tools.enoch.full_repair_progress import build
        p=build();self.assertGreaterEqual(p['current_units_with_imported_review_evidence'],471)
        self.assertEqual(p['evidence_inventory_warnings'],[]);self.assertNotIn(27,p['chapters_with_complete_imported_selected_edition_review']);self.assertFalse(p['completion_proven'])
        flags=record()['source_correction']
        for key in('selected_edition_chapter_reviewed','chapter_publication_approval','full_book_verified','human_specialist_certification','manuscript_witness_certification','graphic_publication_approved'):self.assertFalse(flags[key])
        self.assertEqual(record()['ai_draft']['model_id'],'not_reported')


if __name__=='__main__':unittest.main()
