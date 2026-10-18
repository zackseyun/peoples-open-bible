"""Compare published presentations of the same physical leaf, not witnesses."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("--work-dir", type=Path, required=True)
root = parser.parse_args().work_dir
out = root / "codex-h-pair-registration"
out.mkdir(exist_ok=True)
assert not (out / "report.json").exists()
direct = np.asarray(Image.open(root / "codex-h-2v-overview/assembled.png").convert("RGB"))[:, ::-1].copy()
transfer = np.asarray(Image.open(root / "codex-h-3r-overview/assembled.png").convert("RGB"))
sift = cv2.SIFT_create(nfeatures=6000)
a, da = sift.detectAndCompute(cv2.cvtColor(direct, cv2.COLOR_RGB2GRAY), None)
b, db = sift.detectAndCompute(255-cv2.cvtColor(transfer, cv2.COLOR_RGB2GRAY), None)
pairs = cv2.BFMatcher().knnMatch(da, db, k=2)
good = [m for m, n in pairs if m.distance < .7*n.distance]
src = np.float32([a[m.queryIdx].pt for m in good])
dst = np.float32([b[m.trainIdx].pt for m in good])
if len(good) < 40:
    report = {"status": "insufficient_feature_matches", "matches": len(good),
              "minimum_required": 40, "accepted_transform": False,
              "method": "SIFT6000, ratio0.7, mirrored2v grayscale versus inverted3r grayscale",
              "new_letters": 0}
    (out / "report.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report))
    sys.exit(0)
matrix, mask = cv2.estimateAffinePartial2D(src[::2].copy(), dst[::2].copy(), method=cv2.RANSAC,
    ransacReprojThreshold=2, maxIters=5000, confidence=.999)
assert matrix is not None
pred = src[1::2] @ matrix[:, :2].T + matrix[:, 2]
errors = np.linalg.norm(pred-dst[1::2], axis=1)
report = {"source": "2v overview horizontally mirrored", "target": "3r overview",
    "source_images_are": "Different processed presentations of the same physical leaf; not independent manuscript witnesses or raw spectral exposures.",
    "method": "SIFT6000, ratio0.7, alternate matches fit/check, partial affine RANSAC2px5000iterationsconfidence0.999; no text input",
    "matrix": matrix.tolist(), "matches": len(good), "fit_inliers": int(mask.sum()),
    "heldout_errors": errors.tolist(), "heldout_median": float(np.median(errors)),
    "heldout_p95": float(np.percentile(errors, 95)),
    "passes_navigation_gate": bool(np.median(errors)<=1.5 and np.percentile(errors,95)<=3),
    "caution": "Feature checks may contain orientation duplicates. Navigation agreement does not identify ink chemistry or recover letters."}
aligned = cv2.warpAffine(direct, matrix, (transfer.shape[1], transfer.shape[0]), flags=cv2.INTER_LINEAR)
Image.fromarray(aligned).save(out / "direct-aligned.png")
# A previously inspected control band; not the uncertain two-line region.
box = (350, 765, 1000, 960)
sheet = Image.new("RGB", (650, 390))
sheet.paste(Image.fromarray(aligned).crop(box), (0, 0))
sheet.paste(Image.fromarray(transfer).crop(box), (0, 195))
sheet.save(out / "control-comparison.png")
report["control_box"] = list(box)
report["files"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob("*.png")}
(out / "report.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps({k: v for k, v in report.items() if k != "heldout_errors"}, indent=2))
