"""Exact96:3 whole-pair successor; no neighboring exposure or publication waiver."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import yaml
from tools.enoch import bounded_application as t, batch36_evidence as b, batch35_evidence as prior
from tools.enoch import selected_edition_sources as sources, verse_parser
from tools import export_reader_bible as reader

P = t.APPLICATIONS/b.NAME
j = lambda p: json.loads(p.read_text())

class Batch36Test(unittest.TestCase):
    def fixture(self, root):
        p = Path(root)/b.NAME
        shutil.copytree(P,p)
        return p,j(p/'manifest.json')

    def route(self, p):
        original=t.APPLICATIONS
        routed=MagicMock()
        routed.resolve.return_value=original.resolve()
        routed.__truediv__.side_effect=lambda n:p if n==b.NAME else original/n
        return patch.object(t,'APPLICATIONS',routed)

    def test_exact_one_existing_delta_full966_preimage_and_receipt(self):
        proof=b.verify_current()
        before=prior.historical_postmap()['current_postmap']
        self.assertEqual(proof['prior_historical_postmap'],before)
        self.assertEqual(len(before),966)
        self.assertEqual({k for k in before if before[k]!=proof['current_postmap'][k]},{b.PATH})
        self.assertEqual(proof['actual_current_postmap'],t.corpus_hashes())
        m=t.load_manifest(P)
        self.assertEqual(m['source_baseline_git_commit'],b.BASE)
        self.assertEqual(m['references'],[b.REF])
        self.assertEqual(m['retirements'],[])
        self.assertEqual(m['supersedes'],{})
        self.assertEqual(t.sha((P/'manifest.json').read_bytes()),b.MANIFEST_SHA)
        t.verify_git_preimage(m,b.PATH,before[b.PATH])
        self.assertFalse(j(P/'application.json')['deployed_by_transaction'])

    def test_distinct_exact_v2_whole_pair_and_raw_full8_scopes(self):
        m=t.load_manifest(P)
        self.assertEqual({m['files'][x['input']]for x in m['review_bindings'][b.REF]},{b.INPUT_SHA})
        self.assertEqual({x['reviewer_id']for x in m['review_bindings'][b.REF]},{'/root','/root/author72_34_resume'})
        rows=t.reviewed_rows(P,m['review_bindings'][b.REF],b.REF,m['files'])
        self.assertEqual(rows[0],rows[1])
        self.assertIn('ይከውነክሙ',rows[0]['source']['text'])
        self.assertNotIn('ይከውንክሙ',rows[0]['source']['text'])
        self.assertIn('ሐመምክሙ',rows[0]['source']['text'])
        original=j(t.APPLICATIONS/prior.NAME/'final/ch96/author-input.json')
        for who,(identity,role,review_sha,pv_sha)in b.PAIRS.items():
            inp=j(P/f'final/ch96/{who}-input.json')
            review=j(P/f'final/ch96/{who}-review.json')
            self.assertEqual(len(inp),8)
            for v in [1,2,4,5,6,7,8]:self.assertEqual(inp[v-1],original[v-1])
            self.assertEqual((review['reviewer_id'],review['role']),(identity,role))
            for k in ['source_approved','translation_approved','notes_approved','whole_unit_approved']:
                self.assertIs(t.review_entries(review)[2][k],True)
            self.assertEqual(t.sha((P/f'final/ch96/{who}-review.json').read_bytes()),review_sha)
            self.assertEqual(t.sha((P/f'final/ch96/{who}-provenance.json').read_bytes()),pv_sha)
        # Outside1 HOLD in this peer is not a revocation or another vote for1.
        peer=j(P/'final/ch96/independent-review.json')
        self.assertEqual(t.review_entries(peer)[0]['verdict'],'hold')
        self.assertTrue(peer['prior_paired96_1_approval_retained_externally'])

    def test_history_preserves_adverse_and_withdrawal_not_rebound_votes(self):
        history=P/'history'
        root=history/'ch96-3-root-source-first-20261031'
        peer=history/'ch96-3-independent-20261031'
        self.assertEqual(t.sha((root/'review-input-full8-v1.json').read_bytes()),'54d465c8188feb786168f9a33fc14b755816d363609c24a55612e45a93b289c6')
        withdrawal=j(root/'14-v1-author-approval-withdrawn-20261101.json')
        self.assertEqual(withdrawal['current_author_verdict'],'revise')
        self.assertFalse(withdrawal['whole_unit_approved'])
        self.assertEqual(t.sha((peer/'resumed-20261101/independent-review-full8-v1.json').read_bytes()),'7639eb3cad68cba78a303fb2ba105d467e4c8a458a925f72cd7bd173a0fe8230')
        self.assertEqual(t.review_entries(j(peer/'resumed-20261101/independent-review-full8-v1.json'))[2]['verdict'],'hold')
        finding=j(peer/'haut-source-only-followup-20261101/own-positive-HautI-source-only-finding.json')
        self.assertTrue(finding['no_root_v2_or_semantic_assessment'])
        self.assertEqual(finding['status'],'POSITIVE_HAUT_I_FOR_TARGET_ONLY')
        v1=j(root/'review-input-full8-v1.json')[2]
        v2=j(P/'final/ch96/author-input.json')[2]
        self.assertEqual(v1['translation'],v2['translation'])

    def test_registry_source_ingress_only_exact3_not_canonical_echo(self):
        original=json.loads(subprocess.check_output(['git','show',b.BASE+':'+str(sources.REGISTRY.relative_to(t.ROOT))],cwd=t.ROOT))
        expected=copy.deepcopy(original);expected['units']['96:3']=b.NAME
        from tools.enoch import batch37_evidence as successor
        if (t.APPLICATIONS/successor.NAME/'application.json').is_file():
            successor.verify_current()
            expected['units']['97:1']=successor.NAME
        self.assertEqual(sources.registry_data(),expected)
        self.assertNotIn('96',expected['chapters'])
        with patch.object(t,'TRANSLATION',Path('/nonexistent-canonical-echo')):
            rows=sources.load_unit_overrides(96)
            self.assertEqual([r['verse']for r in rows],[1,3])
            self.assertTrue(all('/final/'in r['evidence']for r in rows))
        parsed,_=verse_parser.load_verse(96,3)
        self.assertEqual(parsed.text,j(P/'final/ch96/author-input.json')[2]['source']['text'])

    def test_source_only_counts_no_new_votes_or_chapter_approval(self):
        m=t.load_manifest(P);i=j(P/'source-only-count-inventory.json')
        self.assertEqual(m['chapter_inventories'],[])
        self.assertEqual(i['new_count_votes'],0)
        self.assertIs(i['wording_approval'],False)
        self.assertIs(i['reader_release_policy_changed'],False)
        self.assertEqual(i['chapters'][0]['units'],list(range(1,9)))
        self.assertEqual(i['chapters'][0]['pdf_pages'],[238,239])
        self.assertEqual(t.sha((P/'original-count91-103-index.json').read_bytes()),b.COUNT_SHA)
        d=yaml.load((t.TRANSLATION/b.PATH).read_bytes(),Loader=t.LOADER)
        for k in ['selected_edition_chapter_reviewed','chapter_publication_approval','full_book_verified','human_specialist_certification','manuscript_witness_certification','graphic_publication_approved']:
            self.assertIs(d['source_correction'][k],False)

    def test_all_explanations_export_and_incomplete_reader_chapter_hold(self):
        d=yaml.load((t.TRANSLATION/b.PATH).read_bytes(),Loader=t.LOADER)
        v=reader._export_record_verse(3,d)
        self.assertEqual(v['footnotes'],d['translation']['footnotes'])
        self.assertEqual(v['source_critical']['text'],d['source']['text'])
        self.assertEqual([n['marker']for n in v['footnotes']],['a','b','c'])
        self.assertEqual(reader._enoch_expected_verse_map()[96],list(range(1,9)))
        payload=reader.export_extra_canonical_book('ENO')
        self.assertNotIn(96,{x['chapter']for x in(payload or {}).get('chapters',[])})
        self.assertEqual(t.sha((t.ROOT/'tools/export_mobile_bible.py').read_bytes()),'2258f72485099fe1014152eeb29394324415940467c2edd9d9da0d48a4a113c3')

    def test_progress486_37_not_fullbook(self):
        from tools.enoch.full_repair_progress import build
        report=build()
        self.assertEqual(report['canonical_file_count'],966)
        self.assertEqual(report['current_units_with_imported_review_evidence'],486)
        self.assertEqual(len(report['chapters_with_complete_imported_selected_edition_review']),37)
        self.assertEqual(next(x for x in report['chapters']if x['chapter']==96)['current_units_with_imported_review_evidence'],[1,3])
        self.assertNotIn(96,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertIs(report['completion_proven'],False)

    def test_rehashed_source_english_and_each_note_rejected(self):
        for mode in ['source','English',0,1,2]:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory()as root:
                p,m=self.fixture(root);f=p/'096-003.candidate.yaml';d=yaml.load(f.read_bytes(),Loader=t.LOADER)
                if mode=='source':d['source']['text']+=' ወ'
                elif mode=='English':d['translation']['text']+=' altered'
                else:d['translation']['footnotes'][mode]['text']+=' altered'
                f.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m['files'][f.name]=t.sha(f.read_bytes());(p/'manifest.json').write_text(json.dumps(m))
                with self.assertRaises(ValueError):t.verify(p,evidence_only=True)

    def test_missing_applied_receipt_does_not_license_successor(self):
        with tempfile.TemporaryDirectory()as root:
            p,_=self.fixture(root);(p/'application.json').unlink()
            with self.route(p),self.assertRaises((ValueError,OSError)):prior.verify_current()

    def test_rehashed_partial_full8_scope_and_role_substitution_rejected(self):
        for mode in ['drop-held-row','self-peer','old-v1-input']:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory()as root:
                p,m=self.fixture(root)
                if mode=='drop-held-row':
                    f=p/'final/ch96/independent-input.json';x=j(f);x.pop();f.write_text(json.dumps(x));m['files']['final/ch96/independent-input.json']=t.sha(f.read_bytes())
                elif mode=='self-peer':m['review_bindings'][b.REF][1]['reviewer_id']='/root'
                else:m['files']['final/ch96/independent-input.json']='54d465c8188feb786168f9a33fc14b755816d363609c24a55612e45a93b289c6'
                with self.assertRaises(ValueError):b._pair(p,m)

    def test_corrupt_or_deployed_receipt_rejected(self):
        for key,value in [('snapshot_file_count',1),('candidate_files',2),('deployed_by_transaction',True),('unrelated_canonical_files_unchanged_at_application',False)]:
            with self.subTest(key=key),tempfile.TemporaryDirectory()as root:
                p,_=self.fixture(root);r=j(p/'application.json');r[key]=value;(p/'application.json').write_text(json.dumps(r))
                with self.route(p),self.assertRaises(ValueError):b.verify_current()

    def test_any_other_canonical_drift_rejected(self):
        current=t.corpus_hashes()
        for path in [b.PATH,'096/001.yaml','095/001.yaml','001/001.yaml']:
            changed=dict(current);changed[path]='0'*64
            with self.subTest(path=path),patch.object(t,'corpus_hashes',return_value=changed),self.assertRaises(ValueError):b.verify_current()
        changed=dict(current);changed['096/004.yaml']='0'*64
        with patch.object(t,'corpus_hashes',return_value=changed),self.assertRaises(ValueError):b.verify_current()

    def test_other_registry_or_complete_chapter_exposure_rejected(self):
        for mode in ['neighbor','chapter','unrelated']:
            reg=copy.deepcopy(sources.registry_data())
            if mode=='neighbor':reg['units']['96:4']=b.NAME
            elif mode=='chapter':reg['chapters']['96']=b.NAME
            else:reg['units']['1:1']='unapproved'
            with self.subTest(mode=mode),patch.object(sources,'registry_data',return_value=reg),self.assertRaises(ValueError):b.verify_current()

    def test_runtime_publish_workflow_unchanged_and_ci_fetches_real_baseline(self):
        path='.github/workflows/publish-pob.yml'
        self.assertEqual((t.ROOT/path).read_bytes(),subprocess.check_output(['git','show',b.BASE+':'+path],cwd=t.ROOT))
        workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn('git fetch --no-tags --depth=1 origin '+b.BASE,workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_enoch_full_repair_batch36.py'",workflow)

if __name__=='__main__':unittest.main()
