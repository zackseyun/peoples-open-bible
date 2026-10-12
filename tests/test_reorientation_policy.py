"""Deterministic application checks, not certification of a translation's theology."""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest
from collections import Counter
from unittest.mock import patch
import yaml
from tools import reorientation_policy as policy

ROOT=Path(__file__).resolve().parents[1]

class ReorientationPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=json.loads(policy.PLAN.read_text())
        cls.items=cls.plan['records']
        cls.by_path={r['path']:r for r in cls.items}
        cls.current={r['path']:policy.load(ROOT/r['path']) for r in cls.items}
        # One git process; preserve object byte counts rather than line-splitting YAML.
        names=[cls.plan['baseline_commit']+':'+r['path'] for r in cls.items]
        raw=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(names)+'\n').encode(),cwd=ROOT)
        cls.baseline={};offset=0
        for r in cls.items:
            end=raw.index(b'\n',offset); header=raw[offset:end].split()
            if len(header)!=3:raise AssertionError('Missing pinned baseline '+r['path'])
            size=int(header[2]);blob=raw[end+1:end+1+size];offset=end+size+2
            if hashlib.sha256(blob).hexdigest()!=r['before_sha256']:raise AssertionError('Baseline hash mismatch '+r['path'])
            cls.baseline[r['path']]=yaml.load(blob,Loader=yaml.CSafeLoader)

    def read(self,tail,simplified=False):
        return policy.load(ROOT/('translation_simplified' if simplified else 'translation')/tail)

    def plain(self,tail,simplified=False):
        doc=self.read(tail,simplified)
        t=doc['translation']['text']
        for n in doc['translation'].get('footnotes')or[]:
            t=t.replace('['+str(n.get('marker'))+']','')
        return t

    def test_every_planned_record_applied_exactly_and_anchored(self):
        self.assertEqual(len(self.items),397)
        for item in self.items:
            with self.subTest(path=item['path']):
                d=self.current[item['path']];m=d['terminology_revision'];t=d['translation']['text']
                self.assertEqual(m['policy_id'],policy.POLICY)
                marker=m['reader_note_marker'];self.assertEqual(t.count('['+marker+']'),1)
                self.assertEqual(t.replace('['+marker+']',''),item['after_text'])
                self.assertEqual(policy.approved_errors(ROOT/item['path'],d,True),[])
                self.assertTrue(any(n['marker']==marker and n['text'] for n in d['translation']['footnotes']))

    def test_note_labels_work_with_existing_publishers(self):
        for item in self.items:
            d=self.current[item['path']];m=d['terminology_revision']['reader_note_marker']
            self.assertRegex(m,r'^[a-z]$')
            self.assertEqual(d['translation']['text'].count('['+m+']'),1)
            # Existing publisher strips ordinary ASCII-letter labels, not r1.
            self.assertNotIn('['+m+']',re.sub(r'\[[a-z]\]','',d['translation']['text']))
            if 'marker_compatibility' in d['terminology_revision']:
                self.assertFalse(d['terminology_revision']['marker_compatibility']['semantic_text_changed'])
                self.assertEqual(d['revisions'][-1]['from_sha256'],d['revisions'][-2]['to_sha256'])

    def test_sources_generation_and_existing_history_preserved(self):
        for item in self.items:
            with self.subTest(path=item['path']):
                old=self.baseline[item['path']];new=self.current[item['path']]
                self.assertEqual(old.get('source'),new.get('source'))
                self.assertEqual(policy.digest(new.get('source')or{}),item['source_sha256'])
                self.assertEqual(old.get('ai_draft'),new.get('ai_draft'))
                self.assertEqual(old.get('base_translation'),new.get('base_translation'))
                self.assertEqual(old.get('source_grounding'),new.get('source_grounding'))
                self.assertEqual(new['revisions'][:len(old.get('revisions',[]))],old.get('revisions',[]))
                self.assertEqual(new['revisions'][-1]['to_sha256'],new['terminology_revision']['after_text_sha256'])
                self.assertEqual(new['status'],'draft')
                self.assertEqual(new['cross_check'],{'status':'needs_review'})
                self.assertNotIn('revision_pass',new)
                self.assertFalse(new['terminology_revision']['independent_scholar_review'])
                archived=[h for h in new['review_history'] if h.get('archived_by')==policy.POLICY]
                for field in policy.ARCHIVE_FIELDS:
                    if field in old:self.assertTrue(any(h['field']==field and h['value']==old[field] for h in archived))

    def test_no_new_intensifiers(self):
        pattern=r'\b(?:fully|completely|radically|truly|wholeheartedly|entirely|absolutely|totally|utterly)\b'
        for item in self.items:
            before=Counter(re.findall(pattern,self.baseline[item['path']]['translation']['text'],re.I))
            after=Counter(re.findall(pattern,item['after_text'],re.I))
            self.assertEqual(before,after,item['path'])
        herm=self.plain('extra_canonical/shepherd_of_hermas/021/004.yaml')
        self.assertIn('reoriented completely',herm);self.assertIn('from their whole heart',herm)
        self.assertIn('ὁλοτελῶς',self.read('extra_canonical/shepherd_of_hermas/021/004.yaml')['source']['text'])

    def test_all_main_english_reader_text_free_of_legacy_terms(self):
        files=subprocess.check_output(['git','ls-files','translation','translation_simplified'],cwd=ROOT,text=True).splitlines()
        failures=[]
        for name in files:
            if not name.endswith('.yaml'):continue
            raw=(ROOT/name).read_text()
            if not policy.TERM.search(raw):continue
            doc=yaml.load(raw,Loader=yaml.CSafeLoader)
            if isinstance(doc,dict) and policy.TERM.search((doc.get('translation')or{}).get('text','')):failures.append(name)
        self.assertEqual(failures,[])

    def test_godward_and_separate_turning_expressions(self):
        for simple in (False,True):
            self.assertIn('Reorient toward God',self.plain('nt/mark/001/015.yaml',simple))
            self.assertIn('reorientation toward God',self.plain('nt/acts/020/021.yaml',simple))
            text=self.plain('nt/acts/026/020.yaml',simple)
            self.assertIn('reorient and turn to God',text)
            self.assertNotIn('toward God and turn to God',text)
            self.assertIn('away from',self.plain('nt/revelation/009/021.yaml',simple))
            self.assertIn('I am reorienting myself',self.plain('nt/luke/017/004.yaml',simple))
            self.assertIn('a change of mind',self.plain('nt/hebrews/012/017.yaml',simple))
            self.assertIn('feel regret',self.plain('ot/job/042/006.yaml',simple))
            self.assertIn('regret',self.plain('ot/jeremiah/031/019.yaml',simple))
            for verse in ('003','005'):
                self.assertIn('reorient toward God',self.plain('nt/luke/013/'+verse+'.yaml',simple))

    def test_exceptional_directions_and_divine_subjects(self):
        self.assertIn('unregretted',self.plain('extra_canonical/1_clement/054/004.yaml'))
        for chapter in ('010','012'):
            text=self.plain('extra_canonical/martyrdom_of_polycarp/'+chapter+'.yaml')
            self.assertIn('reconsider',text);self.assertNotIn('reorient toward God',text)
        herm=self.plain('extra_canonical/shepherd_of_hermas/015/003.yaml')
        self.assertIn('they change their minds and go back again after their evil desires',herm)
        for tail in ('040.yaml','040/004.yaml'):
            self.assertIn('often change their minds',self.plain('extra_canonical/shepherd_of_hermas/'+tail))
        const=self.plain('extra_canonical/apostolic_constitutions/002.yaml')
        self.assertIn('relentest concerning the evils of men',const)
        self.assertIn('will not change His mind',const)
        self.assertIn('felt remorse',self.plain('extra_canonical/apostolic_constitutions/007.yaml'))

    def test_witness_adaptation_disclosed_without_source_mutation(self):
        count=0
        for d in self.current.values():
            if d['terminology_revision']['english_witness_adaptation']:
                count+=1;m=d['terminology_revision']['reader_note_marker']
                note=next(n['text'] for n in d['translation']['footnotes'] if n['marker']==m)
                self.assertIn('not a verbatim quotation',note)
                self.assertIn('not a verbatim quotation or a newly verified translation',note)
        self.assertGreater(count,20)

    def test_morphological_negative_not_dropped_from_lexical_gloss(self):
        d=self.read('nt/revelation/009/021.yaml')
        hit=next(x for x in d['lexical_decisions'] if x['source_word']=='μετενόησαν')
        self.assertIn('did not',hit['chosen'])

    def test_regression_checker_rejects_legacy_reintroduction(self):
        d=copy.deepcopy(self.read('nt/mark/001/015.yaml'))
        d['translation']['text']='Repent and believe.'
        self.assertTrue(policy.approved_errors(ROOT/'translation/nt/mark/001/015.yaml',d))

    def test_selected_reader_exports_preserve_current_wording_and_notes(self):
        from tools import export_mobile_bible as e
        for simple in (False,True):
            root=ROOT/('translation_simplified' if simple else 'translation')
            with patch.object(e.draft,'TRANSLATION_ROOT',root),patch.object(e,'TRANSLATION_ROOT',root),patch.object(e,'APOCRYPHA_ROOT',root/'deuterocanon'),patch.object(e,'EXTRA_CANONICAL_ROOT',root/'extra_canonical'):
                for code,ch,v,tail in [('MRK',1,15,'nt/mark/001/015.yaml'),('ACT',26,20,'nt/acts/026/020.yaml'),('JOB',42,6,'ot/job/042/006.yaml')]:
                    book=e.export_book(code)
                    actual=next(vr for cr in book['chapters'] if cr['chapter']==ch for vr in cr['verses'] if vr['verse']==v)
                    d=policy.load(root/tail)
                    self.assertEqual(actual['text'],d['translation']['text'])
                    mark=d['terminology_revision']['reader_note_marker']
                    self.assertTrue(any(n['marker']==mark for n in actual['footnotes']))

if __name__=='__main__':unittest.main()
