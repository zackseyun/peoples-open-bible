"""Replay only two unchanged original5/21 pre-successor mechanical cases.

Their historical assertions remain intact at pinned7c29. Current paired
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

COMMIT = '7c290e9d069ccabdb91eeccfd82ab592c80aef31'
SUCCESSOR = 'enoch_full_repair_batch13_20261023'
DESCRIPTOR = t.ROOT/'sources/enoch/coverage/frozen-mechanical-gates/5-21-pre-paired-successor-v1.json'
CASES = {'individual21': ('tests/test_enoch21_10_application.py', 'test_enoch21_10_application.Enoch2110Application.test_unit_exact_and_chapter_held', '162b210660168c95d1973917e4b71e95173dd934c07379ec51d7d418cbb418f9'), 'legacy5-export': ('tests/test_enoch_low_risk_transaction.py', 'test_enoch_low_risk_transaction.EnochLowRiskTransactionTest.test_only_chapters_five_and_seventeen_change_in_local_export', 'eb498407d82babd28562867aa44e45cc717901719f229219d7c38f53c2905b59')}


def replay(case):
    if sys.flags.optimize or case not in CASES:
        raise ValueError('Historical5/21 replay needs a registered case and non-optimized Python')
    data = json.loads(DESCRIPTOR.read_text())
    expected = {'kind': 'enoch5-21-pre-paired-successor-gates-v1', 'commit': COMMIT,
                'successor': SUCCESSOR, 'cases': {k: {'test': v[0], 'method': v[1],
                'test_sha256': v[2], 'expected_tests': 1} for k, v in CASES.items()}}
    if data != expected:
        raise ValueError('Historical5/21 descriptor differs')
    if git(t.ROOT, 'rev-parse', '--verify', COMMIT+'^{commit}').decode().strip() != COMMIT:
        raise ValueError('Historical5/21 commit unavailable')
    for test, _, digest in set(CASES.values()):
        if t.sha(git(t.ROOT, 'show', COMMIT+':'+test)) != digest:
            raise ValueError('Unchanged historical5/21 test source differs')
    from tools.enoch.current_evidence import verify_current
    package = t.APPLICATIONS/SUCCESSOR
    if not (package/'application.json').is_file():
        raise ValueError('Installed paired partial5/21 successor missing')
    current = verify_current(package)
    manifest = t.load_manifest(package)
    required = {'1 Enoch 5:9', '1 Enoch 21:9', '1 Enoch 21:10'}
    if not required <= set(current['references']) or any(
            c['chapter'] in (5, 21) for c in manifest['chapter_inventories']) or any(
            r in manifest['references'] for r in ('1 Enoch 5:1', '1 Enoch 5:6', '1 Enoch 21:3', '1 Enoch 21:6')):
        raise ValueError('Installed paired partial5/21 successor differs')
    from tools.enoch.legacy21_evidence import verify_current as verify_old, NAME
    if len(verify_old(t.APPLICATIONS/NAME)['reviewed_supersessions']) != 1:
        raise ValueError('Current21 historical-successor counterproof missing')
    names = git(t.ROOT, 'ls-tree', '-r', '--name-only', COMMIT).decode().splitlines()
    roots = ('tools', 'lib', 'schema', 'shared', 'data', 'sources/enoch',
             'sources/early_christian_texts', 'translation/extra_canonical/1_enoch')
    paths = [r for r in roots if any(n.startswith(r+'/') for n in names)]
    paths += sorted({'/'.join(n.split('/')[:4]) for n in names
                     if n.startswith('sources/textual_restoration/applications/enoch')})
    paths += sorted({v[0] for v in CASES.values()})
    with tempfile.TemporaryDirectory(prefix='pob5-21-pre-successor-') as directory:
        extract_regular(git(t.ROOT, 'archive', '--format=tar', COMMIT, '--', *paths), Path(directory))
        env = dict(os.environ, GIT_DIR=git(t.ROOT, 'rev-parse', '--absolute-git-dir').decode().strip(),
                   GIT_WORK_TREE=directory, GIT_NO_LAZY_FETCH='1')
        env.pop('GIT_INDEX_FILE', None)
        child = subprocess.run([sys.executable, '-I', '-c', CHILD, CASES[case][1]],
                               cwd=directory, env=env, capture_output=True, text=True, timeout=900)
    if child.returncode:
        raise ValueError('Unchanged historical5/21 case failed: '+child.stderr[-8000:])
    result = json.loads(child.stdout)
    if result != {'passed': True, 'tests_run': 1, 'skipped': 0, 'expected_failures': 0}:
        raise ValueError('Historical5/21 original coverage differs')
    return {**result, 'commit': COMMIT, 'original_test_sha256': CASES[case][2],
            'current_corpus_validated': False, 'publication_approved': False}


if __name__ == '__main__':
    print(json.dumps(replay(sys.argv[1]), indent=2))
