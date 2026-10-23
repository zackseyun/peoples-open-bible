"""Replay only two unchanged chapter6 count-only pre-successor mechanical cases.

Their historical assertions remain intact at pinned2b91607. Current mapping-only counterproof is required separately; no wording approval
is inferred from counts or mapping.
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

COMMIT = '2b91607210474c57a16a7f4c3745b2b7b18fce85'
DESCRIPTOR = t.ROOT/'sources/enoch/coverage/frozen-mechanical-gates/6-pre-reviewed-address-map-v1.json'
CASES = {'progress': ('tests/test_enoch_interleaved_structural_counts.py', 'test_enoch_interleaved_structural_counts.InterleavedCountTest.test_current_progress_distinguishes_printed7_from_canonical8_and_never_completes6', 'e7a540d411a5d325bb98f8b94885ed0f4685cbe6e8800335253681f69518a458'), 'audit': ('tests/test_enoch_interleaved_structural_counts.py', 'test_enoch_interleaved_structural_counts.InterleavedCountTest.test_diagnostic_count_difference_does_not_declare_canonical8_spurious', 'e7a540d411a5d325bb98f8b94885ed0f4685cbe6e8800335253681f69518a458')}


def replay(case):
    if sys.flags.optimize or case not in CASES:
        raise ValueError('Historical6 replay needs a registered case and non-optimized Python')
    data = json.loads(DESCRIPTOR.read_text())
    expected = {'kind': 'enoch6-pre-reviewed-address-map-gates-v1', 'commit': COMMIT,
                'mapping_index_sha256': 'ea0b7f90f7096bf407075f8908d6ae75e8e2451470448b2888444082176285f2', 'cases': {k: {'test': v[0], 'method': v[1],
                'test_sha256': v[2], 'expected_tests': 1} for k, v in CASES.items()}}
    if data != expected:
        raise ValueError('Historical6 descriptor differs')
    if git(t.ROOT, 'rev-parse', '--verify', COMMIT+'^{commit}').decode().strip() != COMMIT:
        raise ValueError('Historical6 commit unavailable')
    for test, _, digest in set(CASES.values()):
        if t.sha(git(t.ROOT, 'show', COMMIT+':'+test)) != digest:
            raise ValueError('Unchanged historical6 test source differs')
    from tools.enoch.canonical_address_maps import load_chapter6
    from tools.enoch import structural_counts,interleaved_structural_counts
    proof=load_chapter6()
    current=structural_counts.load_all_inventories()[6]
    raw=interleaved_structural_counts.load(t.ROOT/'sources/enoch/coverage/count1-8-20261022/paired-count-index-v3.json')[6]
    if proof['wording_approval'] is not False or proof['reader_release_policy_changed'] is not False or \
            current['units']!=list(range(1,8)) or current['canonical_address_units']!=list(range(1,9)) or \
            current['canonical_mapping_pending']is not False or raw['canonical_mapping_pending']is not True:
        raise ValueError('Current6 exact count/mapping-only counterproof missing')
    names = git(t.ROOT, 'ls-tree', '-r', '--name-only', COMMIT).decode().splitlines()
    roots = ('tools', 'lib', 'schema', 'shared', 'data', 'sources/enoch',
             'sources/early_christian_texts', 'translation/extra_canonical/1_enoch')
    paths = [r for r in roots if any(n.startswith(r+'/') for n in names)]
    paths += sorted({'/'.join(n.split('/')[:4]) for n in names
                     if n.startswith('sources/textual_restoration/applications/enoch')})
    paths += sorted({v[0] for v in CASES.values()})
    with tempfile.TemporaryDirectory(prefix='pob6-pre-address-map-') as directory:
        extract_regular(git(t.ROOT, 'archive', '--format=tar', COMMIT, '--', *paths), Path(directory))
        env = dict(os.environ, GIT_DIR=git(t.ROOT, 'rev-parse', '--absolute-git-dir').decode().strip(),
                   GIT_WORK_TREE=directory, GIT_NO_LAZY_FETCH='1')
        env.pop('GIT_INDEX_FILE', None)
        child = subprocess.run([sys.executable, '-I', '-c', CHILD, CASES[case][1]],
                               cwd=directory, env=env, capture_output=True, text=True, timeout=900)
    if child.returncode:
        raise ValueError('Unchanged historical6 case failed: '+child.stderr[-8000:])
    result = json.loads(child.stdout)
    if result != {'passed': True, 'tests_run': 1, 'skipped': 0, 'expected_failures': 0}:
        raise ValueError('Historical6 original coverage differs')
    return {**result, 'commit': COMMIT, 'original_test_sha256': CASES[case][2],
            'current_corpus_validated': False, 'publication_approved': False}


if __name__ == '__main__':
    print(json.dumps(replay(sys.argv[1]), indent=2))
