# Pixel preserving context reading

This development check supplies a larger context crop without changing the
photograph's decoded pixels. The tentative image-only reading still disagrees
with the old proposed reference. The reference remains unapproved; this is not
a manuscript variant, a character-accuracy result or a fresh decipherment.

The frozen [region manifest](regions.json) pins the original photograph and the
new 900 × 640 PNG. Its rectangle is `[1230, 570, 900, 640]`. Preparation reuses
the existing generic crop operation:

```bash
python3 tools/dss/pilot.py prepare --pilot sources/textual_restoration/controls/2026-10-10-native-context
```

Pillow is required. The repository virtual environment lacked it; the bundled
Python runtime completed preparation instead, without installing dependencies.
The old 830 × 245 crop equals the new view's `[40, 20, 830, 245]` overlap
pixel-for-pixel. Source and old crop bytes remain unchanged. No resampling,
enhancement, generated ink or ImageGen operation occurs.

One fresh, history-withheld reviewer receives only this new PNG, not the
passage, expected words, editions or previous readings. The [result](result.json)
preserves its exact response and uncertainties. Its original-detail call has
no resize notice, as does root's inspection. This removes the previously
observed explicit full-page downsize, but the returned metadata does not
independently certify the model's actual input dimensions. Local dimensions
and model-delivery metadata are separate observations.

Root knows the edition wording and cannot supply an independent blind label.
The new output is not corrected to that wording. No second-family run or
manuscript-disjoint benchmark occurs. Stop this development case until a
defensible diplomatic reference or genuinely independent, calibrated reading
route is available; do not repeat votes to obtain agreement. Published-reading
comparisons can continue without claiming validated damaged-ink restoration.
