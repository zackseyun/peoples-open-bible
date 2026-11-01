// Flat `unit: chapter` books can embed verse numbers inline inside a single
// text blob. Most use `1 Text...`, while Acts of Paul and Thecla retains
// explicit `1:1 Text...` labels. Split either shape so the reader supplies one
// clean verse marker instead of rendering a duplicate such as `1 1:1`.
export function splitChapterBlob(text, expectedChapter = null) {
  const source = String(text || "");
  const referenceRe = /(?:^|\n\s*\n)(\d+):(\d+)\s+/g;
  const referenceMatches = [...source.matchAll(referenceRe)];
  if (referenceMatches.length >= 2) {
    const chapters = referenceMatches.map((match) => parseInt(match[1], 10));
    const verses = referenceMatches.map((match) => parseInt(match[2], 10));
    const expected = Number(expectedChapter);
    const validChapter = chapters.every((chapter) => (
      Number.isFinite(chapter) && (!Number.isFinite(expected) || chapter === expected)
    ));
    const validVerses = verses[0] === 1 && verses.every((verse, index) => (
      Number.isFinite(verse) && (index === 0 || verse > verses[index - 1])
    ));
    if (validChapter && validVerses) {
      const out = referenceMatches.map((match, index) => {
        const start = (match.index ?? 0) + match[0].length;
        const end = referenceMatches[index + 1]?.index ?? source.length;
        return { verse: verses[index], text: source.slice(start, end).trim() };
      });
      if (out.every((entry) => entry.text)) return out;
    }
  }

  const re = /(^|\n)\s*(\d+)\s+([\s\S]*?)(?=\n\s*\d+\s+|$)/g;
  const out = [];
  let match;
  while ((match = re.exec(source)) !== null) {
    const verse = parseInt(match[2], 10);
    const body = match[3].replace(/\s+$/g, "").trim();
    if (Number.isFinite(verse) && body) out.push({ verse, text: body });
  }
  return out;
}
