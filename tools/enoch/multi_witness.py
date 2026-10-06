"""multi_witness.py — 1 Enoch per-verse witness aggregator (scaffold).

For any verse in 1 Enoch, return the reading from each available
textual witness. The translator prompt will receive this structured
block and use it for textual-critical grounding.

Witness layers (ordered by language authority):

  Zone 1 (our own OCR, CC-BY 4.0 output):
    - Ge'ez: Charles 1906 critical edition (primary)
    - Ge'ez: Dillmann 1851 (secondary, cross-check)
    - Greek: Bouriant 1892 (Codex Panopolitanus, chs 1-32)
    - Greek: Flemming–Radermacher 1901 (edited Greek material, including
      Panopolitanus and Syncellus; not the subsequently discovered Chester Beatty)

  Verified edition controls (not diplomatic manuscript transcriptions):
    - Explicitly checked local per-verse Greek edition records, comparative only

  Zone 1 validation oracle (not vendored, cross-check only):
    - Ge'ez: Beta maṣāḥǝft LIT1340EnochE.xml (Jerabek 1995 / CC-BY-SA
      wrapper / NC inner — kept local only)

  Zone 2 (consult, not reproduced):
    - Milik 1976, The Books of Enoch — Qumran Aramaic reconstructions
    - Nickelsburg 2001 Hermeneia
    - Nickelsburg & VanderKam 2012 Hermeneia
    - Knibb 1978 modern critical Ethiopic
    - Black 1985, OTP Isaac 1983

This is a SCAFFOLD. Actual OCR/transcription is Phase 11b; actual
translation is Phase 11c. The interface below is the target shape
that Phase 11c will consume.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
from dataclasses import dataclass
from typing import Optional

try:
    from . import verse_parser
    from . import dillmann_verse_parser
except ImportError:  # pragma: no cover - direct script execution
    import verse_parser  # type: ignore
    import dillmann_verse_parser  # type: ignore

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SOURCES_ROOT = REPO_ROOT / "sources" / "enoch"
BETAMASAHEFT_LOCAL = pathlib.Path.home() / "cartha-reference-local" / "enoch_betamasaheft"


@dataclass
class EnochWitnessReading:
    language: str       # "geez" | "greek" | "aramaic"
    witness: str        # e.g. "charles_1906" | "dillmann_1851" | "panopolitanus" | "syncellus" | "chester_beatty" | "betamasaheft"
    text: str           # transcribed text in native script
    source_edition: str
    confidence: str     # "high" | "medium" | "low"
    note: str = ""


@dataclass
class EnochVerseWitnessSet:
    chapter: int
    verse: int

    # Ge'ez witnesses (Zone 1 our-OCR + validation oracle)
    geez_charles: Optional[EnochWitnessReading] = None
    geez_dillmann: Optional[EnochWitnessReading] = None
    geez_betamasaheft_oracle: Optional[EnochWitnessReading] = None  # reference only, not for output derivation

    # Greek witnesses (Zone 1 our-OCR)
    greek_panopolitanus: Optional[EnochWitnessReading] = None  # chs 1-32
    greek_syncellus: Optional[EnochWitnessReading] = None      # scattered
    greek_chester_beatty: Optional[EnochWitnessReading] = None # chs 97-107
    # Edited comparative text, never silently placed in a manuscript slot.
    greek_edition_control: Optional[EnochWitnessReading] = None

    def available_witnesses(self) -> list[EnochWitnessReading]:
        out = []
        for w in [self.geez_charles, self.geez_dillmann, self.geez_betamasaheft_oracle,
                  self.greek_panopolitanus, self.greek_syncellus, self.greek_chester_beatty,
                  self.greek_edition_control]:
            if w is not None:
                out.append(w)
        return out

    def has_greek(self) -> bool:
        return any([self.greek_panopolitanus, self.greek_syncellus, self.greek_chester_beatty,
                    self.greek_edition_control])

    def section(self) -> str:
        """The compositional section this verse belongs to."""
        ch = self.chapter
        if 1 <= ch <= 36:
            return "Book of the Watchers"
        if 37 <= ch <= 71:
            return "Book of Parables / Similitudes"
        if 72 <= ch <= 82:
            return "Astronomical Book / Book of the Luminaries"
        if 83 <= ch <= 90:
            return "Book of Dreams / Animal Apocalypse"
        if 91 <= ch <= 108:
            return "Epistle of Enoch"
        return "unknown"


# ---- Zone 2 consult registry (copyrighted; reference only, no text copied) ----

CONSULT_REGISTRY: list[dict] = [
    {
        "name": "Milik, The Books of Enoch: Aramaic Fragments of Qumrân Cave 4 (Oxford)",
        "year": 1976,
        "coverage_chapters": "1-36, 72-108 (partial, depending on fragment)",
        "role": "Qumran Aramaic 4Q201-212 reconstructions. Consult for pre-Christian Aramaic witness to chapters outside the Parables. Footnote fact-level ('4Q204 attests the Greek reading here'); do NOT reproduce Milik's reconstructed Aramaic.",
    },
    {
        "name": "Nickelsburg, 1 Enoch 1: A Commentary (Hermeneia)",
        "year": 2001,
        "coverage_chapters": "1-36, 81-108",
        "role": "Gold-standard modern commentary. Consult for interpretive cruxes and textual-critical decisions. Do NOT track English phrasing — we produce our own.",
    },
    {
        "name": "Nickelsburg & VanderKam, 1 Enoch 2: A Commentary (Hermeneia)",
        "year": 2012,
        "coverage_chapters": "37-71 (the Parables)",
        "role": "The specialist commentary on the Similitudes, which we cannot cross-check against Qumran or Greek. Especially important for this section.",
    },
    {
        "name": "Knibb, The Ethiopic Book of Enoch (2 vols, Oxford)",
        "year": 1978,
        "coverage_chapters": "1-108",
        "role": "Modern critical Ge'ez edition with English translation and apparatus. Consult where Charles 1906 reading is unclear; Knibb's apparatus may preserve variant readings. Do not reproduce.",
    },
    {
        "name": "Black, The Book of Enoch or 1 Enoch: A New English Edition (Brill)",
        "year": 1985,
        "coverage_chapters": "1-108",
        "role": "Modern English translation with commentary. Consult for interpretive context.",
    },
    {
        "name": "Isaac, '1 (Ethiopic Apocalypse of) Enoch' in OTP vol. 1 (Charlesworth, ed.)",
        "year": 1983,
        "coverage_chapters": "1-108",
        "role": "Standard Pseudepigrapha-series English translation. Reference only.",
    },
]


def consult_sources() -> list[dict]:
    """Return Zone 2 scholarly references for Enoch.

    Per REFERENCE_SOURCES.md: these may be consulted during translation;
    their text must not appear in POB output.
    """
    return list(CONSULT_REGISTRY)


def oracle_available() -> bool:
    """True iff the Beta maṣāḥǝft Ge'ez XML is present in the local
    reference workspace (outside the repo). Used for cross-validating
    our own OCR of Charles 1906 + Dillmann 1851.
    """
    return (BETAMASAHEFT_LOCAL / "LIT1340EnochE.xml").exists()


def is_available() -> bool:
    """True iff the Charles chapter OCR is present and parseable enough to inspect."""
    geez_dir = SOURCES_ROOT / "ethiopic" / "transcribed" / "charles_1906"
    return geez_dir.exists() and any(geez_dir.glob("ch*.txt"))


def dillmann_is_available() -> bool:
    """True iff the Dillmann 1851 OCR is present."""
    dillmann_dir = SOURCES_ROOT / "ethiopic" / "transcribed" / "dillmann_1851"
    return dillmann_dir.exists() and any(dillmann_dir.glob("ch*.txt"))


def load_greek_edition_control(chapter: int, verse: int) -> Optional[EnochWitnessReading]:
    """Load only an explicit checked edition record; never infer text from OCR.

    Absence is normal. A present but invalid record is an error, not an excuse
    to silently drop the control or recalculate a missing provenance pin. The
    PDF hash identifies the checked private source; only the vendored raw OCR
    and text hashes can be revalidated by this loader.
    """
    record_path = SOURCES_ROOT / "greek/verified/flemming_1901" / f"{chapter:03d}" / f"{verse:03d}.json"
    if not record_path.exists():
        return None
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if not isinstance(record, dict):
            raise ValueError("record must be an object")
        if type(record.get("schema_version")) is not int or record["schema_version"] != 1:
            raise ValueError("unsupported schema_version")
        for key, expected in (("chapter", chapter), ("verse", verse)):
            if type(record.get(key)) is not int or record[key] != expected:
                raise ValueError(f"mismatched {key}")
        if record.get("reference") != f"1 Enoch {chapter}:{verse}":
            raise ValueError("mismatched reference")
        if record.get("reading_basis") != "published-edition-selected-text":
            raise ValueError("control is not a published-edition selected text")
        edition = record.get("edition")
        text = record.get("text")
        if edition != "Flemming–Radermacher 1901":
            raise ValueError("edition must identify the Flemming–Radermacher 1901 control")
        if not isinstance(text, str) or not text.strip() or not re.search(r"[\u0370-\u03ff\u1f00-\u1fff]", text):
            raise ValueError("nonempty Greek text is required")
        for digest in (record["text_sha256"], record["raw_ocr"]["sha256"], record["pdf"]["sha256"]):
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError("explicit SHA-256 pins are required")
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != record["text_sha256"]:
            raise ValueError("Greek text hash mismatch")
        raw_relative = pathlib.Path(record["raw_ocr"]["repo_path"])
        raw_path = (REPO_ROOT / raw_relative).resolve()
        raw_root = (SOURCES_ROOT / "greek/transcribed").resolve()
        if raw_relative.is_absolute() or not raw_path.is_relative_to(raw_root) or raw_path.suffix != ".txt":
            raise ValueError("raw OCR path must be inside the Greek transcription directory")
        if hashlib.sha256(raw_path.read_bytes()).hexdigest() != record["raw_ocr"]["sha256"]:
            raise ValueError("raw OCR hash mismatch")
        pdf = record["pdf"]
        if not isinstance(pdf["url"], str) or not pdf["url"].startswith("https://"):
            raise ValueError("PDF source URL is required")
        for page_key in ("page", "printed_page"):
            if type(pdf[page_key]) is not int or pdf[page_key] < 1:
                raise ValueError("positive PDF and printed page locators are required")
        limits = record["limits"]
        if not isinstance(limits, list) or not limits or any(not isinstance(item, str) or not item.strip() for item in limits):
            raise ValueError("explicit control limits are required")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise ValueError(f"Invalid Greek edition control {record_path}: {exc}") from exc

    return EnochWitnessReading(
        language="greek",
        witness="flemming_1901_edition_control",
        text=text,
        source_edition=edition,
        confidence="medium",
        note=(
            "Edited comparative control, not a diplomatic manuscript reading or primary Ge'ez/source promotion. "
            f"Record: {record_path.relative_to(REPO_ROOT)}; reading basis: {record['reading_basis']}; "
            f"text SHA-256: {record['text_sha256']}; raw OCR: {record['raw_ocr']['repo_path']} "
            f"(SHA-256 {record['raw_ocr']['sha256']}); PDF {pdf['url']} "
            f"(SHA-256 {pdf['sha256']}), PDF page {pdf['page']}, printed page {pdf['printed_page']}. "
            + " ".join(limits)
        ),
    )


def load_verse(chapter: int, verse: int) -> Optional[EnochVerseWitnessSet]:
    """Return the currently available witness bundle for one verse.

    Loads all available Zone 1 Ge'ez witnesses:
      - Charles 1906 (primary) via verse_parser.py
      - Dillmann 1851 (secondary cross-check) via dillmann_verse_parser.py
    """
    if not is_available():
        return None

    row, _warnings = verse_parser.load_verse(chapter, verse)
    if row is None:
        return None

    witness_set = EnochVerseWitnessSet(
        chapter=chapter,
        verse=verse,
        geez_charles=EnochWitnessReading(
            language="geez",
            witness="charles_1906",
            text=row.text,
            source_edition="Charles 1906 Ethiopic Enoch",
            confidence="medium",
            note=f"Recovered from {row.chapter_file} via tools/enoch/verse_parser.py",
        ),
    )

    if dillmann_is_available():
        d_row, d_warnings = dillmann_verse_parser.load_verse(chapter, verse)
        if d_row is not None:
            witness_set.geez_dillmann = EnochWitnessReading(
                language="geez",
                witness="dillmann_1851",
                text=d_row.text,
                source_edition="Dillmann 1851 Ethiopic Enoch (Lipsiae, Vogel)",
                confidence="medium",
                note=(
                    f"Recovered from {d_row.chapter_file} via tools/enoch/dillmann_verse_parser.py"
                    + (f"; parser warnings: {'; '.join(d_warnings)}" if d_warnings else "")
                ),
            )

    witness_set.greek_edition_control = load_greek_edition_control(chapter, verse)
    return witness_set


def summary() -> dict:
    """Diagnostic summary of what's loadable."""
    out = {
        "pipeline": "enoch_multi_witness",
        "status": "charles_primary_dillmann_secondary",
        "geez_ocr_complete": is_available(),
        "dillmann_ocr_available": dillmann_is_available(),
        "betamasaheft_oracle_available_locally": oracle_available(),
        "greek_ocr_present": any((SOURCES_ROOT / "greek/transcribed").rglob("*.txt")),
        "greek_ocr_complete": None,  # Presence is not verified coverage/completeness.
        "greek_edition_controls_present": any((SOURCES_ROOT / "greek/verified").rglob("*.json")),
        "zone_2_consult_count": len(CONSULT_REGISTRY),
    }
    return out


if __name__ == "__main__":
    import pprint
    print("=== 1 Enoch multi-witness scaffold ===")
    pprint.pp(summary())
    print("\n=== Zone 2 consult registry ===")
    for c in consult_sources():
        print(f"  - {c['name']} ({c['year']})")
        print(f"      coverage: {c['coverage_chapters']}")
        print(f"      role: {c['role'][:100]}")
