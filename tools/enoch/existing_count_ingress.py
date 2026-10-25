"""Reuse a previously paired full source count for an exact partial language unit.

This is not a new count, full-chapter language vote, or reader-release rule.
The legacy same-input full-count certificate remains strict and unchanged.
"""
import json
from tools.enoch import bounded_application as t

INDEX='sources/enoch/coverage/count52-69-20261022/paired-count-index-v2.json'
INDEX_SHA='5abf81f5ee516b3052f79ab1ad84e2ae0f664ff0456052c484b422091328efe1'


def validate(manifest):
    declarations=manifest.get('existing_paired_count_ingress',[])
    if not isinstance(declarations,list):raise ValueError('Existing paired-count ingress must be an explicit list')
    if not declarations:return {}
    # This fixed profile was already imported independently of language packages.
    raw=t.artifact(t.ROOT,INDEX).read_bytes()
    if t.sha(raw)!=INDEX_SHA:raise ValueError('Existing paired-count profile index differs')
    from tools.enoch import structural_count_profiles
    counts=structural_count_profiles.load(t.artifact(t.ROOT,INDEX),root=t.ROOT)
    seen=set();out={};chapters={t.parse_ref(r)[0]for r in manifest['references']}
    other={r['chapter']for k in('chapter_inventories','source_only_count_inventories')for r in manifest.get(k,[])}
    for row in declarations:
        c=row.get('chapter')
        if (type(c)is not int or c in seen or c in other or c not in chapters or c not in counts
                or row.get('profile_index')!=INDEX or row.get('profile_index_sha256')!=INDEX_SHA
                or row.get('independent_count_confirmation')is not True
                or row.get('wording_approval')is not False or row.get('reader_release_policy_changed')is not False
                or row.get('units')!=counts[c]['units']):
            raise ValueError('Existing paired-count ingress scope, evidence or approval limit differs')
        if any(v>len(row['units'])for chapter,v in map(t.parse_ref,manifest['references'])if chapter==c):
            raise ValueError('Individual unit exceeds existing paired source count')
        seen.add(c);out[c]=counts[c]
    return out
