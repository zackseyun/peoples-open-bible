const SLAVE_TERM = /\bslaves?\b/gi;

function preserveCase(source, replacement) {
  if (source === source.toUpperCase()) return replacement.toUpperCase();
  if (
    source[0] === source[0].toUpperCase()
    && source.slice(1) === source.slice(1).toLowerCase()
  ) {
    return `${replacement[0].toUpperCase()}${replacement.slice(1)}`;
  }
  return replacement;
}

/** Canonical CDN policy for reader-facing English Bible wording. */
export function normalizeBibleVerseTerminology(text) {
  if (typeof text !== "string" || text.length === 0) return text;
  return text.replace(SLAVE_TERM, (source) => {
    const replacement = source.toLowerCase() === "slaves" ? "servants" : "servant";
    return preserveCase(source, replacement);
  });
}
