"""Offline fake-store tests; no Azure/AWS SDK, identity or networking."""
import copy
from contextlib import contextmanager
import importlib.util
from pathlib import Path
import types
import unittest

spec = importlib.util.spec_from_file_location('pob_azure_stage', Path(__file__).resolve().parents[1] / 'tools/pob_publisher/azure_stage.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class Store:
    def __init__(self, control):
        self.data = {('preview-receipts', a.CONTROL): a.encoded(control)}
        self.tags = {('preview-receipts', a.CONTROL): 'owner'}
        self.writes = []
        self.fail_at = None
        self.locked = False
        self.corrupt = False
        self.change_owner = False
    @contextmanager
    def lock(self):
        if self.locked:
            raise ValueError('Busy')
        self.locked = True
        def renew():
            if not self.locked:
                raise ValueError('Lost lease')
        try:
            yield renew
        finally:
            self.locked = False
    def get(self, container, key):
        k = (container, key)
        data = self.data.get(k)
        if self.corrupt and '/releases/' in key and data is not None:
            return b'corrupt', self.tags.get(k)
        return data, self.tags.get(k)
    def put(self, key, data, *, etag=None, create=False):
        if self.fail_at == len(self.writes):
            raise ValueError('Injected failed write')
        k = ('$web', key)
        if create:
            if k in self.data:
                raise ValueError('Create conflict')
        elif self.tags.get(k) != etag:
            raise ValueError('CAS conflict')
        self.data[k] = data
        self.tags[k] = str(len(self.writes) + 1)
        self.writes.append(key)
        if self.change_owner:
            self.data[('preview-receipts', a.CONTROL)] = b'changed owner'

class StageTests(unittest.TestCase):
    def setUp(self):
        self.objects = {'cob_preview.json': a.encoded({'translation':'COB: Cartha Open Bible (Preview)','books':[{'name':'1 Enoch','chapters':[{'chapter':95,'verses':[{'verse':1,'text':'Offline fixture only'}]}]}]}), 'manifest.json': a.encoded({'translation_id':'cob_preview','version':'a'*12+'-enoch-notes-v2','compiler_revision':'enoch-notes-v2','commit_sha':'a'*40,'updated_at':'2026-10-31T00:00:00.000Z','books':1,'chapters':1,'verses':1,'bible_url':'cob_preview.json'})}
        self.seal = {'protocol':'pob-azure-offline-package-v1','source_sha':'a'*40,'baseline_inventory_sha256':'b'*64,'compiler_sha256':'c'*64,'parity_passed':True,'objects':{k:a.sha(v) for k,v in self.objects.items()}}
        self.owner = {'protocol':'pob-azure-owner-v1','prefix':a.PREFIX,'baseline_inventory_sha256':'b'*64,'compiler_sha256':'c'*64,'website_exclusion_verified':True,'identity_object_id':'OFFLINE-FAKE-NOT-AZURE-IDENTITY'}
        self.store = Store(self.owner)
    def stage(self, predecessor=None, reviewed=None):
        return a.stage(self.store,self.objects,self.seal,self.owner,predecessor,reviewed_seal_sha256=reviewed or a.sha(a.encoded(self.seal)))
    def test_inactive_factory_never_instantiates_credentials(self):
        with self.assertRaisesRegex(RuntimeError,'Inactive'):
            a.live_store()
    def test_assets_manifest_pointer_order_and_zero_write_replay(self):
        first = self.stage()
        self.assertEqual(first['writes'],3)
        self.assertTrue(self.store.writes[0].endswith('/cob_preview.json'))
        self.assertTrue(self.store.writes[1].endswith('/manifest.json'))
        self.assertEqual(self.store.writes[-1], a.CURRENT)
        self.assertEqual(self.stage()['writes'],0)
        self.assertEqual(len(self.store.writes),3)
    def test_wrong_reviewed_seal_no_operations(self):
        with self.assertRaisesRegex(ValueError,'reviewed seal'):
            self.stage(reviewed='e'*64)
        self.assertFalse(self.store.writes)
    def test_missing_owner_no_writes(self):
        self.store.data.clear()
        with self.assertRaisesRegex(ValueError,'ownership'):
            self.stage()
        self.assertFalse(self.store.writes)
    def test_stale_predecessor_no_payload_writes(self):
        self.store.data[('$web',a.CURRENT)] = b'previous'
        self.store.tags[('$web',a.CURRENT)] = 'newer'
        with self.assertRaisesRegex(ValueError,'Stale predecessor'):
            self.stage('older')
        self.assertFalse(self.store.writes)
    def test_failure_does_not_promote_and_retry_completes(self):
        self.store.fail_at = 1
        with self.assertRaisesRegex(ValueError,'Injected'):
            self.stage()
        self.assertNotIn(('$web',a.CURRENT),self.store.data)
        self.store.fail_at = None
        self.assertEqual(self.stage()['writes'],2)
    def test_changed_owner_before_release_aborts(self):
        self.store.change_owner = True
        with self.assertRaisesRegex(ValueError,'ownership'):
            self.stage()
        self.assertNotIn(('$web',a.CURRENT),self.store.data)
    def test_readback_failure_does_not_promote(self):
        self.store.corrupt = True
        with self.assertRaisesRegex(ValueError,'readback'):
            self.stage()
        self.assertNotIn(('$web',a.CURRENT),self.store.data)
    def test_immutable_collision_is_not_overwritten(self):
        self.stage()
        key = ('$web',self.store.writes[0])
        self.store.data[key] = b'collision'
        with self.assertRaisesRegex(ValueError,'collision'):
            self.stage()
        self.assertEqual(len(self.store.writes),3)
    def test_replay_missing_dependency_is_failure_not_repair(self):
        self.stage()
        del self.store.data[('$web',self.store.writes[0])]
        with self.assertRaisesRegex(ValueError,'Broken replay'):
            self.stage()
        self.assertEqual(len(self.store.writes),3)
    def test_tampered_payload(self):
        self.objects['cob_preview.json'] = b'changed'
        with self.assertRaisesRegex(ValueError,'bytes changed'):
            self.stage()
    def test_source_sha_mismatch(self):
        self.seal['source_sha'] = 'd'*40
        with self.assertRaisesRegex(ValueError,'source.*mismatch'):
            self.stage()
    def test_no_parity_proof(self):
        self.seal['parity_passed'] = False
        with self.assertRaisesRegex(ValueError,'parity'):
            self.stage()
    def test_empty_payload_and_bad_manifest_stats(self):
        for payload, patch in [({'translation':'test','books':[]}, {}), (None, {'verses':999})]:
            objects = copy.deepcopy(self.objects)
            if payload is not None:
                objects['cob_preview.json'] = a.encoded(payload)
            manifest = __import__('json').loads(objects['manifest.json'])
            manifest.update(patch)
            objects['manifest.json'] = a.encoded(manifest)
            seal = copy.deepcopy(self.seal)
            seal['objects'] = {k:a.sha(v) for k,v in objects.items()}
            with self.assertRaises(ValueError):
                a.validate_package(objects, seal)
    def test_unverified_exclusion_or_identity(self):
        for field in ['website_exclusion_verified','identity_object_id']:
            saved = self.owner[field]
            self.owner[field] = False
            with self.assertRaisesRegex(ValueError,'identity/exclusion'):
                self.stage()
            self.owner[field] = saved
    def test_owner_compiler_drift(self):
        self.owner['compiler_sha256'] = 'f'*64
        with self.assertRaisesRegex(ValueError,'Ownership/package'):
            self.stage()
    def test_extra_object_refused(self):
        self.objects['bibles/pob_preview.json'] = b'not this namespace'
        with self.assertRaisesRegex(ValueError,'two canonical'):
            self.stage()
    def test_lock_busy(self):
        self.store.locked = True
        with self.assertRaisesRegex(ValueError,'Busy'):
            self.stage()
        self.assertFalse(self.store.writes)

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.calls=[]
        self.blob=types.SimpleNamespace(upload_blob=lambda *args,**kw:self.calls.append((args,kw)))
        self.service=types.SimpleNamespace(url=f'https://{a.ACCOUNT}.blob.core.windows.net/',get_blob_client=lambda c,k:self.blob)
        self.store=a.AzureBlobStore(self.service,lambda **kw:kw,types.SimpleNamespace(IfNotModified='IfNotModified'))
    def test_sdk_create_only_and_ifmatch(self):
        self.store.put(a.PREFIX+'releases/'+'f'*64+'/manifest.json',b'{}',create=True)
        self.assertFalse(self.calls[0][1]['overwrite'])
        self.store.put(a.CURRENT,b'{}',etag='expected')
        self.assertEqual(self.calls[1][1]['etag'],'expected')
        self.assertEqual(self.calls[1][1]['match_condition'],'IfNotModified')
        self.assertEqual(self.calls[1][1]['content_settings']['cache_control'],'no-store')
    def test_account_and_namespace_denials(self):
        self.service.url='https://other.blob.core.windows.net'
        with self.assertRaises(ValueError): a.AzureBlobStore(self.service,None,None)
        for c,k in [('$web','bibles/pob_preview.json'),('$web',a.PREFIX+'../escape'),('other',a.CURRENT),('preview-receipts','new-control')]:
            with self.assertRaises(ValueError):self.store.blob(c,k)
    def test_no_unconditional_or_arbitrary_key_upload(self):
        for kwargs in [{},{'etag':'x','create':True}]:
            with self.assertRaises(ValueError):self.store.put(a.CURRENT,b'{}',**kwargs)
        with self.assertRaises(ValueError): self.store.put(a.PREFIX+'other.json',b'{}',create=True)
        self.assertFalse(self.calls)

if __name__ == '__main__':
    unittest.main()
