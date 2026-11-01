// Offline package/format and exact-address parity gates. No network or cloud imports.
import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { Readable } from 'node:stream';
import { createGzip } from 'node:zlib';
import { extractVerseRecords, compileBooks } from './compiler.mjs';
import { publisherVersion, PUBLISHER_CONTENT_REVISION } from './vendor/reviewed-enoch-notes.mjs';
export const hash = value => createHash('sha256').update(value).digest('hex');
export function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(k => [k, canonical(value[k])]));
  return value;
}
export const digest = value => hash(JSON.stringify(canonical(value)));
export function inventory(payload) {
  if (digest(Object.keys(payload || {}).sort()) !== digest(['books','translation']) || !payload?.translation || !Array.isArray(payload.books) || !payload.books.length) throw Error('Empty/invalid canonical payload');
  const records = {}, metadata = {}, books = new Set(); let chapters = 0;
  for (const book of payload.books) {
    if (!book.name || books.has(book.name)) throw Error('Duplicate/invalid book');
    books.add(book.name); metadata[book.name] = Object.fromEntries(Object.entries(book).filter(([k]) => k !== 'chapters'));
    const seen = new Set();
    for (const chapter of book.chapters) {
      if (!Number.isSafeInteger(chapter.chapter) || (chapter.chapter < 0 || (chapter.chapter === 0 && book.name !== 'Gospel of Thomas')) || seen.has(chapter.chapter)) throw Error('Duplicate/invalid chapter');
      seen.add(chapter.chapter); chapters++;
      for (const verse of chapter.verses) {
        const key = JSON.stringify([book.name, chapter.chapter, verse.verse]);
        if (!Number.isSafeInteger(verse.verse) || (verse.verse < 0 || (verse.verse === 0 && book.name !== 'Psalms')) || key in records || !verse.text) throw Error('Duplicate/invalid verse');
        records[key] = digest(verse);
      }
    }
  }
  const structure_sha256 = digest(payload.books.map(b => ({ name:b.name, chapters:b.chapters.map(c => ({...Object.fromEntries(Object.entries(c).filter(([k])=>k!=='verses')), verses:c.verses.map(v=>v.verse)})) })));
  return { translation: payload.translation, structure_sha256, metadata, records, books: books.size, chapters, verses: Object.keys(records).length };
}
export function assertParity(baseline, candidate, allowed = {}) {
  const next = inventory(candidate);
  for (const key of ['translation', 'metadata', 'structure_sha256']) if (digest(baseline[key]) !== digest(next[key])) throw Error(`Unapproved ${key} change`);
  if (digest(Object.keys(baseline.records).sort()) !== digest(Object.keys(next.records).sort())) throw Error('Address addition/deletion prohibited, including held neighbors');
  const changed = Object.keys(next.records).filter(k => baseline.records[k] !== next.records[k]).sort();
  if (digest(changed) !== digest(Object.keys(allowed).sort())) throw Error('Unexpected or missing changed record');
  for (const key of changed) if (allowed[key].before !== baseline.records[key] || allowed[key].after !== next.records[key]) throw Error(`Unbound change: ${key}`);
  return { changed, ...next };
}
export async function compileGit(repo, sourceSha) {
  if (!/^[a-f0-9]{40}$/.test(sourceSha)) throw Error('Exact full source SHA required');
  const child = spawn('git', ['-C', repo, 'archive', '--format=tar', '--prefix=pob/', sourceSha, 'translation'], { stdio: ['ignore','pipe','pipe'] });
  let stderr = ''; child.stderr.on('data', x => { stderr += x; });
  const exited = new Promise((resolve, reject) => { child.on('error', reject); child.on('close', code => code === 0 ? resolve() : reject(Error(`git archive failed: ${stderr}`))); });
  // Attach rejection now, including early parser failures, to avoid unhandled promises.
  exited.catch(() => {});
  const gz = child.stdout.pipe(createGzip());
  try { const records = await extractVerseRecords(Readable.toWeb(gz)); await exited; return { translation: 'COB: Cartha Open Bible (Preview)', books: compileBooks(records) }; }
  catch (error) { child.kill(); throw error; }
}
export function bundle(payload, sourceSha, updatedAt) {
  if (!/^[a-f0-9]{40}$/.test(sourceSha) || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(updatedAt) || !Number.isFinite(Date.parse(updatedAt)) || new Date(updatedAt).toISOString()!==updatedAt) throw Error('Pinned SHA and explicit ISO timestamp required');
  const stats = inventory(payload);
  const manifest = { translation_id:'cob_preview', version:publisherVersion(sourceSha), compiler_revision:PUBLISHER_CONTENT_REVISION, commit_sha:sourceSha, updated_at:updatedAt, books:stats.books, chapters:stats.chapters, verses:stats.verses, bible_url:'cob_preview.json' };
  return { 'cob_preview.json': Buffer.from(JSON.stringify(payload,null,4)+'\n'), 'manifest.json':Buffer.from(JSON.stringify(manifest,null,2)+'\n') };
}
