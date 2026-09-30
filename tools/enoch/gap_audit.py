#!/usr/bin/env python3
"""Retired oracle-derived 1 Enoch patcher.

The historical implementation could copy from the rights-ambiguous Beta
maṣāḥǝft validation oracle into POB source, mark AI-appended English as
reviewed, and push it directly to main. That path must not be used. Git history
preserves it for audit; this entrypoint now fails closed.

Use ``tools/enoch/audit_pob_source_coverage.py`` for a read-only inventory,
then draft from the public-domain Charles 1906 Geʿez OCR recovered by
``tools/enoch/verse_parser.py``. Editorial review and normal release gates
remain separate.
"""
from __future__ import annotations

import sys


def main() -> int:
    print(
        "This legacy oracle-derived patcher is retired. Run "
        "tools/enoch/audit_pob_source_coverage.py instead; never derive POB "
        "text from the Beta maṣāḥǝft validation oracle.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
