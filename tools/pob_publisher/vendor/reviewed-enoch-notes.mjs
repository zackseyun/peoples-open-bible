// Canonical source-review approval is supplied by the corpus transaction, not
// inferred from file presence, a complete chapter, or an attractive rendering.
export const ENOCH_NOTE_REVIEW = 'pob-enoch-paired-source-review-v1';

export function reviewedEnochNoteMetadata(doc, section, slug) {
  if (section !== 'extra_canonical' || slug !== '1_enoch' ||
      doc?.source_correction?.individual_unit_application_approved !== true ||
      doc?.source?.edition !== 'charles-1906-enoch' ||
      doc?.source?.language !== 'Geez' || !doc.source.text ||
      !Array.isArray(doc.source.pages) || !doc.source.pages.length) return {};
  const source = {};
  for (const key of ['edition', 'language', 'text', 'pages', 'note', 'confidence',
    'transcription_uncertainties', 'additional_translation_input']) {
    if (doc.source[key] !== undefined) source[key] = doc.source[key];
  }
  return { footnote_review: ENOCH_NOTE_REVIEW, source_critical: source };
}

export function hasReviewedEnochNotes(verse, bookName) {
  return bookName === '1 Enoch' && verse?.footnote_review === ENOCH_NOTE_REVIEW &&
    verse?.source_critical?.edition === 'charles-1906-enoch' &&
    Array.isArray(verse.footnotes) && verse.footnotes.length > 0;
}

// A compiler-only repair must invalidate device/browser caches even when the
// canonical Git SHA has not changed. Keep commit_sha as the exact source lock.
export const PUBLISHER_CONTENT_REVISION = 'enoch-notes-v2';
export function publisherVersion(sourceSha) {
  return `${sourceSha.substring(0, 12)}-${PUBLISHER_CONTENT_REVISION}`;
}
export function isCurrentPublisherManifest(manifest, sourceSha) {
  return manifest?.commit_sha === sourceSha &&
    manifest?.compiler_revision === PUBLISHER_CONTENT_REVISION;
}
