"""Resolve explicit, code-pinned provisional OT selections for drafting only.

The immutable upstream remains the source for unregistered verses. Saved review
flags are checked for consistency, never used as independent authority: the
reviewed input bytes are bound by the index digest pinned in this module.
"""
from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET

import yaml
from jsonschema import Draft202012Validator

try:  # tools/draft.py is also an executable script with tools on sys.path.
    import wlc
except ModuleNotFoundError:
    from tools import wlc

ROOT = Path(__file__).resolve().parents[2]
INDEX = "sources/textual_restoration/selections/drafting_sources.2026-10-10.v1.json"
INDEX_SHA256 = "e4308ce3c076bb075a33d2c9e2eca8592cf6172677b796c5467a1d6008f0773e"
REGISTERED_IDS = frozenset({"ISA.9.2"})


class SelectedSourceError(ValueError):
    """A registered selection cannot be used safely; do not fall back silently."""


@dataclass(frozen=True)
class SelectedOTSource:
    verse: wlc.Verse
    source_payload: dict
    provenance: dict


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _read(root: Path, relative: str, expected: str | None = None) -> bytes:
    """Read a regular in-root path without accepting symlink substitutions."""
    parts = PurePosixPath(relative)
    if (parts.is_absolute() or ".." in parts.parts or str(parts) != relative
            or not parts.parts):
        raise SelectedSourceError(f"Unsafe selected-source path: {relative!r}")
    path = root
    for part in parts.parts:
        path = path / part
        if path.is_symlink():
            raise SelectedSourceError(f"Symlink selected-source input: {relative}")
    if not path.is_file() or not path.resolve().is_relative_to(root):
        raise SelectedSourceError(f"Missing or unsafe selected-source input: {relative}")
    raw = path.read_bytes()
    if expected is not None and _sha(raw) != expected:
        raise SelectedSourceError(f"Selected-source SHA256 drift: {relative}")
    return raw


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SelectedSourceError(message)


def resolve_selected_ot_source(verse, *, root: Path = ROOT) -> SelectedOTSource | None:
    """Copy one actual WLC verse using its explicitly reviewed qere Word.

    Unregistered/non-OT inputs return None. Registered inputs fail closed on
    drift. No Unicode/text normalization or generated reconstruction is used.
    Full canonical *source* equality is required; later English work is allowed.
    """
    if getattr(verse, "book_code", None) not in wlc.OT_BOOKS:
        return None
    verse_id = f"{verse.book_code}.{verse.chapter}.{verse.verse}"
    if verse_id not in REGISTERED_IDS:
        return None
    try:
        return _resolve(verse, Path(root).resolve(), verse_id)
    except SelectedSourceError:
        raise
    except (OSError, ValueError, KeyError, TypeError, AttributeError, ET.ParseError, yaml.YAMLError) as exc:
        raise SelectedSourceError(f"Invalid selected source for {verse_id}: {exc}") from exc


