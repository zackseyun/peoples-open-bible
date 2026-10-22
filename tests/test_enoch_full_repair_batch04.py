"""Exact eighteen-unit source repair, not complete Enoch certification."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from tools import export_mobile_bible as mobile
from tools.enoch import bounded_application as transaction, verse_parser
from tools.enoch.current_evidence import verify_current
from tools.enoch.full_repair_progress import build

PACKAGE=transaction.APPLICATIONS/'enoch_full_repair_batch04_20261020'
COUNTS={50:5,51:5,70:4,107:3}

def record(c,v):
    return yaml.load((transaction.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(),Loader=transaction.LOADER)

class FullRepairBatch04Test(unittest.TestCase):
    def test_exact_application_preserves_unrelated_canonical_files(self):
        result=verify_current(PACKAGE)
        self.assertEqual(result['candidate_files'],18)
        self.assertFalse(result['full_book_verified'])
        receipt=json.loads((PACKAGE/'application.json').read_text())
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        self.assertEqual(len(receipt['canonical_after_sha256']),918)
        manifest=transaction.load_manifest(PACKAGE)
        additions=[r for r in manifest['references'] if
                   '%03d/%03d.yaml'%transaction.parse_ref(r) not in manifest['canonical_baseline_sha256']]
        self.assertEqual(len(additions),13)
        self.assertFalse(manifest.get('retirements',[]))

    def test_declared_full_chapters_use_the_actual_printed_counts_and_pages(self):
        for c,count in COUNTS.items():
            rows,_=verse_parser.parse_chapter(c)
            self.assertEqual([r.verse for r in rows],list(range(1,count+1)))
            self.assertEqual(sorted(int(p.stem) for p in (transaction.TRANSLATION/f'{c:03d}').glob('*.yaml')),
                             list(range(1,count+1)))
        self.assertEqual(record(51,1)['source']['pages'],[131,132])
        self.assertEqual(record(70,2)['source']['pages'],[165,166])
        self.assertEqual(record(107,1)['source']['pages'],[260,261])

    def test_individual_18_negative_and_anomalous_printing_do_not_approve_chapter(self):
        if (transaction.APPLICATIONS/'enoch_full_repair_batch10_20261022/application.json').exists():
            # The old partial18 assertion is replayed unchanged at f082.
            # This requires the installed all16 successor; current18 controls
            # are independently asserted by test_enoch_full_repair_batch10.
            from tools.enoch.replay_18_pre_complete_gate import replay
            result=replay('individual18')
            self.assertEqual((result['tests_run'],result['skipped'],result['expected_failures']), (1,0,0))
            self.assertFalse(result['current_corpus_validated'])
            return
        data=record(18,12)
        self.assertIn('*ኢጽገበ',data['source']['text'])
        self.assertIn('ወኢማን',data['source']['text'])
        self.assertIn('no heaven',data['translation']['text'])
        self.assertIn('nun-shaped',data['translation']['footnotes'][2]['text'])
        self.assertIn('not independently inspected',data['translation']['footnotes'][2]['text'])
        self.assertFalse(data['source_correction']['selected_edition_chapter_reviewed'])
        rows,_=verse_parser.parse_chapter(18)
        row=next(r for r in rows if r.verse==12)
        self.assertEqual(row.text,data['source']['text'])
        self.assertIn('apparatus17',row.source_note)
        self.assertIn('*ኢጽገበ',row.text)
        self.assertNotIn(18,build()['chapters_with_complete_imported_selected_edition_review'])

    def test_critical_and_person_decisions_are_preserved(self):
        self.assertIn('entrusted',record(51,1)['translation']['text'])
        self.assertIn('not a womb',record(51,1)['translation']['footnotes'][0]['text'])
        self.assertIn('not reckoned',record(70,3)['translation']['text'])
        self.assertIn('first-person',record(70,3)['translation']['footnotes'][0]['text'])
        self.assertIn('†',record(107,3)['source']['text'])
        self.assertIn('not silently substituted',record(107,3)['translation']['footnotes'][1]['text'])
        for c,count in COUNTS.items():
            for v in range(1,count+1):
                data=record(c,v)
                self.assertEqual(data['status'],'draft')
                self.assertEqual(data['source']['confidence'],'medium')
                self.assertFalse(data['source_correction']['graphic_publication_approved'])
                self.assertNotIn('oracle',data['source']['note'].casefold())

    def test_progress_has_four_more_chapters_without_full_book_claim(self):
        report=build()
        self.assertGreaterEqual(report['current_units_with_imported_review_evidence'],84)
        self.assertTrue(set(COUNTS)<=set(report['chapters_with_complete_imported_selected_edition_review']))
        self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertFalse(report['completion_proven'])

    def test_mobile_adds_only_four_full_chapters_and_retains_notes(self):
        if (transaction.APPLICATIONS/'enoch_full_repair_batch10_20261022/application.json').exists():
            from tools.enoch.replay_18_pre_complete_gate import replay
            result=replay('export18')
            self.assertEqual((result['tests_run'],result['skipped'],result['expected_failures']), (1,0,0))
            self.assertFalse(result['current_corpus_validated'])
            return
        manifest=transaction.load_manifest(PACKAGE)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);old=root/'1_enoch';shutil.copytree(transaction.TRANSLATION,old)
            for ref in manifest['references']:
                c,v=transaction.parse_ref(ref);relative=f'{c:03d}/{v:03d}.yaml';target=old/relative
                if relative in manifest['baseline_git_blobs']:
                    target.write_bytes(subprocess.run(['git','cat-file','blob',manifest['baseline_git_blobs'][relative]['blob']],
                        cwd=transaction.ROOT,check=True,capture_output=True).stdout)
                else:target.unlink()
            with patch.object(mobile,'EXTRA_CANONICAL_ROOT',root):before=mobile.export_extra_canonical_book('ENO')
            after=mobile.export_extra_canonical_book('ENO')
        before={c['chapter']:c for c in before['chapters']};after={c['chapter']:c for c in after['chapters']}
        self.assertEqual(sorted(set(after)-set(before)),list(COUNTS))
        self.assertEqual({c:d for c,d in after.items() if c not in COUNTS},before)
        self.assertNotIn(18,after)
        for c,count in COUNTS.items():
            self.assertEqual([v['verse'] for v in after[c]['verses']],list(range(1,count+1)))
        self.assertTrue(after[51]['verses'][0]['footnotes'])
        self.assertTrue(after[107]['verses'][2]['footnotes'])

if __name__=='__main__':unittest.main()
