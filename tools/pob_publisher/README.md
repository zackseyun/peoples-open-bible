# Azure-only canonical POB proposal — inactive

Approved scope: **prepare code and offline tests in a draft PR; hold activation**.
No cloud operation, identity login, dispatch, variable change, AWS action, main
merge, routing/DNS change, new resource or permission grant is included.
`azure_stage.live_store()` always raises. There is no upload CLI. The workflow
proposal is outside `.github/workflows` and its job additionally has `if: false`.
The only active new workflow runs offline PR tests on GitHub-hosted runners.
The existing AWS workflow is deliberately unchanged; **do not merge B35 or this
proposal while AWS publication triggers remain active or unverified**.

## Compiler and exact scope

`compiler.mjs` extracts the canonical parser/transforms from CarthaCdkService
`d1d4968db99ca9d7c2b3ee18560ba1e496af374a`, with pinned helper hashes in
`provenance.json`. It has no AWS imports, handlers, clients, environment selection,
HTTP fetches or account access. The one intentional parsing safety difference
rejects malformed YAML rather than silently omitting it. The underlying canonical
transform/format is unchanged. Dependencies are exact-versioned and lockfile-bound.

This is **not** `export_reader_bible.py`: the legacy canonical publisher includes
partial chapters, while that repository reader exporter has completeness guards.
Those guards remain untouched. Existing public addresses are preserved, not newly
certified. In particular, existing partial Enoch 32/95/96 remain as before; B35
must not expose absent 95:6–7, 96:4–8 or any other held neighbor. Psalm verse-zero
titles and the Gospel of Thomas chapter-zero introduction also remain intact.

The sealed baseline fixture contains each raw canonical record's SHA256 and book
metadata, not a second copy of Scripture. It came from the previously retained
public payload and manifest at `a3681961d91c1eb1a609e12cec312a644148f9bb`.
Its raw payload SHA256 is in the fixture; it is **not** reconstructed from the
website's normalized JSON. Full compilation matches **135 books, 2651 chapters,
45231 verse records**, with every record and metadata digest identical. This
proves output equivalence for that snapshot, not that inspected CDK code is the
currently deployed Lambda binary.

The exact B35 fixture binds source `3ca33e73a8b5dc73b98852a1add96cbb58fb63a1`,
the baseline fixture digest, and before/after whole-record hashes for only
95:1–5 and 96:1. That corpus transaction's review manifest is
`0949de859c43f638bc3211c601bdb1e0ea414d26b77ea86296218d9ec549a961`.
Any address addition/deletion, unrelated metadata/English change, missing source,
notes or review protocol, or mismatched before/after hash fails. These fixtures
are offline regression evidence, **not runtime publishing authorization**.

## Offline operation

From the repository root:

```sh
npm ci --prefix tools/pob_publisher --ignore-scripts --no-audit --no-fund
npm test --prefix tools/pob_publisher
python3 -m unittest discover -s tests -p test_pob_azure_stage_proposal.py -v
node tools/pob_publisher/build.mjs "$PWD" \
  3ca33e73a8b5dc73b98852a1add96cbb58fb63a1 \
  tests/fixtures/pob_publisher/baseline-a368.json.gz \
  tests/fixtures/pob_publisher/batch35-changes.json \
  2026-10-31T00:00:00.000Z /absolute/new/offline-output-directory
```

The two pinned source commits must be available locally (CI fetches them without
merging). Compilation reads an exact `git archive`, never the dirty working tree.
The timestamp is an explicit reproducibility input, not evidence of publication.
An output directory cannot preexist or live inside the source checkout. The seal
binds the source, compiler/transform/lockfile dependency set, baseline and change
approval bytes, exact canonical payload and manifest. The printed reviewed-seal
hash uses recursively key-sorted UTF-8 JSON plus one LF, matching Python `encoded`.

## Azure adapter protocol, tested only with an injected fake store

The candidate account/containers reuse the existing website pattern. Actual
managed-identity principal, RBAC, namespace vacancy and export ownership remain
**unverified**. No account/identity/resource is created by this code.

* Candidate public namespace: `canonical-pob/v1/` in existing `$web`.
* Candidate existing-private-container keys: `canonical-pob-control/v1.json` and
  `canonical-pob-control/publish.lock` in `preview-receipts`. **Neither exists by
  assumption or is created here.** Activation must separately authorize/verify
  exact ownership, writer identity and a generic-website-export exclusion.
* `stage` requires exact reviewed seal bytes, the exact expected durable owner
  control, a bound compiler/baseline, and the expected predecessor ETag. Ownership
  is checked before writes and before/after release promotion under a renewed
  lease on the separately provisioned lock blob.
* Payload then manifest are create-only in a content-addressed immutable release
  prefix. Every byte is read back before a conditional `current.json` pointer is
  written last. No object deletion, unguarded overwrite, rollback of a newer
  release, account-key authentication or AWS fallback exists. Failed staging may
  leave unreferenced immutable data; it does not promote a partial release.
* A verified identical replay performs zero writes. Missing replay dependencies,
  immutable collisions, changed owner, lost lease, stale predecessor or bad
  readback fail closed.
* `resolve.mjs` is a pure consumer proof verifier: fixed proposed Azure origin,
  exact source/owner, safe release path, payload+manifest hashes and canonical
  stats. It does no fetch and is **not wired into the website**. A normalized
  website bundle cannot masquerade as raw canonical input.

SDK method mapping uses Microsoft's [BlobClient API](https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.blobclient)
and [blob lease documentation](https://learn.microsoft.com/azure/storage/blobs/storage-blob-lease-python).
`AzureBlobStore` accepts an already supplied fixed-account SDK client; no live
factory is implemented. Its mapped conditional upload arguments are unit-tested,
but no real SDK/cloud integration or permissions claim is made.

## Separate activation gates — not authorized or satisfied

1. Verify actual existing identity and data-plane rights; stop rather than grant
   permissions or create infrastructure if capability is missing.
2. Review/prove namespace vacancy, durable ownership and exclusion from generic
   website exports. Ownership controls/lock blobs need a separate explicit write
   approval; no flag or successful website job substitutes for that transition.
3. Reconcile **all** existing AWS writers. Main's GitHub OIDC/Lambda workflow and
   the IaC-defined hourly `cartha-cob-publisher-hourly` are distinct. Its live
   enabled state was not checked. A skip-ci marker or disabling GitHub alone does
   not prove main can advance without AWS writes. This blocks main merges.
4. Review the exact immutable package and source freshness, serialized stage,
   readback and replay on Azure under separate runtime approval. Implement the
   still-disabled live factory only in that reviewed change.
5. Wire the website to the proof-verified Azure input in a separate reviewed
   change. Preserve its owning note normalization and same-origin reader shape;
   do not change DNS or claim `bible.cartha.com` migrated.
6. Verify exact terminal publication and public custom-host readback. Offline
   parity, fake-store tests and green CI are not deployment or full-book repair.

## Batch 36 successor fixture — still offline only

`batch36-changes.json` pins the tested Batch 36 draft (`ab73737d415d953359073b63a8eea3878af75d8c`).
It preserves all six Batch 35 changes and permits only the separately paired
96:3 repair in addition. The full-dataset regression checks both exact application
manifest hashes, seven total changes versus the retained public baseline, one
change versus Batch 35, unchanged address structure, and absence of held 95:6–7
and 96:4–8. CI fetches that immutable draft commit without merging it.

This fixture does not authorize activation, main merges, additional neighbors,
or publication. The original Batch 35 fixture and all activation gates remain.
