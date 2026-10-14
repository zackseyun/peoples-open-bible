"""Audit published QSD masks; never infer letters or rewrite source images.

Requires NumPy and Pillow. Downloads commit-pinned reference/prediction masks
to an external cache and writes a numeric report. This does not run MTEM.
"""

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

import numpy as np
from PIL import Image


REPO = "TAU-CH/qumran_segmentation_of_ink_and_parchment_in_dead_sea_scroll_fragments"
COMMIT = "22e09c6219b16dafdf3a943fb18df774f7e3e8e8"
DATA = "qumran_segmentation_dataset"
RESULTS = "msem_results"
METRICS = ("precision", "recall", "iou", "f1")


def fetch(url):
    with urlopen(url, timeout=60) as response:
        payload = response.read(32 * 1024 * 1024 + 1)
    if len(payload) > 32 * 1024 * 1024:
        raise ValueError("Acquisition exceeds 32 MiB per-file limit")
    return payload


def scores(counts, undefined=None):
    tp, fp, fn = (counts[k] for k in ("tp", "fp", "fn"))

    def ratio(a, b):
        return a / b if b else undefined

    return dict(zip(METRICS, (ratio(tp, tp + fp), ratio(tp, tp + fn),
                              ratio(tp, tp + fp + fn), ratio(2 * tp, 2 * tp + fp + fn))))


def compare(truth, prediction):
    if truth.shape != prediction.shape:
        raise ValueError("Reference and prediction dimensions differ")
    return {"tp": int(np.count_nonzero(truth & prediction)),
            "fp": int(np.count_nonzero(~truth & prediction)),
            "fn": int(np.count_nonzero(truth & ~prediction)),
            "tn": int(np.count_nonzero(~truth & ~prediction))}


def mean(values):
    selected = [x for x in values if x is not None]
    return sum(selected) / len(selected) if selected else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    tree_url = f"https://api.github.com/repos/{REPO}/git/trees/{COMMIT}?recursive=1"
    tree = json.loads(fetch(tree_url))
    if tree.get("truncated") or tree.get("sha") != COMMIT:
        raise ValueError("Incomplete or unpinned upstream tree")
    entries = {entry["path"]: entry for entry in tree["tree"] if entry["type"] == "blob"}
    names = sorted(Path(path).name for path in entries
                   if path.startswith(f"{DATA}/ink_masks/") and path.endswith(".png"))
    if len(names) != 20:
        raise ValueError(f"Expected 20 reference fragments, got {len(names)}")
    acquired = {}

    def read_mask(path):
        entry = entries[path]
        local = args.cache / path
        if not local.exists():
            payload = fetch(f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{path}")
        else:
            payload = local.read_bytes()
        identity = hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()
        if identity != entry["sha"] or len(payload) != entry["size"]:
            raise ValueError(f"Upstream blob mismatch: {path}")
        if not local.exists():
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(payload)
        with Image.open(local) as im:
            im.load()
            if im.mode != "L":
                raise ValueError(f"Expected grayscale mask: {path} ({im.mode})")
            pixels = np.asarray(im)
            values = np.unique(pixels).tolist()
            if not set(values) <= {0, 255}:
                raise ValueError(f"Nonbinary mask: {path}: {values}")
            shape = list(pixels.shape)
            binary = pixels > 127
        acquired[path] = {"bytes": len(payload), "git_blob_sha1": identity,
                          "sha256": hashlib.sha256(payload).hexdigest(),
                          "shape_hw": shape, "values": values}
        return binary

    methods = {"mtem_ink": ("ink_masks", "ink_masks"),
               "mtem_parchment": ("parchment_masks", "parchment_masks"),
               "otsu_parchment": ("parchment_masks", "otsu_masks")}
    rows = []
    for name in names:
        ink = read_mask(f"{DATA}/ink_masks/{name}")
        parchment = read_mask(f"{DATA}/parchment_masks/{name}")
        for method, (reference_dir, prediction_dir) in methods.items():
            truth = ink if reference_dir == "ink_masks" else parchment
            prediction = read_mask(f"{RESULTS}/{prediction_dir}/{name}")
            counts = compare(truth, prediction)
            rows.append({"fragment": name[:-4], "method": method,
                         "shape_hw": list(truth.shape), **counts,
                         "reference_positive_pixels": int(truth.sum()),
                         "predicted_positive_pixels": int(prediction.sum()),
                         **scores(counts)})
        print(f"Checked {name}", flush=True)

    summaries = {}
    for method in methods:
        selected = [r for r in rows if r["method"] == method]
        totals = {k: sum(r[k] for r in selected) for k in ("tp", "fp", "fn", "tn")}
        nonempty = [r for r in selected if r["tp"] + r["fp"] + r["fn"] > 0]
        paper_scores = [scores(r, undefined=0.0) for r in nonempty]
        summaries[method] = {
            "fragments": len(selected), "pooled_counts": totals,
            "pooled_metrics": scores(totals),
            "macro_metrics_excluding_undefined": {m: mean([r[m] for r in selected]) for m in METRICS},
            "macro_defined_counts": {m: sum(r[m] is not None for r in selected) for m in METRICS},
            "upstream_averaging_fragments": len(nonempty),
            "upstream_averaging_metrics": {m: mean([r[m] for r in paper_scores]) for m in METRICS},
            "empty_reference_fragments": [r["fragment"] for r in selected if not r["reference_positive_pixels"]],
            "empty_pair_fragments": [r["fragment"] for r in selected if not r["reference_positive_pixels"] and not r["predicted_positive_pixels"]],
        }
    report = {"schema_version": "1.0.0", "upstream_repository": REPO,
              "upstream_commit": COMMIT,
              "experiment": "released-prediction metric reproduction",
              "fresh_inference_executed": False, "character_recognition_executed": False,
              "new_manuscript_reading": False, "canonical_change": False,
              "runtime": {"numpy": np.__version__, "pillow": Image.__version__},
              "tool_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "summaries": summaries, "rows": rows, "acquired_files": acquired}
    output = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output.exists() and args.output.read_text() != output:
        raise ValueError("Refusing to overwrite a differing result; choose a new output")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output)
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
