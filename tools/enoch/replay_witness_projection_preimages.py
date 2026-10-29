"""Read-only exact old13/14 byte replay plus the fixed current metadata proof.

The original verify_applied functions remain strict: they must reject the
modified current records. No historical approval is rewritten or generalized.
"""
import importlib,json,tempfile
from pathlib import Path
from unittest.mock import patch
from tools.enoch import bounded_application as t,witness_projection_metadata as projection


def verify(chapter):
    if type(chapter)is not int or chapter not in(13,14):raise ValueError('Only the two fixed original transactions may be replayed')
    release=importlib.import_module(f'tools.textual_restoration.enoch_{chapter}_transaction')
    expected_package=t.APPLICATIONS/('enoch_13_20261007'if chapter==13 else'enoch_14_20261008')
    if release.PACKAGE.resolve()!=expected_package.resolve():raise ValueError('Legacy replay package differs')
    d=projection.read_manifest();current_projection=projection.verify_current(t.APPLICATIONS/projection.NAME)
    manifest=json.loads((release.PACKAGE/'manifest.json').read_text());receipt=json.loads((release.PACKAGE/'application.json').read_text())
    if receipt['manifest_sha256']!=t.sha((release.PACKAGE/'manifest.json').read_bytes()):raise ValueError('Original legacy manifest/receipt differs')
    try:release.verify_applied()
    except ValueError:pass
    else:raise ValueError('Original strict legacy verifier unexpectedly accepted metadata-modified current bytes')
    originals={}
    for c,v in release.REFS:
        name=f'{c:03d}-{v:03d}';ref=f'1 Enoch {c}:{v}';raw=(release.PACKAGE/(name+'.candidate.yaml')).read_bytes();digest=t.sha(raw)
        if manifest['files'][name+'.candidate.yaml']!=digest or receipt['candidate_sha256'][name]!=digest:raise ValueError('Exact historical legacy candidate differs')
        target=t.TRANSLATION/f'{c:03d}/{v:03d}.yaml'
        if ref in d['cases']:
            case=d['cases'][ref]
            if case['original_sha256']!=digest:raise ValueError('Current fixed metadata projection does not bind old legacy preimage')
            if t.sha(target.read_bytes())!=case['candidate_sha256']:
                name='enoch_full_repair_batch33_20261027';p=t.APPLICATIONS/name
                if ref!='1 Enoch 13:6' or t.sha((p/'manifest.json').read_bytes())!='113b61f03934b82eca38023d0d4eb62bb3a78b0c454013d3f12bb4210d6296cc' or {'reference':ref,'superseded_by':name}not in current_projection['reviewed_supersessions']:raise ValueError('No exact fresh13:6 language successor for legacy projection')
                t.verify(p,applied=True,check_corpus=True)
        elif target.read_bytes()!=raw:raise ValueError('Unrelated legacy target changed without a declared successor')
        originals[(c,v)]=raw
    with tempfile.TemporaryDirectory(prefix='enoch-exact-legacy-projection-')as directory:
        root=Path(directory)
        for(c,v),raw in originals.items():
            target=root/f'{c:03d}/{v:03d}.yaml';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        with patch.object(release,'TRANSLATION',root):historical=release.verify_applied()
    return {'legacy_refs':historical['refs'],'original_strict_current_rejection_verified':True,
            'historical_candidate_and_receipt_bytes_verified':True,'current_exact_projection_or_fixed_language_successor_verified':True,
            'new_full_source_or_English_reviews':0,'canonical_changed':False,'full_book_verified':False}
