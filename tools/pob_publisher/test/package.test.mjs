import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { gunzipSync, gzipSync } from 'node:zlib';
import { Readable } from 'node:stream';
import tar from 'tar-stream';
import { compileGit, inventory, assertParity, bundle, digest, hash } from '../package.mjs';
import { extractVerseRecords, compileBooks } from '../compiler.mjs';
import { verifyRelease } from '../resolve.mjs';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const fixture=n=>path.join(root,'tests/fixtures/pob_publisher',n);
const baseline=JSON.parse(gunzipSync(fs.readFileSync(fixture('baseline-a368.json.gz'))));
const changes=JSON.parse(fs.readFileSync(fixture('batch35-changes.json')));
const tiny=()=>({translation:'COB: Cartha Open Bible (Preview)',books:[{name:'1 Enoch',chapters:[{chapter:95,verses:[{verse:1,text:'Reviewed.[a]',footnotes:[{marker:'a',text:'Exact note'}],footnote_review:'pob-enoch-paired-source-review-v1',source_critical:{edition:'charles-1906-enoch',text:'source',pages:[237]}}]}]}]});
test('pinned source + helpers have exact recorded hashes; AWS-free imports',()=>{
 const p=JSON.parse(fs.readFileSync(path.join(root,'tools/pob_publisher/provenance.json')));
 assert.equal(hash(fs.readFileSync(path.join(root,'tools/pob_publisher/compiler.mjs'))),p.compiler_sha256);
 for(const [name,h] of Object.entries(p.vendor_sha256))assert.equal(hash(fs.readFileSync(path.join(root,'tools/pob_publisher/vendor',name))),h);
 const source=fs.readFileSync(path.join(root,'tools/pob_publisher/compiler.mjs'),'utf8');assert.doesNotMatch(source,/S3Client|CloudFrontClient|@aws|process\.env|fetch\(/);
});
test('full baseline compiler parity, including existing partial chapters',async()=>{
 const p=await compileGit(root,baseline.source_sha);assertParity(baseline,p);
 assert.equal(baseline.books,135);assert.equal(baseline.chapters,2651);assert.equal(baseline.verses,45231);
 for(const ch of [32,95,96])assert.ok(Object.keys(baseline.records).some(k=>JSON.parse(k)[0]==='1 Enoch' && JSON.parse(k)[1]===ch));
 assert.ok(baseline.records[JSON.stringify(['Psalms',3,0])]); assert.ok(Object.keys(baseline.records).some(k=>JSON.parse(k)[0]==='Gospel of Thomas'&&JSON.parse(k)[1]===0));
});
test('B35 changes exactly six whole records, no held-neighbor exposure',async()=>{
 assert.equal(hash(fs.readFileSync(fixture('baseline-a368.json.gz'))),changes.baseline_inventory_sha256);
 const p=await compileGit(root,changes.source_sha);const result=assertParity(baseline,p,changes.allowed);assert.equal(result.changed.length,6);
 assert.deepEqual(result.changed.map(k=>JSON.parse(k).slice(1)).sort(),[[95,1],[95,2],[95,3],[95,4],[95,5],[96,1]].sort());
});
for(const [name,edit] of [
 ['deletion',p=>p.books[0].chapters[0].verses.pop()],
 ['new held neighbor',p=>p.books[0].chapters[0].verses.push({verse:6,text:'Not approved'})],
 ['changed English',p=>p.books[0].chapters[0].verses[0].text='Other'],
 ['lost source',p=>delete p.books[0].chapters[0].verses[0].source_critical],
 ['lost notes',p=>delete p.books[0].chapters[0].verses[0].footnotes],
 ['lost protocol',p=>delete p.books[0].chapters[0].verses[0].footnote_review],
 ['book metadata',p=>p.books[0].metadata={unexpected:true}],
 ['translation name',p=>p.translation='Other'],
 ['extra root metadata',p=>p.unapproved='Other'],
 ['extra chapter metadata',p=>p.books[0].chapters[0].unapproved='Other'],
 ['duplicate address',p=>p.books[0].chapters[0].verses.push(p.books[0].chapters[0].verses[0])],
])test(`reject ${name}`,()=>{const before=tiny(),after=tiny();edit(after);assert.throws(()=>assertParity(inventory(before),after));});
test('explicit before/after seals needed for every approved change',()=>{const b=tiny(),p=tiny();p.books[0].chapters[0].verses[0].text='Corrected';const k=JSON.stringify(['1 Enoch',95,1]);const allow={[k]:{before:inventory(b).records[k],after:inventory(p).records[k]}};assertParity(inventory(b),p,allow);allow[k].after='0'.repeat(64);assert.throws(()=>assertParity(inventory(b),p,allow));});
test('canonical bundle deterministic with legacy keys and fixed timestamp',()=>{const p=tiny(),sha='a'.repeat(40),date='2026-10-31T00:00:00.000Z';const b=bundle(p,sha,date);assert.deepEqual(b,bundle(p,sha,date));assert.equal(JSON.parse(b['manifest.json']).version,'aaaaaaaaaaaa-enoch-notes-v2');assert.throws(()=>bundle(p,'main',date));assert.throws(()=>bundle(p,sha,'now'));assert.throws(()=>bundle(p,sha,'2026-02-31T00:00:00.000Z'));});
test('malformed YAML fails instead of silently disappearing',async()=>{const pack=tar.pack();pack.entry({name:'repo/translation/extra_canonical/1_enoch/095/001.yaml'},'translation: [unclosed');pack.finalize();const chunks=[];for await(const c of pack)chunks.push(c);await assert.rejects(extractVerseRecords(Readable.toWeb(Readable.from([gzipSync(Buffer.concat(chunks))]))),/Malformed YAML/);});
test('review protocol does not attach to legacy or unapproved source',()=>{const raws=[{kind:'nested',section:'extra_canonical',bookSlug:'1_enoch',bookName:'1 Enoch',chapter:95,verse:1,text:'Legacy.[a]',footnotes:[{marker:'a',text:'Unreviewed'}]}];const v=compileBooks(raws)[0].chapters[0].verses[0];assert.equal(v.text,'Legacy.');assert.equal(v.footnotes,undefined);assert.equal(v.footnote_review,undefined);});
test('fixed-origin consumer verifies exact bytes and rejects path/source/owner drift',()=>{
 const p=tiny(),source='a'.repeat(40),control='b'.repeat(64),release='c'.repeat(64),b=bundle(p,source,'2026-10-31T00:00:00.000Z');
 const ptr={protocol:'pob-azure-current-v1',release,source_sha:source,control_sha256:control,manifest_key:`canonical-pob/v1/releases/${release}/manifest.json`,manifest_sha256:hash(b['manifest.json']),payload_sha256:hash(b['cob_preview.json'])};
 assert.ok(verifyRelease(ptr,b['manifest.json'],b['cob_preview.json'],source,control).payloadUrl.startsWith('https://carthawebpgtbcmh46gckn6.z5.web.core.windows.net/canonical-pob/v1/'));
 for(const patch of [{manifest_key:'https://evil/manifest.json'},{source_sha:'d'.repeat(40)},{control_sha256:'e'.repeat(64)},{payload_sha256:'f'.repeat(64)},{release:'../escape'}])assert.throws(()=>verifyRelease({...ptr,...patch},b['manifest.json'],b['cob_preview.json'],source,control));
});
