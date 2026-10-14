"""Fixed geometric development check; no edited images or letter labels output.

Fit color-to-IR affine coordinates on tile column 2 and validate on column 3.
The matching features are not certified ink labels. This checks geometry only.
"""

import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text())
    assets = {r["filename"]: r for r in receipt["assets"]}
    cv2.setRNGSeed(1776)
    cv2.setNumThreads(1)
    sift = cv2.SIFT_create(nfeatures=2000, contrastThreshold=0.04)
    matcher = cv2.BFMatcher(cv2.NORM_L2)
    rows = []
    for x, y in ((2, 2), (3, 2), (2, 3), (3, 3)):
        inputs = []
        for kind in ("color", "ir"):
            name = f"4q122-{kind}-x{x}-y{y}-z3.jpg"
            path = args.cache / name
            if hashlib.sha256(path.read_bytes()).hexdigest() != assets[name]["sha256"]:
                raise ValueError("Source hash mismatch")
            gray = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            if gray is None or gray.shape != (512, 512):
                raise ValueError("Unexpected native tile dimensions")
            inputs.append(sift.detectAndCompute(gray, None))
        (ka, da), (kb, db) = inputs
        if da is None or db is None or len(db) < 2:
            continue
        reverse = {m.queryIdx: m.trainIdx for m in matcher.match(db, da)}
        for first, second in matcher.knnMatch(da, db, k=2):
            if first.distance < 0.7 * second.distance and reverse.get(first.trainIdx) == first.queryIdx:
                offset = np.array([512*x, 512*y])
                rows.append({"tile_xy": [x, y], "partition": "fit" if x == 2 else "validation",
                             "color_xy": (np.array(ka[first.queryIdx].pt) + offset).tolist(),
                             "ir_xy": (np.array(kb[first.trainIdx].pt) + offset).tolist(),
                             "descriptor_distance": float(first.distance)})
    fit = [r for r in rows if r["partition"] == "fit"]
    matrix = None
    if len(fit) >= 3:
        matrix, inliers = cv2.estimateAffine2D(
            np.array([r["color_xy"] for r in fit]), np.array([r["ir_xy"] for r in fit]),
            method=cv2.RANSAC, ransacReprojThreshold=3, maxIters=2000, confidence=0.99, refineIters=10)
    if matrix is not None and np.isfinite(matrix).all():
        for row, keep in zip(fit, inliers.ravel()):
            row["ransac_inlier"] = bool(keep)
        for row in rows:
            predicted = matrix @ np.array([*row["color_xy"], 1])
            row["residual_pixels"] = float(np.linalg.norm(predicted - row["ir_xy"]))
    else:
        matrix = None
    validation = [r for r in rows if r["partition"] == "validation"]
    near = sum(r.get("residual_pixels", float("inf")) <= 3 for r in validation)
    fraction = near / len(validation) if validation else None
    checks = {"finite_model": matrix is not None, "validation_count_at_least_25": len(validation) >= 25,
              "validation_fraction_within_3_at_least_90_percent": fraction is not None and fraction >= 0.9,
              "both_validation_tiles_represented": {tuple(r["tile_xy"]) for r in validation} == {(3, 2), (3, 3)}}
    report = {"schema": "pob.4q122_tile_correspondence.v1", "development_not_blind": True,
              "input_receipt_sha256": hashlib.sha256(args.receipt.read_bytes()).hexdigest(),
              "tool_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "runtime": {"opencv": cv2.__version__, "numpy": np.__version__, "threads_reported": cv2.getNumThreads()},
              "affine_color_to_ir": matrix.tolist() if matrix is not None else None,
              "fit_pairs": len(fit), "validation_pairs": len(validation),
              "validation_within_3_pixels": near, "validation_fraction_within_3": fraction,
              "gate": {"status": "pass" if all(checks.values()) else "fail", "checks": checks},
              "rows": rows, "images_written": False, "letter_labels_assigned": False,
              "canonical_change": False}
    raw = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output.exists() and args.output.read_text() != raw:
        raise ValueError("Refusing to overwrite differing correspondence result")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(raw)
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
