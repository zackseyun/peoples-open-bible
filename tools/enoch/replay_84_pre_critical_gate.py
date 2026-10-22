"""Replay the unchanged pre-critical-treatment84 mechanical guard at its tree.

Only the old count-versus-approval test runs here. Current complete84 critical
controls are separately required by batch08 tests; this is not a source vote,
current-corpus proof, arbitrary historical-test runner or publication approval.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from tools.enoch import bounded_application as t
from tools.textual_restoration.replay_unflagged_sample import git,extract_regular

COMMIT='6c8803637481d9e8abc622aa51946b3e7adc4c21'
TEST='tests/test_enoch_editorial_issues.py'
METHOD='test_enoch_editorial_issues.EditorialIssuesTest.test_chapter84_count_does_not_approve_held_text'
DESCRIPTOR=t.ROOT/'sources/enoch/coverage/frozen-mechanical-gates/84-pre-critical-treatment-v1.json'
CHILD="""
import json,pathlib,sys,unittest
root=pathlib.Path.cwd();sys.path[:0]=[str(root/'tests'),str(root)]
suite=unittest.defaultTestLoader.loadTestsFromName(sys.argv[1])
result=unittest.TextTestRunner(stream=sys.stderr).run(suite)
print(json.dumps({'passed':result.wasSuccessful(),'tests_run':result.testsRun,
'skipped':len(result.skipped),'expected_failures':len(result.expectedFailures)}))
sys.exit(0 if result.wasSuccessful() else 1)
"""

def replay():
    if sys.flags.optimize:raise ValueError('Frozen mechanical gate requires non-optimized Python')
    descriptor=json.loads(DESCRIPTOR.read_text())
    if descriptor.get('kind')!='enoch84-pre-critical-treatment-mechanical-gate-v1' or \
            descriptor.get('commit')!=COMMIT or descriptor.get('test')!=TEST or \
            descriptor.get('method')!=METHOD or descriptor.get('expected_tests')!=1 or \
            descriptor.get('successor')!='enoch_full_repair_batch08_20261022':
        raise ValueError('Frozen84 mechanical gate scope differs')
    if git(t.ROOT,'rev-parse','--verify',COMMIT+'^{commit}').decode().strip()!=COMMIT or \
            t.sha(git(t.ROOT,'show',COMMIT+':'+TEST))!=descriptor.get('test_sha256'):
        raise ValueError('Frozen84 original source/test differs')
    from tools.enoch.current_evidence import verify_current
    successor=verify_current(t.APPLICATIONS/descriptor['successor'])
    if not {f'1 Enoch 84:{v}' for v in range(1,7)}<=set(successor['references']):
        raise ValueError('Full84critical successor evidence missing')
    names=git(t.ROOT,'ls-tree','-r','--name-only',COMMIT).decode().splitlines()
    roots=('tools','lib','schema','shared','data','sources/enoch','translation/extra_canonical/1_enoch')
    paths=[root for root in roots if any(name.startswith(root+'/') for name in names)]
    paths+=sorted({'/'.join(name.split('/')[:4]) for name in names
                   if name.startswith('sources/textual_restoration/applications/enoch')})
    paths += [TEST]
    git_dir=git(t.ROOT,'rev-parse','--absolute-git-dir').decode().strip()
    with tempfile.TemporaryDirectory(prefix='pob84-count-gate-history-') as directory:
        extract_regular(git(t.ROOT,'archive','--format=tar',COMMIT,'--',*paths),Path(directory))
        env=dict(os.environ,GIT_DIR=git_dir,GIT_WORK_TREE=directory,GIT_NO_LAZY_FETCH='1')
        env.pop('GIT_INDEX_FILE',None)
        child=subprocess.run([sys.executable,'-I','-c',CHILD,METHOD],cwd=directory,
                             env=env,capture_output=True,text=True,timeout=900)
    if child.returncode:raise ValueError('Unchanged84 pre-critical gate failed: '+child.stderr[:2000])
    result=json.loads(child.stdout)
    if result!={'passed':True,'tests_run':1,'skipped':0,'expected_failures':0}:
        raise ValueError('Frozen84 original gate coverage differs')
    return {**result,'commit':COMMIT,'original_test_sha256':descriptor['test_sha256'],
            'current_corpus_validated':False,'publication_approved':False}

if __name__=='__main__':print(json.dumps(replay(),indent=2))
