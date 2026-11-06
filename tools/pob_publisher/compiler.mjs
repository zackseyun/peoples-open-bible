// Extracted, unchanged canonical transforms from pinned CDK source; see provenance.json.
import { Readable } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import { createGunzip } from 'node:zlib';
import tar from 'tar-stream';
import yaml from 'js-yaml';
import { splitChapterBlob } from './vendor/chapter-blob.mjs';
import { reviewedEnochNoteMetadata, hasReviewedEnochNotes } from './vendor/reviewed-enoch-notes.mjs';
import { normalizeBibleVerseTerminology } from './vendor/terminology-policy.mjs';
import { annotateJesusWords, manuscriptMetadata, splitEditorialParagraphs } from './vendor/extra-canonical-reader.mjs';
const CANONICAL_BOOKS = [
  "Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth",
  "1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra",
  "Nehemiah","Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Solomon",
  "Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos",
  "Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi",
  "Tobit","Judith","Greek Additions to Esther","Wisdom of Solomon","Sirach","Baruch",
  "Additions to Daniel","1 Maccabees","2 Maccabees","1 Esdras","Prayer of Manasseh",
  "Psalm 151","3 Maccabees","4 Maccabees",
  "Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians",
  "Galatians","Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians",
  "1 Timothy","2 Timothy","Titus","Philemon","Hebrews","James","1 Peter","2 Peter",
  "1 John","2 John","3 John","Jude","Revelation",
  // Extra-canonical (ordered after NT in the reader)
  "1 Clement","1 Enoch","2 Baruch","2 Esdras","Bel and the Dragon","Didache",
  "Gospel of Thomas","Gospel of Truth","Jubilees","Letter of Jeremiah",
  "Prayer of Azariah and Song of the Three","Psalms of Solomon",
  "Shepherd of Hermas","Susanna","Thunder, Perfect Mind",
  // Testaments of the Twelve Patriarchs (each testament as its own book)
  "Testament of Reuben","Testament of Simeon","Testament of Levi",
  "Testament of Judah","Testament of Issachar","Testament of Zebulun",
  "Testament of Dan","Testament of Naphtali","Testament of Gad",
  "Testament of Asher","Testament of Joseph","Testament of Benjamin",
];

const BOOK_ALIASES = new Map([
  ["Song of Songs", "Song of Solomon"],
  ["Ecclesiasticus", "Sirach"],
  ["Greek Additions to Daniel", "Additions to Daniel"],
  ["Greek Esther Additions", "Greek Additions to Esther"],
  ["Additions to Esther", "Greek Additions to Esther"],
]);

const SUPERSCRIPT_DIGITS = "¹²³⁰-⁹";
const SUBSCRIPT_DIGITS = "₀-₉";
const SUPERSCRIPT_LETTERS = "ᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ";
const SUBSCRIPT_LETTERS = "ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜ";
const FOOTNOTE_SYMBOLS = `${SUPERSCRIPT_DIGITS}${SUBSCRIPT_DIGITS}${SUPERSCRIPT_LETTERS}${SUBSCRIPT_LETTERS}`;
const FOOTNOTE_MARKER_RE = new RegExp(
  String.raw`\[(?:[A-Za-z]|\d{1,3}|[${FOOTNOTE_SYMBOLS}]+)\]|[${FOOTNOTE_SYMBOLS}]+`,
  "gu",
);
const ORPHAN_TRAILING_LETTER_MARKER_RE = /([.!?—])([A-Z])(?=\s*(?:\n|$))/gu;

function stripVerseFootnoteMarkers(text) {
  if (typeof text !== "string" || text.length === 0) return text;
  return text
    .replace(FOOTNOTE_MARKER_RE, "")
    .replace(ORPHAN_TRAILING_LETTER_MARKER_RE, "$1")
    .replace(/ {2,}/g, " ")
    .trim();
}

