"""Deterministic 57r JPEG spectral pilot, not a transcription or restoration.

Requires NumPy, Pillow and OpenCV. No verse text, generative model, inpainting,
deconvolution or sharpening is used. Inputs are verified and never overwritten.
The fixed geometry applies only to the public 1533 x 2044 folio 57r JPEGs.
"""

import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROI = (280, 200, 1260, 1800)
REFERENCE = "00057-R+MB530GN_005.jpg"


def features(a, detector):
    lo, hi = np.percentile(a[200:1800, 280:1260], [1, 99])
    if hi <= lo:
        return [], None
    norm = np.clip((a.astype(np.float32) - lo) * 255 / (hi - lo), 0, 255).astype(np.uint8)
    small = cv2.resize(norm, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    mask = np.zeros(small.shape, np.uint8)
    mask[100:900, 140:630] = 255
    keypoints, descriptors = detector.detectAndCompute(small, mask)
    return np.float32([np.array(k.pt) * 2 for k in keypoints]), descriptors


def fit(km, dm, kr, dr):
    if dm is None or dr is None:
        return None, {"passed": False, "reason": "no_descriptors"}
    pairs = cv2.BFMatcher().knnMatch(dm, dr, k=2)
    matches = sorted([a for pair in pairs if len(pair) == 2 for a, b in [pair]
                      if a.distance < 0.7 * b.distance], key=lambda m: m.queryIdx)
    if len(matches) < 40:
        return None, {"passed": False, "reason": "fewer_than_40_matches", "matches": len(matches)}
    src = np.float32([km[m.queryIdx] for m in matches])
    dst = np.float32([kr[m.trainIdx] for m in matches])
    matrix, inliers = cv2.estimateAffinePartial2D(src[::2].copy(), dst[::2].copy(),
        method=cv2.RANSAC, ransacReprojThreshold=2, maxIters=5000, confidence=0.999)
    if matrix is None:
        return None, {"passed": False, "reason": "fit_failed", "matches": len(matches)}
    errors = np.linalg.norm(src[1::2] @ matrix[:, :2].T + matrix[:, 2] - dst[1::2], axis=1)
    scale = float(np.hypot(matrix[0, 0], matrix[1, 0]))
    rotation = float(np.degrees(np.arctan2(matrix[1, 0], matrix[0, 0])))
    cells = len({(int(x // 245), int(y // 400)) for x, y in src[1::2]})
    passed = (np.median(errors) <= 1.5 and np.percentile(errors, 95) <= 3
              and 0.98 <= scale <= 1.02 and abs(rotation) <= 1
              and max(abs(matrix[:, 2])) <= 10 and cells >= 6)
    result = {"passed": bool(passed), "matches": len(matches), "fit_inliers": int(inliers.sum()),
              "held_out_matches": len(errors), "median_error_px": float(np.median(errors)),
              "p95_error_px": float(np.percentile(errors, 95)), "spatial_cells": cells,
              "scale": scale, "rotation_degrees": rotation, "matrix": matrix.tolist()}
    return matrix if passed else None, result


def read_verified(source, row):
    name = row["local_file"]
    if Path(name).name != name or not name.endswith(".jpg"):
        raise ValueError("Expected a local JPEG basename")
    path = source / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
        raise ValueError(f"Input hash mismatch: {name}")
    with Image.open(path) as image:
        if image.size != (1533, 2044) or image.mode != "L":
            raise ValueError("Expected the 1533 x 2044 grayscale derivatives")
        return np.asarray(image).copy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    source, out = args.source_dir, args.output_dir
    receipt_path = source / "receipt.json"
    receipt = json.loads(receipt_path.read_text())
    rows = receipt["member_payloads_verified"]
    names = [row["archive_member"] for row in rows]
    if (len(rows) != 51 or len(set(names)) != 51
            or any(not name.startswith("00057-R/00057-R+") for name in names)
            or len({row["local_file"] for row in rows}) != 51):
        raise ValueError("Expected 51 distinct exposures for modern folio 57r")
    selected = [row for row in rows if "+MB" in row["archive_member"] or "+W" in row["archive_member"]]
    if len(selected) != 42:
        raise ValueError("Expected the 42 prespecified MB/W exposures")
    reference_row = next(row for row in selected if row["archive_member"] == "00057-R/" + REFERENCE)
    reference = read_verified(source, reference_row)
    out.mkdir(exist_ok=False)
    cv2.setRNGSeed(1729)
    cv2.setNumThreads(1)
    detector = cv2.SIFT_create(nfeatures=4000)
    kr, dr = features(reference, detector)
    report = {"source_receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "selection": "All MB and W filename families; Aux, RL, RR, TX excluded before fitting",
              "alignment_detection_scale": 0.5, "alignment_errors_in_original_pixels": True,
              "thresholds": {"min_matches": 40, "median_px": 1.5, "p95_px": 3,
                  "scale_min": 0.98, "scale_max": 1.02, "abs_rotation_deg": 1,
                  "abs_translation_px": 10, "min_spatial_cells": 6},
              "roi_xyxy": list(ROI), "reference": REFERENCE, "alignment": [], "channels": [], "views": [],
              "text_input": False, "generative_processing": False, "transcription_performed": False,
              "versions": {"opencv": cv2.__version__, "numpy": np.__version__, "pillow": Image.__version__},
              "limitation": "Feature-level holdout errors are not letter-level validation; SIFT orientation duplicates are not independent physical controls."}
    bands = []
    for row in selected:
        a = read_verified(source, row)
        if row is reference_row:
            transformed = a.astype(np.float32)
            result = {"passed": True, "reference": True}
        else:
            km, dm = features(a, detector)
            matrix, result = fit(km, dm, kr, dr)
            transformed = None if matrix is None else cv2.warpAffine(a.astype(np.float32), matrix,
                (a.shape[1], a.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        result["member"] = row["archive_member"]
        report["alignment"].append(result)
        if transformed is not None:
            bands.append(transformed[200:1800, 280:1260])
            report["channels"].append(row)
        print(row["local_file"], result["passed"], flush=True)
    if len(bands) < 3:
        raise ValueError("Insufficient accepted bands")
    cube = np.stack(bands, axis=-1)
    sample = cube[::8, ::8].reshape(-1, len(bands)).astype(np.float64)
    mean, std = sample.mean(axis=0), sample.std(axis=0)
    if np.any(std < 1e-6):
        raise ValueError("Uninformative band")
    values, vectors = np.linalg.eigh(np.cov((sample - mean) / std, rowvar=False))
    order = np.argsort(values)[::-1]
    values, vectors = values[order], vectors[:, order]
    report.update({"sample_pixels": len(sample), "means": mean.tolist(), "std": std.tolist(),
                   "variance_fractions": (values / values.sum()).tolist()})
    sheet = Image.new("RGB", (6 * 320, ((len(bands) + 5) // 6) * 220), "white")
    draw = ImageDraw.Draw(sheet)
    for i in range(len(bands)):
        if vectors[np.argmax(abs(vectors[:, i])), i] < 0:
            vectors[:, i] *= -1
        weights = vectors[:, i] / std
        score = cube @ weights - mean @ weights
        lo, hi = np.percentile(score, [1, 99])
        view = np.clip((score - lo) / max(hi - lo, 1e-9) * 255, 0, 255).astype(np.uint8)
        image = Image.fromarray(np.rot90(view))
        path = out / f"pc-{i + 1:02d}.png"
        image.save(path)
        report["views"].append({"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                "display_limits": [float(lo), float(hi)]})
        image.thumbnail((320, 196))
        x, y = (i % 6) * 320, (i // 6) * 220
        sheet.paste(image, (x, y + 20))
        draw.text((x + 4, y + 3), f"PC {i + 1}: {values[i] / values.sum():.4f}", fill="black")
    sheet.save(out / "contact-sheet.png")
    report["weights_columns"] = vectors.tolist()
    (out / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(f"PCA completed with {len(bands)} of {len(selected)} prespecified candidate exposures", flush=True)


if __name__ == "__main__":
    main()
