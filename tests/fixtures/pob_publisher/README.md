# Offline canonical-format regression fixtures

`baseline-a368.json.gz` is deterministic gzip of compact JSON containing:
- the retained raw public payload SHA256 and exact source manifest at a3681961;
- translation name and complete book metadata;
- every `[book, chapter, verse]` address and recursively key-sorted whole-record digest.

It has no dependency on a live AWS/CDN endpoint, and it does not contain a copy
of the public English text. It preserves legacy partial chapters, not review
approval. `batch35-changes.json` binds the baseline bytes, exact six before/after
record digests and the already reviewed corpus application manifest. Neither
fixture is a runtime owner control or publication approval. Do not regenerate
these from a website-normalized bundle or auto-accept new hashes.
