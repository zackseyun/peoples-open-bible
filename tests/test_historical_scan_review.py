import copy
import io
import zipfile
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.historical_scan_review import (digest, encoded, endpoint_url, invoke, keyless_client,
                                        observe, request_payload, review_errors, validate_draft, write, dispatch_leaves, pace_writer, english_comparisons)


class ScanReviewTests(unittest.TestCase):
    def test_secondary_comparison_reparses_pinned_markup_without_publisher_glosses(self):
        raw, job, _, _ = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'jsp').mkdir()
            html = ('<script id="__NEXT_DATA__" type="application/json">'+json.dumps({'props':{'pageProps':{'summary':{
                'clearText':'<div class="wasptag">Ahashdah [Sidney Rigdon]</div>'}}}})+'</script>').encode()
            url='https://www.josephsmithpapers.org/paper-summary/doctrine-and-covenants-1835/1'
            path=root/'jsp/page-0001.html';path.write_bytes(html)
            write(path.with_name(path.name+'.receipt.json'),{'url':url,'sha256':digest(html),'bytes':len(html)})
            write(root/'jsp/page-0001.json',{'printed_text':'Ahashdah [Sidney Rigdon]','url':url,'webpage_sha256':digest(html)})
            write(root/'comparison-alignment.candidates.json',{'pages':[{'reference':job['reference'],
                'scan_sha256':digest(raw),'strong_location_lead':True,'candidates':[{'jsp_page':1,
                'comparison_text_sha256':digest(b'Ahashdah [Sidney Rigdon]')}]}]})
            comparison=english_comparisons(root,job)[-1]
            self.assertEqual(comparison['text'],'Ahashdah')
            self.assertEqual(comparison['excluded_editorial_bracket_items'],1)
            self.assertEqual(comparison['raw_markup_sha256'],digest(html))
            path.write_bytes(html+b'changed')
            with self.assertRaisesRegex(ValueError,'provenance'):english_comparisons(root,job)

    def test_archival_encoding_bound_to_pinned_zip_member_and_exact_pixels(self):
        from PIL import Image
        raw, job, draft, review = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); member = 'GR_711_jp2/GR_711_0004.jp2'
            native = Image.new('RGB', (12, 10), (20, 40, 70)); buf = io.BytesIO()
            native.save(buf, format='JPEG2000'); jp2 = buf.getvalue()
            archive = root / 'archive.zip'
            with zipfile.ZipFile(archive, 'w') as container: container.writestr(member, jp2)
            png = root / 'scan.png'; Image.open(io.BytesIO(jp2)).save(png)
            descriptor = {'path':str(png), 'archive_zip_path':str(archive), 'archive_item':'GR_711',
                'physical_leaf':4, 'parent_jpeg_sha256':digest(raw), 'archive_member':member,
                'archive_zip_sha256':digest(archive.read_bytes()), 'archive_jp2_sha256':digest(jp2),
                'sha256':digest(png.read_bytes())}
            job['alternate_facsimiles'] = [descriptor]
            with patch('tools.historical_scan_review.NEWBERRY_JP2_ARCHIVE_SHA256', descriptor['archive_zip_sha256']):
                content = request_payload(job,raw,'writer','draft')['input'][0]['content']
                self.assertEqual(sum(x['type']=='input_image' for x in content), 2)
                self.assertNotIn('FORBIDDEN OCR ANCHOR', json.dumps(content))
                descriptor['physical_leaf'] = 5
                with self.assertRaisesRegex(ValueError, 'provenance'): request_payload(job,raw,'writer','draft')
                descriptor['physical_leaf'] = 4
                Image.new('RGB',(12,10),'white').save(png);descriptor['sha256']=digest(png.read_bytes())
                with self.assertRaisesRegex(ValueError, 'pixels'): request_payload(job,raw,'writer','draft')
            with self.assertRaisesRegex(ValueError, 'provenance'): request_payload(job,raw,'writer','draft')

    def test_isolated_reviewer_quota_is_not_shared_reviewer_quota(self):
        raw, job, draft, _ = self.fixture()
        payload = request_payload(job, raw, 'reviewer', 'review', draft)
        with self.assertRaisesRegex(ValueError, 'token window'):
            pace_writer(payload, 'review', {'reviewer': {'quota_tpm': 1000}})
        with self.assertRaisesRegex(ValueError, 'quota'):
            pace_writer(payload, 'review', {'reviewer': {'quota_tpm': -1}})

    def test_stop_marker_drains_active_unit_and_prevents_new_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            stop = Path(directory) / 'STOP'
            def process(leaf):
                stop.touch()
                return leaf
            results = [(leaf, future.result()) for leaf, future in dispatch_leaves(process, range(10), 1, stop)]
            self.assertEqual(results, [(0, 0)])
            self.assertEqual(list(dispatch_leaves(process, range(10), 4, stop)), [])

    def test_isolated_arm_payload_preserves_other_filters(self):
        root = Path(__file__).resolve().parents[1] / 'infrastructure' / 'historical-review'
        policy = json.loads((root / 'pob-dc-1835-policy.json').read_text())['properties']
        self.assertEqual(policy['basePolicyName'], 'Microsoft.DefaultV2')
        self.assertEqual(policy['mode'], 'Blocking')
        filters = {(f['name'], f['source']): f for f in policy['contentFilters']}
        self.assertEqual(len(filters), 11)
        for name in ['Hate', 'Sexual', 'Violence', 'Selfharm']:
            for source in ['Prompt', 'Completion']:
                self.assertEqual(filters[name,source], {'name':name,'source':source,'blocking':True,
                    'enabled':True,'severityThreshold':'Medium'})
        self.assertTrue(filters['Jailbreak','Prompt']['blocking'])
        self.assertTrue(filters['Jailbreak','Prompt']['enabled'])
        # Preserve actual DefaultV2 code annotation behavior, not an invented default.
        for name in ['Protected Material Text','Protected Material Code']:
            self.assertTrue(filters[name,'Completion']['enabled'])
            self.assertFalse(filters[name,'Completion']['blocking'])
        models = []
        for role in ['writer','reviewer']:
            deployment = json.loads((root / f'pob-dc-1835-{role}.json').read_text())
            self.assertEqual(deployment['sku'], {'name':'GlobalStandard','capacity':100})
            self.assertEqual(deployment['properties']['raiPolicyName'], 'pob-dc-1835-public-domain-review')
            self.assertEqual(deployment['properties']['versionUpgradeOption'], 'NoAutoUpgrade')
            models.append(deployment['properties']['model']['name'])
        self.assertEqual(models, ['gpt-6.1-sol','gpt-5.6-terra'])

    def fixture(self):
        raw=b'scan'
        job={'work':'D&C 1835','reference':'newberry-leaf-0004','source':{'sha256':digest(raw),'edition':'1835'},
             'english_comparisons':[{'text':'FORBIDDEN OCR ANCHOR'}]}
        result={'reference':job['reference'],'full_page_examined':True,'page_kind':'printed_text',
                'lines':[{'line_id':'L001','region':'top','text':'Printed words','uncertainties':[]}],
                'non_printed_material':[],'uncertainties':[],'printed_page_number':None}
        draft={'actual_model':'model-a','deployment_model':{'name':'model-a','version':'1'},'result':result}
        review={'actual_model':'model-b','deployment_model':{'name':'model-b','version':'1'},
                'source_sha256':job['source']['sha256'],'draft_sha256':digest(encoded(draft)),
                'result':{'reference':job['reference'],'full_page_examined':True,
                    'lines':[{'line_id':'L001','verdict':'acceptable','corrected_text':'','reason':'Matches scan','unresolved_issues':[]}],
                    'missing_printed_lines':[],'uncertainties':[],'overall_verdict':'acceptable'}}
        return raw,job,draft,review

    def test_only_https_azure_hosts_before_credential_acquisition(self):
        self.assertEqual(endpoint_url('https://example.openai.azure.com/'),'https://example.openai.azure.com/openai/v1/')
        for value in ['http://example.openai.azure.com','https://example.com','https://user@example.openai.azure.com',
                      'https://example.openai.azure.com/evil','https://example.openai.azure.com?token=x',
                      'https://example.openai.azure.com:444']:
            with self.assertRaises(ValueError):endpoint_url(value)

    def test_explicit_keyless_approval_is_required(self):
        with self.assertRaisesRegex(ValueError,'Explicit approval'):keyless_client({},False)

    def test_keyless_uses_subscription_not_incompatible_tenant_pair(self):
        credential=Mock();provider=Mock();client=Mock()
        with patch.dict(sys.modules,{'azure.identity':SimpleNamespace(AzureCliCredential=credential,get_bearer_token_provider=provider),
                                      'openai':SimpleNamespace(OpenAI=client)}):
            keyless_client({'endpoint':'https://example.openai.azure.com','subscription':'verified-sub','tenant':'verified-tenant'},True)
        credential.assert_called_once_with(subscription='verified-sub',process_timeout=120)
        self.assertTrue(callable(client.call_args.kwargs['api_key']))
        self.assertIs(client.call_args.kwargs['api_key'](),provider.return_value.return_value)
        self.assertEqual(client.call_args.kwargs['max_retries'],0)

    def test_primary_cannot_receive_prior_english_or_ocr(self):
        raw,job,draft,review=self.fixture()
        payload=request_payload(job,raw,'writer','draft')
        text=json.dumps(payload)
        self.assertNotIn('FORBIDDEN OCR ANCHOR',text)
        self.assertNotIn('QUOTED DRAFT',text)
        self.assertFalse(payload['store'])
        self.assertEqual(payload['input'][0]['content'][1]['type'],'input_image')
        with self.assertRaises(ValueError):request_payload(job,b'changed','writer','draft')

    def test_review_has_actual_draft_not_english_comparisons(self):
        raw,job,draft,review=self.fixture()
        text=json.dumps(request_payload(job,raw,'reviewer','review',draft))
        self.assertIn('QUOTED DRAFT DATA',text)
        self.assertIn('Printed words',text)
        self.assertNotIn('FORBIDDEN OCR ANCHOR',text)

    def test_older_english_enters_only_after_independent_source_review(self):
        raw,job,draft,review=self.fixture()
        payload=request_payload(job,raw,'writer','adjudicate',draft,review,[{'text':'OLDER ENGLISH'}],True)
        self.assertIn('OLDER ENGLISH',json.dumps(payload))
        self.assertTrue(payload['store']);self.assertTrue(payload['background'])

    def test_original_pixel_crop_cannot_replace_full_page_or_change_parent(self):
        raw,job,draft,review=self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'crop.png';path.write_bytes(b'crop')
            job['focus_images']=[{'path':str(path),'parent_sha256':digest(raw),'sha256':digest(b'crop'),'bbox_xyxy':[1,2,3,4]}]
            content=request_payload(job,raw,'writer','draft')['input'][0]['content']
            self.assertEqual(sum(item['type']=='input_image' for item in content),2)
            job['focus_images'][0]['parent_sha256']='changed'
            with self.assertRaises(ValueError):request_payload(job,raw,'writer','draft')

    def test_poll_timeout_reobserves_same_handle_without_post(self):
        client=Mock();response=SimpleNamespace(id='resp-live',status='completed')
        client.responses.retrieve.side_effect=[TimeoutError('SECRET'),response]
        with tempfile.TemporaryDirectory() as directory,patch('tools.historical_scan_review.time.sleep'):
            path=Path(directory)/'journal.json';journal={'response_id':'resp-live'}
            self.assertIs(observe(client,'resp-live',journal,path),response)
            self.assertNotIn('SECRET',path.read_text())
        self.assertEqual([call.args for call in client.responses.retrieve.call_args_list],[('resp-live',),('resp-live',)])
        client.responses.create.assert_not_called()

    def test_separate_actual_reviewer_hash_binding_and_complete_coverage(self):
        raw,job,draft,review=self.fixture()
        self.assertEqual(review_errors(job,draft,review),[])
        for key,value in [('actual_model','model-a'),('deployment_model',draft['deployment_model']),
                          ('source_sha256','changed'),('draft_sha256','changed')]:
            changed=copy.deepcopy(review);changed[key]=value
            self.assertTrue(review_errors(job,draft,changed))
        changed=copy.deepcopy(review);changed['result']['lines']=[]
        self.assertTrue(review_errors(job,draft,changed))

    def test_omitted_lines_corrections_uncertainties_cannot_be_accepted(self):
        raw,job,draft,review=self.fixture()
        for field,value in [('missing_printed_lines',[draft['result']['lines'][0]]),
                            ('uncertainties',['unclear']),('full_page_examined',False)]:
            changed=copy.deepcopy(review);changed['result'][field]=value
            self.assertTrue(review_errors(job,draft,changed))
        changed=copy.deepcopy(review);changed['result']['lines'][0]['corrected_text']='A correction'
        self.assertTrue(review_errors(job,draft,changed))

    def test_source_draft_duplicate_lines_and_false_blank_claims_rejected(self):
        raw,job,draft,review=self.fixture()
        changed=copy.deepcopy(draft);changed['result']['lines']*=2
        with self.assertRaises(ValueError):validate_draft(job,changed)
        changed=copy.deepcopy(draft);changed['result']['lines']=[]
        with self.assertRaises(ValueError):validate_draft(job,changed)

    def test_http_failure_is_sanitized_and_never_retried(self):
        raw,job,draft,review=self.fixture()
        client=Mock();client.responses.create.side_effect=RuntimeError('SECRET WOULD BE HERE')
        profile={'writer':{'deployment':'writer','model':{'name':'model-a','version':'1'}}}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)
            with self.assertRaises(RuntimeError) as cm:invoke(client,profile,job,raw,'draft',path)
            self.assertNotIn('SECRET',str(cm.exception))
            self.assertEqual(json.loads((path/'draft.journal.json').read_text())['status'],'outcome_unknown')
            with self.assertRaises(ValueError):invoke(client,profile,job,raw,'draft',path)
            self.assertEqual(client.responses.create.call_count,1)

    def test_completed_cache_bound_to_exact_record_not_reexecuted(self):
        raw,job,draft,review=self.fixture()
        client=Mock();profile={'writer':{'deployment':'writer','model':{'name':'model-a','version':'1'}}}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory);payload=request_payload(job,raw,'writer','draft')
            write(path/'draft.record.json',draft)
            write(path/'draft.journal.json',{'request_sha256':digest(encoded(payload)),
                'record_sha256':digest(encoded(draft)),'status':'completed'})
            self.assertEqual(invoke(client,profile,job,raw,'draft',path),draft)
            client.responses.create.assert_not_called()
            write(path/'draft.record.json',{'changed':True})
            with self.assertRaises(ValueError):invoke(client,profile,job,raw,'draft',path)


if __name__=='__main__':unittest.main()
