"""Forty-two exact applications with real semantic and publication dependencies."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools import export_mobile_bible as mobile
from tools.enoch import bounded_application as transaction, verse_parser
from tools.enoch import legacy_individual_evidence as legacy
from tools.enoch.current_evidence import verify_current
from tools.enoch.full_repair_progress import build

PACKAGE=transaction.APPLICATIONS/'enoch_full_repair_batch06_20261020'
FULL={24:6,25:7,40:10,79:6}

def record(c,v):
    return yaml.load((transaction.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(),Loader=transaction.LOADER)

class FullRepairBatch06Test(unittest.TestCase):
    def test_exact42_units_sixteen_additions_unrelated_bytes_preserved(self):
        result=verify_current(PACKAGE);self.assertEqual(result['candidate_files'],42)
        self.assertFalse(result['full_book_verified'])
        m=transaction.load_manifest(PACKAGE);receipt=json.loads((PACKAGE/'application.json').read_text())
        self.assertEqual(len(receipt['canonical_after_sha256']),939)
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        self.assertEqual(sum('%03d/%03d.yaml'%transaction.parse_ref(r) not in m['canonical_baseline_sha256'] for r in m['references']),16)
        self.assertEqual({c['chapter'] for c in m['chapter_inventories']},set(FULL))

    def test_actual_material_source_and_english_choices(self):
        self.assertIn('ገሙራ',record(24,4)['source']['text'])
        self.assertIn('They will enter',record(25,6)['translation']['text'])
        self.assertIn('the satans',record(40,7)['translation']['text'])
        self.assertIn('closed storehouses',record(41,4)['translation']['text'])
        self.assertIn('his name endures',record(41,6)['translation']['text'])
        self.assertIn('sees them all for judgment',record(41,9)['translation']['text'])
        self.assertIn('፻ወ፸ወ፯',record(79,4)['source']['text'])
        self.assertIn('177 days',record(79,4)['translation']['text'])
        self.assertIn('25 weeks and two days',record(79,4)['translation']['text'])
        self.assertIn('five days',record(79,5)['translation']['text'])
        note=record(41,7)['translation']['footnotes'][0]['text']
        self.assertIn('unstarred “I saw”',note)
        self.assertIn('Note9 concerns the following “path”',note)
        self.assertIn('neither note is attached to the later',note)

    def test_exact_legacy_enum_successor_never_rewrites_old_artifacts_or_gate(self):
        old_package=transaction.APPLICATIONS/legacy.NAME
        old=legacy.historical_record(old_package);new=record(25,7)
        legacy.check_metadata_payload(old,new)
        self.assertEqual(old['source']['text'],new['source']['text'])
        self.assertEqual(old['translation']['text'],new['translation']['text'])
        self.assertEqual(old['translation']['footnotes'][0]['text'],new['translation']['footnotes'][0]['text'])
        result=verify_current(old_package)
        self.assertEqual(result['current_canonical_sha256'],transaction.sha((transaction.TRANSLATION/'025/007.yaml').read_bytes()))
        self.assertEqual(result['reviewed_supersessions'],[{'reference':legacy.REFERENCE,'superseded_by':PACKAGE.name}])
        with self.assertRaisesRegex(ValueError,'Legacy installed candidate differs'):legacy.verify_applied(old_package)

    def test_semantic_and_visibility_release_holds_are_not_applied(self):
        m=transaction.load_manifest(PACKAGE)
        self.assertEqual({r['reference'] for r in m['not_applied']},{'1 Enoch 41:5','1 Enoch 41:8','1 Enoch 80:5','1 Enoch 80:8'})
        receipt=json.loads((PACKAGE/'application.json').read_text())
        # Protect what this application did, without freezing a later accepted repair.
        for item in m['not_applied']:
            ref=item['reference'];c,v=transaction.parse_ref(ref);relative=f'{c:03d}/{v:03d}.yaml'
            self.assertNotIn(ref,m['references'])
            if relative in m['canonical_baseline_sha256']:
                self.assertEqual(receipt['canonical_after_sha256'][relative],m['canonical_baseline_sha256'][relative])
            else:self.assertNotIn(relative,receipt['canonical_after_sha256'])
        for c,v in [(41,3),(80,6)]:self.assertFalse(record(c,v)['source_correction']['selected_edition_chapter_reviewed'])

    def test_progress_and_source_ingress_preserve_all_actual_units_without_full108_claim(self):
        r=build();self.assertGreaterEqual(r['current_units_with_imported_review_evidence'],165)
        self.assertTrue(set(FULL)<=set(r['chapters_with_complete_imported_selected_edition_review']))
        self.assertEqual(r['evidence_inventory_warnings'],[]);self.assertFalse(r['completion_proven'])
        for c,count in FULL.items():
            self.assertEqual([v.verse for v in verse_parser.parse_chapter(c)[0]],list(range(1,count+1)))
        self.assertIn('Book of the Luminaries',record(79,4)['enoch_witnesses']['section'])

    def test_unreviewed_additional_primary_input_cannot_be_laundered(self):
        with tempfile.TemporaryDirectory() as directory:
            package=Path(directory)/PACKAGE.name;shutil.copytree(PACKAGE,package)
            file=package/'040-001.candidate.yaml';data=yaml.load(file.read_bytes(),Loader=transaction.LOADER)
            data['source']['additional_translation_input']={'language':'Greek','text':'unapproved added source'}
            file.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False))
            m=json.loads((package/'manifest.json').read_text());m['files'][file.name]=transaction.sha(file.read_bytes())
            (package/'manifest.json').write_text(json.dumps(m))
            with self.assertRaisesRegex(ValueError,'Candidate differs from accepted source/English/notes'):
                transaction.verify(package,evidence_only=True)

    def test_mobile_adds_only_four_complete_reviewed_chapters_not_held41_80(self):
        m=transaction.load_manifest(PACKAGE)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);old=root/'1_enoch';shutil.copytree(transaction.TRANSLATION,old)
            for ref in m['references']:
                c,v=transaction.parse_ref(ref);relative=f'{c:03d}/{v:03d}.yaml';target=old/relative
                if relative in m['baseline_git_blobs']:
                    target.write_bytes(subprocess.run(['git','cat-file','blob',m['baseline_git_blobs'][relative]['blob']],cwd=transaction.ROOT,check=True,capture_output=True).stdout)
                else:target.unlink()
            with patch.object(mobile,'EXTRA_CANONICAL_ROOT',root):before=mobile.export_extra_canonical_book('ENO')
            after=mobile.export_extra_canonical_book('ENO')
        before={c['chapter']:c for c in before['chapters']};after={c['chapter']:c for c in after['chapters']}
        self.assertEqual(sorted(set(after)-set(before)),list(FULL))
        self.assertEqual({c:d for c,d in after.items() if c not in FULL},before)
        self.assertNotIn(41,after);self.assertNotIn(80,after)
        for c,count in FULL.items():self.assertEqual([v['verse'] for v in after[c]['verses']],list(range(1,count+1)))
        self.assertTrue(after[25]['verses'][6]['footnotes'])
        self.assertTrue(after[79]['verses'][3]['footnotes'])

if __name__=='__main__':unittest.main()
