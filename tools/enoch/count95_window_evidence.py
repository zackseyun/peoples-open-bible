"""One existing-count source window, not a count or language review.

The historical snapshots remain immutable. A proposal alone never permits
current-map drift: only the exact applied receipt enables this last successor.
"""
import argparse
import copy
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile

from tools.enoch import bounded_application as t

PREFIX = 'sources/enoch/coverage/count95-window-20261031'
INDEX = PREFIX + '/index.json'
INDEX_SHA = '3166bb3dcc29e2f7bd1e1165bce64515030dcdf303cdd8c40d19127c3b20f236'
PROOF_SHA = '6a8f1686c7c2799008f4e47186fea2355dbde2833dfb1249c36cc19571dea844'
PATH = 'sources/enoch/ethiopic/page_map.json'
BASE = 'a3681961d91c1eb1a609e12cec312a644148f9bb'
BEFORE_SHA = 'dc672a5dacef5ddca28c354aef1c12dc57d779e88abcb3fbb8887e0ab98c1bd4'
AFTER_SHA = '9cc3409eb2da96372ccf227bdd5ae419c276c786b48247a769a678e50afbca05'
COUNT_INDEX = 'sources/enoch/coverage/count91-103-20261022/paired-count-index-v2.json'
COUNT_INDEX_SHA = 'c72f8a27a25e4f5245422740934102fe5d55dc253454ab2098c0f0b6217b932d'
RECEIPT = PREFIX + '/application.json'
LIMITS = {'new_count_inventories': 0, 'new_count_votes': 0,
          'new_language_votes': 0, 'canonical_YAML_changes': 0,
          'wording_approval': False, 'reader_release_policy_changed': False,
          'publication_approved': False}
CHANGES = [{'json_path': '$.editions.charles_1906.chapters.095.pages',
            'before': [237], 'after': [237, 238]}]


def _json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=True) + '\n').encode()


def _git_before_bytes():
    return subprocess.check_output(['git', 'show', BASE + ':' + PATH], cwd=t.ROOT)


def evidence():
    """Validate historical proof without calling global window/count loaders."""
    raw = t.artifact(t.ROOT, INDEX).read_bytes()
    if t.sha(raw) != INDEX_SHA:
        raise ValueError('95 fixed source-window index differs')
    data = json.loads(raw)
    count_path = t.artifact(t.ROOT, COUNT_INDEX)
    count_raw = count_path.read_bytes()
    if t.sha(count_raw) != COUNT_INDEX_SHA:
        raise ValueError('95 original paired count index differs')
    count_index = json.loads(count_raw)
    expected = {'kind': 'enoch-existing95-source-window-v1',
                'artifact_prefix': PREFIX, 'baseline_commit': BASE,
                'canonical_path': PATH, 'primary_pdf_sha256': t.PRIMARY_SHA,
                'chapter': 95, 'units': list(range(1, 8)),
                'chapter_pages': [237, 238], 'before_sha256': BEFORE_SHA,
                'after_sha256': AFTER_SHA, 'existing_count_index': COUNT_INDEX,
                'existing_count_index_sha256': COUNT_INDEX_SHA,
                'existing_count_profile_files': count_index['files'],
                'files': {PREFIX + '/page-map-before.json': BEFORE_SHA,
                          PREFIX + '/page-map-after.json': AFTER_SHA,
                          PREFIX + '/window-proof.json': PROOF_SHA}, **LIMITS}
    if _json_bytes(data) != _json_bytes(expected):
        raise ValueError('95 exact source-only scope or approval limits differ')
    for name, digest in data['files'].items():
        if t.sha(t.artifact(t.ROOT, name).read_bytes()) != digest:
            raise ValueError('95 pinned source-window artifact differs: ' + name)
    # Directly validate the original complete profile. Calling the union of
    # counts here would recurse through the very window guards using us.
    from tools.enoch import structural_count_profiles
    counts = structural_count_profiles.load(count_path, root=t.ROOT)
    if counts[95]['units'] != list(range(1, 8)):
        raise ValueError('95 existing paired structural count differs')
    original = json.loads(t.artifact(t.ROOT, count_index['input']).read_text())
    rows = [row for row in original['chapters'] if row['chapter'] == 95]
    spans = {str(v): [237] if v <= 5 else [238] for v in range(1, 8)}
    if (len(rows) != 1 or rows[0]['chapter_pdf_pages'] != [237, 238] or
            {str(t.parse_ref(u['reference'])[1]): u['pdf_pages']
             for u in rows[0]['units']} != spans):
        raise ValueError('95 existing paired full chapter/unit spans differ')
    before_raw = t.artifact(t.ROOT, PREFIX + '/page-map-before.json').read_bytes()
    after_raw = t.artifact(t.ROOT, PREFIX + '/page-map-after.json').read_bytes()
    before, after = json.loads(before_raw), json.loads(after_raw)
    proof = json.loads(t.artifact(t.ROOT, PREFIX + '/window-proof.json').read_text())
    expected_proof = {'kind': 'enoch-existing95-source-window-proof-v1',
                      'baseline_commit': BASE, 'canonical_path': PATH,
                      'primary_pdf_sha256': t.PRIMARY_SHA,
                      'before_sha256': BEFORE_SHA, 'after_sha256': AFTER_SHA,
                      'existing_count_index': COUNT_INDEX,
                      'existing_count_index_sha256': COUNT_INDEX_SHA,
                      'chapter': 95, 'units': list(range(1, 8)),
                      'unit_pages': spans, 'changes': CHANGES, **LIMITS}
    if _json_bytes(proof) != _json_bytes(expected_proof):
        raise ValueError('95 bounded window proof or approval limits differ')
    wanted = copy.deepcopy(before)
    if wanted['editions']['charles_1906']['chapters']['095']['pages'] != [237]:
        raise ValueError('95 historical window preimage differs')
    wanted['editions']['charles_1906']['chapters']['095']['pages'] = [237, 238]
    if after != wanted or after_raw != _json_bytes(wanted):
        raise ValueError('95 source-window change exceeds one exact array')
    if _git_before_bytes() != before_raw:
        raise ValueError('95 actual Git window predecessor differs')
    return data, after


