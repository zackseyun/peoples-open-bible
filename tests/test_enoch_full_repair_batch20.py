"""Whole selected17 review with explicit critical qualifications and six successors."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader

P=t.APPLICATIONS/'enoch_full_repair_batch20_20261024'
OLD=t.APPLICATIONS/'enoch_full_repair_batch11_20261022'
MANIFEST='e6ecdc3955bb53a4a108510d0b553a58554fcbd10ce4231cffe23acdd2fbddba'
REFS=[f'1 Enoch 17:{v}'for v in range(1,9)]


def record(v):
    return yaml.load((t.TRANSLATION/f'017/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)


class FullRepairBatch20Test(unittest.TestCase):
    def test_exact_eight_payloads_and_complete_962_file_postmap(self):
        self.assertEqual(t.sha((P/'manifest.json').read_bytes()),MANIFEST)
        m=t.load_manifest(P);r=json.loads((P/'application.json').read_text())
        self.assertEqual(verify_current(P)['references'],REFS)
        self.assertEqual(m['source_baseline_git_commit'],'d03dadea03d61bccea631399659c794532d619fd')
        self.assertEqual(r['snapshot_file_count'],962)
        expected=dict(m['canonical_baseline_sha256'])
        for v in range(1,9):expected[f'017/{v:03d}.yaml']=t.sha((P/f'017-{v:03d}.candidate.yaml').read_bytes())
        self.assertEqual(r['canonical_after_sha256'],expected)
        self.assertTrue(r['unrelated_canonical_files_unchanged_at_application'])
        # The complete map proves the application-time snapshot. Do not freeze
        # unrelated future repairs; current exact17 is checked separately.
        for v in range(1,9):self.assertEqual(t.sha((t.TRANSLATION/f'017/{v:03d}.yaml').read_bytes()),expected[f'017/{v:03d}.yaml'])
        self.assertEqual(m['retirements'],[])

    def test_only_six_exact_old_owners_are_superseded(self):
        m=t.load_manifest(P);old=t.load_manifest(OLD)
        self.assertEqual(set(m['supersedes']),{f'1 Enoch 17:{v}'for v in(1,2,4,5,7,8)})
        for ref,row in m['supersedes'].items():
            _,v=t.parse_ref(ref)
            self.assertEqual(row,{'package':OLD.name,'manifest_sha256':t.sha((OLD/'manifest.json').read_bytes()),'candidate_sha256':old['files'][f'017-{v:03d}.candidate.yaml']})
            self.assertEqual(m['canonical_baseline_sha256'][f'017/{v:03d}.yaml'],row['candidate_sha256'])
        result=verify_current(OLD)
        self.assertEqual({r['reference']for r in result['reviewed_supersessions'] if r['reference'].startswith('1 Enoch 17:')},set(m['supersedes']))

    def test_full_exact_input_and_count_certificate_do_not_invent_extra_passes(self):
        m=t.load_manifest(P);inp=P/'final/ch17-full/review-input.json'
        self.assertEqual(t.sha(inp.read_bytes()),'af45d372fe33cc6b52c7af3c076a5e4c4fa481acdabf1e079c65fc5d9936ee47')
        self.assertEqual([r['reference']for r in json.loads(inp.read_text())],REFS)
        for binding in m['review_bindings'][REFS[0]]:
            for ref in REFS:t.review_row(P,binding,ref,m['files'])
        certificate=m['chapter_inventories'][0]
        self.assertEqual(certificate['chapter'],17);self.assertEqual(certificate['units'],list(range(1,9)))
        self.assertTrue(certificate['independent_count_confirmation'])
        self.assertEqual(m['source_only_count_inventories'],[])
        for v in range(1,9):self.assertTrue(record(v)['source_correction']['selected_edition_chapter_reviewed'])

    def test_spatial_crux_keeps_literal_terms_quivers_and_visible_copula(self):
        d=record(3);s=d['source'];text=d['translation']['text']
        self.assertIn('*አጽናፍ',s['text']);self.assertEqual(s['confidence'],'low')
        for phrase in('at the extremities, in the depth','[there were]','their quivers','sword of fire','all the lightnings'):self.assertIn(phrase,text)
        for phrase in('heavens','storehouses'):self.assertNotIn(phrase,text)
        self.assertIn('exact location and construction remain uncertain',d['translation']['footnotes'][0]['text'])
        self.assertFalse(s.get('additional_translation_input'))

    def test_intrinsic_speaking_gloss_remains_in_source_and_explained_not_narrated(self):
        d=record(4);s=d['source'];note=d['translation']['footnotes'][0]['text']
        self.assertIn('[ዘይትናገር፡]',s['text']);self.assertNotIn('speaks',d['translation']['text'])
        self.assertIn('which speaks',note);self.assertIn('Ethiopic gloss',note)
        self.assertIn('reported superscription and Greek comparison',note)
        self.assertEqual(s['transcription_uncertainties'][0]['status'],'source_preserved_English_omission_explained')
        self.assertFalse(s.get('additional_translation_input'))

    def test_parenthesized_negative_is_not_a_silent_certainty_claim(self):
        d=record(6);s=d['source'];note=d['translation']['footnotes'][0]['text']
        self.assertIn('(ኢ)ያንሶሱ',s['text']);self.assertEqual(s['confidence'],'low')
        self.assertIn('where no flesh walks',d['translation']['text'])
        self.assertIn('all flesh walks there',note)
        self.assertEqual(s['transcription_uncertainties'][0]['status'],'negative_reading_adopted_with_positive_alternative_disclosed')

    def test_gloom_inflection_is_not_normalized_to_headword_or_Greek_winds(self):
        d=record(7);s=d['source'];text=d['translation']['text'];note=d['translation']['footnotes'][0]['text']
        self.assertIn('ቆባሬት',s['text']);self.assertNotIn('ቀበሬት',s['text'])
        self.assertIn('winter darkness',text);self.assertIn('from the whole deep',text)
        self.assertNotIn('winds',text);self.assertNotIn('all the waters',text)
        self.assertEqual(s['pages'],[84,86]);self.assertEqual(s['confidence'],'low')
        self.assertIn('ቆባር',note);self.assertIn('rather than normalized',note)

    def test_remaining_complete_clauses_keep_storm_west_and_singular_mouth(self):
        self.assertIn('whenever they wished',record(1)['translation']['text'])
        self.assertIn('place of whirlwind',record(2)['translation']['text'])
        self.assertIn('toward the west',record(5)['translation']['text'])
        self.assertIn('the mouth of all the earth’s rivers',record(8)['translation']['text'])
        self.assertNotIn('mouths',record(8)['translation']['text'])
        self.assertEqual(record(8)['source']['pages'],[86])

    def test_exact_notes_source_controls_and_critical_brackets_survive_export(self):
        for v in range(1,9):
            d=record(v);out=reader._export_record_verse(v,d)
            self.assertEqual(out['footnote_review'],reader.PROTOCOL)
            self.assertEqual(out['footnotes'],d['translation']['footnotes'])
            # Internal declared-note anchors remain in the exported payload;
            # the existing selected-verse reader removes them at render time.
            self.assertEqual(out['text'],d['translation']['text'])
            for k in('edition','language','text','pages','note','confidence','transcription_uncertainties','additional_translation_input'):
                if k in d['source']:self.assertEqual(out['source_critical'][k],d['source'][k])
            prompt=build_enoch_prompt(17,v)
            for k in('text','confidence','transcription_uncertainties','additional_translation_input'):
                if k in d['source']:self.assertEqual(prompt.source_payload[k],d['source'][k])
        self.assertIn('[there were]',reader._export_record_verse(3,record(3))['text'])

    def test_progress_full17_and_source_registry_are_bounded_not_whole_book(self):
        from tools.enoch.full_repair_progress import build
        report=build();self.assertIn(17,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertGreaterEqual(report['current_units_with_imported_review_evidence'],465)
        self.assertEqual(report['evidence_inventory_warnings'],[]);self.assertFalse(report['completion_proven'])
        registry=json.loads((t.ROOT/'sources/enoch/ethiopic/reviewed_source_registry.json').read_text())
        self.assertEqual(registry['chapters']['17'],P.name)
        self.assertFalse(any(k.startswith('17:')for k in registry['units']))
        for v in range(1,9):
            flags=record(v)['source_correction']
            for k in('full_book_verified','human_specialist_certification','manuscript_witness_certification','graphic_publication_approved','chapter_publication_approval'):self.assertFalse(flags[k])

    def test_rehashed_unreviewed_English_or_source_is_rejected(self):
        for section,field in(('translation','text'),('source','text')):
            with self.subTest(section=section),tempfile.TemporaryDirectory()as directory:
                target=Path(directory)/'package';shutil.copytree(P,target)
                p=target/'017-006.candidate.yaml';d=yaml.load(p.read_bytes(),Loader=t.LOADER)
                d[section][field]+=' unreviewed'
                p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False))
                m=json.loads((target/'manifest.json').read_text());m['files'][p.name]=t.sha(p.read_bytes())
                (target/'manifest.json').write_text(json.dumps(m))
                with self.assertRaises(ValueError):t.verify(target,evidence_only=True)

    def test_application_adds_no_reader_chapter_or_unrelated_export_change(self):
        m=t.load_manifest(P)
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);before=root/'1_enoch';shutil.copytree(t.TRANSLATION,before)
            for v in range(1,9):
                blob=m['baseline_git_blobs'][f'017/{v:03d}.yaml']['blob']
                import subprocess
                (before/f'017/{v:03d}.yaml').write_bytes(subprocess.check_output(['git','cat-file','blob',blob],cwd=t.ROOT))
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):old=reader.export_extra_canonical_book('ENO')
            new=reader.export_extra_canonical_book('ENO')
        a={c['chapter']:c for c in old['chapters']};b={c['chapter']:c for c in new['chapters']}
        self.assertEqual(set(a),set(b));self.assertEqual({c:x for c,x in a.items()if c!=17},{c:x for c,x in b.items()if c!=17})
        self.assertEqual([v['verse']for v in b[17]['verses']],list(range(1,9)))
        legacy=t.ROOT/'tools/export_mobile_bible.py'
        self.assertEqual(hashlib.sha256(legacy.read_bytes()).hexdigest(),'2258f72485099fe1014152eeb29394324415940467c2edd9d9da0d48a4a113c3')


if __name__=='__main__':unittest.main()
