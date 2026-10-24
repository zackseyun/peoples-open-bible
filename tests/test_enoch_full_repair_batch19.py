"""Seven source/English treatments with exact native terminal signs and two holds."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader

P=t.APPLICATIONS/'enoch_full_repair_batch19_20261023'
VERSES=(1,3,4,5,6,7,8)
REFS=[f'1 Enoch 1:{v}'for v in VERSES]
MANIFEST='79470171f9c28732db819b531d22fa18336b8e9eb1ed50a35cf0b06299918f92'
OLD='299374e97a409085e62bdfb4768fd8ed9931bd6378f05a4d98743e5940fb22c6'
NEW='4f27d631724d0a807a44b47da3cdf2a60d84da2a7c0d94b2939eca9ac2d7d163'


def record(v):return yaml.load((t.TRANSLATION/f'001/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)


class FullRepairBatch19Test(unittest.TestCase):
    def test_seven_existing_units_complete_postmap_and_exact_previous_state(self):
        self.assertEqual(t.sha((P/'manifest.json').read_bytes()),MANIFEST)
        proof=verify_current(P);m=t.load_manifest(P);r=json.loads((P/'application.json').read_text())
        self.assertEqual(proof['references'],REFS);self.assertEqual(proof['candidate_files'],7)
        self.assertEqual(r['snapshot_file_count'],962);self.assertTrue(r['unrelated_canonical_files_unchanged_at_application'])
        prior=json.loads((t.APPLICATIONS/'enoch_full_repair_batch18_20261023/application.json').read_text())
        self.assertEqual(m['canonical_baseline_sha256'],prior['canonical_after_sha256'])
        expected=dict(m['canonical_baseline_sha256'])
        for v in VERSES:
            rel=f'001/{v:03d}.yaml';expected[rel]=t.sha((P/f'001-{v:03d}.candidate.yaml').read_bytes())
            self.assertEqual(t.sha((t.TRANSLATION/rel).read_bytes()),expected[rel])
        self.assertEqual(r['canonical_after_sha256'],expected)
        self.assertEqual(m['retirements'],[]);self.assertEqual(m['supersedes'],{})
        self.assertEqual(m['chapter_inventories'],[]);self.assertEqual(m['source_only_count_inventories'],[])

    def test_original_full9_and_new7_are_distinct_immutable_inputs(self):
        original=P/'history/ch01-language-author/review-input.json';current=P/'final/ch01-endings/review-input.json'
        self.assertEqual(t.sha(original.read_bytes()),OLD);self.assertEqual(t.sha(current.read_bytes()),NEW)
        before={r['reference']:r for r in json.loads(original.read_text())};after=json.loads(current.read_text())
        self.assertEqual([r['reference']for r in after],REFS)
        for row in after:
            old=before[row['reference']];v=t.parse_ref(row['reference'])[1]
            self.assertEqual(row['translation']['text'],old['translation']['text'])
            self.assertEqual(row['source']['text'][:-1],old['source']['text'][:-1])
            if v!=7:self.assertEqual(row['translation'],old['translation'])
            else:self.assertNotEqual(row['translation']['footnotes'],old['translation']['footnotes'])
        for name in('history/ch01-language-author/author-review.json','history/ch01-language-exact-peer/independent-review.json'):
            reviews=json.loads((P/name).read_text())['reviews']
            self.assertEqual([r['reference']for r in reviews if r['verdict']=='accept'],REFS)
            self.assertEqual([r['reference']for r in reviews if r['verdict']=='hold'],['1 Enoch 1:2','1 Enoch 1:9'])

    def test_actual_colons_and_fullstops_not_systematic_normalization(self):
        for v in VERSES:self.assertEqual(record(v)['source']['text'][-1],'፡'if v in(1,3,7,8)else'።')
        author=json.loads((P/'final/ch01-endings/author-provenance.json').read_text())
        peer=json.loads((P/'final/ch01-endings/independent-provenance.json').read_text())
        self.assertEqual(author['changed_terminal_refs'],[f'1 Enoch 1:{v}'for v in(1,3,7,8)])
        self.assertEqual(author['unchanged_terminal_refs'],[f'1 Enoch 1:{v}'for v in(4,5,6)])
        self.assertTrue(author['all_English_text_unchanged']);self.assertEqual(author['English_note_changed_only'],'1 Enoch 1:7')
        self.assertEqual(peer['summary']['new_English_language_passes'],0)
        self.assertEqual(peer['summary']['new_provider_calls'],0)
        self.assertFalse(peer['summary']['whole_chapter_complete'])
        self.assertEqual(peer['own_precandidate_additive_source_freeze']['sha256'],'a70c2faf9ecb55e9ef56455b190a956c08da50acbc9c93137232301a7e9ac3e4')

    def test_sink_is_source_backed_not_inherited_rent_asunder_or_an_added_flood(self):
        d=record(7);self.assertTrue(d['source']['text'].startswith('ወትሰጥም'))
        self.assertIn('The earth will sink',d['translation']['text'])
        self.assertIn('everything in the earth will be destroyed',d['translation']['text'])
        self.assertIn('Judgment will come upon all',d['translation']['text'])
        for unsupported in('rent asunder','flood'):self.assertNotIn(unsupported,d['translation']['text'])
        note=d['translation']['footnotes'][0]['text'];self.assertIn('col400',note);self.assertIn('sinking/submergence',note)
        self.assertIn('earlier inherited source transcription',note)

    def test_camp_watchers_and_wax_have_reviewed_notes_not_familiar_completion(self):
        self.assertIn('his encampment',record(4)['translation']['text'])
        self.assertIn('the Watchers will tremble',record(5)['translation']['text'])
        self.assertIn('melt like wax',record(6)['translation']['text'])
        for v in(4,5,6):self.assertTrue(record(v)['translation']['footnotes'])
        for v in VERSES:self.assertFalse(record(v)['source'].get('additional_translation_input'))

    def test_printed_bracketed_dittography_remains_qualified_not_silently_deleted(self):
        d=record(8);self.assertEqual(d['source']['confidence'],'low')
        uncertainty=d['source']['transcription_uncertainties'];self.assertTrue(uncertainty)
        self.assertIn(uncertainty[0]['token'],d['source']['text'])
        self.assertIn('dittography',d['translation']['footnotes'][0]['text'])
        self.assertIn('meaning once',d['translation']['footnotes'][0]['text'])
        self.assertEqual(d['translation']['text'].count('He will make peace'),1)

    def test_two_original_whole_holds_are_not_approved_by_subset_or_count(self):
        m=t.load_manifest(P);self.assertEqual([r['reference']for r in m['not_applied']],['1 Enoch 1:2','1 Enoch 1:9'])
        for v in(2,9):
            rel=f'001/{v:03d}.yaml';self.assertEqual(t.sha((t.TRANSLATION/rel).read_bytes()),m['canonical_baseline_sha256'][rel])
            for b in m['review_bindings']['1 Enoch 1:1']:
                with self.assertRaisesRegex(ValueError,'not in review input|not accepted|missing|not found'):t.review_row(P,b,f'1 Enoch 1:{v}',m['files'])
        from tools.enoch.full_repair_progress import build
        report=build();self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertNotIn(1,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertFalse(report['completion_proven']);self.assertFalse(report['artwork_publication_approval'])

    def test_exact_reviewed_source_ingress_not_canonical_source_echo(self):
        from tools.enoch import selected_edition_sources as s
        registry=s.registry_data();self.assertNotIn('1',registry['chapters'])
        rows={r['verse']:r for r in s.load_unit_overrides(1)}
        for v in VERSES:
            self.assertEqual(registry['units'][f'1:{v}'],P.name)
            self.assertEqual(rows[v]['source']['text'],record(v)['source']['text'])
            self.assertIn('/final/',rows[v]['evidence'])
        for v in(2,9):self.assertNotIn(f'1:{v}',registry['units'])

    def test_exact_explanations_controls_and_source_terminals_survive_export(self):
        book=reader.export_extra_canonical_book('ENO');verses={v['verse']:v for c in book['chapters']if c['chapter']==1 for v in c['verses']}
        for v in VERSES:
            d=record(v);e=verses[v]
            self.assertEqual(e['footnotes'],d['translation']['footnotes']);self.assertEqual(e['footnote_review'],'pob-enoch-paired-source-review-v1')
            for key in('text','pages','note','confidence','additional_translation_input','transcription_uncertainties'):
                if key in d['source']:self.assertEqual(e['source_critical'][key],d['source'][key])
                else:self.assertNotIn(key,e['source_critical'])
            prompt=build_enoch_prompt(1,v)
            for key in('additional_translation_input','transcription_uncertainties'):
                if key in d['source']:self.assertEqual(prompt.source_payload[key],d['source'][key])
                else:self.assertFalse(prompt.source_payload.get(key))
        self.assertFalse(json.loads((P/'explanation-delivery-gate.json').read_text())['candidate_public_delivery_verified'])

    def test_azure_adverse_is_preserved_and_not_counted_as_English_acceptance(self):
        coverage=t.ROOT/'sources/enoch/coverage/azure61-sol-ch01-followup-20261023'
        raw=json.loads((coverage/'exact-1-7/raw-model-text.json').read_text())
        self.assertEqual(raw['verdict'],'hold');self.assertFalse(raw['publication_approved'])
        self.assertEqual(json.loads((coverage/'index.json').read_text())['canonical_votes_imported'],0)
        peer=json.loads((P/'final/ch01-endings/independent-provenance.json').read_text())
        self.assertTrue(any('frozen before reading Azure adverse'in e for e in peer['exposure']))
        self.assertEqual(peer['reviewer_id'],'/root/enoch05_exact_peer')
        for v in VERSES:
            d=record(v);self.assertEqual(d['ai_draft']['model_id'],'not_reported')
            for key in('selected_edition_chapter_reviewed','chapter_publication_approval','full_book_verified','human_specialist_certification','manuscript_witness_certification','graphic_publication_approved'):self.assertFalse(d['source_correction'][key])

    def test_only_chapter1_export_contribution_and_no_new_addresses(self):
        m=t.load_manifest(P)
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);shutil.copytree(t.TRANSLATION,root/'1_enoch')
            for v in VERSES:
                rel=f'001/{v:03d}.yaml';blob=m['baseline_git_blobs'][rel]['blob']
                (root/'1_enoch'/rel).write_bytes(subprocess.check_output(['git','cat-file','blob',blob],cwd=t.ROOT))
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):before=reader.export_extra_canonical_book('ENO')
        after=reader.export_extra_canonical_book('ENO');a={c['chapter']:c for c in before['chapters']};b={c['chapter']:c for c in after['chapters']}
        self.assertEqual(set(a),set(b));self.assertEqual({c for c in a if a[c]!=b[c]},{1})
        for c in a:self.assertEqual([v['verse']for v in a[c]['verses']],[v['verse']for v in b[c]['verses']])

    def test_drifted_review_input_rejected_and_workflow_fetches_actual_baseline(self):
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/P.name;shutil.copytree(P,p);f=p/'final/ch01-endings/review-input.json';f.write_bytes(f.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'artifact changed'):t.load_manifest(p)
        workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn('git fetch --no-tags --depth=1 origin 0a4e4b759254c4023b1bff312947b936b45d8555',workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_enoch_full_repair_batch19.py'",workflow)
