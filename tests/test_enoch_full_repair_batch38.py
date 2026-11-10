"""Exact individual 1:9 application; no chapter or publisher promotion."""
import json
import subprocess
from pathlib import Path
import unittest
from unittest.mock import patch

import yaml

from tools.enoch import batch38_evidence as b, bounded_application as t
from tools.enoch import selected_edition_sources as sources, verse_parser
from tools import export_reader_bible as reader

P = t.APPLICATIONS / b.NAME


class Batch38Test(unittest.TestCase):
    def test_exact_scope_and_current_source_ingress(self):
        proof = b.verify_current()
        before = proof['manifest']['canonical_baseline_sha256']
        self.assertEqual(len(before), 966)
        self.assertEqual({k for k in before if before[k] != proof['current_postmap'][k]}, {b.PATH})
        self.assertEqual(sources.registry_data()['units']['1:9'], b.NAME)
        with patch.object(t, 'TRANSLATION', Path('/no-canonical-echo')):
            overrides = sources.load_unit_overrides(1)
            self.assertIn(9, [row['verse'] for row in overrides])
        row, _ = verse_parser.load_verse(1, 9)
        candidate = yaml.load((P / '001-009.candidate.yaml').read_bytes(), Loader=t.LOADER)
        self.assertEqual(row.text, candidate['source']['text'])
        self.assertIn(b.NAME, row.chapter_file)

    def test_uncertainties_export_without_new_verse_exposure(self):
        d = yaml.load((t.TRANSLATION / b.PATH).read_bytes(), Loader=t.LOADER)
        self.assertEqual(d['source']['confidence'], 'low')
        self.assertIn('†ላዕሌሆሙ፡†', d['source']['text'])
        self.assertIn('ወረስዑ', d['source']['text'])
        v = reader._export_record_verse(9, d)
        self.assertEqual(v['footnotes'], d['translation']['footnotes'])
        self.assertEqual([n['marker'] for n in v['footnotes']], ['a', 'b', 'c'])
        def chapter_one():
            return next(c for c in reader.export_extra_canonical_book('ENO')['chapters'] if c['chapter'] == 1)
        after = chapter_one()
        target = t.TRANSLATION / b.PATH
        preimage = subprocess.check_output(
            ['git', 'show', f'{b.BASE}:{target.relative_to(t.ROOT)}'], cwd=t.ROOT)
        original = Path.read_text
        def read_before(p, *args, **kwargs):
            return preimage.decode() if p == target else original(p, *args, **kwargs)
        with patch.object(Path, 'read_text', read_before):
            before = chapter_one()
        self.assertEqual([v['verse'] for v in before['verses']], [v['verse'] for v in after['verses']])
        self.assertEqual([v for v in before['verses'] if v['verse'] != 9],
                         [v for v in after['verses'] if v['verse'] != 9])
        self.assertFalse(d['source_correction']['chapter_publication_approval'])

    def test_other_canonical_drift_rejected(self):
        hashes = t.corpus_hashes()
        for path in ('001/002.yaml', b.PATH):
            with self.subTest(path=path), patch.object(t, 'corpus_hashes', return_value={**hashes, path: '0' * 64}):
                with self.assertRaises(ValueError):
                    b.verify_current()

    def test_altered_receipt_rejected(self):
        path = P / 'application.json'
        original = Path.read_text
        def read_text(p, *args, **kwargs):
            if p == path:
                return json.dumps({**json.loads(original(p)), 'deployed_by_transaction': True})
            return original(p, *args, **kwargs)
        with patch.object(Path, 'read_text', read_text), self.assertRaisesRegex(ValueError, 'receipt differs'):
            b.verify_current()
