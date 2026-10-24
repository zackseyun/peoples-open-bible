"""Compose one exact language pair with a separate confidence-only qualifier.

The language reviewers' actual historical scan maps remain the primary
evidence. Metadata reviewers need no new photographs or language passes.
No generic source/wording approval or confidence normalization is exposed.
"""
import copy
import json
from tools.enoch import bounded_application as t

REF='1 Enoch 27:4'
OLD='9ff5d5b783e7f774333d1103b033a03a3ad74614c2995db2f3a1cfc3cdf51563'
NEW='eead1fa16b454c4ec2d486eb3a8cacc794d99b09866a715dac02eb8364f2045b'
LANGUAGE_REVIEWS={'24e170d3db7b5408a4f226bb353ddebfcd31f0737e123662088e35a0b8467a6c',
                  '63cc7abee2c891970a51db1c7957afc09dd5301312c0a312cd6a01c367a3d0a6'}
METADATA_REVIEWS={'b169b0d3c90945969e3048bf32df6a18039464a71c40f2afc149840e9b49ae2d',
                  'c12cf470c14e959bde5fe2d44cc84f3bdef60a88b7b85a5a3b6e017c2135af72'}


def validate(package,manifest):
    name=manifest.get('confidence_metadata_evidence')
    if name not in manifest['files']:
        raise ValueError('Confidence27 composite evidence is not pinned')
    data=json.loads(t.artifact(package,name).read_text())
    if (data.get('kind')!='enoch27-exact-language-pair-confidence-only-delta-v1'
            or manifest['references']!=[REF] or data.get('reference')!=REF
            or data.get('primary_pdf_sha256')!=t.PRIMARY_SHA
            or data.get('old_confidence')!=0.91 or data.get('new_confidence')!='medium'
            or data.get('extra_English_language_passes')!=0
            or data.get('extra_provider_calls')!=0 or data.get('extra_photo_views')!=0
            or data.get('language_bindings')!=manifest['review_bindings'][REF]):
        raise ValueError('Confidence27 exact composite scope differs')
    def read(path):
        if path not in manifest['files']:raise ValueError('Unpinned Confidence27 input')
        return json.loads(t.artifact(package,path).read_text())
    oldpath,newpath=data['old_input'],data['new_input']
    if (t.sha(t.artifact(package,oldpath).read_bytes())!=OLD
            or t.sha(t.artifact(package,newpath).read_bytes())!=NEW):
        raise ValueError('Confidence27 exact old/new input differs')
    old,new=read(oldpath),read(newpath)
    if len(old)!=1 or len(new)!=1 or old[0]['reference']!=REF or old[0]['source']['confidence']!=0.91:
        raise ValueError('Confidence27 original one-unit scope differs')
    expected=copy.deepcopy(old);expected[0]['source']['confidence']='medium'
    if new!=expected:
        raise ValueError('Confidence27 attempted change beyond sole confidence qualifier')
    language=data['language_bindings']
    rows=t.reviewed_rows(package,language,REF,manifest['files'])
    if any(r!=old[0]for r in rows) or {manifest['files'][b['review']]for b in language}!=LANGUAGE_REVIEWS:
        raise ValueError('Confidence27 original complete language pair differs')
    actors={b['reviewer_id']for b in language}
    metadata=data['metadata_bindings']
    if len(metadata)!=2 or {b['reviewer_id']for b in metadata}!=actors:
        raise ValueError('Confidence27 exact two-actor metadata pair differs')
    if {manifest['files'].get(b['review'])for b in metadata}!=METADATA_REVIEWS:
        raise ValueError('Confidence27 immutable metadata decisions differ')
    for binding in metadata:
        if binding['input']!=newpath:raise ValueError('Confidence27 metadata input differs')
        result=read(binding['review']);pv=read(binding['provenance'])
        if (pv.get('input_sha256')!=NEW or result.get('input_sha256')!=NEW
                or pv.get('review_sha256')!=manifest['files'][binding['review']]
                or pv.get('source_pdf_sha256')!=t.PRIMARY_SHA
                or pv.get('reviewer_id')!=binding['reviewer_id']
                or result.get('reviewer_id')!=binding['reviewer_id']
                or pv.get('role')!=binding['role'] or result.get('role')!=binding['role']
                or [(r['reference'],r['verdict'])for r in t.review_entries(result)]!=[(REF,'accept')]):
            raise ValueError('Confidence27 exact metadata acceptance/provenance differs')
        keys=('extra_english_passes','provider_calls','new_photo_views')if binding['role']=='author' else ('extra_english_passes','extra_provider_calls','extra_photo_reviews')
        if any(type(result.get(k))is not int or result[k]!=0 for k in keys):
            raise ValueError('Confidence27 metadata invents new language/provider/photo work')
    return new[0]['source']


def accepted_confidence(package,manifest,reference,original):
    if not manifest.get('confidence_metadata_evidence'):return original
    if reference!=REF or original!=0.91:raise ValueError('Confidence27 qualifier applied outside exact unit/value')
    return validate(package,manifest)['confidence']


def qualified_source(package,manifest,reference,source):
    if not manifest.get('confidence_metadata_evidence'):return source
    if reference!=REF:raise ValueError('Confidence27 source projection outside exact unit')
    result=copy.deepcopy(validate(package,manifest))
    original=copy.deepcopy(result);original['confidence']=0.91
    if source!=original:raise ValueError('Confidence27 source projection differs from exact language core')
    return result
