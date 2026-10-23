"""Six actual inherited14v2 accepts, not the adverse24 or a fresh review."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools.enoch import historical_evidence as h,bounded_application as t

INDEX=t.ROOT/'sources/enoch/coverage/historical-input-bindings-20261023.json'
RAW=t.ROOT/'sources/enoch/coverage/historical-raw-receipts-20261023/enoch14-v2'


class Recovered14Test(unittest.TestCase):
    def fixture(self,directory):
        root=Path(directory);d=json.loads(INDEX.read_text())
        for name in d['packages'][0]['files']:
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(t.ROOT/name,p)
        index=root/'index.json';index.write_text(json.dumps(d));return root,d,index

    def test_exact_six_accepts_current_bytes_no_fresh_or_count_claim(self):
        rows=h.load_current(INDEX)
        self.assertEqual(set(rows),{(14,v)for v in(19,20,21,22,23,25)})
        self.assertNotIn((14,24),rows)
        self.assertTrue(all(not x['fresh_review']and not x['full_chapter_count_certified_by_import']for x in rows.values()))
        self.assertEqual(h.load_count_inventories(INDEX),{})
        allrows=h.load_all_current();self.assertTrue(set(rows)<=set(allrows))
        self.assertIn((14,24),allrows) # Separate genuine v3, never v2 promotion.

    def test_original_input_reconstituted_from_exact_bound_prompt_not_guessed(self):
        pv=json.loads((RAW/'original-provenance.json').read_text())
        text=(RAW/'original-review-prompt.txt').read_text()
        embedded=json.loads(text.split('Exact inputs:\n',1)[1])
        raw=(json.dumps(embedded,ensure_ascii=False,indent=2)+'\n').encode()
        self.assertEqual(raw,(RAW/'review-input.reconstituted.json').read_bytes())
        self.assertEqual(t.sha(raw),'a85ae3bd69ec503ac97eb7b2717cf1f61d3424a3683092fe1d9a81550a6c3131')
        self.assertEqual(pv['package_input_sha256']['review-input.json'],t.sha(raw))
        self.assertEqual(pv['package_input_sha256']['review-prompt.txt'],t.sha((RAW/'original-review-prompt.txt').read_bytes()))
        original=json.loads((RAW/'original-raw-review.json').read_text())
        self.assertEqual(h.verdict(original,'1 Enoch 14:24'),'revise')
        self.assertFalse(original['chapter_complete'])

    def test_full_source_policy_allows_only_exact_lifecycle_delta(self):
        d=json.loads(INDEX.read_text());p=d['packages'][0]
        inputs=json.loads((t.ROOT/p['units'][0]['input']).read_text())
        for u in p['units']:
            row=next(x for x in inputs if x['reference']==u['reference'])
            candidate=yaml.load((t.ROOT/u['candidate']).read_bytes(),Loader=t.LOADER)
            h.validate_source_metadata_delta(row['source'],candidate['source'],u['source_metadata_policy'])
            for key in ('text','edition','language','pages','confidence','note','additional_translation_input','transcription_uncertainties'):
                bad=copy.deepcopy(candidate['source']);bad[key]={'unapproved':True}
                with self.assertRaisesRegex(ValueError,'beyond exact'):
                    h.validate_source_metadata_delta(row['source'],bad,u['source_metadata_policy'])
            with self.assertRaisesRegex(ValueError,'Unknown'):
                h.validate_source_metadata_delta(row['source'],candidate['source'],'ignore_notes')

    def test_raw_dependency_drift_rejects_even_before_current_hash_check(self):
        d=json.loads(INDEX.read_text())
        with tempfile.TemporaryDirectory()as directory:
            root,data,index=self.fixture(directory)
            path=root/data['packages'][0]['units'][0]['review']
            path.write_bytes(path.read_bytes()+b'\n')
            with patch.object(t,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'artifact hash differs'):h.load_current(index)

    def test_rebound_wrong_input_and_adverse24_cannot_be_laundered(self):
        with tempfile.TemporaryDirectory()as directory:
            root,d,index=self.fixture(directory);p=d['packages'][0]
            u=p['units'][0];u['input']=u['review'];index.write_text(json.dumps(d))
            with patch.object(t,'ROOT',root):
                with self.assertRaises(ValueError):h.load_current(index)
        with tempfile.TemporaryDirectory()as directory:
            root,d,index=self.fixture(directory);p=d['packages'][0];u=copy.deepcopy(p['units'][0])
            u.update(reference='1 Enoch 14:24',candidate=p['candidate']if 'candidate'in p else p['units'][0]['candidate'].replace('014-019','014-024'))
            # The original24 is retained among pinned files but cannot match v2
            # rejected source. No synthetic v2 acceptance is manufactured.
            p['units'].append(u);index.write_text(json.dumps(d))
            with patch.object(t,'ROOT',root):
                with self.assertRaises(ValueError):h.load_current(index)

    def test_current_semantic_drift_is_not_approved_by_old_input(self):
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);shutil.copytree(t.TRANSLATION,root/'1_enoch')
            p=root/'1_enoch/014/019.yaml';p.write_bytes(p.read_bytes()+b'\n# changed current metadata\n')
            with patch.object(t,'TRANSLATION',root/'1_enoch'):
                rows=h.load_current(INDEX)
            self.assertNotIn((14,19),rows);self.assertEqual(len(rows),5)
