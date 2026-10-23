"""Replay only four unchanged original13:1-3 pre-successor mechanical cases.

Their historical assertions remain intact at pinnede05937e. Current paired
source/English/explanation and old-scope counterproof are required separately.
This is not source approval or a general historical-test escape hatch.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from tools.enoch import bounded_application as t
from tools.enoch.replay_84_pre_critical_gate import CHILD
from tools.textual_restoration.replay_unflagged_sample import git, extract_regular

COMMIT = 'e05937eff24f125aa4b18fb3f5ee9fd0c23270d0'
SUCCESSOR = 'enoch_full_repair_batch17_20261023'
DESCRIPTOR = t.ROOT/'sources/enoch/coverage/frozen-mechanical-gates/13-first3-pre-paired-successor-v1.json'
CASES = {'bytes': ('tests/test_enoch13_legacy_application.py', 'test_enoch13_legacy_application.Enoch13LegacyReview.test_exact_three_records_and_unchanged_selected_source', 'f02a8577f52906b37c8df95a564a29fd5a6a48e27a55e066b6e631cabadf7239'), 'metadata': ('tests/test_enoch13_legacy_application.py', 'test_enoch13_legacy_application.Enoch13LegacyReview.test_schema_marker_routing_and_current_review_truth', 'f02a8577f52906b37c8df95a564a29fd5a6a48e27a55e066b6e631cabadf7239'), 'respite': ('tests/test_enoch13_legacy_application.py', 'test_enoch13_legacy_application.Enoch13LegacyReview.test_respite_is_not_merged_with_petition_or_mercy', 'f02a8577f52906b37c8df95a564a29fd5a6a48e27a55e066b6e631cabadf7239'), 'words': ('tests/test_enoch13_legacy_application.py', 'test_enoch13_legacy_application.Enoch13LegacyReview.test_first_and_third_main_words_retained', 'f02a8577f52906b37c8df95a564a29fd5a6a48e27a55e066b6e631cabadf7239')}


def replay(case):
    if sys.flags.optimize or case not in CASES:
        raise ValueError('Historical13-first3 replay needs a registered case and non-optimized Python')
    data = json.loads(DESCRIPTOR.read_text())
    expected = {'kind': 'enoch13-first3-pre-paired-successor-gates-v1', 'commit': COMMIT,
                'successor': SUCCESSOR, 'cases': {k: {'test': v[0], 'method': v[1],
                'test_sha256': v[2], 'expected_tests': 1} for k, v in CASES.items()}}
    if data != expected:
        raise ValueError('Historical13-first3 descriptor differs')
    if git(t.ROOT, 'rev-parse', '--verify', COMMIT+'^{commit}').decode().strip() != COMMIT:
        raise ValueError('Historical13-first3 commit unavailable')
    for test, _, digest in set(CASES.values()):
        if t.sha(git(t.ROOT, 'show', COMMIT+':'+test)) != digest:
            raise ValueError('Unchanged historical13-first3 test source differs')
    from tools.enoch.current_evidence import verify_current
    package = t.APPLICATIONS/SUCCESSOR
    if not (package/'application.json').is_file():
        raise ValueError('Installed paired partial13/14 successor missing')
    current = verify_current(package)
    manifest = t.load_manifest(package)
    required={f'1 Enoch 13:{v}'for v in(1,2,3)}
    if not required<=set(current['references']) or manifest['chapter_inventories']:
        raise ValueError('Current paired partial13-14 scope differs')
    from tools.enoch.legacy13_parent_evidence import verify_current as verify_old,NAME
    proof=verify_old(t.APPLICATIONS/NAME)
    if {r['reference']for r in proof['reviewed_supersessions']}!=required or proof['historical_independent_source_review_passes_proven']!=0:
        raise ValueError('Current13 editorial-history counterproof missing')
    names = git(t.ROOT, 'ls-tree', '-r', '--name-only', COMMIT).decode().splitlines()
    roots = ('tools', 'lib', 'schema', 'shared', 'data', 'sources/enoch',
             'sources/early_christian_texts', 'translation/extra_canonical/1_enoch')
    paths = [r for r in roots if any(n.startswith(r+'/') for n in names)]
    paths += sorted({'/'.join(n.split('/')[:4]) for n in names
                     if n.startswith('sources/textual_restoration/applications/enoch')})
    paths += sorted({v[0] for v in CASES.values()})
    with tempfile.TemporaryDirectory(prefix='pob13-first3-pre-successor-') as directory:
        extract_regular(git(t.ROOT, 'archive', '--format=tar', COMMIT, '--', *paths), Path(directory))
        env = dict(os.environ, GIT_DIR=git(t.ROOT, 'rev-parse', '--absolute-git-dir').decode().strip(),
                   GIT_WORK_TREE=directory, GIT_NO_LAZY_FETCH='1')
        env.pop('GIT_INDEX_FILE', None)
        child = subprocess.run([sys.executable, '-I', '-c', CHILD, CASES[case][1]],
                               cwd=directory, env=env, capture_output=True, text=True, timeout=900)
    if child.returncode:
        raise ValueError('Unchanged historical13-first3 case failed: '+child.stderr[-8000:])
    result = json.loads(child.stdout)
    if result != {'passed': True, 'tests_run': 1, 'skipped': 0, 'expected_failures': 0}:
        raise ValueError('Historical13-first3 original coverage differs')
    return {**result, 'commit': COMMIT, 'original_test_sha256': CASES[case][2],
            'current_corpus_validated': False, 'publication_approved': False}


if __name__ == '__main__':
    print(json.dumps(replay(sys.argv[1]), indent=2))