def _resolve(verse: wlc.Verse, root: Path, verse_id: str) -> SelectedOTSource:
    index = json.loads(_read(root, INDEX, INDEX_SHA256))
    _require(index["record_version"] == 1
             and index["status"] == "provisional-drafting-only"
             and index["publication_approved"] is False
             and set(index["entries"]) == REGISTERED_IDS, "Invalid pinned selection index")
    entry = index["entries"][verse_id]
    _require(entry["id"] == verse_id
             and entry["target"] == "translation/ot/isaiah/009/002.yaml"
             and entry["wlc"] == "sources/ot/wlc/Isa.xml", "Selected source identity mismatch")
    candidate = json.loads(_read(root, entry["candidate"], entry["candidate_sha256"]))
    receipt = json.loads(_read(root, entry["receipt"], entry["receipt_sha256"]))
    schema = json.loads(_read(root, entry["schema"], entry["schema_sha256"]))
    validation_errors = list(Draft202012Validator(schema).iter_errors(candidate))
    _require(not validation_errors, "Pinned selected-source candidate fails verse schema")
    _require(candidate["id"] == verse_id and candidate["reference"] == verse.reference
             and receipt["target"] == entry["target"]
             and receipt["candidate"] == entry["candidate"]
             and receipt["candidate_sha256"] == entry["candidate_sha256"]
             and receipt["review"]["candidate_sha256"] == entry["candidate_sha256"],
             "Candidate/application/review binding mismatch")
    _require(receipt["review"]["verdict"].startswith("PASS for exact full-record provisional")
             and receipt["application"]["candidate_matches"] is True
             and receipt["application"]["schema_valid"] is True
             and receipt["preflight"]["source_operation_verified"] is True
             and receipt["decision"]["source_changed"] is True
             and receipt["decision"]["upstream_wlc_changed"] is False
             and receipt["decision"]["publication_approved"] is False
             and receipt["decision"]["source_interpretation_settled"] is False
             and receipt["decision"]["novel_reading_demonstrated"] is False
             and receipt["decision"]["canon_changed"] is False,
             "Pinned receipt does not describe the reviewed provisional application")
    canonical_raw = _read(root, entry["target"])
    canonical = yaml.safe_load(canonical_raw)
    _require(canonical["id"] == verse_id and canonical["reference"] == candidate["reference"]
             and canonical["source"] == candidate["source"], "Canonical selected source drift")

    # Freshly parse the pinned bytes; a cached WLC tree is not fresh evidence.
    xml_raw = _read(root, entry["wlc"], entry["wlc_sha256"])
    xml_root = ET.fromstring(xml_raw)
    operation = entry["operation"]
    nodes = xml_root.findall(f".//o:verse[@osisID='{operation['osis_id']}']", wlc.OSIS_NS)
    _require(len(nodes) == 1, "Expected one pinned WLC verse")
    node = nodes[0]
    actual_words = []
    actual_punctuation = []
    for child in node:
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "w":
            text, annotations = wlc.word_text(child)
            actual_words.append(wlc.Word(text, child.attrib.get("lemma", ""),
                                         child.attrib.get("morph", ""),
                                         child.attrib.get("id", ""), annotations))
        elif tag == "seg" and (child.text or "").strip():
            actual_punctuation.append(child.text.strip())
    actual = wlc.Verse(verse.book_code, verse.chapter, verse.verse,
                       actual_words, actual_punctuation)
    _require(asdict(verse) == asdict(actual),
             "Incoming raw WLC Verse differs from pinned XML (including morphology)")
    _require(verse.hebrew_text == receipt["baseline_source"]["text"],
             "Incoming raw source differs from application baseline")
    written_nodes = node.findall(f"o:w[@id='{operation['written_word_id']}']", wlc.OSIS_NS)
    qere_nodes = node.findall("o:note[@type='variant']/o:rdg[@type='x-qere']/o:w", wlc.OSIS_NS)
    qere_nodes = [word for word in qere_nodes if word.attrib.get("id") == operation["qere_word_id"]]
    _require(len(written_nodes) == len(qere_nodes) == 1
             and written_nodes[0].attrib.get("type") == "x-ketiv"
             and wlc.word_text(written_nodes[0])[0] == operation["written_text"]
             and wlc.word_text(qere_nodes[0])[0] == operation["qere_text"],
             "Recorded written/qere operation mismatch")
    written_pos = list(node).index(written_nodes[0])
    _require(written_pos + 1 < len(node)
             and qere_nodes[0] in list(node)[written_pos + 1].iter(),
             "Qere is not the recorded adjacent written-word variant")
    qere = qere_nodes[0]
    qere_text, qere_annotations = wlc.word_text(qere)
    _require(qere.attrib.get("lemma") == "l" and qere.attrib.get("morph") == "HR/Sp3ms",
             "Qere morphology mismatch")
    selected = copy.deepcopy(verse)
    positions = [i for i, word in enumerate(selected.words)
                 if word.word_id == operation["written_word_id"]]
    _require(len(positions) == 1, "Expected one written-word replacement")
    selected.words[positions[0]] = type(verse.words[positions[0]])(qere_text, qere.attrib["lemma"],
                                           qere.attrib["morph"], qere.attrib["id"],
                                           copy.deepcopy(qere_annotations))
    _require(selected.hebrew_text == candidate["source"]["text"]
             and selected.punctuation == verse.punctuation
             and sum(a != b for a, b in zip(selected.words, verse.words)) == 1,
             "Selected source is not exactly one recorded WLC operation")
    pins = {INDEX: INDEX_SHA256, entry["target"]: _sha(canonical_raw)}
    pins.update({entry[name]: entry[f"{name}_sha256"]
                 for name in ("candidate", "receipt", "wlc", "schema")})
    provenance = {
        "selection_id": verse_id,
        "selection_index": INDEX,
        "selection_index_sha256": INDEX_SHA256,
        "pinned_inputs": pins,
        "operation": copy.deepcopy(operation),
        "raw_text_sha256": _sha(verse.hebrew_text.encode("utf-8")),
        "selected_text_sha256": _sha(selected.hebrew_text.encode("utf-8")),
        "selection_status": "provisional",
        "candidate_only": True,
        "publication_approved": False,
        "source_interpretation_settled": False,
        "upstream_wlc_changed": False,
        "scope": "Pinned reviewed source used in drafting; no new adjudication or publication approval.",
    }
    return SelectedOTSource(selected, copy.deepcopy(candidate["source"]), provenance)
