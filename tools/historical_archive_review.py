#!/usr/bin/env python3
"""Source-first, research-only preparation for the historical archive.

No secret access, inference, translation writes, or publication occurs here.
Snapshots and source-comparison bundles go to a caller-selected research folder.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BILARA_COMMIT = 'a20fcb094d1d618080e52f41f24d20d5e347b0f7'
BILARA_BASE = f'https://raw.githubusercontent.com/suttacentral/bilara-data/{BILARA_COMMIT}/'
DHP_RANGES = [(1,20),(21,32),(33,43),(44,59),(60,75),(76,89),(90,99),(100,115),(116,128),(129,145),(146,156),(157,166),(167,178),(179,196),(197,208),(209,220),(221,234),(235,255),(256,272),(273,289),(290,305),(306,319),(320,333),(334,359),(360,382),(383,423)]

def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def dump(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def fetch(url: str, cache: Path) -> bytes:
    record_path=cache.with_name(cache.name+'.receipt.json')
    record=json.loads(record_path.read_text()) if record_path.exists() else None
    if cache.exists():
        raw=cache.read_bytes()
        if not record or record.get('url')!=url or record.get('sha256')!=digest(raw) or record.get('bytes')!=len(raw):
            raise ValueError(f'Cached source has missing or mismatched provenance: {cache}')
        return raw
    request = urllib.request.Request(url, headers={'User-Agent':'POB-SourceReview/1.0 (research-only)'})
    with urllib.request.urlopen(request, timeout=90) as response:
        raw = response.read()
    if record and (record.get('url')!=url or record.get('sha256')!=digest(raw)):
        raise ValueError('Rehydrated upstream source differs from the recorded snapshot; review a new version')
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(raw)
    dump(record_path,{'url':url,'sha256':digest(raw),'bytes':len(raw)})
    return raw

def receipt(url: str, raw: bytes, role: str) -> dict:
    return {'url':url, 'sha256':digest(raw), 'bytes':len(raw), 'role':role}

def source_job(work: str, reference: str, language: str, text: str,
               comparisons: list[dict], *, mode: str = 'original_language_review') -> dict:
    return {'schema_version':1, 'work':work, 'reference':reference, 'mode':mode,
            'source':{'language':language,'text':text,'sha256':digest(text.encode('utf-8'))},
            'english_comparisons':comparisons, 'publication_allowed':False,
            'review_status':'not_started', 'claims':{'manuscript_collation':False,
              'whole_work_verified':False, 'canon_effect':'none'}}

def parse_muller(raw: bytes) -> dict[int,dict]:
    text=raw.decode('utf-8-sig').replace('\r\n','\n')
    end=text.find('*** END OF THE PROJECT GUTENBERG EBOOK')
    if end<0: raise ValueError('Missing Gutenberg end boundary')
    text=text[:end]
    matches=list(re.finditer(r'^(\d{1,3}(?:,\s*\d{1,3})*)\.\s+', text, re.M))
    spans=[[int(n) for n in m[1].split(',')] for m in matches]
    if [n for span in spans for n in span] != list(range(1,424)):
        raise ValueError('Müller verse numbering is incomplete, duplicated, or changed')
    result={}
    for i, m in enumerate(matches):
        body=text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)]
        # Printed chapter headings are metadata, not the preceding verse.
        body=re.split(r'\n\s*Chapter [IVXLC]+\.',body)[0]
        for n in spans[i]:
            result[n]={'text':re.sub(r'\s+',' ',body).strip(),'verse_span':spans[i],
              'alignment':'individual_verse' if len(spans[i])==1 else 'combined_span_not_individually_aligned'}
    return result

def group_bilara(data: dict[str,str], first: int, last: int, *, allow_empty: bool = False) -> dict[int,list[tuple[str,str]]]:
    groups=defaultdict(list)
    for key,value in data.items():
        match=re.fullmatch(r'dhp(\d+):(\d+(?:\.\d+)?)',key)
        if not match: raise ValueError(f'Unexpected source segment: {key}')
        verse=int(match[1])
        if not first <= verse <= last: raise ValueError('Source segment outside declared chapter')
        if match[2].startswith('0.'): continue  # headings and story titles, not verse text
        if not value.strip() and not allow_empty: raise ValueError(f'Empty verse segment: {key}')
        groups[verse].append((key,value.strip()))
    if sorted(groups)!=list(range(first,last+1)): raise ValueError('Missing source verse')
    return dict(groups)

def acquire_dhammapada(out: Path, archive_root: Path) -> dict:
    raw_path=archive_root/'texts/dhammapada.txt'
    raw=raw_path.read_bytes()
    catalog=json.loads((archive_root/'catalog.json').read_text())
    archived=next(w for w in catalog['works'] if w['id']=='dhammapada')
    if digest(raw)!=archived['sha256']: raise ValueError('Archived Müller witness drift')
    muller=parse_muller(raw)
    witnesses=[receipt(archived['source_url'],raw,'historical_english_comparison')]
    for name in ['LICENSE.md','_publication.json','_author.json','_edition.json']:
        data=fetch(BILARA_BASE+name,out/'raw/bilara'/name)
        witnesses.append(receipt(BILARA_BASE+name,data,'license_or_edition_metadata'))
    publications=json.loads((out/'raw/bilara/_publication.json').read_bytes())
    publication=next(v for v in publications.values() if v.get('text_uid')=='dhp' and v.get('author_uid')=='sujato' and v.get('translation_lang_iso')=='en')
    if publication['license']['license_abbreviation']!='CC0' or not publication['is_published']:
        raise ValueError('English comparison license/publication changed')
    def chapter(bounds):
        first,last=bounds; stem=f'dhp{first}-{last}'
        root_path=f'root/pli/ms/sutta/kn/dhp/{stem}_root-pli-ms.json'
        english_path=f'translation/en/sujato/sutta/kn/dhp/{stem}_translation-en-sujato.json'
        root_raw=fetch(BILARA_BASE+root_path,out/'raw/bilara'/root_path)
        english_raw=fetch(BILARA_BASE+english_path,out/'raw/bilara'/english_path)
        root=json.loads(root_raw);english=json.loads(english_raw)
        if set(root)!=set(english): raise ValueError('Pali/English segment alignment changed')
        source=group_bilara(root,first,last)
        # Empty translated heading values are allowed; body values are not.
        translated=group_bilara(english,first,last,allow_empty=True)
        rows=[]
        for n in range(first,last+1):
            source_ids=[key for key,_ in source[n]]
            if source_ids!=[key for key,_ in translated[n]]: raise ValueError('Source order differs from comparison')
            row=source_job('Dhammapada',str(n),'pli','\n'.join(value for _,value in source[n]),[
              {'translator':'F. Max Müller','edition':'Sacred Books of the East X (1881), Gutenberg 2017','text':muller[n]['text'],'verse_span':muller[n]['verse_span'],
               'alignment':muller[n]['alignment'],'role':'comparison_only'},
              {'translator':'Bhikkhu Sujato','edition':f'Bilara published commit {BILARA_COMMIT}','text':'\n'.join(value for _,value in translated[n]),'role':'comparison_only'}])
            row['source'].update({'edition':'Mahāsaṅgīti (Bilara ms)','segment_ids':source_ids,
                'snapshot_sha256':digest(root_raw),'url':BILARA_BASE+root_path,
                'evidence_class':'direct_language_edited_text_not_new_manuscript_reading'})
            rows.append(row)
        return rows,[receipt(BILARA_BASE+root_path,root_raw,'pali_edited_text'),receipt(BILARA_BASE+english_path,english_raw,'cc0_english_comparison')]
    with ThreadPoolExecutor(max_workers=4) as executor:
        chapters=list(executor.map(chapter,DHP_RANGES))
    rows=[row for chapter_rows,_ in chapters for row in chapter_rows]
    if [int(row['reference']) for row in rows]!=list(range(1,424)): raise ValueError('Whole-work inventory mismatch')
    witnesses.extend(witness for _,chapter_witnesses in chapters for witness in chapter_witnesses)
    dump(out/'dhammapada/jobs.json',rows)
    report={'work':'Dhammapada','edition_commit':BILARA_COMMIT,'source_verses':423,'chapters':26,
       'english_comparisons':2,'muller_combined_spans':len(set(tuple(v['verse_span']) for v in muller.values() if len(v['verse_span'])>1)),
       'source_facing_model_reviews':0,'publication_allowed':False,
       'rights':{'sujato':'CC0, verified in pinned publication metadata',
         'muller':'Preserved Gutenberg public-domain-USA witness; its license wrapper remains in original archive',
         'pali_root':'Ancient Pali; digital-edition license scope must be explicitly confirmed before redistribution'},
       'source_quality':'Edited Pali edition; not exhaustive manuscript collation or an autograph',
       'witnesses':witnesses,'jobs_sha256':digest((out/'dhammapada/jobs.json').read_bytes())}
    dump(out/'dhammapada/acquisition.json',report)
    return report

class PrintedTextParser(HTMLParser):
    """Extract only the publisher's printed-text containers, never its notes."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[];self.current=None;self.paragraphs=[]
    def handle_starttag(self, tag, attrs):
        classes=set(dict(attrs).get('class','').split())
        blocked=bool(classes & {'footnote','footnote-ref','page-number','pageNumber','anonymous-block-p'}) or tag in {'script','style'}
        skip=blocked or (self.stack[-1][2] if self.stack else False)
        root=tag=='div' and 'wasptag' in classes and self.current is None and not skip
        if root:self.current=[]
        if tag in {'br','img','hr','meta','link','input'}:
            if tag=='br' and self.current is not None and not skip:self.current.append(' ')
            return
        self.stack.append((tag,root,skip))
    def handle_endtag(self, tag):
        matches=[i for i,item in enumerate(self.stack) if item[0]==tag]
        if not matches:return
        index=matches[-1]
        for _,root,_ in self.stack[index:]:
            if root:
                text=re.sub(r'\s+',' ',''.join(self.current or [])).strip()
                if text:self.paragraphs.append(text)
                self.current=None
        self.stack=self.stack[:index]
    def handle_data(self, data):
        if self.current is not None and not (self.stack[-1][2] if self.stack else False):self.current.append(data)

