"""Inventory published uncertainty; never promote supplied text to observed ink."""

import collections
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument("--work-dir", type=Path, required=True)
ROOT = parser.parse_args().work_dir
archive = ROOT / "codex-h-2105_data.zip"
with zipfile.ZipFile(archive) as bundle:
    assert bundle.namelist() == ["combined-xml.xml"]
    raw = bundle.read("combined-xml.xml")
root = ET.fromstring(raw)
events = []
context = {"folio": None, "line": 0, "verse": None}
counts = collections.Counter()
tags = collections.Counter()

def visit(element):
    tag = element.tag.rsplit("}", 1)[-1]
    tags[tag] += 1
    if tag == "pb":
        context.update(folio=element.get("n"), line=0, verse=None)
    elif tag == "lb":
        context["line"] += 1
    elif tag == "ab":
        context["verse"] = element.get("n")
    if tag in {"unclear", "supplied", "gap"}:
        counts[(context["folio"], tag)] += 1
        events.append({**context, "tag": tag, "attributes": dict(element.attrib),
                       "edition_text": "".join(element.itertext())})
    for child in element:
        visit(child)

visit(root)
report = {
    "source": "https://researchdata.gla.ac.uk/2105/1/2105_data.zip",
    "doi": "10.5525/gla.researchdata.2105",
    "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    "xml_sha256": hashlib.sha256(raw).hexdigest(),
    "status": "published edition inventory only; no new image reading",
    "warning": "Supplied text is editorial completion, not recovered ink. Line numbers count lb milestones after pb; verse context is the current ab milestone.",
    "tag_counts": dict(tags),
    "uncertainty_counts": [{"folio": folio, "tag": tag, "count": count}
                           for (folio, tag), count in counts.items()],
    "events": events,
}
output = ROOT / "codex-h-uncertainty-inventory.json"
output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({"output": str(output), "tag_counts": dict(tags),
                  "uncertainty_events": len(events)}, indent=2))
