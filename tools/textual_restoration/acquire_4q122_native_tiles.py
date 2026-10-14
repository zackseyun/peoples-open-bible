"""Acquire public native-level target tiles without editing manuscript images.

Only the four tiles enclosing the previously identified hole-adjacent region
are acquired per exposure. This is not an entire-pyramid download.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

from PIL import Image

SOURCES = {
    "color": ("B-472934", "K9ldJlHoQqMl7tDDYBNWPnaBvVxfl9yP7KSs_7Gav_rrAlUe9w-2mIxQ"),
    "ir": ("B-472935", "luDzEyC1jGo9z5gjNnYMHqurI7qETRHsOzUTT1CPb3RYbrbcBI3iBaPP"),
}
COORDINATES = ((2, 2), (3, 2), (2, 3), (3, 3))


def inspect_pyramid(payload):
    root = ET.fromstring(payload)
    if root.tag != "TileInfo" or root.get("origin") != "TOP_LEFT":
        raise ValueError("Unexpected image-pyramid format")
    levels = root.findall("pyramid_level")
    dimensions = [int(root.get(k)) for k in ("image_width", "image_height")]
    tile = [int(root.get(k)) for k in ("tile_width", "tile_height")]
    if dimensions != [3296, 3296] or tile != [512, 512] or len(levels) != 4:
        raise ValueError("Image-pyramid dimensions changed")
    if int(levels[3].get("inverse_scale")) != 1:
        raise ValueError("Target level is not native scale")
    if any(int(levels[3].get(k)) != 7 for k in ("num_tiles_x", "num_tiles_y")):
        raise ValueError("Unexpected native tile grid")
    return {"image_dimensions": dimensions, "tile_dimensions": tile,
            "native_level": 3, "native_inverse_scale": 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    assets = []

    def get(name, url):
        path = args.cache / name
        if path.exists():
            payload = path.read_bytes()
        else:
            with urllib.request.urlopen(url, timeout=60) as response:
                payload = response.read()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        row = {"filename": name, "url": url, "bytes": len(payload),
               "sha256": hashlib.sha256(payload).hexdigest()}
        assets.append(row)
        return payload, row

    pyramids = {}
    for kind, (record, token) in SOURCES.items():
        base = f"https://lh6.ggpht.com/{token}"
        raw, row = get(f"4q122-{kind}-tileinfo.xml", base + "=g")
        pyramids[kind] = {"record_url": f"https://www.deadseascrolls.org.il/explore-the-archive/image/{record}",
                          **inspect_pyramid(raw)}
        for x, y in COORDINATES:
            raw, row = get(f"4q122-{kind}-x{x}-y{y}-z3.jpg", f"{base}=x{x}-y{y}-z3")
            with Image.open(io.BytesIO(raw)) as image:
                image.load()
                if image.format != "JPEG" or image.size != (512, 512):
                    raise ValueError("Unexpected tile payload")
                row.update(dimensions=list(image.size), mode=image.mode)
            row.update(tile_xy=[x, y], pyramid_level=3,
                       source_rectangle_xywh=[512*x, 512*y, 512, 512])
    report = {"schema": "pob.4q122_native_tiles.v1", "status": "research-only",
              "tool_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "pyramids": pyramids, "assets": assets,
              "full_pyramids_acquired": False, "tiles_per_exposure": 4,
              "images_edited": False, "transcription_accepted": False,
              "canonical_change": False}
    raw = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output.exists() and args.output.read_text() != raw:
        raise ValueError("Refusing to replace different acquisition receipt")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(raw)
    print(json.dumps({"assets": len(assets), "bytes": sum(r["bytes"] for r in assets)}))


if __name__ == "__main__":
    main()
