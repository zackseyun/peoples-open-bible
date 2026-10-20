"""Make auditable, non-generative views of fixed Mercati image regions.

Coordinates are in the stored image, before optional quarter-turn rotation.
Contrast changes aid inspection; neither this tool nor its statistics read text.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import urllib.request

import numpy as np
from PIL import Image


class RangeReader(io.RawIOBase):
    """Read TIFF directory bytes without silently downloading a whole capture."""

    def __init__(self, url):
        self.url, self.position, self.total = url, 0, None
        self.receipts = []
        self.etag = None
        self.header = None

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        if whence == 0:
            self.position = offset
        elif whence == 1:
            self.position += offset
        elif whence == 2 and self.total is not None:
            self.position = self.total + offset
        else:
            raise ValueError("Unknown seek origin or source length")
        if self.position < 0:
            raise ValueError("Negative source offset")
        return self.position

    def read(self, size=-1):
        if size < 0 or size > 20_000_000:
            raise ValueError("Only bounded range reads are allowed")
        if size == 0:
            return b""
        if self.header is not None and self.position + size <= len(self.header):
            data = self.header[self.position:self.position + size]
            self.position += size
            return data
        if self.header is None and self.position == 0 and size <= 65536:
            self.header = self.fetch(0, 65535)
            self.position = size
            return self.header[:size]
        if self.total is not None:
            size = min(size, self.total - self.position)
        if size <= 0:
            return b""
        start, end = self.position, self.position + size - 1
        data = self.fetch(start, end)
        self.position += size
        return data

    def fetch(self, start, end):
        size = end - start + 1
        request = urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{end}"})
        with urllib.request.urlopen(request, timeout=60) as response:
            content_range = response.headers.get("Content-Range", "")
            prefix, separator, total = content_range.partition("/")
            if (response.status != 206 or not separator or not total.isdigit()
                    or prefix != f"bytes {start}-{end}"):
                raise ValueError("Server did not honor the exact requested byte range")
            total = int(total)
            etag = response.headers.get("ETag")
            if self.total is not None and (total != self.total or etag != self.etag):
                raise ValueError("Source changed between range requests")
            data = response.read(size + 1)
            if len(data) != size:
                raise ValueError("Range response length mismatch")
            self.total, self.etag = total, etag
            self.receipts.append({"range_inclusive": [start, end], "bytes": len(data),
                                  "sha256": hashlib.sha256(data).hexdigest(),
                                  "content_range": content_range})
        return data


def remote_crop(url, box):
    reader = RangeReader(url)
    with Image.open(reader) as image:
        width, height = image.size
        tags = image.tag_v2
        offsets, counts = tags.get(273, ()), tags.get(279, ())
        if (image.mode not in ("I;16", "I;16B", "I;16L") or tags.get(259, 1) != 1
                or tags.get(277, 1) != 1 or tuple(tags.get(258, ())) != (16,)
                or tuple(tags.get(339, (1,))) != (1,)
                or len(offsets) != 1 or len(counts) != 1 or counts[0] != width * height * 2
                or tags.get(278) != height or tags.get(274, 1) != 1):
            raise ValueError("Require an unrotated, uncompressed single-strip 16-bit gray TIFF")
        # Validate geometry without allocating a page-sized array.
        x, y, w, h = box
        if (any(type(n) is not int for n in box) or min(x, y) < 0 or min(w, h) <= 0
                or x + w > width or y + h > height):
            raise ValueError("Invalid remote crop")
        dtype = ">u2" if image.mode == "I;16B" else "<u2"
        reader.seek(offsets[0] + y * width * 2)
        rows = reader.read(h * width * 2)
        pixels = np.frombuffer(rows, dtype=dtype).reshape(h, width)[:, x:x + w].copy()
        source = {"url": url, "full_shape_hw": [height, width], "box_xywh": box,
                  "dtype": dtype, "full_source_bytes": reader.total,
                  "etag": reader.etag, "compression": 1, "strip_offset": offsets[0],
                  "range_receipts": reader.receipts,
                  "full_capture_downloaded": False, "full_capture_sha256": None}
    return pixels, source


def fetch_main():
    parser = argparse.ArgumentParser(description="Acquire exact measured TIFF pixels using public byte ranges")
    parser.add_argument("--url", required=True)
    parser.add_argument("--box", type=int, nargs=4, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sidecar = args.output.with_suffix(".json")
    if args.output.exists() or sidecar.exists():
        raise ValueError("Existing source crops are never overwritten")
    pixels, source = remote_crop(args.url, args.box)
    payload = pixels.tobytes()
    args.output.write_bytes(payload)
    source.update({"crop_sha256": hashlib.sha256(payload).hexdigest(), "crop_bytes": len(payload),
                   "format": "raw row-major measured pixels; decode with dtype and crop width/height",
                   "original_crop_pixels_preserved": True})
    sidecar.write_text(json.dumps(source, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "bytes": len(payload), "range_requests": len(source["range_receipts"])}))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stretch(pixels, low=1, high=99):
    values = np.asarray(pixels, dtype=np.float64)
    if not np.isfinite(values).all() or not 0 <= low < high <= 100:
        raise ValueError("Require finite pixels and ordered percentiles")
    limits = np.percentile(values, [low, high])
    if limits[1] == limits[0]:
        return np.full(values.shape, 127, dtype=np.uint8), limits.tolist()
    scaled = np.clip((values - limits[0]) / (limits[1] - limits[0]), 0, 1)
    return np.rint(255 * scaled).astype(np.uint8), limits.tolist()


def linear_residual(signal, nuisance, calibration):
    signal = np.asarray(signal, dtype=np.float64)
    nuisance = np.asarray(nuisance, dtype=np.float64)
    mask = np.asarray(calibration, dtype=bool)
    if (signal.shape != nuisance.shape or signal.shape != mask.shape
            or not np.isfinite(signal).all() or not np.isfinite(nuisance).all()
            or np.count_nonzero(mask) < 3 or np.std(nuisance[mask]) == 0):
        raise ValueError("Require matching finite fields and a nonconstant calibration region")
    matrix = np.column_stack((nuisance[mask], np.ones(np.count_nonzero(mask))))
    slope, intercept = np.linalg.lstsq(matrix, signal[mask], rcond=None)[0]
    return signal - (slope * nuisance + intercept), [float(slope), float(intercept)]


def crop(pixels, box):
    x, y, width, height = box
    if any(type(n) is not int for n in box) or min(x, y) < 0 or min(width, height) <= 0:
        raise ValueError("Require an integer nonempty crop")
    if x + width > pixels.shape[1] or y + height > pixels.shape[0]:
        raise ValueError("Crop extends beyond source")
    return pixels[y:y + height, x:x + width].copy()


def inspect(source, box, mode="gray", turns=0):
    if source.suffix == ".bin":
        receipt = json.loads(source.with_suffix(".json").read_text())
        payload = source.read_bytes()
        if (hashlib.sha256(payload).hexdigest() != receipt["crop_sha256"]
                or len(payload) != receipt["crop_bytes"]):
            raise ValueError("Measured crop differs from its acquisition receipt")
        _, _, width, height = receipt["box_xywh"]
        pixels = np.frombuffer(payload, dtype=receipt["dtype"]).reshape(height, width)
        metadata = {"shape": list(pixels.shape), "dtype": str(pixels.dtype),
                    "mode": "measured raw crop", "acquisition_receipt_sha256": digest(source.with_suffix(".json"))}
    else:
        with Image.open(source) as image:
            pixels = np.asarray(image)
            metadata = {"shape": list(pixels.shape), "dtype": str(pixels.dtype),
                        "mode": image.mode}
    region = crop(pixels, box)
    if mode == "rgb":
        if region.ndim != 3 or region.shape[2] != 3 or region.dtype != np.uint8:
            raise ValueError("RGB crop requires unmodified 8-bit color pixels")
        return np.rot90(region, turns), {**metadata, "box_xywh": box,
                "quarter_turns_ccw": turns, "mode_requested": mode,
                "percentiles": None, "display_limits": None}
    if mode == "published-red-navigation":
        if region.ndim != 3 or region.shape[2] != 3:
            raise ValueError("Navigation separation requires published RGB pixels")
        rgb = region.astype(np.float64)
        region = rgb[:, :, 0] - (rgb[:, :, 1] + rgb[:, :, 2]) / 2
    elif mode == "gray":
        if region.ndim != 2:
            raise ValueError("Measured gray view requires one channel")
    else:
        raise ValueError("Unknown view mode")
    preview, limits = stretch(region)
    return np.rot90(preview, turns), {**metadata, "box_xywh": box,
            "quarter_turns_ccw": turns, "mode_requested": mode,
            "percentiles": [1, 99], "display_limits": limits}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--box", type=int, nargs=4, required=True)
    parser.add_argument("--mode", choices=("gray", "rgb", "published-red-navigation"), default="gray")
    parser.add_argument("--turns", type=int, choices=range(4), default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sidecar = args.output.with_suffix(".json")
    if args.output.exists() or sidecar.exists():
        raise ValueError("Existing outputs are never overwritten")
    before = digest(args.source)
    if before != args.sha256:
        raise ValueError("Source digest mismatch")
    view, result = inspect(args.source, args.box, args.mode, args.turns)
    Image.fromarray(view).save(args.output)
    if digest(args.source) != before:
        raise ValueError("Source changed during processing")
    result.update({"source": str(args.source), "source_sha256": before,
                   "output_sha256": digest(args.output), "source_unchanged": True,
                   "new_characters_accepted": 0, "transcription_authorized": False})
    sidecar.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "fetch":
        sys.argv.pop(1)
        fetch_main()
    else:
        main()
