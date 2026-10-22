"""Replay three unchanged partial18 guards at their exact pre-complete tree.

The original assertions remain true of that tree. This narrow replay requires
an installed, verified all16 successor first, and is not current corpus proof.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from tools.enoch import bounded_application as t
from tools.textual_restoration.replay_unflagged_sample import git, extract_regular
from tools.enoch.replay_84_pre_critical_gate import CHILD

COMMIT = 'f082317ff0dad41b3ca856f4fd3e3a932f9d5748'
SUCCESSOR = 'enoch_full_repair_batch10_20261022'
DESCRIPTOR = t.ROOT/'sources/enoch/coverage/frozen-mechanical-gates/18-pre-complete-treatment-v1.json'
CASES = {
    'individual18': ('tests/test_enoch_full_repair_batch04.py',
        'test_enoch_full_repair_batch04.FullRepairBatch04Test.test_individual_18_negative_and_anomalous_printing_do_not_approve_chapter'),
    'export18': ('tests/test_enoch_full_repair_batch04.py',
        'test_enoch_full_repair_batch04.FullRepairBatch04Test.test_mobile_adds_only_four_full_chapters_and_retains_notes'),
    'progress18': ('tests/test_enoch_full_repair_batch08.py',
        'test_enoch_full_repair_batch08.FullRepairBatch08Test.test_progress_adds35_reviews_and3full_scopes_not_a_whole_book_certificate'),
}


def replay(case):
    if sys.flags.optimize or case not in CASES:
        raise ValueError('Frozen18 gate requires a registered case and non-optimized Python')
    descriptor = json.loads(DESCRIPTOR.read_text())
    if descriptor.get('kind') != 'enoch18-pre-complete-treatment-mechanical-gates-v1' or \
            descriptor.get('commit') != COMMIT or descriptor.get('successor') != SUCCESSOR or \
            set(descriptor.get('cases', {})) != set(CASES):
        raise ValueError('Frozen18 descriptor scope differs')
    if git(t.ROOT, 'rev-parse', '--verify', COMMIT+'^{commit}').decode().strip() != COMMIT:
        raise ValueError('Frozen18 commit unavailable')
    for key, (test, method) in CASES.items():
        row = descriptor['cases'][key]
        if row != {'test': test, 'method': method, 'expected_tests': 1,
                   'test_sha256': t.sha(git(t.ROOT, 'show', COMMIT+':'+test))}:
            raise ValueError('Frozen18 original source/test differs')
    from tools.enoch.current_evidence import verify_current
    if not (t.APPLICATIONS/SUCCESSOR/'application.json').is_file():
        raise ValueError('Installed full18 paired critical successor missing')
    result = verify_current(t.APPLICATIONS/SUCCESSOR)
    manifest = t.load_manifest(t.APPLICATIONS/SUCCESSOR)
    certificates = [c for c in manifest['chapter_inventories'] if c['chapter'] == 18]
    if not {f'1 Enoch 18:{v}' for v in range(1, 17)} <= set(result['references']) or \
            len(certificates) != 1 or certificates[0]['units'] != list(range(1, 17)):
        raise ValueError('Installed full18 paired critical successor missing')
    names = git(t.ROOT, 'ls-tree', '-r', '--name-only', COMMIT).decode().splitlines()
    roots = ('tools', 'lib', 'schema', 'shared', 'data', 'sources/enoch',
             'sources/early_christian_texts',
             'translation/extra_canonical/1_enoch')
    paths = [root for root in roots if any(n.startswith(root+'/') for n in names)]
    paths += sorted({'/'.join(n.split('/')[:4]) for n in names
                     if n.startswith('sources/textual_restoration/applications/enoch')})
    paths += sorted({test for test, _ in CASES.values()})
    git_dir = git(t.ROOT, 'rev-parse', '--absolute-git-dir').decode().strip()
    with tempfile.TemporaryDirectory(prefix='pob18-partial-gate-history-') as directory:
        extract_regular(git(t.ROOT, 'archive', '--format=tar', COMMIT, '--', *paths), Path(directory))
        env = dict(os.environ, GIT_DIR=git_dir, GIT_WORK_TREE=directory, GIT_NO_LAZY_FETCH='1')
        env.pop('GIT_INDEX_FILE', None)
        child = subprocess.run([sys.executable, '-I', '-c', CHILD, CASES[case][1]],
            cwd=directory, env=env, capture_output=True, text=True, timeout=900)
    if child.returncode:
        raise ValueError('Unchanged partial18 gate failed: '+child.stderr[-8000:])
    summary = json.loads(child.stdout)
    if summary != {'passed': True, 'tests_run': 1, 'skipped': 0, 'expected_failures': 0}:
        raise ValueError('Frozen18 original gate coverage differs')
    return {**summary, 'commit': COMMIT,
            'original_test_sha256': descriptor['cases'][case]['test_sha256'],
            'current_corpus_validated': False, 'publication_approved': False}


if __name__ == '__main__':
    print(json.dumps(replay(sys.argv[1]), indent=2))
