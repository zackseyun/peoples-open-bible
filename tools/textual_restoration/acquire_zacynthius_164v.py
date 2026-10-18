"""Acquire public 164v spectral JPEGs in verified, bounded HTTP ranges.

Only the selected ZIP members are CRC/SHA-256 checked, not the whole archive.
No image processing is performed. Originals are never overwritten.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "dss" / "inspect_remote_zip.py"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("remotezip", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    out = args.output_dir
    out.mkdir(exist_ok=False)
    source = module.RangeSource("https://edata.bham.ac.uk/428/9/00161-00176.zip", 798881705)
    entries = module.index_archive(source)
    selected = [e for e in entries if e.filename.startswith("00164-V/") and not e.is_dir()]
    if len(selected) != 51 or len({e.filename for e in selected}) != 51:
        raise ValueError("Expected 51 unique exposure members")
    start = min(e.header_offset for e in selected)
    last = max(e.header_offset for e in selected)
    end = min(e.header_offset for e in entries if e.header_offset > last)
    chunk_size = 4 * 1024 * 1024
    payload = b"".join(source.read(offset, min(chunk_size, end - offset))
                       for offset in range(start, end, chunk_size))

    class CachedBlock:
        def read(self, offset, length):
            if offset < start or offset + length > end:
                raise ValueError("Member request outside verified range")
            return payload[offset - start:offset - start + length]

    rows = []
    for entry in selected:
        destination = out / Path(entry.filename).name
        digest = module.write_member(CachedBlock(), entry, destination)
        rows.append({"archive_member": entry.filename, "local_file": destination.name,
                     "bytes": entry.file_size, "crc32": f"{entry.CRC:08x}", "sha256": digest})
    receipt = {"url": source.url, "archive_bytes": source.size, "etag": source.etag,
               "http_ranges": source.receipts, "full_archive_hash_verified": False,
               "member_payloads_verified": rows, "total_payload_bytes": sum(r["bytes"] for r in rows),
               "extractor_sha256": hashlib.sha256(TOOL.read_bytes()).hexdigest(),
               "batch_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"CRC verified {len(rows)} exposures, {receipt['total_payload_bytes']} bytes.")


if __name__ == "__main__":
    main()
