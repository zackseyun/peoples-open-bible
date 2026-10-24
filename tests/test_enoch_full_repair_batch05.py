"""Eleven exact repairs, partial chapter boundaries and historical proof import."""
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

PACKAGE=transaction.APPLICATIONS/'enoch_full_repair_batch05_20261020'
PARTIAL=[(42,1),(42,2),(43,1),(43,3),(43,4)]

def record(c,v):
    return yaml.load((transaction.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(),Loader=transaction.LOADER)

class FullRepairBatch05Test(unittest.TestCase):
    def assert_exact42_successor(self,v):
        successor=transaction.APPLICATIONS/'enoch_full_repair_batch25_20261024'
        self.assertEqual(transaction.sha((successor/'manifest.json').read_bytes()),'a63aeb53e3aa258c49d57e24e1bad6fdc6ec3ceca917882ddfc2b94715f92661')
        m=transaction.load_manifest(successor);old=transaction.load_manifest(PACKAGE);ref=f'1 Enoch 42:{v}'
        self.assertEqual(m['supersedes'][ref],{'package':PACKAGE.name,'manifest_sha256':transaction.sha((PACKAGE/'manifest.json').read_bytes()),'candidate_sha256':old['files'][f'042-{v:03d}.candidate.yaml']})
        self.assertEqual(m['canonical_baseline_sha256'][f'042/{v:03d}.yaml'],old['files'][f'042-{v:03d}.candidate.yaml'])
        self.assertEqual(transaction.sha((transaction.TRANSLATION/f'042/{v:03d}.yaml').read_bytes()),m['files'][f'042-{v:03d}.candidate.yaml'])
        self.assertIn(ref,verify_current(successor)['references'])

    def test_exact11_units_and_five_additions_with_no_held_candidate(self):
        result=verify_current(PACKAGE)
        self.assertEqual(result['candidate_files'],11)
        self.assertFalse(result['full_book_verified'])
        manifest=transaction.load_manifest(PACKAGE)
        self.assertEqual(manifest['references_excluded_due_to_holds'],['1 Enoch 42:3','1 Enoch 43:2'])
        for ref in manifest['references_excluded_due_to_holds']:
            self.assertNotIn(ref,manifest['references'])
        receipt=json.loads((PACKAGE/'application.json').read_text())
        self.assertEqual(len(receipt['canonical_after_sha256']),923)
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        self.assertEqual(sum('%03d/%03d.yaml'%transaction.parse_ref(r) not in manifest['canonical_baseline_sha256']
                             for r in manifest['references']),5)

    def test_actual_selected_forms_and_qualified_english(self):
        self.assertIn('ሰረብ',record(28,3)['source']['text'])
        self.assertIn('†ማየ',record(28,3)['source']['text'])
        self.assertIn('great flow',record(28,3)['translation']['text'])
        self.assertIn('provisional contextual',record(28,3)['translation']['footnotes'][0]['text'])
        self.assertIn('great design',record(34,1)['translation']['text'])
        self.assertIn('፩',record(34,2)['source']['text'])
        self.assertIn('ወኢረከበት',record(42,2)['source']['text'])
        self.assertIn('found no dwelling',record(42,2)['translation']['text'])
        self.assertEqual(record(43,4)['source']['text'].count('መንፈሳት'),2)
        self.assertNotIn('መናፍስት',record(43,4)['source']['text'])

    def test_explicit28_successor_preserves_old_source_and_history(self):
        old=yaml.load((previous.PACKAGE/'028-001.candidate.yaml').read_bytes(),Loader=transaction.LOADER)
        self.assertEqual(old['source']['text'],record(28,1)['source']['text'])
        lineage=json.loads((PACKAGE/'28-1-exact-row-lineage.json').read_text())
        self.assertTrue(lineage['final28_1_row_payload_identical_to_previously_assessed_row'])
        result=verify_current(previous.PACKAGE)
        self.assertIn({'reference':'1 Enoch 28:1','superseded_by':PACKAGE.name},result['reviewed_supersessions'])
        self.assertTrue((previous.PACKAGE/'028-001.candidate.yaml').exists())

    def test_partial_source_overrides_never_approve_neighboring_holds(self):
        for c,v in PARTIAL:
            row=next(r for r in verse_parser.parse_chapter(c)[0] if r.verse==v)
            self.assertEqual(row.text,record(c,v)['source']['text'])
            self.assertEqual(row.pages,(record(c,v)['source']['pages'][0],))
            historical=yaml.load((PACKAGE/f'{c:03d}-{v:03d}.candidate.yaml').read_bytes(),Loader=transaction.LOADER)
            self.assertFalse(historical['source_correction']['selected_edition_chapter_reviewed'])
            if c==42:
                self.assert_exact42_successor(v)
                self.assertTrue(record(c,v)['source_correction']['selected_edition_chapter_reviewed'])
            else:self.assertFalse(record(c,v)['source_correction']['selected_edition_chapter_reviewed'])
        manifest=transaction.load_manifest(PACKAGE)
        held=transaction.TRANSLATION/'043/002.yaml'
        self.assertEqual(transaction.sha(held.read_bytes()),manifest['canonical_baseline_sha256']['043/002.yaml'])
        original_receipt=json.loads((PACKAGE/'application.json').read_text())
        self.assertNotIn('042/003.yaml',original_receipt['canonical_after_sha256'])
        later=transaction.APPLICATIONS/'enoch_full_repair_batch25_20261024'
        self.assertIn('1 Enoch 42:3',verify_current(later)['references'])
        self.assertEqual(transaction.sha((transaction.TRANSLATION/'042/003.yaml').read_bytes()),transaction.load_manifest(later)['files']['042-003.candidate.yaml'])
        self.assertNotIn('043-002.candidate.yaml',manifest['files'])

    def test_progress_and_actual_counts_do_not_certify_the_full_book(self):
        report=build()
        self.assertGreaterEqual(report['current_units_with_imported_review_evidence'],123)
        self.assertTrue({15,16,28,29,34,83}<=set(report['chapters_with_complete_imported_selected_edition_review']))
        # Scope historical holds to this application; a later accepted repair is allowed.
        self.assertEqual({c['chapter'] for c in transaction.load_manifest(PACKAGE)['chapter_inventories']},{28,34})
        self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertFalse(report['completion_proven'])
        for c in [28,34]:self.assertEqual([r.verse for r in verse_parser.parse_chapter(c)[0]],[1,2,3])

    def test_mobile_adds28_34_and_only_changes_existing43_without_approving_it(self):
        manifest=transaction.load_manifest(PACKAGE)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);after_root=root/'after';old_root=root/'before'
            applied=after_root/'1_enoch';shutil.copytree(transaction.TRANSLATION,applied)
            # Reconstruct this application's exact contribution, not its two
            # partial42units plus a much later restored3 from the current tree.
            (applied/'042/003.yaml').unlink(missing_ok=True)
            for ref in manifest['references']:
                c,v=transaction.parse_ref(ref)
                (applied/f'{c:03d}/{v:03d}.yaml').write_bytes((PACKAGE/f'{c:03d}-{v:03d}.candidate.yaml').read_bytes())
            old=old_root/'1_enoch';shutil.copytree(applied,old)
            for ref in manifest['references']:
                c,v=transaction.parse_ref(ref);relative=f'{c:03d}/{v:03d}.yaml';target=old/relative
                if relative in manifest['baseline_git_blobs']:
                    target.write_bytes(subprocess.run(['git','cat-file','blob',manifest['baseline_git_blobs'][relative]['blob']],
                        cwd=transaction.ROOT,check=True,capture_output=True).stdout)
                else:target.unlink()
            with patch.object(mobile,'EXTRA_CANONICAL_ROOT',old_root):before=mobile.export_extra_canonical_book('ENO')
            with patch.object(mobile,'EXTRA_CANONICAL_ROOT',after_root):after=mobile.export_extra_canonical_book('ENO')
        before={c['chapter']:c for c in before['chapters']};after={c['chapter']:c for c in after['chapters']}
        self.assertEqual(sorted(set(after)-set(before)),[28,34])
        self.assertEqual([c for c in sorted(before) if before[c]!=after[c]],[43])
        self.assertEqual(before[43]['verses'][1],after[43]['verses'][1])
        self.assertNotIn(42,after)
        self.assertTrue(after[28]['verses'][2]['footnotes'])
        self.assertTrue(after[34]['verses'][1]['footnotes'])

if __name__=='__main__':unittest.main()
