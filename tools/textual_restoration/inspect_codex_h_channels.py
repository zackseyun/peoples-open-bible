"""Fixed RGB channel views, with no fitted or expected-text information."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

p = argparse.ArgumentParser()
p.add_argument("source", type=Path)
p.add_argument("output", type=Path)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
rgb = np.asarray(Image.open(a.source).convert("RGB"), dtype=np.float64)
weights = {"R": [1, 0, 0], "G": [0, 1, 0], "B": [0, 0, 1],
           "R-G": [1, -1, 0], "R-B": [1, 0, -1], "G-B": [0, 1, -1]}
sheet = Image.new("RGB", (990, 948), "white")
draw = ImageDraw.Draw(sheet)
records = []
for i, (name, weight) in enumerate(weights.items()):
    values = rgb @ np.asarray(weight)
    lo, hi = np.percentile(values, [1, 99])
    assert hi > lo
    view = Image.fromarray(np.uint8(np.clip((values-lo)/(hi-lo)*255, 0, 255)))
    path = a.output / f"{name}.png"
    view.save(path)
    records.append({"name": name, "weights": weight, "limits": [lo, hi],
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    thumb = view.copy()
    thumb.thumbnail((330, 444))
    x, y = (i % 3)*330, (i // 3)*474
    draw.text((x+6, y+4), name, fill="black")
    sheet.paste(thumb, (x, y+25))
sheet.save(a.output / "contact.png")
(a.output / "receipt.json").write_text(json.dumps({
    "source_sha256": hashlib.sha256(a.source.read_bytes()).hexdigest(),
    "source_dimensions": [rgb.shape[1], rgb.shape[0]],
    "views": records,
    "warning": "RGB channels of a previously processed composite are not physical spectral bands; no new readings accepted.",
    "contact_sheet": "Thumbnails only; inspect individual PNGs for geometry."
}, indent=2)+"\n")
