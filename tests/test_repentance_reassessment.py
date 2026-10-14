"""Current 397-record contract: editorial decisions, not scholar certification."""
import copy
import json
import re
import subprocess
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import yaml
from tools import reorientation_policy as prior
from tools import repentance_reassessment as policy

ROOT=policy.ROOT

class ContextualRepentanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=json.loads(policy.PLAN.read_text())
        cls.items=cls.plan['records'];cls.by_path={r['path']:r for r in cls.items}
        cls.current={r['path']:prior.load(ROOT/r['path']) for r in cls.items}
        names=[cls.plan['baseline_commit']+':'+r['path'] for r in cls.items]
        raw=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(names)+'\n').encode(),cwd=ROOT)
        cls.before={};cls.raw_before={};offset=0
        for item in cls.items:
            end=raw.index(b'\n',offset);header=raw[offset:end].split()
            if len(header)!=3:raise AssertionError('Missing baseline '+item['path'])
            size=int(header[2]);blob=raw[end+1:end+size+1];offset=end+size+2
            cls.raw_before[item['path']]=blob
            cls.before[item['path']]=yaml.load(blob,Loader=yaml.CSafeLoader)

    def plain(self,tail,simple=False):
        d=self.current[('translation_simplified/' if simple else 'translation/')+tail]
        return re.sub(r'\[[a-z]\]','',d['translation']['text'])

    def test_exact_scope_includes_all_retained_and_followup_decisions(self):
        old=json.loads(prior.PLAN.read_text())
        self.assertEqual(len(self.items),397)
        self.assertEqual(set(self.by_path),{r['path'] for r in old['records']})
        follow=json.loads((ROOT/'config/terminology/reorientation-dialogue-2026-10-12.json').read_text())
        self.assertTrue({r['path'] for r in follow['records']}<=set(self.by_path))
        self.assertEqual(Counter(r['decision'] for r in self.items),{'revise_wording':367,'retain_contextual_wording':30})
        for r in self.items:
            self.assertGreater(len(r['rationale']),50)
            self.assertTrue(r['source_evidence']['limitation'])

    def test_every_input_output_source_note_and_lexical_choice_pinned(self):
        for r in self.items:
            with self.subTest(path=r['path']):
                old=self.before[r['path']];d=self.current[r['path']]
                self.assertEqual(policy.SHA(self.raw_before[r['path']]),r['input_file_sha256'])
                self.assertEqual(policy.SHA(old['translation']['text']),r['before_text_sha256'])
                self.assertEqual(policy.SHA(r['after_text']),r['after_text_sha256'])
                self.assertEqual(policy.approved_errors(ROOT/r['path'],d),[])
                self.assertEqual(prior.approved_errors(ROOT/r['path'],d,True),[])
                self.assertEqual(d['translation']['text'],r['after_text'])
                self.assertEqual(d['terminology_revision']['current_policy_id'],policy.POLICY)
                self.assertEqual(d['translation']['text']==old['translation']['text'],r['decision']=='retain_contextual_wording')
                self.assertNotRegex(d['translation']['text'],r'(?i)\breorient\w*')
                for entry in d.get('lexical_decisions',[]):
                    self.assertNotRegex(entry.get('chosen',''),r'(?i)\breorient\w*')

    def test_unrelated_fields_sources_generation_and_history_not_rewritten(self):
        permitted=set(policy.FIELDS)|{'review_history','revisions','revision_pass','source_audit'}
        for r in self.items:
            old=self.before[r['path']];new=self.current[r['path']]
            for field in set(old)|set(new):
                if field not in permitted:self.assertEqual(old.get(field),new.get(field),(r['path'],field))
            for field in ('review_history','revisions'):
                self.assertEqual(new[field][:len(old[field])],old[field],r['path'])
            for field in policy.FIELDS:
                if field in old:
                    archive=[x for x in new['review_history'] if x.get('archived_by')==policy.POLICY and x['field']==field]
                    self.assertEqual(len(archive),1)
                    self.assertEqual(archive[0]['sha256'],prior.digest(old[field]))
                    self.assertFalse(archive[0]['certifies_this_candidate'])
            revision=new['revisions'][-1]
            self.assertEqual(revision['from_sha256'],old['terminology_revision']['after_text_sha256'])
            self.assertEqual(revision['to_sha256'],new['terminology_revision']['after_text_sha256'])
            self.assertEqual(new['status'],'draft');self.assertEqual(new['cross_check'],{'status':'needs_review'})
            self.assertFalse(new['terminology_revision']['independent_scholar_review'])

    def test_reader_annotations_preserved_and_current_notes_anchored(self):
        for r in self.items:
            d=self.current[r['path']];old=self.before[r['path']];m=r['reader_note_marker']
            self.assertRegex(m,r'^[a-z]$')
            self.assertEqual(d['translation']['text'].count('['+m+']'),1)
            self.assertEqual([n['marker'] for n in d['translation']['footnotes']],
                             [n['marker'] for n in old['translation']['footnotes']])
            for n in old['translation']['footnotes']:
                if n['marker']==m:continue
                # Existing unrelated annotations are never removed, even if a
                # historical chapter already reused a label before this review.
                self.assertEqual(d['translation']['text'].count('['+n['marker']+']'),
                                 old['translation']['text'].count('['+n['marker']+']'))
            if d['terminology_revision']['english_witness_adaptation']:
                self.assertIn('not a verbatim quotation or a newly verified translation',r['reader_note'])

    def test_no_new_intensifiers_and_comparative_repair_kept(self):
        pattern=r'\b(?:fully|completely|radically|truly|wholeheartedly|entirely|absolutely|totally|utterly)\b'
        for r in self.items:
            self.assertEqual(Counter(re.findall(pattern,self.before[r['path']]['translation']['text'],re.I)),
                             Counter(re.findall(pattern,r['after_text'],re.I)),r['path'])
        for simple in (False,True):
            self.assertIn('more joy',self.plain('nt/luke/015/007.yaml',simple))
            self.assertIn('repented completely',self.plain('extra_canonical/shepherd_of_hermas/021/004.yaml',simple))

    def test_core_contextual_choices_in_both_editions(self):
        for simple in (False,True):
            self.assertIn('Repent and believe',self.plain('nt/mark/001/015.yaml',simple))
            self.assertIn('repentance toward God',self.plain('nt/acts/020/021.yaml',simple))
            self.assertIn('repent and turn to God',self.plain('nt/acts/026/020.yaml',simple))
            self.assertIn('produces repentance',self.plain('nt/2_corinthians/007/010.yaml',simple))
            self.assertIn('without regret',self.plain('nt/2_corinthians/007/010.yaml',simple))
            self.assertIn('I repent',self.plain('nt/luke/017/004.yaml',simple))
            self.assertIn('if he repents',self.plain('nt/luke/017/003.yaml',simple).lower())
            self.assertIn('a change of mind',self.plain('nt/hebrews/012/017.yaml',simple))
            self.assertIn('after I turned away',self.plain('ot/jeremiah/031/019.yaml',simple))
            self.assertIn('I was sorry for what I had done',self.plain('ot/jeremiah/031/019.yaml',simple))
            self.assertIn('feel regret',self.plain('ot/job/042/006.yaml',simple))
            for v in ('003','005'):self.assertIn('unless you repent',self.plain('nt/luke/013/'+v+'.yaml',simple))

    def test_adverse_changes_divine_subjects_and_sincerity(self):
        self.assertIn('Repentance from a sincere heart',self.plain('extra_canonical/2_clement/009.yaml'))
        self.assertIn('unregretted',self.plain('extra_canonical/1_clement/054/004.yaml'))
        self.assertIn('reconsider',self.plain('extra_canonical/martyrdom_of_polycarp/010.yaml'))
        self.assertIn('change their minds and go back again',self.plain('extra_canonical/shepherd_of_hermas/015/003.yaml'))
        self.assertIn('often change their minds',self.plain('extra_canonical/shepherd_of_hermas/040.yaml'))
        self.assertIn('to repent because',self.plain('extra_canonical/shepherd_of_hermas/015.yaml'))
        self.assertIn('they change their mind',self.plain('extra_canonical/shepherd_of_hermas/015.yaml'))
        self.assertIn('relentest concerning the evils of men',self.plain('extra_canonical/apostolic_constitutions/002.yaml'))
        self.assertIn('will not change His mind',self.plain('extra_canonical/apostolic_constitutions/002.yaml'))
        self.assertIn('felt remorse',self.plain('extra_canonical/apostolic_constitutions/007.yaml'))
        for simple in (False,True):
            self.assertIn('changed my attitude toward Joseph',self.plain('extra_canonical/testaments_twelve_patriarchs/gad/005/006.yaml',simple))

    def test_rejects_old_wording_tampering_missing_metadata_and_unknown_path(self):
        name='translation/nt/mark/001/015.yaml';d=copy.deepcopy(self.current[name])
        d['translation']['text']=self.before[name]['translation']['text']
        d['terminology_revision']['after_text_sha256']=policy.SHA(d['translation']['text'])
        self.assertTrue(policy.approved_errors(ROOT/name,d))
        d=copy.deepcopy(self.current[name]);del d['terminology_revision']['current_policy_id']
        self.assertTrue(policy.approved_errors(ROOT/name,d))
        d=copy.deepcopy(self.current[name]);d['source']['text']='changed'
        self.assertTrue(policy.approved_errors(ROOT/name,d))
        self.assertTrue(policy.approved_errors(ROOT/'translation/unknown.yaml',self.current[name]))

    def test_idempotent_check_and_apply(self):
        for apply in (False,True):
            with patch.object(Path,'write_text',side_effect=AssertionError('unexpected rewrite')):
                self.assertEqual(policy.run(apply=apply)['already_applied'],397)

    def test_preflight_last_input_drift_prevents_all_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp)
            for name,raw in self.raw_before.items():
                p=tmp/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            last=tmp/self.items[-1]['path'];last.write_bytes(last.read_bytes()+b'\n# drift\n')
            with patch.object(policy,'ROOT',tmp),patch.object(policy,'approved_errors',return_value=[]),\
                 patch.object(Path,'write_text',side_effect=AssertionError('partial write')):
                with self.assertRaisesRegex(ValueError,'input/source changed'):
                    policy.run(apply=True)

    def test_retained_exception_can_be_rebuilt_without_false_certification(self):
        r=next(x for x in self.items if x['id']=='JER.31.19')
        rebuilt=policy.build_record(self.before[r['path']],r,self.plan['baseline_commit'],'test')
        self.assertEqual(rebuilt['translation']['text'],self.before[r['path']]['translation']['text'])
        self.assertFalse(rebuilt['terminology_revision']['independent_scholar_review'])

if __name__=='__main__':unittest.main()
