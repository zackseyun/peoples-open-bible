"""Replay the recorded 57r line-control check, not a manuscript transcription.

The affine transform and line bands are historical inspection choices, not
estimates to refit to a desired reading. No generated or completed letters.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def color_difference(rgb):
    a = rgb.astype(np.float32)
    return a[:, :, 2] - a[:, :, 1]


def component_box(source_box, matrix):
    points = np.array([(x, y) for x in (source_box[0], source_box[2])
                       for y in (source_box[1], source_box[3])], dtype=np.float64)
    points = (points - [1000, 1200]) * [2000 / 6800, 1324 / 4500]
    inverse = cv2.invertAffineTransform(matrix)
    points = points @ inverse[:, :2].T + inverse[:, 2] - [200, 273]
    return tuple(np.r_[np.floor(points.min(axis=0)).astype(int) - 3,
                          np.ceil(points.max(axis=0)).astype(int) + 3].tolist())


def gradients(a):
    a = cv2.GaussianBlur(a, (3, 3), .8)
    return cv2.magnitude(cv2.Sobel(a, cv2.CV_32F, 1, 0, ksize=3),
                         cv2.Sobel(a, cv2.CV_32F, 0, 1, ksize=3))


def patch_checks(aligned, composite_blue):
    first, second = gradients(aligned), gradients(composite_blue)
    window = cv2.createHanningWindow((128, 128), cv2.CV_32F)
    rows = []
    for y in [320, 520, 720, 920, 1120]:
        for x in [240, 480, 720, 960, 1200, 1440, 1680]:
            a = first[y-64:y+64, x-64:x+64]
            b = second[y-64:y+64, x-64:x+64]
            shift, response = cv2.phaseCorrelate(a.copy(), b.copy(), window)
            rows.append({"center_xy": [x, y], "shift_xy": list(shift), "response": response,
                         "shift_norm_px": float(np.linalg.norm(shift))})
    return rows


def patch_gate(rows):
    strong = [row for row in rows if row["response"] >= .3]
    return (len(strong) >= 20 and np.median([r["shift_norm_px"] for r in strong]) <= 1.5
            and np.percentile([r["shift_norm_px"] for r in strong], 95) <= 3)


def read_image(path, digest):
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError(f"Input hash mismatch: {path.name}")
    with Image.open(path) as image:
        return np.array(image)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-reference", required=True, type=Path)
    parser.add_argument("--composite", required=True, type=Path)
    parser.add_argument("--pca-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    records = Path(__file__).resolve().parents[2] / "sources/textual_restoration/discovery"
    record = json.loads((records / "zacynthius_line_controls.2026-10-17.v1.json").read_text())
    prior = json.loads((records / "zacynthius_spectral_pilot.2026-10-17.v1.json").read_text())
    checks = record["patch_check"]
    matrix = np.array(record["navigation_matrix_rotated_raw_to_composite"])
    raw = read_image(args.raw_reference, checks["raw_sha256"])
    rgb = read_image(args.composite, checks["composite_sha256"])
    if raw.shape != (2044, 1533) or rgb.shape != (1324, 2000, 3):
        raise ValueError("Unexpected input geometry")
    out = args.output_dir
    out.mkdir(exist_ok=False)
    raw = np.rot90(raw).astype(np.float32)
    rgb = rgb.astype(np.float32)
    aligned = cv2.warpAffine(raw, matrix, (2000, 1324), flags=cv2.INTER_LINEAR)
    rows = patch_checks(aligned, rgb[:, :, 2])
    score = color_difference(rgb)
    yy, xx = np.indices((980, 1600), dtype=np.float32)
    mapx = (xx + 200) * matrix[0, 0] + (yy + 273) * matrix[0, 1] + matrix[0, 2]
    mapy = (xx + 200) * matrix[1, 0] + (yy + 273) * matrix[1, 1] + matrix[1, 2]
    mapped = cv2.remap(score, mapx.astype(np.float32), mapy.astype(np.float32), cv2.INTER_LINEAR)
    boxes = {name: component_box(box, matrix) for name, box in record["source_bands_xyxy"].items()}
    correlations = []
    for i, view in enumerate(prior["processing"]["views"], 1):
        a = read_image(args.pca_dir / view["file"], view["sha256"]).astype(np.float32)
        if a.shape != (980, 1600):
            raise ValueError("Unexpected component geometry")
        row = {"component": i}
        for name in ("selection_line3", "check_line2"):
            x0, y0, x1, y1 = boxes[name]
            row[name + "_correlation"] = float(np.corrcoef(
                -a[y0:y1, x0:x1].ravel(), mapped[y0:y1, x0:x1].ravel())[0, 1])
        correlations.append(row)
        if i == 7:
            for name, (x0, y0, x1, y1) in boxes.items():
                Image.fromarray(a[y0:y1, x0:x1].astype(np.uint8)).save(out / f"{name}.png")
                local = mapped[y0:y1, x0:x1]
                lo, hi = np.percentile(local, [1, 99])
                comparison = 255 - np.clip((local - lo) * 255 / max(hi - lo, 1e-6), 0, 255).astype(np.uint8)
                Image.fromarray(comparison).save(out / f"{name}-published-color-difference.png")
    result = {"patches": rows, "patch_gate_passed": bool(patch_gate(rows)),
              "pc_boxes_xyxy": boxes, "correlations": correlations, "selected_component": 7,
              "reading_accuracy_measured": False, "transcription_performed": False,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "versions": {"opencv": cv2.__version__, "numpy": np.__version__, "pillow": Image.__version__}}
    (out / "report.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"patch_gate_passed": result["patch_gate_passed"], "pc7": correlations[6]}))


if __name__ == "__main__":
    main()
