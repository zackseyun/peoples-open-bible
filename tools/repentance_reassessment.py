#!/usr/bin/env python3
"""Apply/check the exact, contextual reconsideration of the 397 earlier records.

No runtime string replacement. The reviewed plan pins every input and output;
preflight every record before writing any. Never mutate historical source layers.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from datetime import datetime, timezone
try:
    from tools import reorientation_policy as prior
except ImportError:
    import reorientation_policy as prior

ROOT = Path(__file__).resolve().parents[1]
POLICY = 'repentance-contextual-2026-10-13'
PLAN_REL = 'config/terminology/repentance-contextual-2026-10-13.json'
PLAN = ROOT / PLAN_REL
REPORT = 'docs/REPENTANCE_REASSESSMENT_2026-10-13.md'
SHA = lambda text: hashlib.sha256(text.encode() if isinstance(text, str) else text).hexdigest()
FIELDS = ('translation', 'lexical_decisions', 'theological_decisions',
          'simplification_decisions', 'interpretive_expansions', 'retained_terms',
          'translation_notes', 'terminology_revision', 'status', 'cross_check')

@lru_cache(maxsize=1)
def plan_by_path():
    return {r['path']: r for r in json.loads(PLAN.read_text())['records']}

def approved_errors(path, doc):
    """Check committed output, not a mutable hash supplied by the record itself."""
    try:
        name = Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return ['Reassessment path outside canonical root']
    item = plan_by_path().get(name)
    meta = doc.get('terminology_revision') or {}
    if item is None:
        return ['Unknown reassessment record'] if meta.get('current_policy_id') == POLICY else []
    errors = []
    if meta.get('current_policy_id') != POLICY:
        return ['Contextual repentance review has not been applied']
    if doc.get('translation', {}).get('text') != item['after_text']:
        errors.append('Reader text differs from exact contextual repentance decision')
    if prior.digest(doc.get('source') or {}) != item['source_sha256']:
        errors.append('Recorded source differs from reviewed source')
    marker = item['reader_note_marker']
    notes = [n for n in doc['translation'].get('footnotes', []) if n.get('marker') == marker]
    if len(notes) != 1 or notes[0].get('text') != item['reader_note']:
        errors.append('Contextual reader explanation differs from reviewed note')
    for update in item['lexical_updates']:
        entries = doc.get('lexical_decisions') or []
        if (len(entries) <= update['index'] or
            entries[update['index']].get('source_word') != update['source_word'] or
            entries[update['index']].get('chosen') != update['after_chosen']):
            errors.append('Live lexical decision differs from reviewed choice')
    if meta.get('after_text_sha256') != item['after_text_sha256']:
        errors.append('Revision output hash differs from plan')
    return errors

def superseded(item):
    """Remove only the previous policy's live judgments; archive them first."""
    if not isinstance(item, dict):
        return False
    return (item.get('doctrine_reference') == 'DOCTRINE.md: Reorientation terminology (2026-10-11)'
            or item.get('issue') == 'Context-sensitive reorientation terminology'
            or item.get('term') == 'reorient / reorientation'
            or item.get('pob_phrase') == 'reorient / reorientation'
            or item.get('risk') == 'Reorient is less common English and explicit Godward wording is a contextual expansion.'
            or item.get('reasoning_layer_used') == 'Maintainer-approved contextual wording follow-up')

