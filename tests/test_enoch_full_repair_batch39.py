"""Verify three exact reviewed units, the sole missing address, and reader scope."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.enoch import batch39_evidence as b, batch38_evidence as prior
from tools.enoch import bounded_application as t, existing_count_ingress, selected_edition_sources as sources
from tools import export_reader_bible as reader

P = t.APPLICATIONS / b.NAME


class Batch39Test(unittest.TestCase):
    def test_exact_current_delta_and_retained_count(self):
        proof = b.verify_current()
        old = prior.historical_postmap()['current_postmap']
        new = proof['current_postmap']
        self.assertEqual((len(old), len(new)), (966, 967))
        self.assertEqual(set(new) - set(old), {'066/002.yaml'})
        self.assertEqual({k for k in new if new[k] != old.get(k)}, b.CHANGED_PATHS)
        actual=prior.verify_current()['actual_current_postmap']
        self.assertEqual(proof['actual_current_postmap'],actual)
        from tools.enoch import batch40_evidence
        added=batch40_evidence.CHANGED_PATHS if proof.get('verified_current_successor')==batch40_evidence.NAME else set()
        from tools.enoch import batch41_evidence
        if (t.APPLICATIONS/batch41_evidence.NAME/'application.json').is_file():
            batch41_evidence.verify_current()
            added=added | batch41_evidence.CHANGED_PATHS
        self.assertEqual({k for k in actual if actual[k]!=new.get(k)},added)
        self.assertEqual(existing_count_ingress.validate(proof['manifest'])[66]['units'], [1, 2, 3])
        self.assertEqual(proof['manifest']['chapter_inventories'], [])

    def test_source_ingress_exact_pair_not_canonical_echo(self):
        m = t.load_manifest(P)
        for c,v in ((7,3),(66,1),(66,2)):
            ref=f'1 Enoch {c}:{v}'
            a,peer=t.reviewed_rows(P,m['review_bindings'][ref],ref,m['files'])
            self.assertEqual(a,peer)
            with patch.object(t,'TRANSLATION',Path('/no-canonical-echo')):
                rows=sources.load_unit_overrides(c)
            out=next(r for r in rows if r['verse']==v)
            self.assertEqual(out['source']['text'],a['source']['text'])
            self.assertIn(b.NAME,out['evidence'])
        a=json.loads((P/'final/ch07/author-input.json').read_text())[0]
        self.assertIn('ሴስዮት',a['source']['text'])
        self.assertNotIn('ሴስዮቶ',a['source']['text'])

    def test_reader_only_reviewed_7_3_and_complete_66(self):
        after=reader.export_extra_canonical_book('ENO')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            shutil.copytree(t.TRANSLATION,root/'1_enoch')
            for relative in sorted(b.CHANGED_PATHS):
                dest=root/'1_enoch'/relative
                if relative=='066/002.yaml':
                    dest.unlink()
                else:
                    path=t.TRANSLATION.relative_to(t.ROOT)/relative
                    dest.write_bytes(subprocess.check_output(['git','show',f'{b.BASE}:{path}'],cwd=t.ROOT))
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):
                before=reader.export_extra_canonical_book('ENO')
        a={c['chapter']:c['verses'] for c in before['chapters']}
        z={c['chapter']:c['verses'] for c in after['chapters']}
        self.assertEqual(set(z)-set(a),{66})
        self.assertEqual({c for c in a if a[c]!=z[c]},{7})
        self.assertEqual([v for v in a[7] if v['verse']!=3],[v for v in z[7] if v['verse']!=3])
        self.assertEqual([v['verse'] for v in z[66]],[1,2,3])
        for c,v in ((7,3),(66,1),(66,2)):
            row=t.yaml.load((P/f'{c:03d}-{v:03d}.candidate.yaml').read_bytes(),Loader=t.LOADER)
            self.assertEqual(next(x for x in z[c] if x['verse']==v),reader._export_record_verse(v,row))

    def test_extra_or_missing_canonical_address_rejected(self):
        current=t.corpus_hashes()
        missing=dict(current);del missing['066/002.yaml']
        for changed in (missing,{**current,'066/004.yaml':'0'*64}):
            with patch.object(t,'corpus_hashes',return_value=changed),self.assertRaises(ValueError):
                b.verify_current()
