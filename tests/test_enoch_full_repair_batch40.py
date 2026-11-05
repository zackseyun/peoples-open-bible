"""Exact combined 32:3 and 32:6, with the previous reader hold preserved in history."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.enoch import batch39_evidence as prior, batch40_evidence as b
from tools.enoch import bounded_application as t, selected_edition_sources as sources
from tools import export_reader_bible as reader

P = t.APPLICATIONS / b.NAME


class Batch40Test(unittest.TestCase):
    def test_fixed_combined_delta_and_previous_missing_address(self):
        old = prior.historical_postmap()['current_postmap']
        proof = b.verify_current()
        new = proof['current_postmap']
        self.assertEqual((len(old),len(new)),(967,968))
        self.assertEqual(set(new)-set(old),{'032/006.yaml'})
        self.assertEqual({k for k in new if old.get(k)!=new[k]},b.CHANGED_PATHS)
        self.assertEqual(proof['manifest']['references'],b.REFS)
        self.assertEqual(proof['manifest']['chapter_inventories'],[])
        self.assertEqual(prior.verify_current()['actual_current_postmap'],new)

    def test_review_and_source_ingress_preserve_exact_uncertainties(self):
        m=t.load_manifest(P)
        with patch.object(t,'TRANSLATION',Path('/no-canonical-echo')):
            overrides={r['verse']:r for r in sources.load_unit_overrides(32)}
        self.assertEqual(sorted(overrides),list(range(1,7)))
        for v in (3,6):
            ref=f'1 Enoch 32:{v}'
            a,peer=t.reviewed_rows(P,m['review_bindings'][ref],ref,m['files'])
            self.assertEqual(a,peer)
            self.assertEqual(overrides[v]['source']['text'],a['source']['text'])
            self.assertIn(b.NAME,overrides[v]['evidence'])
            self.assertEqual(a['source']['confidence'],'low')
            self.assertTrue(a['source']['transcription_uncertainties'])
        a=json.loads((P/'final/32-3/author-input.json').read_text())[0]
        self.assertIn('ከሐክቲሆሙ',a['source']['text'])
        self.assertIn('[ከሐክቲሆሙ, meaning unclear]',a['translation']['text'])
        self.assertIn('pleasant fragrance',a['translation']['text'])
        self.assertNotIn('from afar',a['translation']['text'])

    def test_offline_reader_adds_only_complete_chapter_32(self):
        after=reader.export_extra_canonical_book('ENO')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            shutil.copytree(t.TRANSLATION,root/'1_enoch')
            (root/'1_enoch/032/006.yaml').unlink()
            (root/'1_enoch/032/003.yaml').write_bytes(subprocess.check_output(
                ['git','show',b.BASE+':translation/extra_canonical/1_enoch/032/003.yaml'],cwd=t.ROOT))
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):
                before=reader.export_extra_canonical_book('ENO')
        a={c['chapter']:c for c in before['chapters']}
        z={c['chapter']:c for c in after['chapters']}
        self.assertEqual(set(z),set(a)|{32})
        self.assertEqual({k:z[k] for k in a},a)
        self.assertEqual([r['verse'] for r in z[32]['verses']],list(range(1,7)))
        for v in range(1,7):
            row=t.yaml.load((t.TRANSLATION/f'032/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)
            self.assertEqual(z[32]['verses'][v-1],reader._export_record_verse(v,row))
            self.assertFalse(row['source_correction']['graphic_publication_approved'])

    def test_other_or_partial_canonical_change_rejected(self):
        current=t.corpus_hashes()
        for key in ('032/003.yaml','032/006.yaml','032/005.yaml','066/002.yaml'):
            with self.subTest(key=key),patch.object(t,'corpus_hashes',return_value={**current,key:'0'*64}):
                with self.assertRaises(ValueError):
                    b.verify_current()

    def test_isolated_application_receipt_cannot_pass_exact_gate(self):
        receipt=P/'application.json'
        read=Path.read_text
        def altered(path,*args,**kwargs):
            s=read(path,*args,**kwargs)
            if path==receipt:
                d=json.loads(s)
                d['references']=['1 Enoch 32:6']
                return json.dumps(d)
            return s
        with patch.object(Path,'read_text',altered),self.assertRaisesRegex(ValueError,'receipt differs'):
            b.verify_current()
