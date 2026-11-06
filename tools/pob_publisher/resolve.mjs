// Consumer proof verifier only; no network, fallback, environment-selected origin or runtime activation.
import { hash, inventory } from './package.mjs';
const ORIGIN='https://carthawebpgtbcmh46gckn6.z5.web.core.windows.net';
export function verifyRelease(pointer, manifestBytes, payloadBytes, sourceSha, controlSha) {
  if (pointer?.protocol!=='pob-azure-current-v1' || !/^[a-f0-9]{64}$/.test(pointer.release || '') || !/^[a-f0-9]{40}$/.test(sourceSha || '') || !/^[a-f0-9]{64}$/.test(controlSha || '') || pointer.source_sha!==sourceSha || pointer.control_sha256!==controlSha) throw Error('Untrusted release/source/owner');
  const base=`canonical-pob/v1/releases/${pointer.release}/`;
  if (pointer.manifest_key!==base+'manifest.json' || hash(manifestBytes)!==pointer.manifest_sha256 || hash(payloadBytes)!==pointer.payload_sha256) throw Error('Invalid release path/bytes');
  const manifest=JSON.parse(manifestBytes), payload=JSON.parse(payloadBytes), stats=inventory(payload);
  if (manifest.commit_sha!==sourceSha || manifest.compiler_revision!=='enoch-notes-v2' || manifest.translation_id!=='cob_preview' || manifest.bible_url!=='cob_preview.json' || ['books','chapters','verses'].some(k=>manifest[k]!==stats[k])) throw Error('Canonical format/version/stats mismatch');
  return {manifest,payload,payloadUrl:`${ORIGIN}/${base}cob_preview.json`};
}
