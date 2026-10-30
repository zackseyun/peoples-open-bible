# 1 Enoch (Ge'ez): Word-Level Image Dataset

A word-level image dataset of the Ge'ez (Classical Ethiopic) text of the Book of 1 Enoch, based on R. H. Charles's 1906 edition. Every word is cropped from the printed page scan and aligned with its transcribed text, chapter by chapter and verse by verse.

It is intended for Ge'ez / Ethiopic text recognition, word spotting, and digital-humanities research on 1 Enoch.

## Source

- **Edition:** R. H. Charles, *The Ethiopic Version of the Book of Enoch*, Oxford: Clarendon Press, 1906.
- **Page scans:** <https://archive.org/details/ethiopicversiono00charuoft> (Internet Archive; listed as not in copyright).
- **Language:** Ge'ez (`gez`), Ethiopic script.

## Provenance of the text

The main text source was AI-generated: it comes from the [People's Open Bible](https://github.com/zackseyun/peoples-open-bible) repository (`zackseyun/peoples-open-bible`, CC BY 4.0), whose texts were produced by AI models. This dataset is published in a fork of that repository. It was built from that text, which was then corrected directly. After the corrections, the whole dataset was reviewed in full.

## What was done

- Text correction, applied directly to the AI-generated base text.
- Word segmentation: each word was cropped from the page scan.
- Alignment: each cropped word image is linked to its text, with chapter, verse and word indices.
- Full review of the finished dataset.

Text correction, word segmentation, alignment and review: Pîrvu Beniamin.

## Contents

```
ch01/
  ch01.json        verses of chapter 1 (word images + text)
  words/
    1.webp
    2.webp
    ...
ch02/
  ...
1 Enoch.json          the whole book in one file (with title, language, license)
viewer.html        browse the book in a browser (see below)
```

Images are stored as WebP (converted from the original PNG crops). Image paths in the JSON are relative to the chapter folder, for example `words/12.webp` inside `ch01/`.

## Data format

`1 Enoch.json` contains the book metadata and a `text` list with one entry per verse. Each `chNN/chNN.json` contains only the verse entries of that chapter. Every verse lists its words in reading order, and every word entry holds the path of its image together with its aligned text.

```json
{
  "title": "1 Enoch (Ge'ez)",
  "language": "gez",
  "license": "CC BY 4.0",
  "text": [
    {
      "chapter_index": 1,
      "verse_index": 1,
      "words": [
        { "word_index": 0, "image": "words/1.webp" }
      ]
    }
  ]
}
```

## Viewer

Open `viewer.html` in any browser (no server needed). It shows the word images together with their text, verse by verse, either one chapter at a time or the whole book, with controls for image height, text size, RTL order, and jumping to a chapter or verse.

## Known limitations

- The text started as an AI-generated draft. It was corrected and fully reviewed, but errors may remain.
- The text follows the 1906 edition with corrections. It is not a critical edition and does not replace later scholarship on the Ethiopic text of 1 Enoch.

## License

- **This dataset** (cropped word images as compiled, segmentation, aligned and corrected text, JSON files): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- **Underlying sources:** the 1906 edition and its scans are not in copyright (see the Internet Archive item above). The base text comes from the [People's Open Bible](https://github.com/zackseyun/peoples-open-bible), which is also CC BY 4.0. This dataset is published in a fork of that repository, so credit goes directly to the People's Open Bible project and its contributors.

## Acknowledgments

Page scans courtesy of the Internet Archive. Text edition by R. H. Charles (1906). Base text from the People's Open Bible project.
