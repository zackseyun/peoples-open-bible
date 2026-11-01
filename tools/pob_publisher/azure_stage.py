"""Inactive Azure adapter proposal. No live factory/CLI or ownership creation.

Only injected stores can exercise this transaction. Real identity/RBAC,
namespace exclusion, source freshness and AWS-writer quiescence are unverified.
"""
from contextlib import contextmanager
import hashlib
import json
import re

PREFIX = 'canonical-pob/v1/'
CONTROL = 'canonical-pob-control/v1.json'
LOCK = 'canonical-pob-control/publish.lock'
CURRENT = PREFIX + 'current.json'
ACCOUNT = 'carthawebpgtbcmh46gckn6'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()

def live_store():
    # Deliberate non-configurable interlock, not an env flag someone may flip.
    # A separately reviewed activation change must implement the factory.
    raise RuntimeError('Inactive proposal: no live Azure client or credentials instantiated')


class AzureBlobStore:
    """SDK mapping, supplied client only; production factory intentionally absent.

    Client must be the existing fixed-account managed-identity client after the
    separate activation gate. No account keys, DefaultAzureCredential fallback,
    new containers, delete operations, DNS or control/lease creation here.
    SDK API: https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.blobclient
    """
    def __init__(self, service, content_settings, match_conditions):
        if service.url.rstrip('/') != f'https://{ACCOUNT}.blob.core.windows.net':
            raise ValueError('Unexpected storage account')
        self.service, self.settings, self.conditions = service, content_settings, match_conditions

    def blob(self, container, key):
        if container not in ('$web', 'preview-receipts'):
            raise ValueError('Unexpected container')
        if container == '$web':
            if not key.startswith(PREFIX) or '..' in key or '\\' in key:
                raise ValueError('Outside canonical namespace')
        elif key not in (CONTROL, LOCK):
            raise ValueError('Outside existing control namespace')
        return self.service.get_blob_client(container, key)

    def get(self, container, key):
        # Missing objects are distinct from authentication/network failures.
        from azure.core.exceptions import ResourceNotFoundError
        try:
            stream = self.blob(container, key).download_blob()
            return stream.readall(), stream.properties.etag
        except ResourceNotFoundError:
            return None, None

    def put(self, key, data, *, etag=None, create=False):
        if key != CURRENT and not re.fullmatch(PREFIX + r'releases/[a-f0-9]{64}/(?:cob_preview|manifest)\.json', key):
            raise ValueError('Unexpected publication key')
        if create == (etag is not None):
            raise ValueError('Exactly one conditional write mode required')
        kwargs = {'overwrite': not create, 'content_settings': self.settings(
            content_type='application/json', cache_control='no-store' if key == CURRENT else 'public,max-age=31536000,immutable')}
        if not create:
            kwargs.update(etag=etag, match_condition=self.conditions.IfNotModified)
        self.blob('$web', key).upload_blob(data, **kwargs)

    @contextmanager
    def lock(self):
        # Lease blob must already exist from separately authorized activation.
        lease = self.blob('preview-receipts', LOCK).acquire_lease(lease_duration=60)
        try:
            yield lease.renew
        finally:
            lease.release()


