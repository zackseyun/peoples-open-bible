#!/usr/bin/env python3
"""Apply/check the maintainer-authorized, individually bounded English wording plan.

No runtime thesaurus substitution and no source-text rewriting. The committed
plan locks every input file and exact proposed reader text. Historical provenance
is preserved; earlier model approval is not carried forward onto this revision.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import pathlib
import re
import subprocess
from datetime import datetime, timezone
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLAN = ROOT / 'config/terminology/reorientation-english-2026-10-11.json'
POLICY = 'reorientation-english-2026-10-11'
TERM = re.compile(r'\b(?:un)?repent\w*\b', re.I)
COGNITIVE = re.compile(r'change (?:your|their) thinking|change (?:your|their) minds?|change of mind',re.I)
ARCHIVE_FIELDS = ('status','revision_pass','cross_check','source_audit','lexical_decisions',
                  'theological_decisions','simplification_decisions','interpretive_expansions',
                  'translation_notes','retained_terms')


def digest(value):
    if not isinstance(value, bytes):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True).encode()
    return hashlib.sha256(value).hexdigest()


def load(path):
    return yaml.load(path.read_text(encoding='utf-8'), Loader=yaml.CSafeLoader)


def norm(s):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c))


def relevant(decision):
    s = json.dumps(decision, ensure_ascii=False)
    return bool(TERM.search(s) or COGNITIVE.search(s) or re.search('μετανο|μετενο',norm(s)))


def wording_note(item, doc):
    kind=item['mode']
    if kind in {'godward','addressed'}:
        note=('Traditionally "repent" or "repentance." Reorientation means a change of disposition and direction, not merely feeling sorry. The direction toward God is explicit in Acts 20:21 and is made explicit from the context here; it is not a separate meaning-component of the Greek word. No added degree of completeness is intended.')
        if item['id']=='ACT.20.21':
            note=('Traditionally "repentance toward God." The Greek explicitly supplies the direction toward God here. "Reorientation" denotes changed disposition and direction, not merely regret, and does not add a claim about completeness.')
    elif kind=='neutral':
        note=('Traditionally "repent" or "repentance." "Reorient" and "reorientation" describe a change of disposition and direction. The surrounding passage supplies the direction; this wording does not erase named wrongdoing, distinct turning expressions, or sorrow, and does not by itself assert a completed moral transformation.')
    else:
        note='Earlier reader wording used a form of "repent." '+item['rationale']
    source=doc.get('source') or {}
    if source.get('text_scope')=='public_domain_english_witness' or source.get('language')=='English':
        note+=' This reader text adapts the recorded English translation witness; it is not a verbatim quotation or a newly verified translation of the ancient-language text. The source witness is unchanged.'
    return note


def new_lexical(decision, item, text):
    # This is a current audit entry, not an assertion that an earlier lexicon
    # consultation recommended our newly approved English phrase.
    d=copy.deepcopy(decision)
    before=str(d.get('chosen',''))
    kind=item['mode']
    target=' toward God' if kind=='godward' else ' toward you' if kind=='addressed' else ''
    def preserve_case(old,new):
        return new[0].upper()+new[1:] if old[:1].isupper() else new
    forms={'repentance':'reorientation'+target,'repent':'reorient'+target,
           'repents':'reorients'+target,'repented':'reoriented'+target,
           'repenting':'reorienting'+target,'repentant':'reoriented'+target,
           'unrepentant':'unwilling to reorient'+target,'unrepented':'unregretted',
           'repenteth':'reorients'+target,'repentest':'reorient'+target}
    if kind=='regret':forms.update(repentance='regret',repent='feel regret',repents='feels regret',repented='felt regret',repenting='feeling regret')
    if kind in {'change_of_mind','reconsider'}:forms.update(repentance='a change of mind',repent='reconsider',repents='reconsiders',repented='reconsidered',repenting='reconsidering')
    if kind=='turning':forms.update(repentance='turning back',repent='turn back',repents='turns back',repented='turned back')
    if kind=='sorrow':forms['repentance']='sorrow'
    chosen=TERM.sub(lambda m:preserve_case(m.group(),forms.get(m.group().lower(),'reorientation')),before)
    if kind in {'godward','addressed','neutral'}:
        for pattern,replacement in [(r'change (?:your|their) thinking','reorient'+target),(r'change (?:your|their) minds?','reorient'+target),(r'change of mind','reorientation'+target),(r'that change','reorientation')]:
            chosen=re.sub(pattern,lambda m:preserve_case(m.group(),replacement),chosen,flags=re.I)
        chosen=chosen.replace('toward God toward God','toward God')
        chosen=re.sub(r'(reorient(?:ed|ing|s)?)(?: toward (?:God|you))? of ',r'\1 away from ',chosen)
        chosen=chosen.replace('reorientation from ','reorientation away from ')
        chosen=chosen.replace('unwilling to reorient toward God heart','heart unwilling to reorient toward God')
    if chosen==before:
        # Some old chosen fields were already inconsistent with their own source.
        source=norm(str(d.get('source_word','')))
        noun=bool(re.search(r'μετανοι(?:α|αν|ας)\b',source))
        chosen=('reorientation' if noun else 'reorient')+target
    # A clause may deliberately express the departure instead of a destination.
    if 'toward God' not in text:chosen=chosen.replace(' toward God','')
    if 'toward you' not in text:chosen=chosen.replace(' toward you','')
    alternatives=list(d.get('alternatives') or [])
    if before and before!=chosen and before not in alternatives:alternatives.insert(0,before)
    d.update(chosen=chosen,alternatives=alternatives,
             rationale=item['rationale']+' This is a scoped terminology decision, not a new independent lexicon consultation or a whole-verse accuracy certification.',
             lexicon='Recorded source and contextual English comparison; see docs/REORIENTATION_POLICY_2026-10-11.md',
             doctrine_reference='DOCTRINE.md: Reorientation terminology (2026-10-11)')
    return d


def build_record(doc,item,timestamp):
    result=copy.deepcopy(doc)
    old=doc['translation']['text']
    if digest(doc.get('source') or {})!=item['source_sha256']:
        raise ValueError('Source mismatch: '+item['path'])
    text=item['after_text']
    notes=copy.deepcopy(doc['translation'].get('footnotes') or [])
    # Correct only terminology explanations which explicitly asserted the old
    # chosen wording, not historical alternatives or unrelated source notes.
    for n in notes:
        body=n.get('text','')
        if item['id']=='MAT.3.2' and ('literally =' in body or 'fundamental reorientation' in body):
            n['text']='Traditionally "Repent." The Greek calls for changed disposition and direction in response to the kingdom proclamation. "Toward God" makes the contextual direction explicit; it is not contained in the verb by itself. Sorrow is neither the whole meaning nor excluded.'
        if item['id']=='MAN.1.8' and "'appoint' was chosen" in body:
            n['text']='Or "did not set reorientation before the righteous." The Greek verb can mean "set" or "appoint"; the noun is traditionally "repentance."'
        if item['id']=='SIR.18.21' and "here it is rendered 'repentance'" in body:
            n['text']='Or "show your return." Greek epistrophe denotes a turning back; the immediate reference to sins gives this movement its moral context.'
        if item['id']=='WIS.12.10' and 'literally' in body:
            n['text']='Or "you were giving an opportunity for reorientation." Greek topos supplies the image of room/place; metanoia is traditionally rendered "repentance."'
    marker='r1'
    used={str(n.get('marker')) for n in notes}
    while marker in used or '['+marker+']' in text:
        marker='r'+str(int(marker[1:])+1)
    match=re.search(r'\breorient\w*(?: toward (?:God|you))?|\bunregretted\b|\b(?:feel |felt )?regret\w*|\breconsider\w*|\ba change of mind\b|\bchange their minds\b|\bchanged my attitude\b|\bturn(?:ing|ed)? back\b|\bsorrow\b|\bgrief\b|\bbroken spirit\b',text,re.I)
    if not match:raise ValueError('Cannot anchor policy note: '+item['path'])
    text=text[:match.end()]+'['+marker+']'+text[match.end():]
    notes.append({'marker':marker,'text':wording_note(item,doc),'reason':'lexical_alternative'})
    result['translation']['text']=text
    result['translation']['footnotes']=notes
    history=result.setdefault('review_history',[])
    for field in ARCHIVE_FIELDS:
        if field in doc:
            history.append({'field':field,'value':copy.deepcopy(doc[field]),'archived_by':POLICY,
                            'archived_from_baseline_sha256':item['before_sha256'],
                            'certifies_this_candidate':False,'historical_review_inputs_verified':False})
    # Previous full text/notes remain in git at the pinned baseline; preserve
    # explicit paths/hashes rather than copying megabyte chapter records again.
    history.append({'field':'translation','baseline_commit':item['baseline_commit'],
                    'baseline_path':item['path'],'sha256':digest(doc['translation']),
                    'archived_by':POLICY,'certifies_this_candidate':False})
    for k in ('revision_pass','source_audit'):result.pop(k,None)
    result['status']='draft'
    result['cross_check']={'status':'needs_review'}
    result['lexical_decisions']=[new_lexical(d,item,text) if relevant(d) and (TERM.search(str(d.get('chosen',''))) or COGNITIVE.search(str(d.get('chosen',''))) or re.search('μετανο|μετενο',norm(str(d.get('source_word',''))))) else d for d in (doc.get('lexical_decisions') or [])]
    # Move superseded translation judgments out of the live reasoning layer;
    # retain unrelated judgments and all originals in review_history.
    result['theological_decisions']=[d for d in doc.get('theological_decisions')or[] if not relevant(d)]
    result['theological_decisions'].append({'issue':'Context-sensitive reorientation terminology',
         'chosen_reading':re.sub(r'\[r\d+\]','',text) if len(text)<1500 else 'The exact reader wording is recorded in the hash-bound terminology plan.',
         'alternative_readings':['Traditional repent/repentance wording, preserved at the baseline commit.'],
         'rationale':item['rationale'], 'doctrine_reference':'DOCTRINE.md: Reorientation terminology (2026-10-11)'})
    for field in ('simplification_decisions','interpretive_expansions','retained_terms'):
        if isinstance(doc.get(field),list):result[field]=[d for d in doc[field] if not relevant(d)]
    if item['path'].startswith('translation_simplified/'):
        result.setdefault('retained_terms',[]).append({'term':'reorient / reorientation','reason':'Maintainer-approved shared English terminology. The anchored reader note explains changed disposition and direction; context-specific exceptions are preserved.'})
        if item['mode'] in {'godward','addressed'}:
            result.setdefault('interpretive_expansions',[]).append({'pob_phrase':'reorient / reorientation','rendering':'toward God' if item['mode']=='godward' else 'toward you','claim':'Make the destination supplied by the religious context explicit, without claiming it is lexical content of metanoia.','evidence':[item['rationale']],'confidence':'moderate','alternatives_preserved':['reorient / reorientation without an expressed destination']})
    if isinstance(doc.get('translation_notes'),dict):
        # Notes about the old decision are historical, not current endorsement.
        result['translation_notes']=copy.deepcopy(doc['translation_notes'])
        for k,v in result['translation_notes'].items():
            if isinstance(v,list):result['translation_notes'][k]=[d for d in v if not relevant(d)]
        result['translation_notes'].setdefault('risk_flags',[]).append({'risk':'Reorient is less common English and explicit Godward wording is a contextual expansion.','mitigation':'Explain it in the reader note; preserve source-specific exceptions and avoid added intensifiers.'})
    source=doc.get('source') or {}
    adaptation=source.get('text_scope')=='public_domain_english_witness' or source.get('language')=='English'
    result['terminology_revision']={'policy_id':POLICY,'timestamp':timestamp,'baseline_commit':item['baseline_commit'],
          'baseline_file_sha256':item['before_sha256'],'mode':item['mode'],'reader_note_marker':marker,
          'source_changed':False,'english_witness_adaptation':adaptation,'independent_scholar_review':False,
          'maintainer_approval_scope':'English terminology policy and POB/SPOB/extra-canonical scope; not a claim of human review of every proposed line.',
          'after_text_sha256':hashlib.sha256(text.encode()).hexdigest()}
    revision={'timestamp':timestamp,'adjudicator':'Codex: maintainer-authorized terminology application',
              'category':'terminology','policy_id':POLICY,'rationale':item['rationale'],
              'from_sha256':hashlib.sha256(old.encode()).hexdigest(),'to_sha256':hashlib.sha256(text.encode()).hexdigest(),
              'baseline_commit':item['baseline_commit'],'baseline_path':item['path']}
    if len(old)<10000:revision.update({'from':old,'to':text})
    else:revision['exact_replacement_record']='config/terminology/reorientation-english-2026-10-11.json#'+item['path']
    result.setdefault('revisions',[]).append(revision)
    return result


def patch_top_level(raw, old, new):
    """Preserve untouched YAML bytes, including source and original generation."""
    node=yaml.compose(raw,Loader=yaml.CSafeLoader)
    starts={k.value:k.start_mark.index for k,v in node.value}
    keys=[k.value for k,v in node.value]
    spans={k:(starts[k],starts[keys[i+1]] if i+1<len(keys) else len(raw)) for i,k in enumerate(keys)}
    patches=[]
    for k in old:
        if k not in new: patches.append((*spans[k],''))
        elif old[k]!=new[k]:
            replacement=yaml.safe_dump({k:new[k]},allow_unicode=True,sort_keys=False,width=1000)
            patches.append((*spans[k],replacement))
    for start,end,replacement in sorted(patches,reverse=True):raw=raw[:start]+replacement+raw[end:]
    additions={k:v for k,v in new.items() if k not in old}
    if additions:raw=raw.rstrip()+'\n'+yaml.safe_dump(additions,allow_unicode=True,sort_keys=False,width=1000)
    assert yaml.load(raw,Loader=yaml.CSafeLoader)==new
    return raw


def approved_errors(path, doc, require_exact=False):
    meta=doc.get('terminology_revision')or{}
    if meta.get('policy_id')!=POLICY:return []
    text=(doc.get('translation')or{}).get('text','')
    errors=[]
    if TERM.search(text):errors.append('Legacy repent-family word reintroduced into approved reader text')
    if require_exact and hashlib.sha256(text.encode()).hexdigest()!=meta.get('after_text_sha256'):
        errors.append('Reader text no longer matches this recorded terminology revision')
    return errors


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply',action='store_true');ap.add_argument('--check',action='store_true')
    args=ap.parse_args();plan=json.loads(PLAN.read_text());timestamp=datetime.now(timezone.utc).isoformat()
    prepared=[];errors=[];skipped=0
    # Preflight all targets before writing any file.
    for raw_item in plan['records']:
        item=dict(raw_item,baseline_commit=plan['baseline_commit']);path=ROOT/item['path'];raw=path.read_bytes();doc=yaml.load(raw,Loader=yaml.CSafeLoader)
        if (doc.get('terminology_revision')or{}).get('policy_id')==POLICY:
            errors.extend(item['path']+': '+e for e in approved_errors(path,doc,True));skipped+=1;continue
        if args.check:errors.append(item['path']+': policy not applied');continue
        if digest(raw)!=item['before_sha256']:errors.append(item['path']+': input changed since plan review');continue
        new=build_record(doc,item,timestamp)
        prepared.append((path,patch_top_level(raw.decode(),doc,new)))
    if errors:raise SystemExit('\n'.join(errors))
    if args.apply:
        for path,raw in prepared:path.write_text(raw,encoding='utf-8')
    print(json.dumps({'planned':len(prepared),'already_applied':skipped,'written':len(prepared) if args.apply else 0,'check':args.check}))
if __name__=='__main__':main()
