"""Reproduce the bounded Jeroboam note application; never writes files."""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import export_mobile_bible as exporter

CONTRACT = ROOT / 'sources/textual_restoration/comparisons/kings12_reader_contract.2026-10-17.v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['preflight', 'applied'])
    parser.add_argument('--structural-only', action='store_true')
    args = parser.parse_args()
    c = json.loads(CONTRACT.read_text())
    item = c['record']
    raw_archive = subprocess.check_output(
        ['git', 'archive', c['baseline_commit'], c['book_baseline']['path']], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(raw_archive)) as archive:
        raw = {m.name: archive.extractfile(m).read() for m in archive.getmembers()
               if m.isfile() and m.name.endswith('.yaml')}
    assert len(raw) == c['book_baseline']['yaml_count']
    assert digest({p: sha(b) for p, b in raw.items()}) == c['book_baseline']['sha256']
    for p, expected in c['input_pins'].items():
        assert sha((ROOT / p).read_bytes()) == expected, p
    before = yaml.safe_load(raw[item['path']])
    assert sha(raw[item['path']]) == item['before_sha256']
    candidate_raw = (ROOT / item['candidate']).read_bytes()
    assert sha(candidate_raw) == item['candidate_sha256']
    candidate = yaml.safe_load(candidate_raw)
    expected = copy.deepcopy(before)
    expected['translation']['text'] = item['text']
    expected['translation']['footnotes'].append(c['new_note'])
    expected['status'] = 'draft'
    expected['cross_check'] = {'status': 'needs_review'}
    expected.pop('revision_pass')
    expected['review_history'] = copy.deepcopy(before.get('review_history', []))
    for field in c['archives']:
        value = before
        for part in field.split('.'):
            value = value[part]
        expected['review_history'].append({
            'field': field, 'value': copy.deepcopy(value),
            'archived_from_baseline_commit': c['baseline_commit'],
            'archived_from_baseline_sha256': item['before_sha256'],
            'historical_review_inputs_verified': False,
            'certifies_this_candidate': False,
        })
    expected['revisions'] = copy.deepcopy(before.get('revisions', [])) + [c['revision_record']]
    assert candidate == expected, 'Unexpected full-record delta'
    Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(candidate)
    plain = lambda s: re.sub(r'\[[a-z]+\]', '', s)
    assert plain(candidate['translation']['text']) == plain(before['translation']['text'])
    assert re.findall(r'\[([a-z]+)\]', item['text']) == ['a', 'b', 'c']
    assert 'assembly[b] of Israel' in item['text'] and 'Rehoboam[c], saying,' in item['text']
    assert candidate['source'] == before['source'] and candidate['ai_draft'] == before['ai_draft']
    for p, content in raw.items():
        wanted = candidate_raw if args.mode == 'applied' and p == item['path'] else content
        assert (ROOT / p).read_bytes() == wanted, p
    protected = ROOT / c['protected_unrelated']['path']
    if protected.exists():
        assert sha(protected.read_bytes()) == c['protected_unrelated']['sha256']
    result = {'mode': args.mode, 'schema_exact_delta_archives_anchors': 'pass',
              'unchanged_other_canonical_records': len(raw) - 1,
              'source_marker_free_english_AI_provenance_unchanged': True,
              'protected_unrelated_present': protected.exists(),
              'protected_unrelated_unchanged_if_present': True, 'export_checked': False}
    if not args.structural_only:
        records = {(int(Path(p).parent.name), int(Path(p).stem)): yaml.safe_load(b)
                   for p, b in raw.items()}
        def render(values):
            def load(code, chapter, verse):
                assert code == '1KI'
                return values[(chapter, verse)]
            with patch.object(exporter, 'load_translation_record', side_effect=load):
                return exporter.export_book('1KI')
        old = render(records)
        records[(12, 3)] = candidate
        new = render(records)
        index = lambda b: {(ch['chapter'], v['verse']): v
                           for ch in b['chapters'] for v in ch['verses']}
        a, b = index(old), index(new)
        changed = sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))
        assert changed == [(12, 3)]
        restored = copy.deepcopy(new)
        for ch in restored['chapters']:
            for i, verse in enumerate(ch['verses']):
                if (ch['chapter'], verse['verse']) == (12, 3):
                    ch['verses'][i] = a[(12, 3)]
        assert restored == old, 'Other exported unit or metadata changed'
        assert b[(12, 3)]['text'] == item['text']
        assert b[(12, 3)]['footnotes'] == candidate['translation']['footnotes']
        if args.mode == 'applied':
            assert exporter.load_translation_record('1KI', 12, 3) == candidate
            assert exporter._export_record_verse(3, candidate) == b[(12, 3)]
        result.update(export_checked=True, chapter_count=len(new['chapters']),
                      unit_count=len(b), changed_export_ids=changed,
                      other_exported_units_unchanged=len(b) - 1,
                      before_export_sha256=digest(old), candidate_export_sha256=digest(new),
                      actual_live_loader_verified=args.mode == 'applied')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