def parse_jsp_page(raw: bytes) -> tuple[str,dict]:
    html=raw.decode('utf-8')
    match=re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',html,re.S)
    if not match: raise ValueError('JSP page schema changed')
    page=json.loads(match[1])['props']['pageProps']['summary']
    parser=PrintedTextParser();parser.feed(page['clearText']);parser.close()
    if parser.current is not None:raise ValueError('Unclosed printed-text container')
    paragraphs=parser.paragraphs
    # JSP inserts a locator after the historical text. It is not on the scan.
    marker=f"[p. {page.get('editorialPageNumber')}]"
    if paragraphs and page.get('editorialPageNumber') and paragraphs[-1].endswith(marker):
        paragraphs[-1]=paragraphs[-1][:-len(marker)].rstrip()
    if not paragraphs: raise ValueError('Missing source transcription body')
    return '\n\n'.join(paragraphs),page

def acquire_dc_opening(out: Path, archive_root: Path) -> dict:
    catalog=json.loads((archive_root/'catalog.json').read_text())
    work=next(w for w in catalog['works'] if w['id']=='doctrine-and-covenants')
    raw=(archive_root/'texts/doctrine-and-covenants.txt').read_bytes()
    if digest(raw)!=work['sha256']: raise ValueError('D&C archive witness drift')
    ocr=raw.decode('utf-8').strip(); chunks=[
      ('title',9,4,ocr[:ocr.index('.1835.')+len('.1835.')]),
      ('preface-iii',11,6,ocr[ocr.index('PREFACE.'):ocr.index('\niv \n')]),
    ]
    reports=[]
    for name,jsp_page,leaf,current in chunks:
        url=f'https://www.josephsmithpapers.org/paper-summary/doctrine-and-covenants-1835/{jsp_page}'
        webpage=fetch(url,out/f'raw/jsp/{name}.html');text,page=parse_jsp_page(webpage)
        image_url=f'https://archive.org/download/GR_711/page/n{leaf}.jpg'
        scan=fetch(image_url,out/f'doctrine-and-covenants/scans/{name}.jpg')
        job=source_job('Doctrine and Covenants (1835)',name,'en',text,[
          {'translator':'not a translation','edition':'Newberry GR_711 OCR','text':current,'role':'ocr_candidate'}],mode='english_edition_scan_review')
        job['source'].update({'url':url,'evidence_class':'published_reading_of_other_copy_same_edition',
          'webpage_sha256':digest(webpage),'facsimile_url':image_url,'facsimile_sha256':digest(scan),
          'facsimile_path':str((out/f'doctrine-and-covenants/scans/{name}.jpg').resolve())})
        job['required_checks']=['printed edition identity','direct scan comparison','OCR errors versus real edition differences','no modernization','original-language translation claim not applicable']
        dump(out/f'doctrine-and-covenants/{name}.job.json',job)
        import difflib
        tokens=lambda value:re.findall(r"\w+(?:['’]\w+)?",value.casefold())
        a,b=tokens(current),tokens(text);matcher=difflib.SequenceMatcher(None,a,b,autojunk=False)
        changes=[{'op':tag,'ocr':' '.join(a[i:j]),'published_reading':' '.join(b[k:l])} for tag,i,j,k,l in matcher.get_opcodes() if tag!='equal']
        reports.append({'reference':name,'ocr_sha256':digest(current.encode()),'published_reading_sha256':digest(text.encode()),
          'source_url':url,'scan_url':image_url,'scan_sha256':digest(scan),'difference_groups':len(changes),
          'differences':changes,'status':'mechanical_comparison_not_source_approval','publication_allowed':False})
    report={'work':'Doctrine and Covenants (1835)','scope':'title page and first preface page only',
        'whole_edition_verified':False,'original_language_retranslation':False,'source_facing_model_reviews':0,
        'archive_sha256':digest(raw),'pages':reports,'rights':'Private research comparisons only; JSP editorial material is not republished',
        'review_status':'awaiting_scan_facing_review','publication_allowed':False}
    dump(out/'doctrine-and-covenants/acquisition.json',report)
    return report

