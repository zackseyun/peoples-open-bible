"""Run the installed Azure CLI with finite HTTP socket deadlines.

Uses the CLI's existing identity and normal `az rest` arguments. It does not
retrieve credentials, alter models/policies, or supervise/kill a live request.
Only newly launched requests use these network-layer deadlines.
"""
from __future__ import annotations

import sys

CONNECT_TIMEOUT_SECONDS = 30
READ_TIMEOUT_SECONDS = 600


def install_deadlines(session_class):
    original = session_class.send

    def bounded_send(self, request, **kwargs):
        if kwargs.get("timeout") is None:
            kwargs["timeout"] = (CONNECT_TIMEOUT_SECONDS, READ_TIMEOUT_SECONDS)
        return original(self, request, **kwargs)

    session_class.send = bounded_send


def main() -> int:
    import requests
    from azure.cli.core import get_default_cli
    install_deadlines(requests.Session)
    return get_default_cli().invoke(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
