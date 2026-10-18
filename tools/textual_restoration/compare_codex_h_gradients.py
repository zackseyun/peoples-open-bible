"""A single predeclared edge-representation check, with unchanged match gates."""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("--work-dir", type=Path, required=True)
root = parser.parse_args().work_dir
from check_zacynthius_line_controls import gradients

out = root / "codex-h-gradient-registration"
out.mkdir(exist_ok=True)
assert not (out / "report.json").exists()
direct = np.asarray(Image.open(root / "codex-h-2v-overview/assembled.png").convert("RGB"))[:, ::-1].copy()
transfer = np.asarray(Image.open(root / "codex-h-3r-overview/assembled.png").convert("RGB"))
views = []
limits = []
for rgb in [direct, transfer]:
    grad = gradients(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY))
    high = float(np.percentile(grad, 99))
    limits.append(high)
    views.append(np.uint8(np.clip(grad/high*255, 0, 255)))
sift = cv2.SIFT_create(nfeatures=6000)
a, da = sift.detectAndCompute(views[0], None)
b, db = sift.detectAndCompute(views[1], None)
good = [m for m, n in cv2.BFMatcher().knnMatch(da, db, k=2) if m.distance < .7*n.distance]
report = {"method": "Gaussian3 sigma0.8 then Sobel3 magnitude, whole-image99th-percentile scaling, SIFT6000, ratio0.7; no expected text",
    "scaling_high": limits, "matches": len(good), "minimum_required": 40,
    "accepted_transform": False, "new_letters": 0}
if len(good) >= 40:
    src = np.float32([a[m.queryIdx].pt for m in good])
    dst = np.float32([b[m.trainIdx].pt for m in good])
    matrix, mask = cv2.estimateAffinePartial2D(src[::2].copy(), dst[::2].copy(), method=cv2.RANSAC,
        ransacReprojThreshold=2, maxIters=5000, confidence=.999)
    assert matrix is not None
    errors = np.linalg.norm(src[1::2] @ matrix[:, :2].T + matrix[:, 2]-dst[1::2], axis=1)
    median, p95 = float(np.median(errors)), float(np.percentile(errors,95))
    report.update(matrix=matrix.tolist(), fit_inliers=int(mask.sum()),
        heldout_errors=errors.tolist(), heldout_median=median, heldout_p95=p95,
        accepted_transform=median<=1.5 and p95<=3)
    if report["accepted_transform"]:
        mapped = cv2.warpAffine(direct, matrix, (transfer.shape[1],transfer.shape[0]))
        Image.fromarray(mapped).save(out / "direct-aligned.png")
(out / "report.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items() if k!="heldout_errors"}, indent=2))
