"""One real43:3 source-form correction, not a chapter/context completion claim."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import yaml
from tools.enoch import bounded_application as t
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader

P=t.APPLICATIONS/'enoch_full_repair_batch26_20261024'
OLD=t.APPLICATIONS/'enoch_full_repair_batch05_20261020'
SHA='10207d1f6bee5b1484cf6180102f97c4c0d81ac35a370cb6c02da44886ef5e99'
REF='1 Enoch 43:3'
def record(v):return yaml.load((t.TRANSLATION/f'043/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)

class Batch26Test(unittest.TestCase):
    def test_exact_one_and_complete965_postmap_no_additions(self):
        self.assertEqual(t.sha((P/'manifest.json').read_bytes()),SHA);m=t.load_manifest(P);r=json.loads((P/'application.json').read_text())
        self.assertEqual(verify_current(P)['references'],[REF]);self.assertEqual(m['source_baseline_git_commit'],'5b22f0473ab30393c37303b0baa7895907d18a70')
        self.assertEqual(m['canonical_baseline_sha256'],json.loads((t.APPLICATIONS/'enoch_full_repair_batch25_20261024/application.json').read_text())['canonical_after_sha256'])
        expected=dict(m['canonical_baseline_sha256']);expected['043/003.yaml']=m['files']['043-003.candidate.yaml'];self.assertEqual(r['canonical_after_sha256'],expected)
        self.assertEqual(r['snapshot_file_count'],965);self.assertTrue(r['unrelated_canonical_files_unchanged_at_application']);self.assertEqual(m['retirements'],[])

    def test_selected_hidden_ending_corrected_without_normalization(self):
        old=yaml.load((OLD/'043-003.candidate.yaml').read_bytes(),Loader=t.LOADER);new=record(3)
        self.assertIn('ዘኅቡእ፡',old['source']['text']);self.assertIn('ዘኅቡአ፡',new['source']['text']);self.assertNotIn('ዘኅቡእ፡',new['source']['text'])
        self.assertEqual(new['source']['text'],old['source']['text'].replace('ዘኅቡእ፡','ዘኅቡአ፡'))
        self.assertIn('*እሙንቱ',new['source']['text'])

    def test_all_relative_clauses_object_and_star_explanation_retained(self):
        d=record(3);text=d['translation']['text']
        for phrase in('I asked him','the angel who was walking with me','who had shown me what was hidden','What are these?[a]'):self.assertIn(phrase,text)
        note=d['translation']['footnotes'][0];self.assertEqual(note['marker'],'a');self.assertIn('editorial asterisk',note['text']);self.assertIn('plural',note['text'])

    def test_explicit_exact_B05_owner_preimage_and_current_successor(self):
        m=t.load_manifest(P);old=t.load_manifest(OLD)
        self.assertEqual(m['supersedes'],{REF:{'package':OLD.name,'manifest_sha256':t.sha((OLD/'manifest.json').read_bytes()),'candidate_sha256':old['files']['043-003.candidate.yaml']}})
        self.assertEqual(m['canonical_baseline_sha256']['043/003.yaml'],old['files']['043-003.candidate.yaml'])
        self.assertIn({'reference':REF,'superseded_by':P.name},verify_current(OLD)['reviewed_supersessions'])

    def test_original_fullfour_decisions_not_changed_to_blanket_accept(self):
        m=t.load_manifest(P);p=P/'final/ch43-full/review-input.json'
        self.assertEqual(t.sha(p.read_bytes()),'eeac12d8bb0ed41d66bfcbaf1c82fa31b1ad0a814e067e3fe645842fbaf455b3')
        for b in m['review_bindings'][REF]:
            t.review_row(P,b,REF,m['files']);rows=t.review_entries(json.loads((P/b['review']).read_text()))
            self.assertEqual([(r['reference'],r['verdict'])for r in rows],[(f'1 Enoch 43:{v}',vote)for v,vote in[(1,'accept'),(2,'hold'),(3,'accept'),(4,'hold')]])

    def test_identical_source_context1_not_rewritten_and_holds2_4_unchanged(self):
        m=t.load_manifest(P)
        for v in(1,2):
            self.assertEqual(t.sha((t.TRANSLATION/f'043/{v:03d}.yaml').read_bytes()),m['canonical_baseline_sha256'][f'043/{v:03d}.yaml']);self.assertFalse((P/f'043-{v:03d}.candidate.yaml').exists())
        # OriginalB26 did not change4. Only exactB27 may now supersede it.
        receipt=json.loads((P/'application.json').read_text());self.assertEqual(receipt['canonical_after_sha256']['043/004.yaml'],m['canonical_baseline_sha256']['043/004.yaml'])
        from test_enoch_full_repair_batch27 import assert_current4
        assert_current4(self)
        rows=json.loads((P/'final/ch43-full/review-input.json').read_text());old=yaml.load((OLD/'043-001.candidate.yaml').read_bytes(),Loader=t.LOADER)
        self.assertEqual(rows[0]['source']['text'],old['source']['text']);self.assertEqual(m['not_applied'][0]['verdicts'],['accept','accept']);self.assertIn('stylistic',m['not_applied'][0]['reason'])
        self.assertEqual(m['chapter_inventories'],[]);self.assertEqual(m['source_only_count_inventories'][0]['units'],[1,2,3,4])

    def test_partial_registry_source_prompt_and_existing_details_export(self):
        from tools.enoch.selected_edition_sources import registry_data
        reg=registry_data();self.assertNotIn('43',reg['chapters']);self.assertEqual(reg['units']['43:3'],P.name)
        self.assertEqual(reg['units']['43:1'],OLD.name)
        from test_enoch_full_repair_batch27 import assert_current4
        assert_current4(self)
        d=record(3);out=reader._export_record_verse(3,d);prompt=build_enoch_prompt(43,3)
        self.assertEqual(out['text'],d['translation']['text']);self.assertEqual(out['footnotes'],d['translation']['footnotes']);self.assertEqual(out['footnote_review'],reader.PROTOCOL)
        self.assertEqual(out['source_critical']['text'],d['source']['text']);self.assertEqual(prompt.source_payload['text'],d['source']['text'])

    def test_rehashed_old_ending_or_dropped_note_not_approved(self):
        for mode in('old_source','drop_note'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory()as directory:
                q=Path(directory)/'package';shutil.copytree(P,q);p=q/'043-003.candidate.yaml';d=yaml.load(p.read_bytes(),Loader=t.LOADER)
                if mode=='old_source':d['source']['text']=d['source']['text'].replace('ዘኅቡአ፡','ዘኅቡእ፡')
                else:d['translation']['footnotes']=[]
                p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m=json.loads((q/'manifest.json').read_text());m['files'][p.name]=t.sha(p.read_bytes());(q/'manifest.json').write_text(json.dumps(m))
                with self.assertRaises(ValueError):t.verify(q,evidence_only=True)

    def test_no_new_record_fullchapter_or_book_completion_credit(self):
        from tools.enoch.full_repair_progress import build
        r=build();self.assertEqual(r['canonical_file_count'],966);self.assertEqual(r['current_units_with_imported_review_evidence'],476)
        self.assertEqual(len(r['chapters_with_complete_imported_selected_edition_review']),36);self.assertNotIn(43,r['chapters_with_complete_imported_selected_edition_review']);self.assertFalse(r['completion_proven'])
        flags=record(3)['source_correction']
        for key in('selected_edition_chapter_reviewed','chapter_publication_approval','full_book_verified','human_specialist_certification','manuscript_witness_certification','graphic_publication_approved'):self.assertFalse(flags[key])

    def test_workflow_fetches_actual_preimage_and_runs_gate(self):
        s=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text();self.assertIn('git fetch --no-tags --depth=1 origin 5b22f0473ab30393c37303b0baa7895907d18a70',s)
        self.assertIn("python -m unittest discover -s tests -p 'test_enoch_full_repair_batch26.py'",s)
