"""One explicit same-request diagnostic recovery for old unclassified failures.

Never changes a prompt, model, endpoint or permission, and never retries a known
authorization/content-filter failure. Preserves the original failed receipt.
"""
import argparse
import fcntl
import json
from pathlib import Path
import re

from tools.extra_texts import pseudo_clementine_pages as p


def recover(page: int, cache: Path) -> dict:
    directory = p.SOURCE / "pages-blind" / f"{page:03d}"
    with (directory / ".lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        failures = []
        for path in sorted(directory.glob("*.response.attempt*.json")):
            receipt = json.loads(path.read_text())
            if receipt.get("status") != "error" or receipt.get("error_kind") != "terminal_cli_error":
                continue
            # A later successful attempt already resolved this exact request.
            request_hash = receipt["request_sha256"]
            stem = re.sub(r"\.attempt\d+\.json$", "", path.name)
            related = [json.loads(f.read_text()) for f in directory.glob(stem + "*.json")]
            if any(r.get("status") == "success" and r.get("request_sha256") == request_hash for r in related):
                continue
            request_path = cache / f"{request_hash}.request.json"
            if not request_path.exists():
                raise ValueError("Exact cached request is missing; reconstruct it through process_page first")
            body = json.loads(request_path.read_text())
            if p.sha(p.canonical(body)) != request_hash:
                raise ValueError("Cached request hash mismatch")
            recovery = directory / (stem + ".recovery1")
            prior = list(directory.glob(recovery.name + ".attempt*.json"))
            if prior:
                failures.append({"page": page, "receipt": path.name, "status": "diagnostic_already_recorded"})
                continue
            # The original was a terminal process result, not an observation timeout.
            response = p.invoke(body, cache, recovery)
            failures.append({"page": page, "receipt": path.name, "status": "diagnostic_completed",
                             "finish_reason": response.get("choices", [{}])[0].get("finish_reason")})
        return {"page": page, "recoveries": failures}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", type=int, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(recover(args.page, args.cache)), flush=True)
