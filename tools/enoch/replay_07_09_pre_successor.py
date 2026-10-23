"""Replay only five unchanged original7/8/9 pre-successor mechanical cases.

Their historical assertions remain intact at pinned2b91607. Current paired
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

COMMIT = '2b91607210474c57a16a7f4c3745b2b7b18fce85'
SUCCESSOR = 'enoch_full_repair_batch14_20261023'
DESCRIPTOR = t.ROOT/'sources/enoch/coverage/frozen-mechanical-gates/7-9-pre-paired-successor-v1.json'
CASES = {'78bytes': ('tests/test_enoch7_8_application.py', 'test_enoch7_8_application.Enoch78.test_application_bytes_and_only_two_existing_replacements', '769b95a859155f08e64e28ac6f4aad98ab25757babc581df61eb4706e02a53f1'), '78metadata': ('tests/test_enoch7_8_application.py', 'test_enoch7_8_application.Enoch78.test_schema_notes_and_truthful_provenance', '769b95a859155f08e64e28ac6f4aad98ab25757babc581df61eb4706e02a53f1'), '78critical': ('tests/test_enoch7_8_application.py', 'test_enoch7_8_application.Enoch78.test_critical_and_uncertain_readings_not_harmonized', '769b95a859155f08e64e28ac6f4aad98ab25757babc581df61eb4706e02a53f1'), '910bytes': ('tests/test_enoch9_10_application.py', 'test_enoch9_10_application.Enoch910.test_receipt_after_and_25before_hashes', 'cb839497286aaf2ebaba0e1a0f7156f4c0e0ee394fa70e38dd80ce750843aeb4'), '910metadata': ('tests/test_enoch9_10_application.py', 'test_enoch9_10_application.Enoch910.test_schema_notes_and_provenance_are_truthful', 'cb839497286aaf2ebaba0e1a0f7156f4c0e0ee394fa70e38dd80ce750843aeb4')}


def replay(case):
    if sys.flags.optimize or case not in CASES:
        raise ValueError('Historical7-9 replay needs a registered case and non-optimized Python')
    data = json.loads(DESCRIPTOR.read_text())
    expected = {'kind': 'enoch7-9-pre-paired-successor-gates-v1', 'commit': COMMIT,
                'successor': SUCCESSOR, 'cases': {k: {'test': v[0], 'method': v[1],
                'test_sha256': v[2], 'expected_tests': 1} for k, v in CASES.items()}}
    if data != expected:
        raise ValueError('Historical7-9 descriptor differs')
    if git(t.ROOT, 'rev-parse', '--verify', COMMIT+'^{commit}').decode().strip() != COMMIT:
        raise ValueError('Historical7-9 commit unavailable')
    for test, _, digest in set(CASES.values()):
        if t.sha(git(t.ROOT, 'show', COMMIT+':'+test)) != digest:
            raise ValueError('Unchanged historical7-9 test source differs')
    from tools.enoch.current_evidence import verify_current
    package = t.APPLICATIONS/SUCCESSOR
    if not (package/'application.json').is_file():
        raise ValueError('Installed paired partial5/21 successor missing')
    current = verify_current(package)
    manifest = t.load_manifest(package)
    required={f'1 Enoch 7:{v}'for v in(1,2,4,5,6)}|{f'1 Enoch 8:{v}'for v in(2,4)}|{f'1 Enoch 9:{v}'for v in(1,3,5,7,8,9)}
    if not required<=set(current['references']) or any(c['chapter']in(7,8,9)for c in manifest['chapter_inventories']):
        raise ValueError('Current paired partial7-9 scope differs')
    from tools.enoch.legacy_editorial_evidence import verify_current as verify_old,NAMES
    for name in NAMES:
        proof=verify_old(t.APPLICATIONS/name)
        if not proof['reviewed_supersessions']or proof['historical_independent_review_passes_proven']!=0:
            raise ValueError('Current7-9 editorial-history counterproof missing')
    names = git(t.ROOT, 'ls-tree', '-r', '--name-only', COMMIT).decode().splitlines()
    roots = ('tools', 'lib', 'schema', 'shared', 'data', 'sources/enoch',
             'sources/early_christian_texts', 'translation/extra_canonical/1_enoch')
    paths = [r for r in roots if any(n.startswith(r+'/') for n in names)]
    paths += sorted({'/'.join(n.split('/')[:4]) for n in names
                     if n.startswith('sources/textual_restoration/applications/enoch')})
    paths += sorted({v[0] for v in CASES.values()})
    with tempfile.TemporaryDirectory(prefix='pob7-9-pre-successor-') as directory:
        extract_regular(git(t.ROOT, 'archive', '--format=tar', COMMIT, '--', *paths), Path(directory))
        env = dict(os.environ, GIT_DIR=git(t.ROOT, 'rev-parse', '--absolute-git-dir').decode().strip(),
                   GIT_WORK_TREE=directory, GIT_NO_LAZY_FETCH='1')
        env.pop('GIT_INDEX_FILE', None)
        child = subprocess.run([sys.executable, '-I', '-c', CHILD, CASES[case][1]],
                               cwd=directory, env=env, capture_output=True, text=True, timeout=900)
    if child.returncode:
        raise ValueError('Unchanged historical7-9 case failed: '+child.stderr[-8000:])
    result = json.loads(child.stdout)
    if result != {'passed': True, 'tests_run': 1, 'skipped': 0, 'expected_failures': 0}:
        raise ValueError('Historical7-9 original coverage differs')
    return {**result, 'commit': COMMIT, 'original_test_sha256': CASES[case][2],
            'current_corpus_validated': False, 'publication_approved': False}


if __name__ == '__main__':
    print(json.dumps(replay(sys.argv[1]), indent=2))
