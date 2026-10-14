"""Development-only spectral classifier; output numbers, never restored images.

Requires NumPy, Pillow and OpenCV. Run evaluate_qsd_release.py first. All model
settings are fixed in the dated research report. No Hebrew is read or supplied.
"""

import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from evaluate_qsd_release import COMMIT, DATA, REPO, METRICS, compare, fetch, mean, scores


def features(first, last, two_band):
    if two_band:
        return np.column_stack((first, last, last - first)).astype(np.float32) / 65535
    return last.astype(np.float32).reshape(-1, 1) / 65535


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--release-report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    release = json.loads(args.release_report.read_text())
    if release["upstream_commit"] != COMMIT:
        raise ValueError("Unexpected reference revision")
    tree = json.loads(fetch(f"https://api.github.com/repos/{REPO}/git/trees/{COMMIT}?recursive=1"))
    if tree.get("truncated") or tree.get("sha") != COMMIT:
        raise ValueError("Incomplete or unpinned tree")
    entries = {x["path"]: x for x in tree["tree"] if x["type"] == "blob"}
    names = sorted(r["fragment"] for r in release["rows"] if r["method"] == "mtem_ink")
    if len(names) != 20 or len(set(names)) != 20:
        raise ValueError("Expected all 20 unique fragments")
    acquired = {}

    def read(path):
        local = args.cache / path
        payload = local.read_bytes() if local.exists() else fetch(
            f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{path}")
        blob = hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()
        if blob != entries[path]["sha"] or len(payload) != entries[path]["size"]:
            raise ValueError(f"Blob mismatch: {path}")
        if not local.exists():
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(payload)
        with Image.open(local) as im:
            pixels = np.array(im)
        acquired[path] = {"sha256": hashlib.sha256(payload).hexdigest(),
                          "git_blob_sha1": blob, "bytes": len(payload),
                          "shape_hw": list(pixels.shape), "dtype": str(pixels.dtype)}
        return pixels

    def fragment(name):
        first = read(f"{DATA}/multispectral_images/{name}_001.tif")
        last = read(f"{DATA}/multispectral_images/{name}_012.tif")
        ink = read(f"{DATA}/ink_masks/{name}.png")
        parchment = read(f"{DATA}/parchment_masks/{name}.png")
        if first.dtype != np.uint16 or last.dtype != np.uint16:
            raise ValueError("Expected original 16-bit spectral data")
        if first.ndim != 2 or not (first.shape == last.shape == ink.shape == parchment.shape):
            raise ValueError("Mismatched image dimensions")
        if not set(np.unique(ink)) <= {0, 255} or not set(np.unique(parchment)) <= {0, 255}:
            raise ValueError("Invalid reference mask")
        labels = (parchment > 127).astype(np.int32)
        labels[ink > 127] = 2
        return first.reshape(-1).astype(np.float32), last.reshape(-1).astype(np.float32), labels.reshape(-1)

    first, last, labels = fragment("124_001")
    rng = np.random.default_rng(1776)
    selected = np.concatenate([rng.choice(np.flatnonzero(labels == k),
                                         min(10000, int((labels == k).sum())), replace=False)
                               for k in range(3)])
    models = {}
    cv2.setNumThreads(1)
    for name, two_band in (("last_band", False), ("two_band", True)):
        cv2.setRNGSeed(1776)
        model = cv2.ml.RTrees_create()
        model.setMaxDepth(12)
        model.setMinSampleCount(10)
        model.setRegressionAccuracy(0)
        model.setUseSurrogates(False)
        model.setMaxCategories(3)
        model.setActiveVarCount(2 if two_band else 1)
        model.setTermCriteria((cv2.TERM_CRITERIA_MAX_ITER, 100, 0))
        if not model.train(features(first[selected], last[selected], two_band),
                           cv2.ml.ROW_SAMPLE, labels[selected]):
            raise RuntimeError("Training failed")
        models[name] = (model, two_band)
    rows = []
    for fragment_name in names:
        first, last, labels = fragment(fragment_name)
        for model_name, (model, two_band) in models.items():
            counts = dict.fromkeys(("tp", "fp", "fn", "tn"), 0)
            for start in range(0, len(labels), 200000):
                end = start + 200000
                _, prediction = model.predict(features(first[start:end], last[start:end], two_band))
                batch = compare(labels[start:end] == 2, prediction.reshape(-1) == 2)
                counts = {k: counts[k] + batch[k] for k in counts}
            rows.append({"fragment": fragment_name, "model": model_name,
                         "used_for_training": fragment_name == "124_001",
                         **counts, **scores(counts)})
        print(f"Predicted {fragment_name}", flush=True)
    summaries = {}
    for name in models:
        selected_rows = [r for r in rows if r["model"] == name and not r["used_for_training"]]
        counts = {k: sum(r[k] for r in selected_rows) for k in ("tp", "fp", "fn", "tn")}
        summaries[name] = {"evaluation_fragments": len(selected_rows),
                           "pooled_counts": counts, "pooled_metrics": scores(counts),
                           "macro_metrics_excluding_undefined": {
                               m: mean([r[m] for r in selected_rows]) for m in METRICS},
                           "macro_defined_counts": {
                               m: sum(r[m] is not None for r in selected_rows) for m in METRICS}}
    report = {"schema_version": "1.0.0", "upstream_repository": REPO,
              "upstream_commit": COMMIT, "experiment": "spectral classifier development test",
              "training_fragment": "124_001", "training_pixels": len(selected),
              "seed": 1776, "trees": 100, "max_depth": 12, "min_sample_count": 10,
              "model_family": "OpenCV RTrees", "fresh_inference_executed": True,
              "blind_evaluation": False, "manuscript_disjoint_verified": False,
              "image_outputs_written": False, "new_manuscript_reading": False,
              "canonical_change": False,
              "runtime": {"numpy": np.__version__, "opencv": cv2.__version__,
                          "pillow": Image.__version__, "threads_requested": 1,
                          "threads_reported": cv2.getNumThreads()},
              "tool_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "release_report_sha256": hashlib.sha256(args.release_report.read_bytes()).hexdigest(),
              "summaries": summaries, "rows": rows, "acquired_files": acquired}
    output = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output.exists() and args.output.read_text() != output:
        raise ValueError("Refusing to overwrite differing results")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output)
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
