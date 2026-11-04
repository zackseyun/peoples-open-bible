# Shepherd of Hermas source PDFs — manifest

Source scope: [`README.md`](README.md)

The local PDF scans are **not committed**. This file records the
expected files currently present in the workspace.

| Expected path | Edition | Year | Size (bytes) | SHA-256 | Notes |
|---|---|---:|---:|---|---|
| `scans/lightfoot_1891_apostolic_fathers.pdf` | J. B. Lightfoot & J. R. Harmer, *The Apostolic Fathers* (revised texts; includes the Shepherd of Hermas) | 1891 | 32,598,336 | `61e70902ce15d4f11dc28b5d40dc5aa5853fb3330720cfef226ed081c68cb7af` | Internet Archive item visible in PDF metadata: `apostolicfathers00lighuoft` |

## Additional repair sources acquired 2026-11-03

These scans are kept outside Git; the acquisition URLs allow rehydration.
Editions and facsimiles do not count as additional independent manuscripts.

| Internet Archive item / PDF | Role | Size (bytes) | SHA-256 |
|---|---|---:|---|
| [apostolicfather01lakegoog.pdf](https://archive.org/download/apostolicfather01lakegoog/apostolicfather01lakegoog.pdf) | Kirsopp Lake, *The Apostolic Fathers*, vol. II (1917), Greek text and apparatus; physical pages 19 and 21 consulted for the opening | 12,565,229 | `231f54d5bdff97aabfaffebd43bd98a36dea110f4a59d8aae6a381f8ffe0aa04` |
| [facsimilesofatho00herm.pdf](https://archive.org/download/facsimilesofatho00herm/facsimilesofatho00herm.pdf) | Lake (1907), Athos Hermas facsimiles; acquired, direct collation pending | 7,241,953 | `c9e89bef57d68ccf74428800116dc912f0249fcba00e55a181a5cc3898a1a5e4` |
| [bwb_KU-773-309.pdf](https://archive.org/download/bwb_KU-773-309/bwb_KU-773-309.pdf) | Stählin (1906), *Clemens Alexandrinus* II; title leaf and printed p.136 (physical pp.5,154) read for bounded indirect quotation comparison | 34,791,969 | `58f50e5bf428cd918f8a792586891665196446cbe4b248027eec2e7537d943bb` |

## Michigan consultation edition

[Bonner, *A Papyrus Codex of the Shepherd of Hermas* (1934)](https://www.fulcrum.org/concern/monographs/1544bs12m),
DOI `10.3998/mpub.9690312`, is available through University of Michigan
Press/Fulcrum. A local consultation download was acquired 2026-11-03 (177
physical PDF pages). It retains a 1934 copyright notice; its text, commentary,
reconstructions and images are not vendored. Only scoped factual manuscript
readings and lacuna observations are recorded in the repair ledger. Physical
pages 110–112, 124, and 131–132 were visually inspected, corresponding to
printed pages 99–101, 113, and 120–121. A personalized download may differ
byte-for-byte on retrieval, so no fixed rehydration hash is asserted.

## Verification command for public-domain scans

```bash
shasum -a 256 sources/shepherd_of_hermas/scans/*.pdf
```
