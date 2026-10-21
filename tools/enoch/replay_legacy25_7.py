"""Replay both unchanged original25:7 checks at their immutable applied tree.

This tests historical reproducibility only, never current canonical approval.
No current parser, test code or current verse files enter the private replay.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from tools.enoch import bounded_application as transaction
from tools.textual_restoration.replay_unflagged_sample import git, extract_regular

COMMIT='e535f38cf637133f09519899049fbf374c44a29c'
TEST='tests/test_enoch25_7_application.py'
TEST_SHA='ba7600b703f4a66b0f524e5374740e5d0b7e5764733b961a3a922f43fce47467'
PACKAGE='sources/textual_restoration/applications/enoch_25_7_20261017'
CHILD="""
import json,pathlib,sys,unittest
root=pathlib.Path.cwd();sys.path[:0]=[str(root/'tests'),str(root)]
suite=unittest.defaultTestLoader.loadTestsFromName('test_enoch25_7_application')
result=unittest.TextTestRunner(stream=sys.stderr).run(suite)
print(json.dumps({'passed':result.wasSuccessful(),'tests_run':result.testsRun,
'skipped':len(result.skipped),'expected_failures':len(result.expectedFailures)}))
sys.exit(0 if result.wasSuccessful() else 1)
"""


def replay(repo=transaction.ROOT):
    if sys.flags.optimize:raise ValueError('Historical replay requires non-optimized Python')
    if git(repo,'rev-parse','--verify',COMMIT+'^{commit}').decode().strip()!=COMMIT:
        raise ValueError('Frozen Enoch commit differs')
    if transaction.sha(git(repo,'show',COMMIT+':'+TEST))!=TEST_SHA:
        raise ValueError('Frozen Enoch test differs')
    paths=['tools/enoch',TEST,'sources/enoch/ethiopic/transcribed/charles_1906/ch25.txt',
           'sources/enoch/ethiopic/transcribed/charles_1906/ch26.txt',
           'translation/extra_canonical/1_enoch/025',PACKAGE+'/application.json']
    paths += [f'{PACKAGE}/review-pass{n}/{name}' for n in (1,2)
              for name in ['review.json','provenance.json','review-input.json']]
    with tempfile.TemporaryDirectory(prefix='pob-enoch25-7-history-') as directory:
        extract_regular(git(repo,'archive','--format=tar',COMMIT,'--',*paths),Path(directory))
        child=subprocess.run([sys.executable,'-I','-c',CHILD],cwd=directory,
                             capture_output=True,text=True,timeout=180)
    if child.returncode:raise ValueError('Original Enoch25:7 replay failed: '+child.stderr)
    result=json.loads(child.stdout)
    if result!={'passed':True,'tests_run':2,'skipped':0,'expected_failures':0}:
        raise ValueError('Original Enoch25:7 check coverage differs')
    return {**result,'commit':COMMIT,'original_test_sha256':TEST_SHA,
            'current_corpus_validated':False,'application_approved':False}

if __name__=='__main__':print(json.dumps(replay(),indent=2))
