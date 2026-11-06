const JESUS_SPEAKER_RE = /(?:\[\s*)?(?:Jesus|the Savior|the Saviour|the Lord|the Living One|the Holy One|he who is holy)(?:\s*\])?[^\n.!?;:“”"]{0,80}\b(?:said|asked|answered|replied|responded|continued|told|cried out|spoke)/giu;
const OTHER_SPEAKER_RE = /(?:\[\s*)?(?:Judas|Thomas|Mary|Matthew|Peter|Philip|the disciples?|his disciples?|they|the apostles?|the child(?: Jesus)?|Joseph|the teacher|the priest|the angel)(?:\s*\])?\s+(?:then\s+|also\s+|again\s+)?(?:said|asked|answered|replied|responded|continued|told|cried out|spoke)/giu;

const LORD_TITLE_BOOKS = new Set([
  "2 Clement",
  "Book of Thomas the Contender",
  "Dialogue of the Savior",
  "Gospel of Peter",
  "Fragments of Papias",
  "Polycarp to the Philippians",
]);
const JESUS_SPEECH_BOOKS = new Set([
  "2 Clement",
  "Apocryphon of John",
  "Book of Thomas the Contender",
  "Dialogue of the Savior",
  "Fragments of Papias",
  "Gospel of Judas",
  "Gospel of Mary",
  "Gospel of Peter",
  "Gospel of Philip",
  "Infancy Gospel of Thomas",
  "Letter of Peter to Philip",
  "Polycarp to the Philippians",
  "Sophia of Jesus Christ",
]);

const MANUSCRIPT_IMAGE_URLS = Object.freeze({
  gospel_of_thomas: "https://www.gospels.net/manuscript#the-gospel-of-thomas",
  gospel_of_truth: "https://ccdl.claremont.edu/digital/collection/nha",
  gospel_of_philip: "https://www.gospels.net/manuscript#the-gospel-of-philip",
  treatise_on_the_resurrection: "https://ccdl.claremont.edu/digital/collection/nha",
  apocryphon_of_john: "https://ccdl.claremont.edu/digital/collection/nha",
  hypostasis_of_the_archons: "https://ccdl.claremont.edu/digital/collection/nha",
  on_the_origin_of_the_world: "https://ccdl.claremont.edu/digital/collection/nha",
  sophia_of_jesus_christ: "https://ccdl.claremont.edu/digital/collection/nha",
  gospel_of_the_egyptians: "https://ccdl.claremont.edu/digital/collection/nha",
  dialogue_of_the_savior: "https://ccdl.claremont.edu/digital/collection/nha",
  exegesis_on_the_soul: "https://ccdl.claremont.edu/digital/collection/nha",
  book_of_thomas_the_contender: "https://ccdl.claremont.edu/digital/collection/nha",
  tripartite_tractate: "https://ccdl.claremont.edu/digital/collection/nha",
  letter_of_peter_to_philip: "https://ccdl.claremont.edu/digital/collection/nha",
  gospel_of_judas: "https://commons.wikimedia.org/wiki/Codex_Tchacos",
  gospel_of_mary: "https://www.gospels.net/manuscript#the-gospel-of-mary",
  gospel_of_peter: "https://www.gospels.net/manuscript#the-gospel-of-peter",
  protoevangelium_of_james: "https://www.gospels.net/manuscript#the-infancy-gospel-of-james",
  infancy_gospel_of_thomas: "https://www.gospels.net/manuscript#the-infancy-gospel-of-thomas",
  "1_clement": "https://www.bl.uk/collection/digitised-manuscripts-archives?ref=Royal_MS_1_D_VIII",
  "2_clement": "https://www.bl.uk/collection/digitised-manuscripts-archives?ref=Royal_MS_1_D_VIII",
  shepherd_of_hermas: "https://www.codexsinaiticus.org/en/manuscript.aspx",
  epistle_of_barnabas: "https://www.codexsinaiticus.org/en/manuscript.aspx",
});

function quoteRangeAfter(text, start) {
  const candidates = [
    { index: text.indexOf("“", start), closer: "”" },
    { index: text.indexOf('"', start), closer: '"' },
  ].filter((item) => item.index >= 0).sort((a, b) => a.index - b.index);
  if (!candidates.length) return null;
  const { index, closer } = candidates[0];
  const close = text.indexOf(closer, index + 1);
  return { start: index + 1, end: close >= 0 ? close : text.length, remainsOpen: close < 0 };
}

export function jesusRangesForText(text, {
  continuingJesusSpeech = false,
  allowLordTitle = true,
} = {}) {
  const ranges = [];
  let carry = continuingJesusSpeech;
  if (carry && /^[\s]*[“"]/.test(text)) {
    const quoteStart = text.search(/[“"]/);
    const closer = text[quoteStart] === "“" ? "”" : '"';
    const close = text.indexOf(closer, quoteStart + 1);
    ranges.push({ start: quoteStart + 1, end: close >= 0 ? close : text.length });
    carry = close < 0;
  }

  JESUS_SPEAKER_RE.lastIndex = 0;
  OTHER_SPEAKER_RE.lastIndex = 0;
  const attributions = [
    ...Array.from(text.matchAll(JESUS_SPEAKER_RE), (match) => ({ match, isJesus: true }))
      .filter(({ match }) => {
        const prefix = text.slice(Math.max(0, match.index - 12), match.index).toLowerCase();
        if (prefix.endsWith("of ") || prefix.endsWith("of the ")) return false;
        return allowLordTitle || !match[0].toLowerCase().includes("lord");
      }),
    ...Array.from(text.matchAll(OTHER_SPEAKER_RE), (match) => ({ match, isJesus: false })),
  ].sort((a, b) => a.match.index - b.match.index);

  for (const attribution of attributions) {
    const matchEnd = attribution.match.index + attribution.match[0].length;
    const quote = quoteRangeAfter(text, matchEnd);
    if (!quote) {
      if (!attribution.isJesus) carry = false;
      continue;
    }
    if (attributions.some((item) => item.match.index > matchEnd && item.match.index < quote.start)) continue;
    if (attribution.isJesus && quote.end > quote.start) ranges.push({ start: quote.start, end: quote.end });
    carry = attribution.isJesus && quote.remainsOpen;
  }

  const merged = [];
  for (const range of ranges.sort((a, b) => a.start - b.start || a.end - b.end)) {
    const previous = merged[merged.length - 1];
    if (previous && range.start <= previous.end) previous.end = Math.max(previous.end, range.end);
    else merged.push({ ...range });
  }
  return { ranges: merged, continuingJesusSpeech: carry };
}

export function splitEditorialParagraphs(text) {
  return String(text || "")
    .split(/\n+/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean)
    .map((paragraph, index) => ({
      verse: index + 1,
      text: paragraph,
      isEditorialSection: true,
    }));
}

export function annotateJesusWords(records) {
  const groups = new Map();
  records.forEach((record) => {
    const key = `${record.bookName}\u0000${record.chapter}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(record);
  });
  for (const list of groups.values()) {
    if (!JESUS_SPEECH_BOOKS.has(list[0]?.bookName)) continue;
    list.sort((a, b) => a.verse - b.verse);
    let carry = false;
    for (const record of list) {
      const result = jesusRangesForText(record.text, {
        continuingJesusSpeech: carry,
        allowLordTitle: LORD_TITLE_BOOKS.has(record.bookName),
      });
      carry = result.continuingJesusSpeech;
      if (result.ranges.length) record.jesusWords = result.ranges;
    }
  }
  return records;
}

export function manuscriptMetadata(bookSlug, source = {}) {
  const imagesUrl = MANUSCRIPT_IMAGE_URLS[bookSlug] || "";
  const metadata = {
    ...(String(source.manuscript || "").trim() ? { manuscript: String(source.manuscript).trim() } : {}),
    ...(String(source.ancient_language || "").trim() ? { ancient_language: String(source.ancient_language).trim() } : {}),
    ...(String(source.witness_url || "").trim() ? { source_witness_url: String(source.witness_url).trim() } : {}),
    ...(imagesUrl ? { manuscript_images_url: imagesUrl } : {}),
    ...(bookSlug === "gospel_of_judas" ? {
      manuscript_thumbnail_url: "https://commons.wikimedia.org/wiki/Special:Redirect/file/Codex_Tchacos_p33.jpg?width=960",
    } : {}),
  };
  if (!Object.keys(metadata).length) return null;
  metadata.division_note = "Numbered reading units are modern paragraph divisions, not ancient verse numbers.";
  return metadata;
}
