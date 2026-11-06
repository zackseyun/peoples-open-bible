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

B38 fixture: exact reviewed source head 661a61a3b19f2d16819a5f7cd7916f5bedc9b814.
Only 1 Enoch 1:9 differs from B37; the cumulative allowlist has nine records.
All 135 books, 2651 chapters and 45231 addresses remain bound to the baseline.
This is an offline test fixture, not activation or language approval for any
neighbor. B38 corpus CI passed twice and its 796 local Enoch tests passed.

B41 offline address-scope fixture: compared with B38, only five existing
reviewed records change and only 32:6 and 66:2 are added. The default publisher
still refuses structural additions. The test removes the two exact additions
from a copy only to compare all remaining addresses, structure, metadata and
reviewed before/after hashes. That comparison is not a deployable payload or
an address-authorization change. Runtime activation remains held.
