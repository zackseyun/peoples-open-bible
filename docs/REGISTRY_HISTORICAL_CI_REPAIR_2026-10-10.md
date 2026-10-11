# Historical registry CI repair

PR135's two checks, `114380240888` and `114380185503`, failed in
“Test reader notes and consultation policy.” Both reached the same assertion
in `test_ecclesiastes8_10_ctat.py`: an older CTAT registration test compared
all forty pre-registration witness entries with today's live registry.
The Nahum follow-up intentionally updated `8hev-greek-minor-prophets`, so
that historical assertion incorrectly prohibited a later reviewed update.
The four-test local reproduction also failed at that assertion. Catalog and
complete reader-corpus checks passed in the failed CI jobs; later tests were
not reached and are not reported validated by those runs.

The repair binds the original transaction to its actual after-commit
`26ef853ffc6702ee5f3986818c3d3c8ffbd379ef`. Its exact registry SHA256 is
`5d7b59587bc57b348900c424405cd89ae2be622f5ae1efd38f0ca1e3b36ad244`.
The original before-commit/hash, forty unchanged entries, one added CTAT
entry, rights fields and schema/semantic checks remain asserted. A separate
test validates the live registry without treating an arbitrary historical
snapshot as permanent current data. The workflow fetches that immutable
after-commit explicitly so the historical test also works in its shallow
checkout. No check is skipped, baseline substituted, or CI gate bypassed.

Twenty-five related local tests pass in 2.961 seconds: five CTAT, six Nahum
published-source, nine historical-runner and five Micah comparison checks.
The extra CTAT test is a distinct current-registry check; reruns are not counted
as new research evidence. This validates the scoped implementation locally,
not the full CI job or historical originality of the source readings.

One bounded independent code critique passes the exact repair. It confirms the
after-commit directly follows the baseline, preserves forty entries and adds
only the CTAT entry; both hashes match and the commit exists on the configured
remote. Its five CTAT tests and diff check also pass, not additional distinct
checks in the twenty-five-test root count. The two code files are pinned
as `e534f2abc2a1e2ddb9cc9ff2536f232035720bff7319c3e03ccdf9283649b80a`
(CTAT test) and
`9e7aeacc271c47870803416155092fc641b6964db9c11769c056288e5fb2e010`
(workflow). The repair will update PR135; dependent PR136 must carry it too.
Old failed runs remain part of the record. New head-triggered jobs, merge
verification and main push are separate delivery events.
