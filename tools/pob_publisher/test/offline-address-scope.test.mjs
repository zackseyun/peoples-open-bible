import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {compileGit,inventory,assertParity,hash} from '../package.mjs';

const root=fileURLToPath(new URL('../../../',import.meta.url));
const fixture=JSON.parse(fs.readFileSync(new URL('../../../tests/fixtures/pob_publisher/batch41-address-scope.json',import.meta.url)));
const ref=(c,v)=>JSON.stringify(['1 Enoch',c,v]);

test('B41 offline comparison proves only two reviewed address additions; default gate stays closed',async()=>{
  assert.equal(fixture.runtime_activation_authorized,false);
  assert.equal(fixture.scope,'offline_comparison_only_no_runtime_address_waiver');
  assert.deepEqual(Object.keys(fixture.added_addresses).sort(),[ref(32,6),ref(66,2)].sort());
  assert.deepEqual(Object.keys(fixture.existing_changes).sort(),
    [ref(2,2),ref(3,1),ref(7,3),ref(32,3),ref(66,1)].sort());
  assert.equal(fixture.review_application_manifests.length,3);
  for(const m of fixture.review_application_manifests){
    assert.equal(hash(execFileSync('git',['-C',root,'show',m.source_sha+':'+m.path])),m.sha256);
  }
  const previous=await compileGit(root,fixture.previous_source_sha);
  const candidate=await compileGit(root,fixture.source_sha);
  const a=inventory(previous),z=inventory(candidate);
  assert.equal(a.verses,45231);
  assert.equal(z.verses,45233);
  assert.deepEqual(Object.keys(a.records).filter(k=>!(k in z.records)),[]);
  assert.deepEqual(Object.fromEntries(Object.keys(z.records).filter(k=>!(k in a.records)).map(k=>[k,z.records[k]])),fixture.added_addresses);
  assert.throws(()=>assertParity(a,candidate,fixture.existing_changes),/Unapproved structure_sha256 change/);

  // This projection is ONLY an offline equality test, never a release payload.
  const normalized=structuredClone(candidate);
  const book=normalized.books.find(b=>b.name==='1 Enoch');
  for(const [chapter,verse,expected] of [[32,6,[1,2,3,4,5,6]],[66,2,[1,2,3]]]){
    const ch=book.chapters.find(c=>c.chapter===chapter);
    assert.deepEqual(ch.verses.map(v=>v.verse),expected);
    ch.verses=ch.verses.filter(v=>v.verse!==verse);
  }
  assertParity(a,normalized,fixture.existing_changes);
});