// Map testament slug directory names to canonical book names.
const TESTAMENT_SLUG_TO_NAME = new Map([
  ["reuben", "Testament of Reuben"],
  ["simeon", "Testament of Simeon"],
  ["levi", "Testament of Levi"],
  ["judah", "Testament of Judah"],
  ["issachar", "Testament of Issachar"],
  ["zebulun", "Testament of Zebulun"],
  ["dan", "Testament of Dan"],
  ["naphtali", "Testament of Naphtali"],
  ["gad", "Testament of Gad"],
  ["asher", "Testament of Asher"],
  ["joseph", "Testament of Joseph"],
  ["benjamin", "Testament of Benjamin"],
]);

function parseReferenceBook(reference = "") {
  const ref = String(reference).trim();
  const idx = ref.lastIndexOf(" ");
  const book = idx === -1 ? ref : ref.slice(0, idx);
  return BOOK_ALIASES.get(book) || book;
}

// Testament chapters use "N. text" markers (number + period + space).
// Crucially, verse 1 is unnumbered — it's the text before the first "2. "
// marker — so splitChapterBlob cannot be used here.
function splitTestamentChapter(text) {
  const re = /\n+\s*(\d+)\.\s+/g;
  const splits = [];
  let lastIndex = 0;
  let lastVerseNum = 1;
  let match;
  while ((match = re.exec(text)) !== null) {
    const body = text.slice(lastIndex, match.index).trim();
    if (body) splits.push({ verse: lastVerseNum, text: body });
    lastVerseNum = parseInt(match[1], 10);
    lastIndex = match.index + match[0].length;
  }
  const lastBody = text.slice(lastIndex).trim();
  if (lastBody) splits.push({ verse: lastVerseNum, text: lastBody });
  return splits.filter((s) => s.text);
}

function textParagraphs(text) {
  return String(text || "")
    .split(/\n+/)
    .map((p) => p.trim())
    .filter(Boolean);
}

function readInt(value, fallback = null) {
  const n = Number.parseInt(value, 10);
  return Number.isFinite(n) ? n : fallback;
}

function normalizeReaderSections(doc) {
  const nav = doc?.reader_navigation && typeof doc.reader_navigation === "object"
    ? doc.reader_navigation
    : {};
  const raw = Array.isArray(doc?.reader_sections)
    ? doc.reader_sections
    : Array.isArray(nav?.reader_sections)
      ? nav.reader_sections
      : [];
  return raw
    .map((section, idx) => {
      if (!section || typeof section !== "object") return null;
      const number = readInt(
        section.section ?? section.number ?? section.order,
        idx + 1,
      );
      const start = readInt(
        section.paragraph_start ?? section.paragraphStart ?? section.start,
        null,
      );
      const end = readInt(
        section.paragraph_end ?? section.paragraphEnd ?? section.end,
        start,
      );
      const title = String(
        section.title ?? section.heading ?? section.label ?? "",
      ).trim();
      if (!Number.isFinite(number) || !start || !end || end < start) return null;
      return {
        number,
        title,
        paragraphStart: start,
        paragraphEnd: end,
      };
    })
    .filter(Boolean);
}

function splitReaderSections(text, readerSections) {
  if (!Array.isArray(readerSections) || readerSections.length === 0) return [];
  const paragraphs = textParagraphs(text);
  if (paragraphs.length === 0) return [];

  const out = [];
  const covered = [];
  for (const section of readerSections) {
    if (
      section.paragraphStart < 1 ||
      section.paragraphEnd < section.paragraphStart ||
      section.paragraphEnd > paragraphs.length
    ) {
      return [];
    }
    const body = paragraphs
      .slice(section.paragraphStart - 1, section.paragraphEnd)
      .join("\n")
      .trim();
    if (!body) return [];
    for (let i = section.paragraphStart; i <= section.paragraphEnd; i += 1) {
      covered.push(i);
    }
    out.push({
      verse: section.number,
      text: body,
      editorialHeading: section.title,
      sectionLabel: `§${section.number}`,
      isEditorialSection: true,
    });
  }

  const expected = Array.from({ length: paragraphs.length }, (_, i) => i + 1);
  covered.sort((a, b) => a - b);
  if (
    covered.length !== expected.length ||
    covered.some((value, index) => value !== expected[index])
  ) {
    return [];
  }
  return out;
}

