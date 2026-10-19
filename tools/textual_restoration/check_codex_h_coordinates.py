"""Check fixed identity coordinates between public Codex H presentations.

This tests page navigation. It does not register individual letters or establish
ink chemistry. The lower field and all failed patches remain in the report.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from check_zacynthius_line_controls import gradients, patch_gate, read_image

CENTERS_X = (220, 370, 520, 670, 820, 970, 1120)
CENTERS_Y = {
    "upper": (350, 500, 650, 800, 950),
    "lower": (1070, 1198, 1326, 1454, 1582),
}


def measure_region(direct, processed, region, expected_shape=(1775, 1320, 3)):
    if direct.shape != expected_shape or processed.shape != direct.shape:
        raise ValueError(f"Expected matching RGB overview images with shape {expected_shape}")
    if expected_shape[0] < max(CENTERS_Y[region]) + 64 or expected_shape[1] < max(CENTERS_X) + 64:
        raise ValueError("Overview does not contain the complete fixed patch grid")
    first, second = [gradients(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32))
                     for rgb in (direct, processed)]
    window = cv2.createHanningWindow((128, 128), cv2.CV_32F)
    rows = []
    for y in CENTERS_Y[region]:
        for x in CENTERS_X:
            shift, response = cv2.phaseCorrelate(
                first[y-64:y+64, x-64:x+64].copy(),
                second[y-64:y+64, x-64:x+64].copy(), window)
            rows.append({"center_xy": [x, y], "shift_xy": list(shift),
                         "response": response, "shift_norm_px": float(np.linalg.norm(shift))})
    strong = [row for row in rows if row["response"] >= .3]
    return {"rows": rows, "strong_count": len(strong), "gate_passed": bool(patch_gate(rows)),
            "strong_median": float(np.median([r["shift_norm_px"] for r in strong])) if strong else None,
            "strong_p95": float(np.percentile([r["shift_norm_px"] for r in strong], 95)) if strong else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--region", choices=CENTERS_Y, required=True)
    parser.add_argument("--pair", choices=["paris", "kyiv"], default="paris")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    record_name = ("codex_h_public_trace_gate.2026-10-18.v1.json" if args.pair == "paris"
                   else "codex_h_prior_art_kyiv.2026-10-18.v1.json")
    prior_path = Path(__file__).resolve().parents[2] / "sources/textual_restoration/discovery" / record_name
    prior = json.loads(prior_path.read_text())
    hashes = {r["local_name"]: r["assembled_sha256"] for r in prior["acquisitions"]}
    names = (("codex-h-2v-overview", "codex-h-3r-overview") if args.pair == "paris"
             else ("codex-h-40v-overview", "codex-h-41r-overview"))
    expected_shape = (1775, 1320, 3) if args.pair == "paris" else (1759, 1396, 3)
    arrays = [read_image(args.work_dir / name / "assembled.png", hashes[name]) for name in names]
    direct, processed = arrays[0][:, ::-1].copy(), arrays[1]
    result = measure_region(direct, processed, args.region, expected_shape)
    args.output_dir.mkdir(exist_ok=False)
    sheet = Image.new("RGB", (128*7, 256*5))
    for j, y in enumerate(CENTERS_Y[args.region]):
        for i, x in enumerate(CENTERS_X):
            box = (x-64, y-64, x+64, y+64)
            sheet.paste(Image.fromarray(direct).crop(box), (i*128, j*256))
            sheet.paste(Image.fromarray(processed).crop(box), (i*128, j*256+128))
    sheet_path = args.output_dir / "patch-pairs.png"
    sheet.save(sheet_path)
    result.update(region=args.region, input_sha256=[hashes[name] for name in names],
                  method=f"Horizontal mirror of{'2v' if args.pair == 'paris' else '40v'}, identity coordinates, fixed35patches, existing Gaussian3 sigma0.8/Sobel3 gradients, phase correlation with128px Hanning window",
                  gate="At least20patches response>=0.3, shift median<=1.5px, p95<=3px; inherited from Zacynthius patch control",
                  warning="Navigation only; shared capture and host writing may dominate. No letter recovery or layer attribution is established.",
                  new_characters=0, patch_pairs_sha256=hashlib.sha256(sheet_path.read_bytes()).hexdigest(),
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (args.output_dir / "report.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
