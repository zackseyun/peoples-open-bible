// Offline only: no HTTP, credentials, cloud SDK, dispatch, or upload command.
import fs from 'node:fs';
import path from 'node:path';
import { gunzipSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';
import { compileGit, assertParity, bundle, hash, canonical } from './package.mjs';
const [repo, sourceSha, baselinePath, changesPath, updatedAt, output] = process.argv.slice(2);
if (!output) throw Error('Usage: node build.mjs REPO SOURCE_SHA BASELINE.json.gz CHANGES.json UPDATED_AT OUTPUT_DIRECTORY');
const baselineBytes=fs.readFileSync(baselinePath), baseline=JSON.parse(gunzipSync(baselineBytes));
const changesBytes=fs.readFileSync(changesPath), changes=JSON.parse(changesBytes);
const compilerFiles=['compiler.mjs','package.mjs','build.mjs','package-lock.json','vendor/chapter-blob.mjs','vendor/extra-canonical-reader.mjs','vendor/reviewed-enoch-notes.mjs','vendor/terminology-policy.mjs'];
const compilerIdentity=()=>hash(JSON.stringify(compilerFiles.map(name=>[name,hash(fs.readFileSync(fileURLToPath(new URL(name,import.meta.url))))])));
const compilerSha=compilerIdentity();
if (changes.source_sha!==sourceSha || changes.baseline_sha!==baseline.source_sha || changes.baseline_inventory_sha256!==hash(baselineBytes)) throw Error('Unbound source/baseline approval');
const payload=await compileGit(repo,sourceSha);
if (compilerIdentity()!==compilerSha || hash(fs.readFileSync(baselinePath))!==hash(baselineBytes) || hash(fs.readFileSync(changesPath))!==hash(changesBytes)) throw Error('Compiler or proof inputs changed during compilation');
const parity=assertParity(baseline,payload,changes.allowed);
const objects=bundle(payload,sourceSha,updatedAt);
const seal={protocol:'pob-azure-offline-package-v1', source_sha:sourceSha, compiler_sha256:compilerSha, baseline_inventory_sha256:hash(baselineBytes), changes_sha256:hash(changesBytes), parity_passed:true, changed:parity.changed, objects:Object.fromEntries(Object.entries(objects).map(([k,v])=>[k,hash(v)]))};
// Never overwrite an earlier reviewed package or write into the source checkout.
if (fs.existsSync(output)) throw Error('Output must not already exist');
if (path.resolve(output).startsWith(path.resolve(repo)+path.sep)) throw Error('Output must be outside source checkout');
fs.mkdirSync(output,{recursive:true});for(const [name,bytes] of Object.entries(objects))fs.writeFileSync(path.join(output,name),bytes,{flag:'wx'});
fs.writeFileSync(path.join(output,'seal.json'),JSON.stringify(seal,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({source_sha:sourceSha,books:parity.books,chapters:parity.chapters,verses:parity.verses,changed:parity.changed,reviewed_seal_sha256:hash(JSON.stringify(canonical(seal))+'\n'),cloud_writes:0}));