export async function extractVerseRecords(tarballWebStream) {
  const raws = [];
  const extract = tar.extract();

  extract.on("entry", (header, stream, next) => {
    const name = header.name.replace(/^[^/]+\//, "");
    // Per-verse T12P files live one level deeper than other extra_canonical
    // books (testament folder + chapter folder + verse file), so they need
    // their own pattern; the generic nestedMatch only allows two folders
    // before the chapter/verse digits.
    const testamentsNestedMatch = name.match(/^translation\/extra_canonical\/testaments_twelve_patriarchs\/([^/]+)\/(\d{3})\/(\d{3})\.ya?ml$/i);
    const nestedMatch = !testamentsNestedMatch && name.match(/^translation\/([^/]+)\/([^/]+)\/(\d{3})\/(\d{3})\.ya?ml$/i);
    const flatMatch = name.match(/^translation\/extra_canonical\/([^/]+)\/(\d{1,3})\.ya?ml$/i);
    // Testaments: translation/extra_canonical/testaments_twelve_patriarchs/<testament>/NNN.yaml
    const testamentsMatch = name.match(/^translation\/extra_canonical\/testaments_twelve_patriarchs\/([^/]+)\/(\d{1,3})\.ya?ml$/i);

    if (header.type !== "file" || (!testamentsNestedMatch && !nestedMatch && !flatMatch && !testamentsMatch)) {
      stream.on("end", next);
      stream.resume();
      return;
    }

    const chunks = [];
    stream.on("data", (c) => chunks.push(c));
    stream.on("end", () => {
      try {
        const doc = yaml.load(Buffer.concat(chunks).toString("utf-8"));
        const text = String(doc?.translation?.text ?? "").trim();
        const reference = String(doc?.reference ?? "").trim();
        const bookField = String(doc?.book ?? "").trim();
        const bookName = bookField || parseReferenceBook(reference);
        const isExtraCanonical = Boolean(
          testamentsNestedMatch || flatMatch || testamentsMatch || nestedMatch?.[1] === "extra_canonical",
        );
        const sourceMetadata = isExtraCanonical
          ? manuscriptMetadata(
              testamentsNestedMatch?.[1] || nestedMatch?.[2] || flatMatch?.[1] || testamentsMatch?.[1] || "",
              doc?.source || {},
            )
          : null;
        if (!text || !bookName) {
          next();
          return;
        }

        // Only keep footnotes that are actually referenced inline in the
        // text (as "[marker]"). Background notes like marker: "1:2" or
        // reason: "previous_rendering" stay out of the CDN payload —
        // they'd never render and would just bloat the JSON.
        const allFootnotes = Array.isArray(doc?.translation?.footnotes)
          ? doc.translation.footnotes
          : [];
        const footnotes = [];
        for (const f of allFootnotes) {
          if (!f || f.text == null) continue;
          const rawMarker = String(f.marker ?? "").trim();
          if (!rawMarker) continue;
          const stripped = rawMarker.replace(/^\[|\]$/g, "");
          if (!stripped) continue;
          const inlineRef = `[${stripped}]`;
          if (!text.includes(inlineRef)) continue;
          footnotes.push({
            marker: stripped,
            text: String(f.text).trim(),
            ...(f.reason ? { reason: String(f.reason) } : {}),
          });
        }

        if (testamentsNestedMatch) {
          const [, testamentSlug, chRaw, vRaw] = testamentsNestedMatch;
          const canonicalName = TESTAMENT_SLUG_TO_NAME.get(testamentSlug.toLowerCase());
          if (!canonicalName) { next(); return; }
          raws.push({
            kind: "nested",
            section: "extra_canonical",
            bookSlug: `testaments_twelve_patriarchs/${testamentSlug}`,
            bookName: canonicalName,
            chapter: parseInt(chRaw, 10),
            verse: parseInt(vRaw, 10),
            text,
            footnotes,
            sourceMetadata,
          });
        } else if (nestedMatch) {
          const [, section, bookSlug, chRaw, vRaw] = nestedMatch;
          raws.push({
            kind: "nested",
            section,
            bookSlug,
            bookName,
            ...reviewedEnochNoteMetadata(doc, section, bookSlug),
            chapter: parseInt(chRaw, 10),
            verse: parseInt(vRaw, 10),
            text,
            footnotes,
            sourceMetadata,
          });
        } else if (testamentsMatch) {
          // Each testament is a separate book; chapters are the NNN file index.
          const [, testamentSlug, fileRaw] = testamentsMatch;
          const canonicalName = TESTAMENT_SLUG_TO_NAME.get(testamentSlug.toLowerCase());
          if (!canonicalName) { next(); return; }
          const unit = String(doc?.unit ?? "").trim();
          const chapterTitle = String(doc?.source?.chapter_title ?? "").trim();
          const blockIndex = parseInt(doc?.source?.block_index, 10);
          raws.push({
            kind: "flat",
            section: "extra_canonical",
            bookSlug: `testaments_twelve_patriarchs/${testamentSlug}`,
            bookName: canonicalName,
            fileIndex: parseInt(fileRaw, 10),
            unit,
            chapterTitle,
            blockIndex: Number.isFinite(blockIndex) ? blockIndex : null,
            text,
            footnotes,
            readerSections: normalizeReaderSections(doc),
            sourceMetadata,
          });
        } else {
          const [, bookSlug, fileRaw] = flatMatch;
          const unit = String(doc?.unit ?? "").trim();
          const chapterTitle = String(doc?.source?.chapter_title ?? "").trim();
          const blockIndex = parseInt(doc?.source?.block_index, 10);
          raws.push({
            kind: "flat",
            section: "extra_canonical",
            bookSlug,
            bookName,
            fileIndex: parseInt(fileRaw, 10),
            unit,
            chapterTitle,
            blockIndex: Number.isFinite(blockIndex) ? blockIndex : null,
            text,
            footnotes,
            readerSections: normalizeReaderSections(doc),
            sourceMetadata,
          });
        }
      } catch (error) {
        // Proposal safety change: never silently omit malformed Scripture.
        extract.destroy(new Error(`Malformed YAML: ${name}`, { cause: error }));
      }
      next();
    });
    stream.on("error", next);
  });

  const nodeStream = Readable.fromWeb(tarballWebStream);
  await pipeline(nodeStream, createGunzip(), extract);
  return raws;
}

// Second pass: turn raw records into a flat list of
// { bookName, chapter, verse, text }. Handles three flat-file unit types
// separately so each book's intrinsic structure survives:
//   - line_block  → group by source.chapter_title; verse = block_index
//   - chapter     → split the inline-numbered blob into one record per verse
//   - saying/section/other → one file → chapter N, verse 1 (legacy shape)
// A flat record is dropped if a nested record exists for the same book,
// so any partially-migrated book serves nested drafts without duplicates.
export function normalizeRecords(raws) {
  const metadataByBook = new Map();
  raws.forEach((record) => {
    if (record.sourceMetadata && !metadataByBook.has(record.bookName)) {
      metadataByBook.set(record.bookName, record.sourceMetadata);
    }
  });
  const bookHasNested = new Set(
    raws.filter((r) => r.kind === "nested").map((r) => r.bookName),
  );

  const out = [];
  const flatBySlug = new Map();

  const filterForText = (footnotes, text) =>
    (footnotes || []).filter((f) => text.includes(`[${f.marker}]`));

  for (const r of raws) {
    if (r.kind === "nested") {
      out.push({
        bookName: r.bookName,
        chapter: r.chapter,
        verse: r.verse,
        text: r.text,
        footnotes: r.footnotes || [],
        footnote_review: r.footnote_review,
        source_critical: r.source_critical,
        sourceMetadata: r.sourceMetadata || null,
      });
      continue;
    }

    if (bookHasNested.has(r.bookName)) {
      // Book has a nested per-verse draft — the flat chapter-level file
      // is a stale pre-split original; ignore it.
      continue;
    }

    if (!flatBySlug.has(r.bookSlug)) flatBySlug.set(r.bookSlug, []);
    flatBySlug.get(r.bookSlug).push(r);
  }

  for (const [, list] of flatBySlug) {
    list.sort((a, b) => a.fileIndex - b.fileIndex);
    const first = list[0];
    const unit = first.unit;

    if (unit === "line_block") {
      // Group by chapter_title in first-encounter order.
      const chapterNumByTitle = new Map();
      for (const r of list) {
        const title = r.chapterTitle || `Section ${r.fileIndex}`;
        if (!chapterNumByTitle.has(title)) {
          chapterNumByTitle.set(title, chapterNumByTitle.size + 1);
        }
        const chapter = chapterNumByTitle.get(title);
        const verse = r.blockIndex ?? r.fileIndex;
        out.push({
          bookName: r.bookName,
          chapter,
          verse,
          text: r.text,
          footnotes: r.footnotes || [],
        });
      }
      continue;
    }

    const isTestamentBook = first.bookSlug.startsWith(
      "testaments_twelve_patriarchs/",
    );

    if (isTestamentBook) {
      // Testament chapters use "N. text" markers with an unnumbered verse 1.
      for (const r of list) {
        const split = splitTestamentChapter(r.text);
        if (split.length > 0) {
          for (const { verse, text } of split) {
            out.push({
              bookName: r.bookName,
              chapter: r.fileIndex,
              verse,
              text,
              footnotes: filterForText(r.footnotes, text),
            });
          }
        } else {
          out.push({
            bookName: r.bookName,
            chapter: r.fileIndex,
            verse: 1,
            text: r.text,
            footnotes: r.footnotes || [],
          });
        }
      }
      continue;
    }

    // Reader-navigation sections split a long flat source record into
    // smaller, explicitly editorial reading blocks. This preserves the
    // translated wording exactly, while giving clients headings and smaller
    // selectable units for books like Gospel of Truth.
    if (Array.isArray(first.readerSections) && first.readerSections.length > 0) {
      for (const r of list) {
        const split = splitReaderSections(r.text, r.readerSections);
        if (split.length > 0) {
          for (const section of split) {
            out.push({
              bookName: r.bookName,
              chapter: r.fileIndex,
              verse: section.verse,
              text: section.text,
              footnotes: filterForText(r.footnotes, section.text),
              editorialHeading: section.editorialHeading,
              sectionLabel: section.sectionLabel,
              isEditorialSection: section.isEditorialSection,
            });
          }
        } else {
          out.push({
            bookName: r.bookName,
            chapter: r.fileIndex,
            verse: 1,
            text: r.text,
            footnotes: r.footnotes || [],
          });
        }
      }
      continue;
    }

    if (unit === "chapter") {
      // Each file is one chapter, verses are numbered inline in the blob.
      for (const r of list) {
        const split = splitChapterBlob(r.text, r.fileIndex);
        if (split.length > 0) {
          for (const { verse, text } of split) {
            out.push({
              bookName: r.bookName,
              chapter: r.fileIndex,
              verse,
              text,
              footnotes: filterForText(r.footnotes, text),
            });
          }
        } else {
          // Couldn't find inline verse numbers — fall back to a single
          // verse so the chapter at least renders rather than disappears.
          out.push({
            bookName: r.bookName,
            chapter: r.fileIndex,
            verse: 1,
            text: r.text,
            footnotes: r.footnotes || [],
          });
        }
      }
      continue;
    }

    // Editorial prose uses its existing blank-line paragraphs as modern reader
    // units. Single-paragraph sayings retain the legacy verse-1 address.
    for (const r of list) {
      const paragraphs = splitEditorialParagraphs(r.text);
      for (const paragraph of paragraphs) {
        out.push({
          bookName: r.bookName,
          chapter: r.fileIndex,
          verse: paragraph.verse,
          text: paragraph.text,
          footnotes: filterForText(r.footnotes, paragraph.text),
          isEditorialSection: paragraph.isEditorialSection,
          sourceMetadata: r.sourceMetadata || null,
        });
      }
    }
  }

  out.forEach((record) => {
    record.sourceMetadata ||= metadataByBook.get(record.bookName) || null;
  });
  return annotateJesusWords(out);
}

export function compileBooks(raws) {
  const records = normalizeRecords(raws);
  const byBook = new Map();
  for (const rec of records) {
    if (!byBook.has(rec.bookName)) byBook.set(rec.bookName, new Map());
    const byChapter = byBook.get(rec.bookName);
    if (!byChapter.has(rec.chapter)) byChapter.set(rec.chapter, new Map());
    byChapter.get(rec.chapter).set(rec.verse, {
      text: rec.text,
      footnotes: rec.footnotes || [],
      footnote_review: rec.footnote_review,
      source_critical: rec.source_critical,
      editorialHeading: rec.editorialHeading || "",
      sectionLabel: rec.sectionLabel || "",
      isEditorialSection: Boolean(rec.isEditorialSection),
      jesusWords: rec.jesusWords || [],
      sourceMetadata: rec.sourceMetadata || null,
    });
  }

  const order = new Map(CANONICAL_BOOKS.map((name, idx) => [name, idx]));
  const bookNames = [...byBook.keys()].sort((a, b) => {
    const ai = order.has(a) ? order.get(a) : 9999;
    const bi = order.has(b) ? order.get(b) : 9999;
    if (ai !== bi) return ai - bi;
    return a.localeCompare(b);
  });

  const books = [];
  for (const bookName of bookNames) {
    const chaptersMap = byBook.get(bookName);
    const chapterNums = [...chaptersMap.keys()].sort((a, b) => a - b);
    const chapters = chapterNums.map((chapter) => {
      const verseMap = chaptersMap.get(chapter);
      const verses = [...verseMap.keys()]
        .sort((a, b) => a - b)
        .map((verse) => {
          const v = verseMap.get(verse);
          const reviewedNotes = hasReviewedEnochNotes(v, bookName);
          const entry = {
            verse,
            text: normalizeBibleVerseTerminology(reviewedNotes ? v.text : stripVerseFootnoteMarkers(v.text)),
          };
          if (reviewedNotes) {
            entry.footnotes = v.footnotes;
            entry.footnote_review = v.footnote_review;
            entry.source_critical = v.source_critical;
          }
          if (v.editorialHeading) {
            entry.editorial_heading = v.editorialHeading;
            entry.section_heading = v.editorialHeading;
          }
          if (v.sectionLabel) {
            entry.section_label = v.sectionLabel;
          }
          if (v.isEditorialSection) {
            entry.is_editorial_section = true;
          }
          return entry;
        });
      const speakerRecords = verses.map((entry) => ({
        bookName,
        chapter,
        verse: entry.verse,
        text: entry.text,
      }));
      annotateJesusWords(speakerRecords);
      speakerRecords.forEach((record, index) => {
        if (record.jesusWords?.length) {
          verses[index].jesus_words = record.jesusWords;
        }
      });
      return { chapter, verses };
    });
    const sourceMetadata = [...chaptersMap.values()]
      .flatMap((verseMap) => [...verseMap.values()])
      .map((verse) => verse.sourceMetadata)
      .find(Boolean);
    if (chapters.length) {
      books.push({
        name: bookName,
        ...(sourceMetadata ? { metadata: sourceMetadata } : {}),
        chapters,
      });
    }
  }
  return books;
}
