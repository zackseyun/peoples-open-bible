"""Acquire a bounded region of the published, zero-overlap DZI pyramid."""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("--folio", choices=["2v", "3r", "40v", "41r"], default="3r")
parser.add_argument("--work-dir", type=Path, required=True)
parser.add_argument("--level", type=int, required=True)
parser.add_argument("--box", type=int, nargs=4)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
root = args.work_dir
descriptor = (root / f"codex-h-{args.folio}.dzi").read_bytes()
node = ET.fromstring(descriptor)
size = node.find("{http://schemas.microsoft.com/deepzoom/2008}Size")
width, height = int(size.get("Width")), int(size.get("Height"))
tile_size = int(node.get("TileSize"))
assert node.get("Overlap") == "0" and node.get("Format") == "jpeg"
max_level = math.ceil(math.log2(max(width, height)))
assert 0 <= args.level <= max_level
divisor = 2 ** (max_level - args.level)
width, height = math.ceil(width / divisor), math.ceil(height / divisor)
x0, y0, x1, y1 = args.box or [0, 0, width, height]
assert 0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height
args.output.mkdir(parents=True, exist_ok=False)
result = Image.new("RGB", (x1 - x0, y1 - y0))
receipt = {"descriptor_url": f"https://codexh.arts.gla.ac.uk/data/G015-Images/{args.folio}/{args.folio}.dzi",
           "descriptor_sha256": hashlib.sha256(descriptor).hexdigest(),
           "level": args.level, "level_dimensions": [width, height],
           "box": [x0, y0, x1, y1], "tiles": [],
           "operation": "Decoded JPEG tiles pasted at integer offsets; no resampling or enhancement.",
           "evidence": "Published processed composite, not raw spectral measurements."}
for row in range(y0 // tile_size, (y1 - 1) // tile_size + 1):
    for col in range(x0 // tile_size, (x1 - 1) // tile_size + 1):
        name = f"{col}_{row}.jpeg"
        url = f"https://codexh.arts.gla.ac.uk/data/G015-Images/{args.folio}/{args.folio}_files/{args.level}/{name}"
        with urllib.request.urlopen(url, timeout=60) as response:
            assert response.status == 200
            data = response.read()
        tile = Image.open(io.BytesIO(data))
        tile.load()
        expected = (min(tile_size, width-col*tile_size), min(tile_size, height-row*tile_size))
        assert tile.size == expected, (name, tile.size, expected)
        (args.output / name).write_bytes(data)
        result.paste(tile.convert("RGB"), (col*tile_size-x0, row*tile_size-y0))
        receipt["tiles"].append({"url": url, "bytes": len(data),
                                  "sha256": hashlib.sha256(data).hexdigest(),
                                  "size": list(tile.size)})
        print(name, flush=True)
output = args.output / "assembled.png"
result.save(output)
receipt["assembled_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
(args.output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(output)
