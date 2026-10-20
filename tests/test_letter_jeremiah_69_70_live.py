"""Live correction safeguards, separate from the unchanged historical proof."""
import json
import subprocess
from pathlib import Path
from unittest.mock import patch

from tests import test_letter_jeremiah_69_70_correction as original

APPLIED = 'a0ae3c29b4525087faa1ceab1ed2822301aa2f37'
METHOD = 'docs/TEXTUAL_ADJUDICATION_METHOD.md'


def reviewed(path):
    return subprocess.check_output(['git', 'show', f'{APPLIED}:{path}'], cwd=original.ROOT)


class LetterJeremiahLiveSuccessorTests(original.LetterJeremiahCorrectionTests):
    """Inherit all four source/candidate/corpus/export checks without edits."""

    def check_live_evidence(self):
        raw = (original.ROOT / original.EVIDENCE).read_bytes()
        self.assertEqual(raw, reviewed(original.EVIDENCE), original.EVIDENCE)
        evidence = json.loads(raw)
        self.assertEqual(evidence['baseline_commit'], original.BASE)
        # Every original historical pin remains binding, including the method.
        for path, pin in evidence['historical_input_pins'].items():
            self.assertEqual(original.sha(original.historical(path)), pin, path)
        # Includes the original test itself: never rewrite or repin that proof.
        for path, pin in evidence['reviewed_file_pins'].items():
            self.assertEqual(original.sha((original.ROOT / path).read_bytes()), pin, path)
        self.assertIn(METHOD, evidence['unchanged_live_inputs'])
        for path in evidence['unchanged_live_inputs']:
            if path != METHOD:
                self.assertEqual((original.ROOT / path).read_bytes(), original.historical(path), path)
        workflow = (original.ROOT / '.github/workflows/corpus-integrity.yml').read_text()
        for commit in (original.BASE, APPLIED):
            self.assertIn(f'git fetch --no-tags --depth=1 origin {commit}', workflow)
        self.assertIn('python -m tools.textual_restoration.replay_historical_tests letter_jeremiah69_70', workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_letter_jeremiah_69_70_live.py'", workflow)

    def test_frozen_evidence_and_ci_setup(self):
        self.check_live_evidence()

    def test_current_method_may_evolve_without_repinning_historical_method(self):
        read_bytes = Path.read_bytes

        def future_method(path, *args, **kwargs):
            if path == original.ROOT / METHOD:
                return b'a future methodology revision, not historical evidence'
            return read_bytes(path, *args, **kwargs)

        with patch.object(Path, 'read_bytes', future_method):
            self.check_live_evidence()

    def test_corrupted_historical_method_is_rejected(self):
        historical = original.historical

        def corrupt(path):
            return b'changed historical method' if path == METHOD else historical(path)

        with patch.object(original, 'historical', side_effect=corrupt):
            with self.assertRaises(AssertionError):
                self.check_live_evidence()

    def test_corrupted_live_source_original_test_and_evidence_are_rejected(self):
        read_bytes = Path.read_bytes
        for target in ('sources/lxx/swete/transcribed/vol3_p0407.txt',
                       'sources/lxx/swete/transcribed/vol3_p0407.meta.json',
                       'tests/test_letter_jeremiah_69_70_correction.py', original.EVIDENCE):
            with self.subTest(target=target):
                def corrupt(path, *args, **kwargs):
                    raw = read_bytes(path, *args, **kwargs)
                    return raw + b'\nchanged' if path == original.ROOT / target else raw

                with patch.object(Path, 'read_bytes', corrupt):
                    with self.assertRaises(AssertionError):
                        self.check_live_evidence()