def validate_package(objects, seal):
    if set(objects) != {'cob_preview.json', 'manifest.json'}:
        raise ValueError('Exactly the two canonical objects required')
    if seal.get('protocol') != 'pob-azure-offline-package-v1':
        raise ValueError('Unknown package protocol')
    if set(seal.get('objects', {})) != set(objects):
        raise ValueError('Unexpected sealed object')
    for name, body in objects.items():
        if seal.get('objects', {}).get(name) != sha(body):
            raise ValueError('Package bytes changed')
    manifest = json.loads(objects['manifest.json'])
    payload = json.loads(objects['cob_preview.json'])
    required = {'translation_id', 'version', 'compiler_revision', 'commit_sha', 'updated_at', 'books', 'chapters', 'verses', 'bible_url'}
    if set(manifest) != required or manifest['translation_id'] != 'cob_preview' or manifest['bible_url'] != 'cob_preview.json' or manifest['compiler_revision'] != 'enoch-notes-v2':
        raise ValueError('Unexpected canonical manifest format')
    books = payload.get('books', [])
    if not payload.get('translation') or not books:
        raise ValueError('Empty canonical payload')
    stats = {'books': len(books), 'chapters': sum(len(b['chapters']) for b in books), 'verses': sum(len(c['verses']) for b in books for c in b['chapters'])}
    if any(manifest[k] != value for k, value in stats.items()):
        raise ValueError('Canonical statistics mismatch')
    if manifest['version'] != seal.get('source_sha', '')[:12] + '-enoch-notes-v2':
        raise ValueError('Compiler/source version mismatch')
    if not re.fullmatch('[a-f0-9]{40}', seal.get('source_sha', '')) or manifest['commit_sha'] != seal['source_sha']:
        raise ValueError('Stale/source mismatch')
    if seal.get('parity_passed') is not True or not re.fullmatch('[a-f0-9]{64}', seal.get('baseline_inventory_sha256', '')):
        raise ValueError('Missing offline parity proof')
    if not re.fullmatch('[a-f0-9]{64}', seal.get('compiler_sha256', '')):
        raise ValueError('Missing exact compiler binding')
    return manifest


def stage(store, objects, seal, expected_control, predecessor_etag, *, reviewed_seal_sha256):
    """Transaction protocol tested on an in-memory store, not deployed.

    Immutable payloads first, immutable manifest next, conditional current pointer
    last. Failure leaves only unreferenced immutable objects; never rolls back a
    newer release. No existing object deletion and zero-write verified replay.
    """
    if sha(encoded(seal)) != reviewed_seal_sha256:
        raise ValueError('Package differs from exact reviewed seal')
    manifest = validate_package(objects, seal)
    if expected_control.get('protocol') != 'pob-azure-owner-v1' or expected_control.get('prefix') != PREFIX:
        raise ValueError('Missing exact ownership protocol')
    for key in ('baseline_inventory_sha256', 'compiler_sha256'):
        if expected_control.get(key) != seal.get(key):
            raise ValueError('Ownership/package mismatch')
    if expected_control.get('website_exclusion_verified') is not True or not expected_control.get('identity_object_id'):
        raise ValueError('Unverified owner identity/exclusion')
    control_bytes = encoded(expected_control)
    release = sha(encoded(seal))
    base = PREFIX + 'releases/' + release + '/'
    pointer = encoded({'protocol': 'pob-azure-current-v1', 'source_sha': manifest['commit_sha'],
                       'release': release, 'manifest_key': base+'manifest.json',
                       'manifest_sha256': sha(objects['manifest.json']), 'payload_sha256': sha(objects['cob_preview.json']), 'control_sha256': sha(control_bytes)})
    with store.lock() as renew:
        def owner():
            renew()
            if store.get('preview-receipts', CONTROL)[0] != control_bytes:
                raise ValueError('Missing/changed ownership control')
        owner()
        current, etag = store.get('$web', CURRENT)
        replay = current == pointer
        if not replay and etag != predecessor_etag:
            raise ValueError('Stale predecessor; no payload writes')
        writes = 0
        for name in ('cob_preview.json', 'manifest.json'):
            owner()
            key = base + name
            existing, _ = store.get('$web', key)
            if existing is None:
                if replay:
                    raise ValueError('Broken replay dependency')
                store.put(key, objects[name], create=True)
                writes += 1
            elif existing != objects[name]:
                raise ValueError('Immutable object collision')
            if store.get('$web', key)[0] != objects[name]:
                raise ValueError('Exact readback failed')
        owner()
        if not replay:
            store.put(CURRENT, pointer, etag=etag, create=etag is None)
            writes += 1
        if store.get('$web', CURRENT)[0] != pointer:
            raise ValueError('Current readback failed')
        owner()
    return {'writes': writes, 'release': release, 'replay': replay}
