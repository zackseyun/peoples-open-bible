"""Current Esdras7 safeguards without rewriting its immutable application proof."""
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

from tests import test_1esdras7_word_application as original

APPLIED = '9f4f2198128fa969948b4822cc423dba6f352228'
WORKFLOW = '.github/workflows/corpus-integrity.yml'


def reviewed(path):
    return subprocess.check_output(['git', '--no-replace-objects', 'show',
                                    f'{APPLIED}:{path}'], cwd=original.ROOT)


class EsdrasSevenLiveSuccessorTests(original.EsdrasSevenWordTests):
    """Inherit all five candidate/source/normalization/live/export checks."""

    def check_live_evidence(self):
        raw = (original.ROOT / original.EVIDENCE).read_bytes()
        self.assertEqual(raw, reviewed(original.EVIDENCE), original.EVIDENCE)
        evidence = json.loads(raw)
        self.assertEqual(evidence['baseline_commit'], original.BASE)
        self.assertTrue({original.SOURCE, original.ENGLISH, original.CANDIDATE,
                         original.NORMALIZED, 'docs/1ESDRAS_7_WORD_REPAIR_2026-10-19.md',
                         'tools/build_normalized_deuterocanon_corpus.py',
                         'tests/test_1esdras7_word_application.py', WORKFLOW,
                         'tools/textual_restoration/replay_historical_tests.py'}
                        <= set(evidence['reviewed_file_pins']))
        self.assertIn(original.CORPUS, evidence['historical_input_pins'])
        manifest = ''.join(path + '\t' + original.sha(raw) + '\n'
                           for path, raw in sorted(self.book.items()) if '/007/' in path)
        self.assertEqual(original.sha(manifest.encode()), evidence['canonical_baseline_manifest_sha256'])
        for path, pin in evidence['historical_input_pins'].items():
            self.assertEqual(original.sha(original.historical(path)), pin, path)
        for path in evidence['unchanged_live_inputs']:
            self.assertEqual((original.ROOT / path).read_bytes(), original.historical(path), path)
        for path, pin in evidence['reviewed_file_pins'].items():
            # Only workflow execution evolves; its original bytes remain pinned.
            raw = reviewed(path) if path == WORKFLOW else (original.ROOT / path).read_bytes()
            self.assertEqual(original.sha(raw), pin, path)
        mutable_implementations = {original.NORMALIZED, 'tools/build_normalized_deuterocanon_corpus.py',
                                  WORKFLOW, 'tools/textual_restoration/replay_historical_tests.py',
                                  'tests/test_replay_historical_tests.py'}
        for chapter in (5, 6, 8):
            path = original.PREFIX + f'comparisons/1esdras{chapter}_application.2026-10-19.v1.json'
            self.assertEqual((original.ROOT / path).read_bytes(), original.historical(path))
            previous = json.loads(original.historical(path))
            for frozen_path in set(previous['reviewed_file_pins']) - mutable_implementations:
                self.assertEqual((original.ROOT / frozen_path).read_bytes(),
                                 original.historical(frozen_path), frozen_path)
        workflow = (original.ROOT / WORKFLOW).read_text()
        for commit in (original.BASE, APPLIED, 'c083d5b872d1bb70c79f065cf0007cb97ffceb97',
                       '08a8a4cc05fcb8eb91580e01fb506a90de9799a9'):
            self.assertIn(f'git fetch --no-tags --depth=1 origin {commit}', workflow)
        for chapter in (5, 6, 8):
            self.assertIn(f'python -m tools.textual_restoration.replay_historical_tests esdras{chapter}_partition', workflow)
        self.assertIn('python -m tools.textual_restoration.replay_1esdras7_word', workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_1esdras7_word_live.py'", workflow)

    def test_historical_reviewed_pins_and_original5_6_8_evidence_remain_immutable(self):
        self.check_live_evidence()

    def test_current_workflow_can_evolve_without_repinning_original(self):
        read_text = Path.read_text

        def future_workflow(path, *args, **kwargs):
            raw = read_text(path, *args, **kwargs)
            return raw + '\n# future workflow comment\n' if path == original.ROOT / WORKFLOW else raw

        with patch.object(Path, 'read_text', future_workflow):
            self.check_live_evidence()

    def test_corrupted_historical_workflow_is_rejected(self):
        old_reviewed = reviewed

        def corrupt(path):
            return b'changed historical workflow' if path == WORKFLOW else old_reviewed(path)

        with patch(__name__ + '.reviewed', side_effect=corrupt):
            with self.assertRaises(AssertionError):
                self.check_live_evidence()

    def test_corrupted_live_evidence_source_proof_and_shared_runner_are_rejected(self):
        read_bytes = Path.read_bytes
        for target in (original.EVIDENCE, original.CANDIDATE,
                       'sources/lxx/swete/transcribed/vol2_p0167.txt',
                       'tests/test_1esdras7_word_application.py',
                       'tools/textual_restoration/replay_historical_tests.py'):
            with self.subTest(target=target):
                def corrupt(path, *args, **kwargs):
                    raw = read_bytes(path, *args, **kwargs)
                    return raw + b'\nchanged' if path == original.ROOT / target else raw

                with patch.object(Path, 'read_bytes', corrupt):
                    with self.assertRaises(AssertionError):
                        self.check_live_evidence()
