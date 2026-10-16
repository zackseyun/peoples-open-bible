#!/usr/bin/env python3
"""Fail-closed, two-unit 1 Enoch 29 printed-edition application.

verify is read-only. apply changes only 029/001.yaml and 029/002.yaml after
scan, independent-review, baseline and export checks. No upload or publication.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from unittest.mock import patch
import yaml

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools import export_mobile_bible as exporter
from tools.enoch import verse_parser
P=ROOT/'sources/textual_restoration/applications/enoch_29_20261016'
BASE=ROOT/'translation/extra_canonical/1_enoch/029'
REFS=(1,2)

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def source(verse:int)->Path:return BASE/f'{verse:03}.yaml'
def name(verse:int)->str:return f'029-{verse:03}'

def review_core(row:dict)->dict:
 return {'reference':row['reference'],'source_text':row['source']['text'],'translation':row['translation']}
def core_sha(row:dict)->str:
 return hashlib.sha256(json.dumps(review_core(row),sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def verify_evidence(*, applied:bool=False, require_local_scans:bool=False)->dict:
 manifest=json.loads((P/'manifest.json').read_text())
 if manifest['status']!='reviewed_candidates_ready_for_bounded_application' or manifest['source_scope']!='1 Enoch 29:1-2 only':raise ValueError('Source scope or private archive not ready')
 for filename,expected in manifest['files'].items():
  if sha(P/filename)!=expected:raise ValueError('Candidate or baseline drift: '+filename)
 for key,filename in [('private_scan_archive_sha256','private-scan-archive.json'),('final_source_review_sha256','final-source-review.json'),('source_cleanup_sha256','source-cleanup.json'),('review_sha256','review-final/review.json'),('review_provenance_sha256','review-final/provenance.json')]:
  if sha(P/filename)!=manifest[key]:raise ValueError('Evidence drift: '+filename)
 provenance=json.loads((P/'review-final/provenance.json').read_text())
 if provenance['authentication']!='ChatGPT login' or provenance['canonical_translation_changed'] is not False or provenance['human_specialist_certification'] is not False:raise ValueError('Unsupported reviewer provenance')
 for filename,expected in provenance['package_input_sha256'].items():
  if sha(P/'review-final'/filename)!=expected:raise ValueError('Reviewer input changed: '+filename)
 if provenance['review_sha256']!=manifest['review_sha256']:raise ValueError('Independent review changed')
 scan=provenance['scan_image_sha256']
 if scan!=manifest['scan_image_sha256'] or len(scan)!=3:raise ValueError('Primary scan binding differs')
 for path,digest in scan.items():
  image=Path(path)
  if image.is_file():
   if sha(image)!=digest:raise ValueError('Primary scan drift: '+path)
  elif require_local_scans:
   raise ValueError('Required primary scan unavailable: '+path)
 archive=json.loads((P/'private-scan-archive.json').read_text())
 if archive['profile']!='default' or archive['account']!='320447260467' or {x['sha256'] for x in archive['assets']}!=set(scan.values()) or len(archive['assets'])!=3:raise ValueError('Private source archive differs')
 if any(x['profile']!='default' or x['account']!='320447260467' or x['private'] is not True or x['readback_byte_verified'] is not True for x in archive['assets']):raise ValueError('Private source readback missing')
 final=json.loads((P/'final-source-review.json').read_text());review=json.loads((P/'review-final/review.json').read_text());inputs=json.loads((P/'review-final/review-input.json').read_text())
 if not final['chapter_complete'] or not review['chapter_complete'] or [x['reference'] for x in review['reviews']]!=['1 Enoch 29:1','1 Enoch 29:2'] or any(x['verdict']!='accept' for x in review['reviews']):raise ValueError('Whole-chapter independent acceptance absent')
 if final['review_sha256']!=manifest['review_sha256'] or final['human_specialist_certification'] is not False:raise ValueError('Review status differs')
 historical=json.loads((P/'prior-revise-review.json').read_text())
 if historical['review']['reviews'][1]['verdict']!='revise' or historical['review']['chapter_complete'] is not True:raise ValueError('Failed prior review not preserved')
 candidates={}
 for verse in REFS:
  tag=name(verse);current=source(verse);baseline=P/f'{tag}.baseline.yaml';candidate=P/f'{tag}.candidate.yaml'
  expected_current=candidate if applied else baseline
  if not current.exists() or current.read_bytes()!=expected_current.read_bytes():raise ValueError('Canonical source differs from transaction state: '+tag)
  row=yaml.safe_load(candidate.read_text());old=yaml.safe_load(baseline.read_text())
  primary,_=verse_parser.load_verse(29,verse)
  if primary is None or row['id']!=f'1EN.29.{verse}' or row['source']['text']!=primary.text:raise ValueError('Primary text differs: '+tag)
  if row['source_correction']['baseline_sha256']!=sha(baseline) or row['source_correction']['publication_approval'] is not True or row['source_correction']['human_specialist_certification'] is not False or row['source_correction']['manuscript_witness_certification'] is not False:raise ValueError('Source approval scope differs: '+tag)
  if final['reviews'][tag]!=review['reviews'][verse-1] or final['reviewed_content_sha256'][tag]!=core_sha(row) or core_sha(row)!=core_sha(inputs[verse-1]):raise ValueError('Reviewed content differs: '+tag)
  text=row['translation']['text'];notes=row['translation']['footnotes'];markers=re.findall(r'\[([a-z])\]',text)
  if len(set(markers))!=len(markers) or set(markers)!={n['marker'] for n in notes} or any(not n['text'] for n in notes):raise ValueError('Footnote anchors incomplete: '+tag)
  for field in ('status','source','translation','revision_pass','cross_check','ai_draft','lexical_decisions','theological_decisions','revisions','enoch_witnesses'):
   if field in old and not any(h.get('field')==field and h.get('value')==old[field] and h.get('certifies_this_candidate') is False for h in row['review_history']):raise ValueError('Stale metadata not archived: '+tag+':'+field)
  candidates[verse]=row
 if not candidates[2]['source']['text'].endswith('ይትማሰሉ፡ (ከርካዕ።)') or '†ኵነኔ፡ †ፈድፋደ፡' not in candidates[2]['source']['text']:raise ValueError('Cross-page ending or critical marks absent')
 return candidates

def verify_export()->dict:
 before=exporter.export_extra_canonical_book('ENO');assert before
 with tempfile.TemporaryDirectory(prefix='enoch29-') as tmp:
  temp=Path(tmp);shutil.copytree(BASE.parent,temp/'1_enoch')
  for verse in REFS:shutil.copy2(P/f'{name(verse)}.candidate.yaml',temp/'1_enoch/029'/f'{verse:03}.yaml')
  with patch.object(exporter,'EXTRA_CANONICAL_ROOT',temp):after=exporter.export_extra_canonical_book('ENO')
 a={r['chapter']:r['verses'] for r in before['chapters']};b={r['chapter']:r['verses'] for r in after['chapters']}
 changed=[chapter for chapter in a if a.get(chapter)!=b.get(chapter)]
 if changed!=[29] or [v['verse'] for v in a[29]]!=[1,2] or [v['verse'] for v in b[29]]!=[1,2]:raise ValueError('Export delta escapes chapter29')
 return {'changed_chapters':[29],'verses':[1,2],'baseline_export_chapters':len(a),'candidate_export_chapters':len(b)}

def verify_applied()->dict:
 verify_evidence(applied=True)
 manifest=json.loads((P/'manifest.json').read_text());receipt=json.loads((P/'application.json').read_text())
 if sha(P/'manifest.json')!=receipt['manifest_sha256'] or receipt['status']!='applied_verified' or receipt['refs']!=['29:1','29:2']:raise ValueError('Application receipt changed')
 for verse in REFS:
  if sha(source(verse))!=manifest['files'][f'{name(verse)}.candidate.yaml']:raise ValueError('Applied source drift')
 return receipt

def apply()->dict:
 verify_evidence(require_local_scans=True);delta=verify_export();old={source(v):source(v).read_bytes() for v in REFS}
 try:
  for verse in REFS:
   path=source(verse);temp=path.with_suffix('.yaml.enoch29-pending');temp.write_bytes((P/f'{name(verse)}.candidate.yaml').read_bytes());os.replace(temp,path)
  receipt={'status':'applied_verified','refs':['29:1','29:2'],'export_delta':delta,'manifest_sha256':sha(P/'manifest.json'),'candidate_sha256':{name(v):sha(source(v)) for v in REFS},'graphic_reader_published':False}
  (P/'application.json').write_text(json.dumps(receipt,indent=2)+'\n');verify_applied();return receipt
 except Exception:
  for path,data in old.items():path.write_bytes(data)
  (P/'application.json').unlink(missing_ok=True)
  raise

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('verify','apply','verify-applied'));args=parser.parse_args()
 result=verify_applied() if args.action=='verify-applied' else apply() if args.action=='apply' else {'evidence_refs':list(verify_evidence()),'export_delta':verify_export()}
 print(json.dumps(result,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
