"""Replay only two unchanged original32 pre-successor mechanical cases.

Their historical assertions remain intact at pinned af21. Current paired
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

COMMIT = 'af21d2ccfa20d3df47ac633c3d591a688d7c2c01'
SUCCESSOR = 'enoch_full_repair_batch12_20261022'
DESCRIPTOR = t.ROOT/'sources/enoch/coverage/frozen-mechanical-gates/32-pre-paired-successor-v1.json'
CASES = {'north': ('tests/test_enoch32_north_correction.py', 'test_enoch32_north_correction.Enoch32NorthCorrection.test_bounded_correction_not_publication', 'cb6d5421955945e6231ef565399899cf66a8a94d15c42cd04a177218d0b6431b'), 'crosspage5': ('tests/test_enoch32_5_application.py', 'test_enoch32_5_application.Enoch325Application.test_complete_individual_unit_and_chapter_hold', 'aee0ebe89bdbf2fa217ec1f99c357fe01a744340fb9dafd67d15909bc785fe09')}


def replay(case):
    if sys.flags.optimize or case not in CASES:
        raise ValueError('Historical32 replay needs a registered case and non-optimized Python')
    data = json.loads(DESCRIPTOR.read_text())
    expected = {'kind': 'enoch32-pre-paired-successor-gates-v1', 'commit': COMMIT,
                'successor': SUCCESSOR, 'cases': {k: {'test': v[0], 'method': v[1],
                'test_sha256': v[2], 'expected_tests': 1} for k, v in CASES.items()}}
    if data != expected:
        raise ValueError('Historical32 descriptor differs')
    if git(t.ROOT, 'rev-parse', '--verify', COMMIT+'^{commit}').decode().strip() != COMMIT:
        raise ValueError('Historical32 commit unavailable')
    for test, _, digest in set(CASES.values()):
        if t.sha(git(t.ROOT, 'show', COMMIT+':'+test)) != digest:
            raise ValueError('Unchanged historical32 test source differs')
    from tools.enoch.current_evidence import verify_current
    package = t.APPLICATIONS/SUCCESSOR
    if not (package/'application.json').is_file():
        raise ValueError('Installed paired partial32 successor missing')
    current = verify_current(package)
    manifest = t.load_manifest(package)
    required = {f'1 Enoch 32:{v}' for v in (1, 2, 4, 5)}
    if not required <= set(current['references']) or manifest['chapter_inventories'] or \
            '1 Enoch 32:3' in manifest['references'] or '1 Enoch 32:6' in manifest['references']:
        raise ValueError('Installed paired partial32 successor differs')
    from tools.enoch.legacy32_evidence import verify_current as verify_old, NAMES
    for name in NAMES:
        if len(verify_old(t.APPLICATIONS/name)['reviewed_supersessions']) != 1:
            raise ValueError('Current32 historical-successor counterproof missing')
    names = git(t.ROOT, 'ls-tree', '-r', '--name-only', COMMIT).decode().splitlines()
    roots = ('tools', 'lib', 'schema', 'shared', 'data', 'sources/enoch',
             'sources/early_christian_texts', 'translation/extra_canonical/1_enoch')
    paths = [r for r in roots if any(n.startswith(r+'/') for n in names)]
    paths += sorted({'/'.join(n.split('/')[:4]) for n in names
                     if n.startswith('sources/textual_restoration/applications/enoch')})
    paths += sorted({v[0] for v in CASES.values()})
    with tempfile.TemporaryDirectory(prefix='pob32-pre-successor-') as directory:
        extract_regular(git(t.ROOT, 'archive', '--format=tar', COMMIT, '--', *paths), Path(directory))
        env = dict(os.environ, GIT_DIR=git(t.ROOT, 'rev-parse', '--absolute-git-dir').decode().strip(),
                   GIT_WORK_TREE=directory, GIT_NO_LAZY_FETCH='1')
        env.pop('GIT_INDEX_FILE', None)
        child = subprocess.run([sys.executable, '-I', '-c', CHILD, CASES[case][1]],
                               cwd=directory, env=env, capture_output=True, text=True, timeout=900)
    if child.returncode:
        raise ValueError('Unchanged historical32 case failed: '+child.stderr[-8000:])
    result = json.loads(child.stdout)
    if result != {'passed': True, 'tests_run': 1, 'skipped': 0, 'expected_failures': 0}:
        raise ValueError('Historical32 original coverage differs')
    return {**result, 'commit': COMMIT, 'original_test_sha256': CASES[case][2],
            'current_corpus_validated': False, 'publication_approved': False}


if __name__ == '__main__':
    print(json.dumps(replay(sys.argv[1]), indent=2))
