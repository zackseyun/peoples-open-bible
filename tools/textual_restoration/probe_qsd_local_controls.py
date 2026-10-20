"""Compare fixed QSD training coverage and local features without reading text.

Uses only existing hash-pinned cache files. Outputs numbers and prediction
digests, not restored images. This is development, not blind transcription.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from evaluate_qsd_release import COMMIT, DATA, RESULTS, METRICS, compare, mean, scores
from probe_qsd_spectral_classifier import features as raw_features


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_z(image, sigma=8.0, floor=1 / 1024, clip=8.0):
    unit = image.astype(np.float32) / 65535
    average = cv2.GaussianBlur(unit, (0, 0), sigma, borderType=cv2.BORDER_REFLECT_101)
    square = cv2.GaussianBlur(unit * unit, (0, 0), sigma, borderType=cv2.BORDER_REFLECT_101)
    deviation = np.sqrt(np.maximum(square - average * average, floor * floor))
    return np.clip((unit - average) / deviation, -clip, clip).astype(np.float32)


def selected_pixels(labels, seed, maximum=10000):
    rng = np.random.default_rng(seed)
    return np.concatenate([rng.choice(np.flatnonzero(labels == label),
                                     min(maximum, int(np.count_nonzero(labels == label))),
                                     replace=False) for label in range(3)])


def batch_features(first, last, selection, mode, normalized=None):
    raw = raw_features(first[selection], last[selection], True)
    if mode == "raw":
        return raw
    if mode != "local" or normalized is None:
        raise ValueError("Local features require measured-band neighborhood statistics")
    return np.column_stack((raw, normalized[0][selection], normalized[1][selection])).astype(np.float32)


def summarize(rows):
    totals = {key: sum(row[key] for row in rows) for key in ("tp", "fp", "fn", "tn")}
    positive = [row for row in rows if row["reference_positive_pixels"] > 0]
    return {"evaluation_fragments": len(rows), "pooled_counts": totals,
            "pooled_metrics": scores(totals),
            "macro_all_defined": {metric: mean([r[metric] for r in rows]) for metric in METRICS},
            "macro_all_defined_counts": {metric: sum(r[metric] is not None for r in rows) for metric in METRICS},
            "nonempty_reference_fragments": len(positive),
            "nonempty_reference_macro_f1": mean([r["f1"] for r in positive]),
            "empty_reference_false_positives": {r["fragment"]: r["fp"] for r in rows if not r["reference_positive_pixels"]}}


def development_screen(rows, reference_rows):
    result, reference = summarize(rows), summarize(reference_rows)
    difficult = next(row for row in rows if row["fragment"] == "124_008")
    difficult_reference = next(row for row in reference_rows if row["fragment"] == "124_008")
    precision = result["pooled_metrics"]["precision"]
    checks = {"pooled_precision": precision is not None and precision >= reference["pooled_metrics"]["precision"],
              "fixed_nonempty_macro_f1": result["nonempty_reference_macro_f1"] >= reference["nonempty_reference_macro_f1"],
              "difficult_fragment_f1": difficult["f1"] >= difficult_reference["f1"],
              "empty_controls": set(result["empty_reference_false_positives"]) == {"690_015", "690_016"}
              and not any(result["empty_reference_false_positives"].values())}
    return {"checks": checks, "passed": all(checks.values()), "transcription_deployment_authorized": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Choose a new output; existing results are not overwritten")
    folder = Path(__file__).resolve().parents[2] / "sources/textual_restoration/discovery"
    release_path = folder / "qsd_release_evaluation.2026-10-13.v1.json"
    prior_path = folder / "qsd_spectral_probe.2026-10-13.v1.json"
    protocol = json.loads(args.protocol.read_text())
    if (protocol["upstream_commit"] != COMMIT or digest(release_path) != protocol["release_report_sha256"]
            or digest(prior_path) != protocol["prior_probe_sha256"]):
        raise ValueError("Protocol input pins differ")
    release, prior = [json.loads(path.read_text()) for path in (release_path, prior_path)]
    verified = {}

    def read(path, pins):
        local = args.cache / path
        pin = pins[path]
        payload = local.read_bytes()
        if hashlib.sha256(payload).hexdigest() != pin["sha256"] or len(payload) != pin["bytes"]:
            raise ValueError(f"Changed cached source: {path}")
        with Image.open(local) as image:
            pixels = np.array(image)
        if list(pixels.shape) != pin["shape_hw"]:
            raise ValueError(f"Changed dimensions: {path}")
        verified[path] = pin
        return pixels

    def fragment(name):
        first, last = [read(f"{DATA}/multispectral_images/{name}_{band}.tif", prior["acquired_files"])
                       for band in ("001", "012")]
        ink, parchment = [read(f"{DATA}/{kind}_masks/{name}.png", prior["acquired_files"])
                           for kind in ("ink", "parchment")]
        if (first.dtype != np.uint16 or last.dtype != np.uint16 or first.ndim != 2
                or not first.shape == last.shape == ink.shape == parchment.shape
                or not set(np.unique(ink)) <= {0, 255} or not set(np.unique(parchment)) <= {0, 255}):
            raise ValueError(f"Invalid measured bands or masks: {name}")
        labels = (parchment > 127).astype(np.int32)
        labels[ink > 127] = 2
        normalized = tuple(local_z(image, protocol["local_sigma_pixels"], protocol["local_std_floor"],
                                   protocol["local_z_clip"]).ravel() for image in (first, last))
        return first.astype(np.float32).ravel(), last.astype(np.float32).ravel(), labels.ravel(), normalized

    cv2.setNumThreads(1)
    training = {}
    for index, name in enumerate(protocol["training_regimes"]["diverse"]):
        first, last, labels, normalized = fragment(name)
        selected = selected_pixels(labels, protocol["seed"] + index,
                                   protocol["training_pixels_per_class_per_fragment_max"])
        training[name] = {"labels": labels[selected], "sample_sha256": hashlib.sha256(selected.astype("<i8").tobytes()).hexdigest(),
                          "features": {mode: batch_features(first, last, selected, mode, normalized)
                                       for mode in protocol["feature_modes"]}}
    models = {}
    for regime, names in protocol["training_regimes"].items():
        for mode in protocol["feature_modes"]:
            matrix = np.concatenate([training[name]["features"][mode] for name in names])
            labels = np.concatenate([training[name]["labels"] for name in names])
            cv2.setRNGSeed(protocol["seed"])
            model = cv2.ml.RTrees_create()
            model.setMaxDepth(protocol["max_depth"])
            model.setMinSampleCount(protocol["min_sample_count"])
            model.setRegressionAccuracy(0)
            model.setUseSurrogates(False)
            model.setMaxCategories(3)
            model.setActiveVarCount(protocol["active_variables"])
            model.setTermCriteria((cv2.TERM_CRITERIA_MAX_ITER, protocol["trees"], 0))
            if not model.train(matrix, cv2.ml.ROW_SAMPLE, labels):
                raise RuntimeError("Training failed")
            models[f"{regime}_{mode}"] = (model, mode)
            print(f"Trained {regime}_{mode}: {len(labels)} labeled pixels", flush=True)
    all_names = sorted(r["fragment"] for r in release["rows"] if r["method"] == "mtem_ink")
    if len(all_names) != 20 or len(set(all_names)) != 20:
        raise ValueError("Expected20 unique benchmark fragments")
    evaluation_names = [name for name in all_names if name not in training]
    if len(evaluation_names) != 18:
        raise ValueError("Expected18 common comparison fragments")
    rows, reference_rows = [], []
    for name in evaluation_names:
        first, last, labels, normalized = fragment(name)
        truth = labels == 2
        published = read(f"{RESULTS}/ink_masks/{name}.png", release["acquired_files"])
        reference_counts = compare(truth, (published > 127).ravel())
        reference_rows.append({"fragment": name, "reference_positive_pixels": int(truth.sum()),
                               **reference_counts, **scores(reference_counts)})
        for model_name, (model, mode) in models.items():
            counts = dict.fromkeys(("tp", "fp", "fn", "tn"), 0)
            prediction_digest = hashlib.sha256()
            for start in range(0, len(labels), protocol["prediction_batch_pixels"]):
                selected = slice(start, start + protocol["prediction_batch_pixels"])
                _, prediction = model.predict(batch_features(first, last, selected, mode, normalized))
                binary = prediction.ravel() == 2
                prediction_digest.update(binary.tobytes())
                batch = compare(truth[selected], binary)
                counts = {key: counts[key] + batch[key] for key in counts}
            rows.append({"fragment": name, "model": model_name, "reference_positive_pixels": int(truth.sum()),
                         "prediction_binary_sha256": prediction_digest.hexdigest(), **counts, **scores(counts)})
        print(f"Compared all pixels: {name}", flush=True)
    summaries = {name: summarize([r for r in rows if r["model"] == name]) for name in models}
    screens = {name: development_screen([r for r in rows if r["model"] == name], reference_rows) for name in models}
    baseline = [r for r in rows if r["model"] == "single_raw"]
    historical = {r["fragment"]: r for r in prior["rows"] if r["model"] == "two_band"}
    baseline_exact = all(all(r[key] == historical[r["fragment"]][key] for key in ("tp", "fp", "fn", "tn")) for r in baseline)
    for path, pin in verified.items():
        if digest(args.cache / path) != pin["sha256"]:
            raise ValueError(f"Source changed during processing: {path}")
    result = {"date_local": protocol["date_local"], "protocol": protocol, "protocol_sha256": digest(args.protocol),
              "tool_sha256": digest(Path(__file__)), "fresh_inference_executed": True,
              "blind_evaluation": False, "manuscript_disjoint_verified": False,
              "evaluation_fragments": evaluation_names, "evaluation_includes_training": False,
              "training_samples": {name: {"pixels": len(item["labels"]), "sample_sha256": item["sample_sha256"]} for name, item in training.items()},
              "reference_summary": summarize(reference_rows), "summaries": summaries, "development_screens": screens,
              "rows": rows, "reference_rows": reference_rows, "verified_inputs": verified,
              "all_input_hashes_unchanged_after_processing": True, "prior_raw_confusion_counts_exact": baseline_exact,
              "runtime": {"numpy": np.__version__, "opencv": cv2.__version__, "pillow": Image.__version__,
                          "threads_requested": 1, "threads_reported": cv2.getNumThreads()},
              "image_outputs_written": False, "new_characters_accepted": 0, "canonical_change": False,
              "transcription_deployment_authorized": False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"reference": result["reference_summary"], "summaries": summaries, "screens": screens,
                      "prior_raw_confusion_counts_exact": baseline_exact}, indent=2))


if __name__ == "__main__":
    main()