def audit_church_orders(root: Path=ROOT) -> list[dict]:
    import yaml
    result=[]
    for name in ['apostolic_tradition','apostolic_constitutions','didascalia_apostolorum','apostolic_church_order']:
        manifest=json.loads((root/f'sources/early_christian_texts/{name}/manifest.json').read_text())
        files=sorted((root/f'translation/extra_canonical/{name}').glob('*.yaml'))
        rows=[yaml.safe_load(p.read_text()) for p in files]
        result.append({'id':name,'title':manifest['title'],'drafting_basis':manifest['current_drafting_basis']['kind'],
          'drafting_language_counts':{language:sum(r.get('source',{}).get('language')==language for r in rows)
            for language in sorted(set(r.get('source',{}).get('language','missing') for r in rows))},
          'chapters':len(files),'direct_source_language_review':manifest.get('direct_source_language_review'),
          'manifest_sha256':digest((root/f'sources/early_christian_texts/{name}/manifest.json').read_bytes()),
          'direct_language_verified':False,'publication_approval':'not_conferred_by_this_audit'})
    return result

def validate_review(job: dict, draft: dict, review: dict) -> list[str]:
    errors=[]
    if review.get('source_sha256')!=job['source']['sha256']: errors.append('source hash mismatch')
    draft_hash=digest(json.dumps(draft,ensure_ascii=False,sort_keys=True).encode())
    if review.get('draft_sha256')!=draft_hash: errors.append('draft hash mismatch')
    if not review.get('reviewer_model') or review.get('reviewer_model')==draft.get('generator_model'): errors.append('separate reviewer identity required')
    expected=[u['reference'] for u in draft.get('units',[])]
    actual=[u.get('reference') for u in review.get('units',[])]
    if not expected or actual!=expected: errors.append('review unit coverage mismatch')
    for unit in review.get('units',[]):
        if unit.get('verdict')!='acceptable' or unit.get('unresolved_issues'): errors.append(f"unresolved unit {unit.get('reference')}")
    if not review.get('rights_accepted'): errors.append('output/source rights review outstanding')
    if not review.get('scan_checked') and job['mode']=='english_edition_scan_review': errors.append('direct scan check required')
    if review.get('whole_work_verified') and not job.get('whole_work_scope_complete'): errors.append('pilot cannot approve whole work')
    return errors

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive-root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--acquire',choices=['none','dhammapada','dc','both'],default='none')
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    catalog=json.loads((args.archive_root/'catalog.json').read_text())
    evidence=[]
    for work in catalog['works']:
        raw=(args.archive_root/work['text_path'].split('/historical-library/')[-1]).read_bytes()
        if digest(raw)!=work['sha256']: raise ValueError(f"Archive drift: {work['id']}")
        evidence.append({'id':work['id'],'title':work['title'],'edition':work['edition'],'source_url':work['source_url'],
          'sha256':digest(raw),'current_review_status':work['review_status'],'full_pob_source_pass_verified':False})
    report={'checked_on':dt.datetime.now(dt.timezone.utc).isoformat(),'archive_works':evidence,
       'church_orders':audit_church_orders(),'publication_allowed':False,
       'verification_limit':'Inventory and hashes are not proof of English translation fidelity.'}
    if args.acquire in ['dhammapada','both']:report['dhammapada_acquisition']=acquire_dhammapada(out,args.archive_root)
    if args.acquire in ['dc','both']:report['dc_opening_acquisition']=acquire_dc_opening(out,args.archive_root)
    dump(out/'audit.json',report)
    print(json.dumps({'archive_works':len(evidence),'church_orders':len(report['church_orders']),
       'source_passes_verified':0,'dhammapada_source_verses':report.get('dhammapada_acquisition',{}).get('source_verses',0),
       'dc_opening_pages':len(report.get('dc_opening_acquisition',{}).get('pages',[])),
       'publication_allowed':False},indent=2))

if __name__=='__main__':main()