def _expected_receipt():
    return {'kind': 'enoch-existing95-source-window-application-v1',
            'status': 'applied_verified', 'index_sha256': INDEX_SHA,
            'proof_sha256': PROOF_SHA, 'baseline_commit': BASE,
            'canonical_path': PATH, 'primary_pdf_sha256': t.PRIMARY_SHA,
            'before_sha256': BEFORE_SHA, 'after_sha256': AFTER_SHA,
            'existing_count_index_sha256': COUNT_INDEX_SHA,
            'changes': CHANGES, **LIMITS}


def _optional_bytes(path):
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def _applied_receipt():
    receipt = _optional_bytes(t.artifact(t.ROOT, RECEIPT))
    if receipt != _json_bytes(_expected_receipt()):
        raise ValueError('95 exact applied source-window receipt differs')
    if t.sha(t.artifact(t.ROOT, PATH).read_bytes()) != AFTER_SHA:
        raise ValueError('Current full source map needs an explicit reviewed window successor')
    return json.loads(receipt)


def window_successor(before_sha256):
    if before_sha256 != BEFORE_SHA:
        raise ValueError('95 window successor has a different predecessor')
    evidence()
    if t.artifact(t.ROOT, RECEIPT).exists():
        _applied_receipt()
        return AFTER_SHA
    # Proposal files are deliberately not an application receipt.
    if t.sha(t.artifact(t.ROOT, PATH).read_bytes()) != BEFORE_SHA:
        raise ValueError('Current full source map needs an explicit reviewed window successor')
    return BEFORE_SHA


def verify_current_windows():
    expected = window_successor(BEFORE_SHA)
    if t.sha(t.artifact(t.ROOT, PATH).read_bytes()) != expected:
        raise ValueError('Current full source map needs an explicit reviewed window successor')
    return True


def verify_applied():
    evidence()
    return _applied_receipt()


def _lock_path():
    # Stable outside the repository; never unlink a live lock inode. All
    # callers of this transaction for the same checkout share this lock.
    key = hashlib.sha256(str(t.ROOT.resolve()).encode()).hexdigest()
    return Path(tempfile.gettempdir()) / ('enoch-source-window-' + key + '.lock')


@contextmanager
def _exclusive_lock():
    fd = os.open(_lock_path(), os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


class AtomicWriteError(RuntimeError):
    def __init__(self, message, replaced):
        super().__init__(message)
        self.replaced = replaced


def _atomic_write(path, raw, expected):
    """Replace only a fresh exact preimage; retain commit state on I/O error."""
    fd, name = tempfile.mkstemp(prefix='.' + path.name + '.count95-', dir=path.parent)
    pending = Path(name)
    replaced = False
    try:
        mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
        os.fchmod(fd, mode)
        with os.fdopen(fd, 'wb') as stream:
            fd = None
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        if _optional_bytes(path) != expected:
            raise ValueError('95 fresh preimage changed before atomic replacement')
        os.replace(pending, path)
        replaced = True
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except Exception as error:
        raise AtomicWriteError(str(error), replaced) from error
    finally:
        if fd is not None:
            os.close(fd)
        pending.unlink(missing_ok=True)


def apply():
    """Apply only this window and receipt; never write YAML, Git, or counts.

    Advisory locking serializes cooperating callers. Fresh preimage checks and
    conditional rollback additionally refuse to overwrite a different state
    introduced by a noncooperating writer. Such external interference fails
    closed; it is not a claim of atomicity across arbitrary external writers.
    """
    with _exclusive_lock():
        evidence()
        target, receipt_path = t.artifact(t.ROOT, PATH), t.artifact(t.ROOT, RECEIPT)
        if receipt_path.exists():
            raise ValueError('95 window already has an application receipt')
        before = t.artifact(t.ROOT, PREFIX + '/page-map-before.json').read_bytes()
        after = t.artifact(t.ROOT, PREFIX + '/page-map-after.json').read_bytes()
        receipt = _json_bytes(_expected_receipt())
        if _optional_bytes(target) != before:
            raise ValueError('95 current map preimage changed before apply')
        map_written = receipt_written = False
        phase = 'map'
        try:
            _atomic_write(target, after, before)
            map_written = True
            evidence()  # Recheck immutable evidence before publishing a receipt.
            if _optional_bytes(target) != after:
                raise ValueError('95 map changed before receipt publication')
            phase = 'receipt'
            _atomic_write(receipt_path, receipt, None)
            receipt_written = True
            return verify_applied()
        except Exception as error:
            if isinstance(error, AtomicWriteError) and error.replaced:
                if phase == 'map':
                    map_written = True
                else:
                    receipt_written = True
            current_receipt = _optional_bytes(receipt_path)
            if current_receipt is not None:
                if not receipt_written or current_receipt != receipt:
                    raise RuntimeError('95 concurrent receipt changed; rollback refused') from error
                receipt_path.unlink()
            # Never restore our preimage over somebody else's different map.
            if map_written and _optional_bytes(target) == after:
                _atomic_write(target, before, after)
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('verify', 'verify-applied', 'apply'))
    args = parser.parse_args()
    if args.operation == 'apply':
        result = apply()
    elif args.operation == 'verify-applied':
        result = verify_applied()
    else:
        result = {'current_windows_verified': verify_current_windows(), **LIMITS}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