def build_record(doc, item, baseline, timestamp):
    result = copy.deepcopy(doc)
    for field in FIELDS:
        if field in doc:
            # Whole translation is available at the pinned input. Avoid duplicating
            # 100k-character historical chapters in every later audit record.
            entry = {'field': field, 'archived_by': POLICY, 'baseline_commit': baseline,
                     'baseline_path': item['path'], 'sha256': prior.digest(doc[field]),
                     'certifies_this_candidate': False}
            if field != 'translation':
                entry['value'] = copy.deepcopy(doc[field])
            result.setdefault('review_history', []).append(entry)
    result['translation']['text'] = item['after_text']
    for note in result['translation'].get('footnotes', []):
        if note['marker'] == item['reader_note_marker']:
            note['text'] = item['reader_note']
        elif item['id'] == 'MAN.1.8' and 'did not set reorientation' in note.get('text', ''):
            note['text'] = 'Or "did not set repentance before the righteous." The Greek verb can mean "set" or "appoint"; preserve the negation.'
        elif item['id'] == 'WIS.12.10' and 'opportunity for reorientation' in note.get('text', ''):
            note['text'] = 'Or "you were giving an opportunity for repentance." Greek topos supplies the image of room or place.'
        elif item['id'] == 'MAT.3.2' and '"Toward God" makes' in note.get('text', ''):
            note['text'] = 'Repent calls for changed disposition and conduct in response to the kingdom proclamation, not merely regret or a different opinion.'
    for update in item['lexical_updates']:
        lex = result['lexical_decisions'][update['index']]
        if lex.get('source_word') != update['source_word'] or lex.get('chosen') != update['before_chosen']:
            raise ValueError('Lexical input drift: ' + item['path'])
        alternatives = list(lex.get('alternatives') or [])
        if update['before_chosen'] != update['after_chosen'] and update['before_chosen'] not in alternatives:
            alternatives.insert(0, update['before_chosen'])
        lex.update(chosen=update['after_chosen'], alternatives=alternatives,
                   rationale=item['rationale'] + ' Contextual editorial assessment, not independent scholarly certification.',
                   lexicon='Recorded source/witness and contextual review; see ' + REPORT,
                   doctrine_reference='DOCTRINE.md: Repentance terminology (2026-10-13)')
    for field in ('theological_decisions', 'simplification_decisions', 'interpretive_expansions', 'retained_terms'):
        if isinstance(result.get(field), list):
            result[field] = [x for x in result[field] if not superseded(x)]
    if isinstance(result.get('translation_notes'), dict):
        for key, value in result['translation_notes'].items():
            if isinstance(value, list):
                result['translation_notes'][key] = [x for x in value if not superseded(x)]
    result.setdefault('theological_decisions', []).append({
        'issue': 'Contextual repentance reassessment',
        'chosen_reading': item['after_text'].replace('[' + item['reader_note_marker'] + ']', '')
            if len(item['after_text']) < 1500 else 'Exact reader wording is recorded in ' + PLAN_REL + '#' + item['path'],
        'alternative_readings': ['Prior wording and its rationale remain at the pinned baseline and in review history.'],
        'rationale': item['rationale'],
        'doctrine_reference': 'DOCTRINE.md: Repentance terminology (2026-10-13)'})
    if item['path'].startswith('translation_simplified/') and 'repent' in item['after_text'].lower():
        result.setdefault('retained_terms', []).append({'term': 'repent / repentance',
            'reason': 'Recognizable shared terminology, explained in its local context rather than replaced by technical reorientation language.'})
    result['status'] = 'draft'
    result['cross_check'] = {'status': 'needs_review'}
    result.pop('revision_pass', None)
    result.pop('source_audit', None)
    result['terminology_revision'].update(current_policy_id=POLICY,
        after_text_sha256=item['after_text_sha256'], independent_scholar_review=False,
        contextual_reassessment={'policy_id': POLICY, 'timestamp': timestamp, 'baseline_commit': baseline,
            'input_file_sha256': item['input_file_sha256'], 'decision': item['decision'],
            'maintainer_approval_scope': 'Reconsider each earlier English terminology change; not a claim of individual human or scholarly review.'})
    revision = {'timestamp': timestamp, 'adjudicator': 'Codex: maintainer-authorized contextual reassessment',
        'category': 'terminology', 'policy_id': POLICY, 'baseline_commit': baseline,
        'baseline_path': item['path'], 'from_sha256': item['before_text_sha256'],
        'to_sha256': item['after_text_sha256'], 'rationale': item['rationale'],
        'exact_replacement_record': PLAN_REL + '#' + item['path']}
    result.setdefault('revisions', []).append(revision)
    return result

def run(apply=False, check=False):
    plan = json.loads(PLAN.read_text())
    original = json.loads(prior.PLAN.read_text())
    names = [r['path'] for r in plan['records']]
    if len(names) != 397 or len(set(names)) != 397 or set(names) != {r['path'] for r in original['records']}:
        raise ValueError('Reassessment must cover exactly all original 397 records')
    prepared, errors, already = [], [], 0
    timestamp = datetime.now(timezone.utc).isoformat()
    for item in plan['records']:
        path = ROOT / item['path']
        raw = path.read_bytes()
        doc = prior.load(path)
        if (doc.get('terminology_revision') or {}).get('current_policy_id') == POLICY:
            errors.extend(item['path'] + ': ' + e for e in approved_errors(path, doc))
            already += 1
            continue
        if check:
            errors.append(item['path'] + ': not applied')
            continue
        if SHA(raw) != item['input_file_sha256'] or prior.digest(doc.get('source') or {}) != item['source_sha256']:
            errors.append(item['path'] + ': input/source changed since review')
            continue
        if SHA(item['after_text']) != item['after_text_sha256']:
            errors.append(item['path'] + ': plan output hash mismatch')
            continue
        new = build_record(doc, item, plan['baseline_commit'], timestamp)
        errors.extend(item['path'] + ': ' + e for e in approved_errors(path, new))
        prepared.append((path, prior.patch_top_level(raw.decode(), doc, new)))
    if errors:
        raise ValueError('\n'.join(errors))
    if apply:
        for path, raw in prepared:
            path.write_text(raw)
    return {'reviewed': len(names), 'prepared': len(prepared), 'already_applied': already,
            'written': len(prepared) if apply else 0, 'check': check}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--apply', action='store_true')
    group.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print(json.dumps(run(args.apply, args.check)))
