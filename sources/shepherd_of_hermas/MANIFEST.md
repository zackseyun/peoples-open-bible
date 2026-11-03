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

## Verification command

```bash
shasum -a 256 sources/shepherd_of_hermas/scans/*.pdf
```
