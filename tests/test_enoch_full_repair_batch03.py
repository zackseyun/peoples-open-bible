"""Reviewed address repair and explicit supersession, not full-book approval."""
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
from tools.enoch.current_evidence import verify_current
from tools.enoch.full_repair_progress import build
from tools.textual_restoration import enoch_20261020_transaction as previous

PACKAGE=transaction.APPLICATIONS/'enoch_full_repair_batch03_20261020'


def record(c,v):
    return yaml.load((transaction.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(),
                     Loader=transaction.LOADER)


class FullRepairBatch03Test(unittest.TestCase):
    def test_exact_application_and_retirement_receipt(self):
        result=verify_current(PACKAGE)
        self.assertEqual(result['candidate_files'],17)
        self.assertFalse(result['full_book_verified'])
        receipt=json.loads((PACKAGE/'application.json').read_text())
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        self.assertEqual(len(receipt['canonical_after_sha256']),905)
        self.assertEqual(receipt['retired_references'],[f'1 Enoch 105:{v}' for v in range(3,12)])

    def test_actual_selected_addresses_and_source_pages(self):
        for c,count in ((4,1),(104,13),(105,2)):
            rows,_=verse_parser.parse_chapter(c)
            self.assertEqual([r.verse for r in rows],list(range(1,count+1)))
            self.assertEqual(sorted(int(p.stem) for p in
                (transaction.TRANSLATION/f'{c:03d}').glob('*.yaml')),list(range(1,count+1)))
        self.assertEqual(record(104,1)['source']['pages'],[254,255])
        self.assertEqual(record(105,1)['source']['pages'],[257])
        self.assertEqual(record(105,2)['source']['pages'],[257])
        self.assertEqual(record(4,1)['source']['pages'],[44,46])
        self.assertIn('እምቀ',record(4,1)['source']['text'])

    def test_material_english_and_disclosures(self):
        three=record(104,3)['translation']
        self.assertIn('it will appear to you',three['text'])
        self.assertIn('precise subject is not expressed',three['footnotes'][0]['text'])
        self.assertIn('angels',three['text'])
        one=record(105,1)['translation']
        self.assertIn('announce',one['text'])
        self.assertNotIn('themselves heard',one['text'])
        self.assertIn('supplying that verb a second time',one['footnotes'][0]['text'])
        self.assertIn('I and my son',record(105,2)['translation']['text'])
        self.assertTrue(record(4,1)['translation']['text'].endswith('its heat.'))

    def test_source_only_supersession_never_rewrites_prior_evidence(self):
        old=yaml.load((previous.PACKAGE/'063-007.candidate.yaml').read_bytes(),Loader=transaction.LOADER)
        new=record(63,7)
        self.assertEqual(old['translation'],new['translation'])
        self.assertEqual(old['source']['text'].replace('መናፍስት','መንፈሳት'),new['source']['text'])
        self.assertFalse(new['source_correction']['selected_edition_chapter_reviewed'])
        with self.assertRaisesRegex(ValueError,'Applied candidate differs'):
            previous.verify(applied=True)
        result=verify_current(previous.PACKAGE)
        self.assertIn({'reference':'1 Enoch 63:7','superseded_by':PACKAGE.name},result['reviewed_supersessions'])

    def test_progress_includes_chapters_without_declaring_the_book_complete(self):
        report=build()
        self.assertTrue({4,36,37,38,39,45,104,105} <=
                        set(report['chapters_with_complete_imported_selected_edition_review']))
        self.assertEqual(len(report['chapters']),108)
        self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertFalse(report['completion_proven'])
        self.assertFalse(report['artwork_publication_approval'])

    def test_mobile_export_restores_actual_104_105_and_only_changes_existing_4(self):
        manifest=transaction.load_manifest(PACKAGE)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);old=root/'1_enoch'
            shutil.copytree(transaction.TRANSLATION,old)
            refs=manifest['references']+[r['reference'] for r in manifest['retirements']]
            for ref in refs:
                c,v=transaction.parse_ref(ref);relative=f'{c:03d}/{v:03d}.yaml';target=old/relative
                if relative in manifest['baseline_git_blobs']:
                    blob=manifest['baseline_git_blobs'][relative]['blob']
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(subprocess.run(['git','cat-file','blob',blob],
                        cwd=transaction.ROOT,check=True,capture_output=True).stdout)
                else:target.unlink()
            with patch.object(mobile,'EXTRA_CANONICAL_ROOT',root):
                before=mobile.export_extra_canonical_book('ENO')
            after=mobile.export_extra_canonical_book('ENO')
        before={c['chapter']:c for c in before['chapters']}
        after={c['chapter']:c for c in after['chapters']}
        self.assertEqual(sorted(set(after)-set(before)),[104,105])
        self.assertEqual([c for c in sorted(set(before)&set(after)) if before[c]!=after[c]],[4])
        self.assertEqual([v['verse'] for v in after[104]['verses']],list(range(1,14)))
        self.assertEqual([v['verse'] for v in after[105]['verses']],[1,2])
        self.assertTrue(after[104]['verses'][2]['footnotes'])
        self.assertTrue(after[105]['verses'][0]['footnotes'])


if __name__=='__main__':unittest.main()
