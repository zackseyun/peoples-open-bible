"""Pre-author serialization preflight only. Passing is NEVER language approval."""
from pathlib import Path
import argparse,json,re,hashlib,sys
import jsonschema
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R))
SCHEMA=json.loads((R/'schema/verse.schema.json').read_text())
def findings(rows):
 errors=[]
 if not isinstance(rows,list)or not rows:return['Input must be a nonempty list of submitted rows.']
 refs=[]
 for i,row in enumerate(rows):
  if not isinstance(row,dict):errors.append(f'Row{i}:notanobject');continue
  ref=row.get('reference');refs.append(ref);prefix=f'{ref or i}:'
  match=re.fullmatch(r'1 Enoch ([1-9][0-9]*):([1-9][0-9]*)',ref if isinstance(ref,str)else'')
  if not match or not 1<=int(match[1])<=108:errors.append(prefix+'referenceinvalid')
  elif row.get('id')!=f'1EN.{match[1]}.{match[2]}'or row.get('book')!='1 Enoch':errors.append(prefix+'identitydiffers')
  for field in ['source','translation']:
   obj=row.get(field)
   if not isinstance(obj,dict):errors.append(prefix+field+'missingobject');continue
   for e in jsonschema.Draft202012Validator(SCHEMA['properties'][field]).iter_errors(obj):errors.append(prefix+field+'.'+'.'.join(map(str,e.path))+':'+e.message)
  src=row.get('source',{});trans=row.get('translation',{})
  src=src if isinstance(src,dict)else{};trans=trans if isinstance(trans,dict)else{}
  if src.get('edition')!='charles-1906-enoch'or src.get('language')!='Geez':errors.append(prefix+'selectededition/languageinvalid')
  if src.get('confidence')not in['medium','low']:errors.append(prefix+'explicitboundedconfidence required')
  if any(x in (src.get('text','')if isinstance(src.get('text',''),str)else'')for x in['\ufffd','□','⟦','UNRESOLVED']):errors.append(prefix+'placeholderorunresolvedfidels:mustremainHOLD,notintegrationready')
  if src.get('confidence')=='low':
   if not src.get('note')or not src.get('transcription_uncertainties')or not trans.get('footnotes'):errors.append(prefix+'lowconfidence needs honest accepted selected-critical-scope/source-note/explanation controls; NEVER invent unknowns or raise confidence')
  notes=trans.get('footnotes',[]);notes=notes if isinstance(notes,list)else[];markers=[n.get('marker')if isinstance(n.get('marker'),str)else None for n in notes if isinstance(n,dict)];anchors=re.findall(r'\[([a-z])\]',trans.get('text','')if isinstance(trans.get('text',''),str)else'')
  if len(markers)!=len(set(markers))or set(markers)!=set(anchors):errors.append(prefix+'internalexplanationanchors/definitionsdiffer')
 if len(refs)!=len(set(map(repr,refs))):errors.append('Duplicate submitted references.')
 return errors
def receipt_findings(input_path,review_path,provenance_path):
 from tools.enoch import bounded_application as transaction
 errors=[]
 submitted=json.loads(input_path.read_text());review=json.loads(review_path.read_text());pv=json.loads(provenance_path.read_text())
 try:
  decisions=transaction.review_entries(review)
 except ValueError as error:
  errors.append(str(error));decisions=[]
 if set(r.get('reference')for r in decisions)!=set(r.get('reference')for r in submitted):errors.append('Explicit decision set differs from submitted references.')
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 if pv.get('input_sha256')!=sha(input_path)or pv.get('review_sha256')!=sha(review_path):errors.append('Provenance does not bind exact input/review bytes.')
 if not pv.get('reviewer_id')or pv.get('role')not in['author','corrective_author','independent_reviewer']:errors.append('Actual reviewer identity/role is missing.')
 if review.get('reviewer_id')!=pv.get('reviewer_id')or review.get('role')!=pv.get('role'):errors.append('Review/provenance actual identity or role differs.')
 if pv.get('source_pdf_sha256')!=transaction.PRIMARY_SHA:errors.append('Primary PDF identity differs.')
 scans=pv.get('scan_image_sha256',{})
 if not isinstance(scans,dict)or not scans or any(not isinstance(v,str)or not re.fullmatch('[0-9a-f]{64}',v)for v in scans.values()):errors.append('Missing flat actual scan-image hash map.')
 return errors
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('inputs',nargs='+',type=Path);p.add_argument('--review',type=Path);p.add_argument('--provenance',type=Path);a=p.parse_args();failed=False
 if bool(a.review)!=bool(a.provenance)or(a.review and len(a.inputs)!=1):p.error('Receipt preflight requires one input plus both review and provenance.')
 for path in a.inputs:
  errors=findings(json.loads(path.read_text()))
  if a.review:errors.extend(receipt_findings(path,a.review,a.provenance))
  print(json.dumps({'input':str(path),'serialization_preflight_pass':not errors,'errors':errors,'language_source_English_or_publication_approved':False},ensure_ascii=False));failed|=bool(errors)
 raise SystemExit(int(failed))
