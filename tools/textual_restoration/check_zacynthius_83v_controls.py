"""Replay the fixed 83v navigation and frozen-PC7 comparison.

No refitting, character recognition, generative processing or completion.
The transform is a navigation estimate, not validated undertext registration.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def load_helper(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--pca-dir", required=True, type=Path)
    parser.add_argument("--composite", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    contrast = load_helper("probe_zacynthius_83v_contrast")
    controls = load_helper("check_zacynthius_line_controls")
    pca_path = args.pca_dir / "report.json"
    pca = json.loads(pca_path.read_text())
    receipt_path = args.source_dir / "receipt.json"
    receipt = json.loads(receipt_path.read_text())
    if pca.get("folio") != "164v" or len(pca["views"]) != 42:
        raise ValueError("Expected the modern 164v PCA report")
    if pca["source_receipt_sha256"] != hashlib.sha256(receipt_path.read_bytes()).hexdigest():
        raise ValueError("PCA receipt mismatch")
    reference = next(row for row in receipt["member_payloads_verified"]
                     if row["archive_member"] == "00164-V/00164-V+MB530GN_005.jpg")
    raw = contrast.read_image(args.source_dir / "00164-V+MB530GN_005.jpg", reference["sha256"])
    rgb = contrast.read_image(args.composite, "338dbac8f176629f42f780b528d7d26aa195c130529ad23899b7e5060d52dc29")
    if raw.shape != (2044, 1533) or rgb.shape != (1286, 2000, 3):
        raise ValueError("Unexpected source geometry")
    args.output_dir.mkdir(exist_ok=False)
    matrix = contrast.MATRIX
    raw = np.rot90(raw).astype(np.float32)
    rgb = rgb.astype(np.float32)
    aligned = cv2.warpAffine(raw, matrix, (2000, 1286), flags=cv2.INTER_LINEAR)
    patches = controls.patch_checks(aligned, rgb[:, :, 2])
    yy, xx = np.indices((980, 1600), dtype=np.float32)
    mapx = (xx+200)*matrix[0, 0] + (yy+273)*matrix[0, 1] + matrix[0, 2]
    mapy = (xx+200)*matrix[1, 0] + (yy+273)*matrix[1, 1] + matrix[1, 2]
    mapped = cv2.remap(controls.color_difference(rgb), mapx.astype(np.float32), mapy.astype(np.float32), cv2.INTER_LINEAR)
    boxes = {name: contrast.component_box(box) for name, box in contrast.SOURCE_BOXES.items()}
    correlations, views = [], []
    for i, view in enumerate(pca["views"], 1):
        if Path(view["file"]).name != view["file"]:
            raise ValueError("Expected local component basename")
        a = contrast.read_image(args.pca_dir / view["file"], view["sha256"]).astype(np.float32)
        if a.shape != (980, 1600):
            raise ValueError("Unexpected component geometry")
        row = {"component": i}
        for name in ("selection_line1", "check_line3"):
            x0, y0, x1, y1 = boxes[name]
            row[name+"_correlation"] = float(np.corrcoef(-a[y0:y1, x0:x1].ravel(), mapped[y0:y1, x0:x1].ravel())[0, 1])
        correlations.append(row)
        if i == 7:
            for name, (x0, y0, x1, y1) in boxes.items():
                strip = np.rot90(a[y0:y1, x0:x1].astype(np.uint8), 2)
                comparison = np.rot90(mapped[y0:y1, x0:x1], 2)
                lo, hi = np.percentile(comparison, [1, 99])
                comparison = 255-np.clip((comparison-lo)*255/max(hi-lo, 1e-6), 0, 255).astype(np.uint8)
                for suffix, data in [("", strip), ("-published-color-difference", comparison)]:
                    path = args.output_dir / (name+suffix+".png")
                    Image.fromarray(data).save(path)
                    views.append({"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "shape_hw": list(data.shape)})
    report = {"script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "pca_report_sha256": hashlib.sha256(pca_path.read_bytes()).hexdigest(),
              "patches": patches, "patch_gate_passed": bool(controls.patch_gate(patches)),
              "selected_component": 7, "pc_boxes_xyxy": boxes,
              "correlations": correlations, "views": views,
              "independent_validation": False, "new_reading": False}
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"patch_gate_passed": report["patch_gate_passed"], "pc7": correlations[6]}))


if __name__ == "__main__":
    main()
