#!/usr/bin/env python3
"""Run a bounded scan review through the existing ChatGPT-signed-in Codex CLI.

Never reads auth.json, extracts credentials, invokes Vertex, installs candidates,
or grants publication approval. Results remain editorial review artifacts.
The package must supply review-input.json, review-prompt.txt and review.schema.json.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(package: Path, images: list[Path], output: Path) -> list[str]:
    args = ['codex', 'exec', '--ephemeral', '--sandbox', 'read-only',
            '--color', 'never', '--output-schema', str(package / 'review.schema.json'),
            '-o', str(output)]
    for image in images:
        args.extend(['-i', str(image)])
    return [*args, '-']


def validate_result(result: dict, expected_refs: list[str]) -> None:
    reviews = result.get('reviews', [])
    refs = [row.get('reference') for row in reviews]
    if len(refs) != len(set(refs)) or set(refs) != set(expected_refs):
        raise ValueError('Reviewer reference set differs from bounded input')
    if any(row.get('verdict') not in ('accept', 'revise', 'hold') for row in reviews):
        raise ValueError('Unknown review verdict')


def editorially_accepted(result: dict) -> bool:
    # A reviewer can find all source units recovered yet request spelling or
    # translation repairs. Structural coverage is not editorial approval.
    return result.get('chapter_complete') is True and bool(result.get('reviews')) \
        and all(row['verdict'] == 'accept' for row in result['reviews'])


def run(package: Path, images: list[Path], output_dir: Path, timeout: int = 900) -> dict:
    package = package.resolve(strict=True)
    images = [image.resolve(strict=True) for image in images]
    if not images:
        raise ValueError('At least one actual source scan image is required')
    inputs = json.loads((package / 'review-input.json').read_text())
    refs = [row['reference'] for row in inputs]
    if len(refs) != len(set(refs)):
        raise ValueError('Duplicate input references')
    login = subprocess.run(['codex', 'login', 'status'], capture_output=True, text=True, timeout=30)
    if login.returncode or 'Logged in using ChatGPT' not in login.stdout + login.stderr:
        raise RuntimeError('This review route requires the existing ChatGPT Codex login')
    hashes = {name: sha(package / name) for name in
              ('review-input.json', 'review-prompt.txt', 'review.schema.json')}
    image_hashes = {str(image): sha(image) for image in images}
    output_dir.mkdir(parents=True, exist_ok=True)
    result_file = output_dir / 'review.json'
    if result_file.exists():
        raise FileExistsError('Preserve prior review output; use a fresh output directory')
    completed = subprocess.run(command(package, images, result_file),
                               cwd=package, input=(package / 'review-prompt.txt').read_text(),
                               text=True, capture_output=True, timeout=timeout)
    log = completed.stdout + '\n' + completed.stderr
    (output_dir / 'review.log').write_text(log)
    if completed.returncode or not result_file.exists():
        raise RuntimeError(f'Codex review failed (exit {completed.returncode}); inspect saved log')
    if any(sha(package / name) != digest for name, digest in hashes.items()) or \
            any(sha(Path(image)) != digest for image, digest in image_hashes.items()):
        raise RuntimeError('Source inputs changed during review; do not use result')
    result = json.loads(result_file.read_text())
    validate_result(result, refs)
    model = re.search(r'^model:\s*(.+)$', log, re.MULTILINE)
    provenance = {'backend': 'codex-cli', 'authentication': 'ChatGPT login',
                  'model': model.group(1).strip() if model else 'not reported',
                  'package_input_sha256': hashes, 'scan_image_sha256': image_hashes,
                  'review_sha256': sha(result_file), 'canonical_translation_changed': False,
                  'human_specialist_certification': False}
    (output_dir / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--image', type=Path, action='append', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.package, args.image, args.output_dir)
    print(json.dumps({'reviews': len(result['reviews']),
                      'chapter_complete': result['chapter_complete'],
                      'editorially_accepted': editorially_accepted(result),
                      'published': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
