"""Reproduce the two fixed Mercati inspections from hash-checked crop receipts.

No downloads or character recognition. OpenCV offsets are navigation estimates,
not evidence that a letter has been read. All original crop bytes remain intact.
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from probe_mercati_spectral import crop, digest, linear_residual, stretch


def measured(path):
    receipt = json.loads(path.with_suffix(".json").read_text())
    if digest(path) != receipt["crop_sha256"] or path.stat().st_size != receipt["crop_bytes"]:
        raise ValueError(f"Changed source crop: {path}")
    _, _, width, height = receipt["box_xywh"]
    return np.fromfile(path, dtype=receipt["dtype"]).reshape(height, width), receipt


def geometry(reference, candidate, box):
    first, second = [crop(a, box).astype(np.float32) for a in (reference, candidate)]
    window = cv2.createHanningWindow((first.shape[1], first.shape[0]), cv2.CV_32F)
    shift, response = cv2.phaseCorrelate(first, second, window)
    return {"estimated_dx_dy": list(shift), "response": response,
            "patch_xywh_local": box, "resampling_applied": False}


def panel(path, views, region):
    width, height = region[2:]
    result = Image.new("RGB", (width, len(views) * (height + 24)), "white")
    draw = ImageDraw.Draw(result)
    for index, (name, view) in enumerate(views.items()):
        top = index * (height + 24)
        draw.text((4, top + 4), name, fill="black")
        result.paste(Image.fromarray(crop(view, region)), (0, top + 24))
    result.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Choose a new output directory; no results are overwritten")
    args.output.mkdir(parents=True)
    root = Path(__file__).resolve().parents[2]
    sources = root / "sources/textual_restoration/discovery"
    cases = {}
    originals = {}
    for page, protocol_name, patch in [
        ("27", "mercati_ps49_12_protocol.2026-10-19.v1.json", [0, 0, 300, 900]),
        ("60", "mercati_ps31_24_protocol.2026-10-19.v1.json", [0, 0, 3000, 100]),
    ]:
        protocol_path = sources / protocol_name
        protocol = json.loads(protocol_path.read_text())
        bands, receipts, views, displays = {}, {}, {}, {}
        for code in protocol["measured_capture_codes"]:
            suffix = "365uv" if page == "27" and code == "MB365UV_011" else code
            path = args.cache / f"page{page}-{suffix}.bin"
            pixels, receipt = measured(path)
            if receipt["box_xywh"] != protocol["context_xywh"]:
                raise ValueError("Crop geometry differs from the fixed protocol")
            originals[str(path)] = digest(path)
            originals[str(path.with_suffix(".json"))] = digest(path.with_suffix(".json"))
            bands[code], receipts[code] = pixels, receipt
            views[code], limits = stretch(pixels)
            output = args.output / f"page{page}-{code}.png"
            Image.fromarray(views[code]).save(output)
            displays[code] = {"output": output.name, "sha256": digest(output),
                              "limits_1_99_percentile": limits}
        reference = bands["MB450RB_002"]
        checks = {name: geometry(reference, pixels, patch) for name, pixels in bands.items()}
        result = {"protocol": protocol_name, "protocol_sha256": digest(protocol_path),
                  "protocol_content": protocol, "inputs": receipts, "views": displays,
                  "geometry_estimates": checks}
        if page == "60":
            signal, nuisance = bands["MB365UV_011"], bands["MB850IR_013"]
            mask = np.zeros(signal.shape, dtype=bool)
            mask[:100], mask[-100:] = True, True
            residual, coefficients = linear_residual(signal, nuisance, mask)
            views["UV-minus-fitted-IR"], limits = stretch(residual)
            output = args.output / "page60-residual.png"
            Image.fromarray(views["UV-minus-fitted-IR"]).save(output)
            result["linear_diagnostic"] = {"slope_intercept": coefficients,
                "calibration_first_last_rows": 100, "fit_pixels": int(mask.sum()),
                "output": output.name, "sha256": digest(output), "limits": limits,
                "can_authenticate_residual_only_strokes": False,
                "caveat": "Unresampled edges and chemical stains can survive subtraction."}
            region = protocol["uppertext_sigma_search_xywh"]
        else:
            region = protocol["target_xywh"]
        local = [region[0] - protocol["context_xywh"][0],
                 region[1] - protocol["context_xywh"][1], *region[2:]]
        output = args.output / f"page{page}-target-panel.png"
        panel(output, views, local)
        result["target_panel"] = {"output": output.name, "sha256": digest(output),
                                   "region_xywh_local": local}
        cases[page] = result
    if not all(digest(Path(path)) == pin for path, pin in originals.items()):
        raise ValueError("An original crop or receipt changed during analysis")
    result = {"cases": cases, "all_crop_inputs_unchanged": True,
              "tool_sha256": digest(Path(__file__)),
              "probe_tool_sha256": digest(Path(__file__).with_name("probe_mercati_spectral.py")),
              "runtime": {"numpy": np.__version__, "opencv": cv2.__version__, "pillow": Image.__version__},
              "new_characters_accepted": 0, "canonical_change": False,
              "transcription_authorized": False}
    (args.output / "measurements.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote both fixed cases to {args.output}")


if __name__ == "__main__":
    main()
