"""Exact whole97:1 supersession, immutable adverse history and release bounds."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock,patch
import yaml
from tools.enoch import bounded_application as t,batch37_evidence as b,batch36_evidence as prior
from tools.enoch import selected_edition_sources as sources,verse_parser
from tools import export_reader_bible as reader
P=t.APPLICATIONS/b.NAME
j=lambda p:json.loads(p.read_text())

class Batch37Test(unittest.TestCase):
    def fixture(self,root):
        p=Path(root)/b.NAME;shutil.copytree(P,p);return p,j(p/'manifest.json')

    def route(self,p):
        original=t.APPLICATIONS;routed=MagicMock();routed.resolve.return_value=original.resolve()
        routed.__truediv__.side_effect=lambda n:p if n==b.NAME else original/n
        return patch.object(t,'APPLICATIONS',routed)

    def test_exact_one_current_delta_and_predecessor_chain(self):
        proof=b.verify_current();before=prior.historical_postmap()['current_postmap']
        self.assertEqual(proof['prior_historical_postmap'],before)
        self.assertEqual(len(before),966)
        self.assertEqual({k for k in before if before[k]!=proof['current_postmap'][k]},{b.PATH})
        current = t.corpus_hashes()
        self.assertEqual(proof['actual_current_postmap'],current)
        from tools.enoch import batch38_evidence
        changes = batch38_evidence.CHANGED_PATHS if proof.get('verified_current_successor') == batch38_evidence.NAME else set()
        from tools.enoch import batch39_evidence
        if (t.APPLICATIONS/batch39_evidence.NAME/'application.json').is_file():
            batch39_evidence.verify_current()
            changes = changes | batch39_evidence.CHANGED_PATHS
            from tools.enoch import batch40_evidence
            if (t.APPLICATIONS/batch40_evidence.NAME/'application.json').is_file():
                batch40_evidence.verify_current();changes = changes | batch40_evidence.CHANGED_PATHS
        self.assertEqual({k for k in current if proof['current_postmap'].get(k) != current[k]},changes)
        self.assertEqual(prior.verify_current()['actual_current_postmap'],t.corpus_hashes())
        m=t.load_manifest(P);self.assertEqual(m['source_baseline_git_commit'],b.BASE)
        self.assertEqual(m['references'],[b.REF]);self.assertEqual(m['retirements'],[])
        self.assertEqual(m['supersedes'],{b.REF:{'package':b.OLD,'manifest_sha256':b.OLD_SHA,'candidate_sha256':before[b.PATH]}})
        self.assertFalse(j(P/'application.json')['deployed_by_transaction'])

    def test_exact_full10_whole_pair_not_source_only_vote(self):
        m=t.load_manifest(P);b._pair(P,m)
        self.assertEqual({m['files'][x['input']]for x in m['review_bindings'][b.REF]},{b.INPUT_SHA})
        rows=t.reviewed_rows(P,m['review_bindings'][b.REF],b.REF,m['files']);self.assertEqual(rows[0],rows[1])
        self.assertIn('ኃጥአን',rows[0]['source']['text']);self.assertIn('ወይትሐጐሉ',rows[0]['source']['text'])
        self.assertNotIn('ወይትሐጕሉ',rows[0]['source']['text'])
        self.assertEqual(len(rows[0]['translation']['footnotes']),2)
        for who in b.PAIRS:
            decisions=t.review_entries(j(P/f'final/ch97/{who}-review.json'))
            self.assertEqual([x['verdict']for x in decisions],['accept']+['hold']*9)
        for v in range(2,11):
            with self.assertRaises(ValueError):t.reviewed_rows(P,m['review_bindings'][b.REF],f'1 Enoch 97:{v}',m['files'])

    def test_adverse_source_meaning_and_note_history_preserved(self):
        root=P/'history/ch97-1-new-Uoft-root-corrective-author-20261102'
        peer=P/'history/ch97-1-Uoft-whole-independent-20261102'
        self.assertEqual(t.sha((root/'04-own-primary-meaning-freeze-before-current-payload.json').read_bytes()),'e83242865fbf257d03038503b750f0140c948adcf409f9ae5714073b7962a971')
        self.assertTrue(j(root/'08-v1-author-notes-whole-approval-withdrawal.json')['whole_approval_withdrawn'])
        self.assertEqual(t.review_entries(j(peer/'exact-candidate-v1-review/independent-review-full10-v1.json'))[0]['verdict'],'revise')
        old=j(root/'review-input-full10-v1.json');new=j(P/'final/ch97/author-input.json')
        expected=copy.deepcopy(old);expected[0]['translation']['footnotes'][0]['text']=expected[0]['translation']['footnotes'][0]['text'].replace('the preceding verb','the verb')
        self.assertEqual(new,expected)

    def test_individual_source_overrides_old_chapter_not_canonical_echo(self):
        registry=sources.registry_data()
        self.assertEqual(registry['chapters']['97'],b.OLD)
        self.assertEqual(registry['units']['97:1'],b.NAME)
        with patch.object(t,'TRANSLATION',Path('/no-canonical-echo')):
            rows=sources.load_unit_overrides(97)
            self.assertEqual([x['verse']for x in rows],[1])
            self.assertIn('/final/ch97/',rows[0]['evidence'])
        row,_=verse_parser.load_verse(97,1)
        self.assertEqual(row.text,j(P/'final/ch97/author-input.json')[0]['source']['text'])
        self.assertIn(b.NAME,row.chapter_file)

    def test_retained_count_zero_new_votes_and_no_chapter_claim(self):
        m=t.load_manifest(P);i=j(P/'source-only-count-inventory.json')
        self.assertEqual(m['chapter_inventories'],[]);self.assertEqual(i['new_count_votes'],0)
        self.assertFalse(i['wording_approval']);self.assertFalse(i['reader_release_policy_changed'])
        self.assertEqual(i['chapters'][0]['units'],list(range(1,11)))
        self.assertEqual(i['chapters'][0]['pdf_pages'],[239,240,241])
        d=yaml.load((t.TRANSLATION/b.PATH).read_bytes(),Loader=t.LOADER)
        for k in ['selected_edition_chapter_reviewed','chapter_publication_approval','full_book_verified','human_specialist_certification','manuscript_witness_certification','graphic_publication_approved']:
            self.assertIs(d['source_correction'][k],False)

    def test_notes_export_and_no_new_neighbor_exposure(self):
        d=yaml.load((t.TRANSLATION/b.PATH).read_bytes(),Loader=t.LOADER)
        v=reader._export_record_verse(1,d);self.assertEqual(v['footnotes'],d['translation']['footnotes'])
        self.assertEqual(v['source_critical']['text'],d['source']['text'])
        self.assertEqual([n['marker']for n in v['footnotes']],['a','b'])
        payload=reader.export_extra_canonical_book('ENO');c=next(x for x in payload['chapters']if x['chapter']==97)
        self.assertEqual(len(c['verses']),10)
        self.assertNotIn(96,{x['chapter']for x in payload['chapters']})

    def test_rehashed_source_english_each_note_rejected(self):
        for mode in ['source','English',0,1]:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory()as root:
                p,m=self.fixture(root);f=p/'097-001.candidate.yaml';d=yaml.load(f.read_bytes(),Loader=t.LOADER)
                if mode=='source':d['source']['text']+=' ወ'
                elif mode=='English':d['translation']['text']+=' altered'
                else:d['translation']['footnotes'][mode]['text']+=' altered'
                f.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m['files'][f.name]=t.sha(f.read_bytes());(p/'manifest.json').write_text(json.dumps(m))
                with self.assertRaises(ValueError):t.verify(p,evidence_only=True)

    def test_missing_or_corrupt_receipt_does_not_license_successor(self):
        for mode in ['missing','deployed','other-scope','manifest']:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory()as root:
                p,m=self.fixture(root);f=p/'application.json'
                if mode=='missing':f.unlink()
                else:
                    r=j(f)
                    if mode=='deployed':r['deployed_by_transaction']=True
                    elif mode=='other-scope':r['candidate_files']=2
                    else:r['manifest_sha256']='0'*64
                    f.write_text(json.dumps(r))
                with self.route(p),self.assertRaises((ValueError,OSError)):prior.verify_current()

    def test_full10_old_receipt_and_identity_substitution_rejected(self):
        for mode in ['drop-held','self-peer','old-input']:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory()as root:
                p,m=self.fixture(root)
                if mode=='drop-held':
                    f=p/'final/ch97/independent-input.json';x=j(f);x.pop();f.write_text(json.dumps(x));m['files']['final/ch97/independent-input.json']=t.sha(f.read_bytes())
                elif mode=='self-peer':m['review_bindings'][b.REF][1]['reviewer_id']='/root'
                else:m['files']['final/ch97/independent-input.json']='a654dd44220665482b31a0aa73d296fc68ce1f5a5d19b61e09132e352f5f0d79'
                with self.assertRaises(ValueError):b._pair(p,m)

    def test_any_other_canonical_drift_rejected(self):
        before=t.corpus_hashes()
        for path in [b.PATH,'097/002.yaml','096/001.yaml','001/001.yaml','096/004.yaml']:
            changed=dict(before);changed[path]='0'*64
            with self.subTest(path=path),patch.object(t,'corpus_hashes',return_value=changed),self.assertRaises(ValueError):b.verify_current()

    def test_other_registry_drift_rejected(self):
        for mode in ['neighbor','chapter','unrelated']:
            reg=copy.deepcopy(sources.registry_data())
            if mode=='neighbor':reg['units']['97:2']=b.NAME
            elif mode=='chapter':reg['chapters']['97']=b.NAME
            else:reg['units']['1:1']='unapproved'
            with self.subTest(mode=mode),patch.object(sources,'registry_data',return_value=reg),self.assertRaises(ValueError):b.verify_current()

    def test_no_publisher_change_and_ci_fetches_real_baseline(self):
        path='.github/workflows/publish-pob.yml'
        self.assertEqual((t.ROOT/path).read_bytes(),subprocess.check_output(['git','show',b.BASE+':'+path],cwd=t.ROOT))
        workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn('git fetch --no-tags --depth=1 origin '+b.BASE,workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_enoch_full_repair_batch37.py'",workflow)

if __name__=='__main__':unittest.main()
