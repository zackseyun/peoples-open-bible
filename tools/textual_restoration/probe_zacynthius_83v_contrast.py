"""Non-generative spectral regression on an already readable neighboring strip.

This estimates a linear contrast from measured bands, not letters. The training
target is a previously processed composite, so agreement is not independent
evidence of manuscript text. The uncertain strip never enters the regression.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

SOURCE_BOXES = {"selection_line1": [6000, 4720, 7000, 4900],
                "check_line3": [6000, 5260, 7000, 5480],
                "uncertain_line2_band": [2800, 4930, 7100, 5210]}
MATRIX = np.array([[-1.1432323313076673, -0.0002814655344116605, 2175.540214778326],
                   [0.0002814655344116605, -1.1432323313076673, 1371.7149669084126]])


def read_image(path, digest):
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError("Input hash mismatch")
    with Image.open(path) as image:
        return np.array(image)


def component_box(source_box):
    points = np.array([(x, y) for x in (source_box[0], source_box[2])
                       for y in (source_box[1], source_box[3])], dtype=np.float64)
    points = (points-[1000, 2000])*[2000/7000, 1286/4500]
    inverse = cv2.invertAffineTransform(MATRIX)
    points = points @ inverse[:, :2].T + inverse[:, 2] - [200, 273]
    return tuple(np.r_[np.floor(points.min(axis=0)).astype(int)-3,
                          np.ceil(points.max(axis=0)).astype(int)+3].tolist())


def fit_contrast(x, y, alpha=.1):
    x, y = np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64)
    if (x.ndim != 2 or y.ndim != 1 or len(x) != len(y) or len(x) <= x.shape[1]
            or not np.isfinite(x).all() or not np.isfinite(y).all()
            or not np.isfinite(alpha) or alpha <= 0):
        raise ValueError("Invalid regression input")
    mean, std, target_mean = x.mean(axis=0), x.std(axis=0), float(y.mean())
    if np.any(std < 1e-6) or y.std() < 1e-6:
        raise ValueError("Uninformative regression input")
    z = (x-mean)/std
    weights = np.linalg.solve(z.T@z/len(z) + alpha*np.eye(x.shape[1]), z.T@(y-target_mean)/len(z))
    return {"means": mean.tolist(), "std": std.tolist(), "weights": weights.tolist(),
            "target_mean": target_mean, "alpha": alpha, "training_pixels": len(x)}


def predict(x, model):
    return (x-np.array(model["means"]))/np.array(model["std"]) @ np.array(model["weights"]) + model["target_mean"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--pca-dir", required=True, type=Path)
    parser.add_argument("--composite", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    receipt_path = args.source_dir / "receipt.json"
    pca_path = args.pca_dir / "report.json"
    receipt, pca = json.loads(receipt_path.read_text()), json.loads(pca_path.read_text())
    if pca.get("folio") != "164v" or len(pca["channels"]) != 42:
        raise ValueError("Expected the 42 accepted modern 164v bands")
    if pca["source_receipt_sha256"] != hashlib.sha256(receipt_path.read_bytes()).hexdigest():
        raise ValueError("PCA source receipt mismatch")
    args.output_dir.mkdir(exist_ok=False)
    cv2.setNumThreads(1)
    rgb = read_image(args.composite, "338dbac8f176629f42f780b528d7d26aa195c130529ad23899b7e5060d52dc29").astype(np.float32)
    if rgb.shape != (1286, 2000, 3):
        raise ValueError("Unexpected composite geometry")
    yy, xx = np.indices((980, 1600), dtype=np.float32)
    mapx = (xx+200)*MATRIX[0, 0] + (yy+273)*MATRIX[0, 1] + MATRIX[0, 2]
    mapy = (xx+200)*MATRIX[1, 0] + (yy+273)*MATRIX[1, 1] + MATRIX[1, 2]
    mapped = cv2.remap(rgb[:, :, 2]-rgb[:, :, 1], mapx.astype(np.float32), mapy.astype(np.float32), cv2.INTER_LINEAR)
    boxes = {name: component_box(box) for name, box in SOURCE_BOXES.items()}
    bands = {name: [] for name in boxes}
    alignments = {row["member"]: row for row in pca["alignment"]}
    verified = {row["archive_member"]: row for row in receipt["member_payloads_verified"]}
    for row in pca["channels"]:
        if row != verified[row["archive_member"]] or Path(row["local_file"]).name != row["local_file"]:
            raise ValueError("Unverified exposure")
        a = read_image(args.source_dir / row["local_file"], row["sha256"]).astype(np.float32)
        if a.shape != (2044, 1533):
            raise ValueError("Unexpected exposure geometry")
        alignment = alignments[row["archive_member"]]
        if not alignment["passed"]:
            raise ValueError("Rejected exposure cannot be used")
        if not alignment.get("reference"):
            a = cv2.warpAffine(a, np.array(alignment["matrix"]), (1533, 2044), flags=cv2.INTER_LINEAR)
        rotated = np.rot90(a[200:1800, 280:1260])
        for name, (x0, y0, x1, y1) in boxes.items():
            bands[name].append(rotated[y0:y1, x0:x1])
    cubes = {name: np.stack(items, axis=-1) for name, items in bands.items()}
    x0, y0, x1, y1 = boxes["selection_line1"]
    model = fit_contrast(cubes["selection_line1"].reshape(-1, 42), mapped[y0:y1, x0:x1].ravel())
    predicted = {name: predict(cube, model) for name, cube in cubes.items()}
    limits = np.percentile(predicted["selection_line1"], [1, 99])
    comparisons, views = {}, []
    for name, data in predicted.items():
        x0, y0, x1, y1 = boxes[name]
        target = mapped[y0:y1, x0:x1]
        if name != "uncertain_line2_band":
            comparisons[name] = {"correlation": float(np.corrcoef(data.ravel(), target.ravel())[0, 1]),
                "rmse_composite_units": float(np.sqrt(np.mean((data-target)**2)))}
        pixels = 255-np.clip((data-limits[0])*255/(limits[1]-limits[0]), 0, 255).astype(np.uint8)
        destination = args.output_dir / (name+".png")
        Image.fromarray(np.rot90(pixels, 2)).save(destination)
        views.append({"file": destination.name, "sha256": hashlib.sha256(destination.read_bytes()).hexdigest()})
    report = {"script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "source_receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
              "pca_report_sha256": hashlib.sha256(pca_path.read_bytes()).hexdigest(),
              "composite_sha256": hashlib.sha256(args.composite.read_bytes()).hexdigest(),
              "model": model, "source_boxes_xyxy": SOURCE_BOXES, "pc_boxes_xyxy": boxes,
              "display_limits_from_training_only": limits.tolist(), "comparisons": comparisons,
              "views": views, "generative_processing": False, "text_input": False,
              "training_target": "Published composite B-G in neighboring line 1",
              "target_line_used_in_regression": False, "independent_ink_validation": False,
              "reading_accuracy_measured": False, "new_reading": False}
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    print(json.dumps(comparisons, indent=2))


if __name__ == "__main__":
    main()
