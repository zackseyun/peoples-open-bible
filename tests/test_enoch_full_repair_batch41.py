"""Exact 2:2/3:1 repair; uncertainty and previous holds remain visible."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.enoch import batch40_evidence as prior, batch41_evidence as b
from tools.enoch import bounded_application as t, selected_edition_sources as sources
from tools import export_reader_bible as reader

P=t.APPLICATIONS/b.NAME


class Batch41Test(unittest.TestCase):
    def test_exact_existing_addresses_and_corpus_preimage(self):
        old=prior.historical_postmap()['current_postmap']
        proof=b.verify_current()
        new=proof['current_postmap']
        self.assertEqual(set(new),set(old))
        self.assertEqual(len(new),968)
        self.assertEqual({k for k in new if new[k]!=old[k]},b.CHANGED_PATHS)
        self.assertEqual(prior.verify_current()['actual_current_postmap'],new)
        self.assertEqual(proof['manifest']['chapter_inventories'],[])

    def test_exact_pair_uncertainty_and_source_ingress_not_canonical_echo(self):
        m=t.load_manifest(P)
        for c,v in ((2,2),(3,1)):
            ref=f'1 Enoch {c}:{v}'
            a,peer=t.reviewed_rows(P,m['review_bindings'][ref],ref,m['files'])
            self.assertEqual(a,peer)
            self.assertEqual(a['source']['confidence'],'low')
            self.assertTrue(a['source']['transcription_uncertainties'])
            with patch.object(t,'TRANSLATION',Path('/no-canonical-echo')):
                rows={x['verse']:x for x in sources.load_unit_overrides(c)}
            self.assertEqual(rows[v]['source']['text'],a['source']['text'])
            self.assertIn(b.NAME,rows[v]['evidence'])
        row=json.loads((P/'final/ch02/author-input.json').read_text())[0]
        self.assertIn('ወለብዉ',row['source']['text'])
        self.assertIn('ተፍጻሜቱ',row['source']['text'])
        self.assertIn('while appearing',row['translation']['text'])

    def test_reader_changes_exactly_two_units_without_new_address(self):
        after=reader.export_extra_canonical_book('ENO')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            shutil.copytree(t.TRANSLATION,root/'1_enoch')
            for rel in b.CHANGED_PATHS:
                path=t.TRANSLATION.relative_to(t.ROOT)/rel
                (root/'1_enoch'/rel).write_bytes(subprocess.check_output(
                    ['git','show',f'{b.BASE}:{path}'],cwd=t.ROOT))
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):
                before=reader.export_extra_canonical_book('ENO')
        index=lambda book:{(c['chapter'],v['verse']):v for c in book['chapters'] for v in c['verses']}
        a,z=index(before),index(after)
        self.assertEqual(a.keys(),z.keys())
        self.assertEqual({k for k in a if a[k]!=z[k]},{(2,2),(3,1)})
        for c,v in ((2,2),(3,1)):
            d=t.yaml.load((P/f'{c:03d}-{v:03d}.candidate.yaml').read_bytes(),Loader=t.LOADER)
            self.assertEqual(z[(c,v)],reader._export_record_verse(v,d))
            self.assertFalse(d['source_correction']['chapter_publication_approval'])

    def test_unrelated_or_partial_postmap_rejected(self):
        current=t.corpus_hashes()
        for k in ('002/002.yaml','003/001.yaml','002/003.yaml'):
            with self.subTest(k=k),patch.object(t,'corpus_hashes',return_value={**current,k:'0'*64}),self.assertRaises(ValueError):
                b.verify_current()
