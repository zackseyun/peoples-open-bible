"""Replay only the unchanged original6 parent transaction mechanical case.

Their historical assertions remain intact at pinned2b91607. Current qualified paired coda and unchanged held6/7 are required separately.
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
SUCCESSOR = 'enoch_full_repair_batch14_20261023'
DESCRIPTOR = t.ROOT/'sources/enoch/coverage/frozen-mechanical-gates/6-pre-critical-coda-v1.json'
CASES = {'original': ('tests/test_enoch_6_transaction.py', 'test_enoch_6_transaction.EnochSixTransactionTest.test_frozen_source_and_review_package', 'e47b0b59a90e16a6ce0c540fe48d7cc9d9f37c6388a977712373d7b43df587c5')}


def replay(case):
    if sys.flags.optimize or case not in CASES:
        raise ValueError('Historical6coda replay needs a registered case and non-optimized Python')
    data = json.loads(DESCRIPTOR.read_text())
    expected = {'kind': 'enoch6-pre-critical-coda-gate-v1', 'commit': COMMIT,
                'successor': SUCCESSOR, 'cases': {k: {'test': v[0], 'method': v[1],
                'test_sha256': v[2], 'expected_tests': 1} for k, v in CASES.items()}}
    if data != expected:
        raise ValueError('Historical6coda descriptor differs')
    if git(t.ROOT, 'rev-parse', '--verify', COMMIT+'^{commit}').decode().strip() != COMMIT:
        raise ValueError('Historical6coda commit unavailable')
    for test, _, digest in set(CASES.values()):
        if t.sha(git(t.ROOT, 'show', COMMIT+':'+test)) != digest:
            raise ValueError('Unchanged historical6coda test source differs')
    from tools.enoch.current_evidence import verify_current
    package = t.APPLICATIONS/SUCCESSOR
    if not (package/'application.json').is_file():
        raise ValueError('Installed paired partial5/21 successor missing')
    current = verify_current(package)
    manifest = t.load_manifest(package)
    if '1 Enoch 6:8' not in current['references'] or any(c['chapter']==6 for c in manifest['chapter_inventories']):
        raise ValueError('Current6coda individual scope differs')
    from tools.enoch.legacy6_evidence import verify_current as verify_old,NAME
    proof=verify_old(t.APPLICATIONS/NAME)
    if proof['historical_independent_review_passes_proven']!=0 or proof['reviewed_supersessions']!=[{'reference':'1 Enoch 6:8','superseded_by':SUCCESSOR}]:
        raise ValueError('Current6coda parent history counterproof missing')
    import yaml
    d=yaml.load((t.TRANSLATION/'006/008.yaml').read_bytes(),Loader=t.LOADER)
    if d['source']['confidence']!='low' or not d['source']['transcription_uncertainties'] or 'ሀበይተ'not in d['source']['text'] or 'ሐበይተ'not in d['translation']['footnotes'][0]['text']:
        raise ValueError('Current6coda qualified orthographic distinction missing')
    names = git(t.ROOT, 'ls-tree', '-r', '--name-only', COMMIT).decode().splitlines()
    roots = ('tools', 'lib', 'schema', 'shared', 'data', 'sources/enoch',
             'sources/early_christian_texts', 'translation/extra_canonical/1_enoch')
    paths = [r for r in roots if any(n.startswith(r+'/') for n in names)]
    paths += sorted({'/'.join(n.split('/')[:4]) for n in names
                     if n.startswith('sources/textual_restoration/applications/enoch')})
    paths += sorted({v[0] for v in CASES.values()})
    with tempfile.TemporaryDirectory(prefix='pob6-pre-critical-coda-') as directory:
        extract_regular(git(t.ROOT, 'archive', '--format=tar', COMMIT, '--', *paths), Path(directory))
        env = dict(os.environ, GIT_DIR=git(t.ROOT, 'rev-parse', '--absolute-git-dir').decode().strip(),
                   GIT_WORK_TREE=directory, GIT_NO_LAZY_FETCH='1')
        env.pop('GIT_INDEX_FILE', None)
        child = subprocess.run([sys.executable, '-I', '-c', CHILD, CASES[case][1]],
                               cwd=directory, env=env, capture_output=True, text=True, timeout=900)
    if child.returncode:
        raise ValueError('Unchanged historical6coda case failed: '+child.stderr[-8000:])
    result = json.loads(child.stdout)
    if result != {'passed': True, 'tests_run': 1, 'skipped': 0, 'expected_failures': 0}:
        raise ValueError('Historical6coda original coverage differs')
    return {**result, 'commit': COMMIT, 'original_test_sha256': CASES[case][2],
            'current_corpus_validated': False, 'publication_approved': False}


if __name__ == '__main__':
    print(json.dumps(replay(sys.argv[1]), indent=2))
