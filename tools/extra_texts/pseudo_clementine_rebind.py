"""Retain unchanged genuine Azure draft rows after another row's source curation.

This never reuses an approval or alters English. New independent review is
mandatory. The complete original request/response/record remain provenance.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime,timezone
from tools.extra_texts import pseudo_clementine_pages as p,pseudo_clementine_translation as tr
from tools.extra_texts.pseudo_clementine_selected import load_selected


def derive(parent_path: Path, references: list[str], destination: Path) -> dict:
    parent_path=parent_path.resolve();destination=destination.resolve()
    parent_path.relative_to(p.ROOT);destination.relative_to(p.ROOT)
    parent=json.loads(parent_path.read_text())
    if parent.get('stage')!='draft' or parent.get('backend')!='azure':raise ValueError('Only genuine Azure generation can be rebound here')
    files=parent['evidence_files'];request_path=(p.ROOT/files['request']).resolve();response_path=(p.ROOT/files['response']).resolve()
    request_path.relative_to(p.ROOT);response_path.relative_to(p.ROOT)
    request=json.loads(request_path.read_text());response=json.loads(response_path.read_text())
    old_rows=request['context']['passages'];actual=tr.validate_response(request,response,parent.get('audit_citation_corrections'),verified_source_rows=old_rows)
    if any(parent[k]!=actual[k] for k in ['output_hash','response_hash','model','request_hash','source_hash','references','output']):raise ValueError('Original generation evidence changed')
    if not references or [ref for ref in parent['references'] if ref in references]!=references:raise ValueError('Invalid source subset')
    current=load_selected(parent['work'])['passages'];selected=[row for row in current if row['reference'] in references]
    if selected!=[row for row in old_rows if row['reference'] in references]:raise ValueError('Cannot rebind changed Greek; fresh translation required')
    output={'passages':[row for row in parent['output']['passages'] if row['reference'] in references]}
    record={'version':2,'kind':'unchanged_greek_draft_subset','work':parent['work'],'stage':'draft','backend':'azure','model':parent['model'],'source_variant':'lagarde1865','references':references,'source_hash':tr.digest(selected),'output':output,'output_hash':tr.digest(output),'request_hash':parent['request_hash'],'recorded_at':datetime.now(timezone.utc).isoformat(),'publication_status':'candidate_only_not_reviewed','generation_provenance':{'method':'Exact unchanged-source and unchanged-English rows from actual prior Azure generation; no review reused','parent_record_sha256':p.sha(parent_path.read_bytes()),'original_source_hash':parent['source_hash'],'original_output_hash':parent['output_hash'],'original_response_hash':parent['response_hash']},'evidence_files':{'parent_draft_record':str(parent_path.relative_to(p.ROOT)),'request':files['request'],'response':files['response']}}
    if destination.exists():
        prior=json.loads(destination.read_text())
        if any(prior.get(k)!=v for k,v in record.items() if k!='recorded_at'):raise ValueError('Refusing to overwrite different derivation')
        return prior
    p.save(destination,record);return record
