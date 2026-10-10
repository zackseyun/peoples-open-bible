#!/usr/bin/env python3
"""Check current surface/lexical layers at historical SP issue locators."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import urlopen

from tools.textual_restoration import audit_samaritan_editorial_issues as A
from tools.textual_restoration import build_samaritan_screen as S

OUT = S.ROOT / "sources/textual_restoration/discovery/samaritan_feature_layers.2026-10-10.v1.json"
FEATURE_PINS = {
    "g_cons": "ff1f78d6fe67608fedbccda145aa715f0217b7b500003c4e50ba6a97dc9621b3",
    "g_cons_raw": "ab87f3acba16033345d16b3d569a8f80fa5f7103ec08de14a5203c0561e147b2",
    "g_cons_utf8": "6baf6b5d2240322bc83351f6bd67c914f585652e28f8e1032a736208e6ecd6a7",
    "lex": "9759a318f694ee16446ccea8bdb399616e14572e4c7ad5530f0ced60481a1fe8",
}


def parse_node_feature(raw: bytes) -> dict[int, str]:
    """Read the pinned string-node format, including implicit increasing IDs.

    Reject unsupported range syntax rather than silently expanding a new
    upstream format. This parser does not implement every Text-Fabric format.
    """
    header, data = raw.decode("utf-8").split("\n\n", 1)
    lines = header.splitlines()
    if lines[0] != "@node" or "@valueType=str" not in lines or "@version=7.1.3" not in lines:
        raise ValueError("unexpected node-feature header")
    result, node = {}, 0
    for line in data.splitlines():
        if "\t" in line:
            parts = line.split("\t")
            if len(parts) != 2 or not parts[0].isdigit():
                raise ValueError("unsupported node feature row")
            node, value = int(parts[0]), parts[1]
        else:
            node += 1
            value = line
        if node < 1 or node in result or not value:
            raise ValueError("empty, duplicate or invalid feature node")
        result[node] = value
    if not result:
        raise ValueError("empty feature")
    return result


def feature_url(name: str) -> str:
    if name not in FEATURE_PINS:
        raise ValueError("unknown feature")
    return f"https://raw.githubusercontent.com/DT-UCPH/sp/{S.COMMIT}/tf/{S.VERSION}/{name}.tf"


def load_features(directory: Path | None, fetch: bool) -> tuple[dict, list]:
    if (directory is None) == (not fetch):
        raise ValueError("select one local directory or explicit online fetch")
    features, inputs = {}, []
    for name, expected in FEATURE_PINS.items():
        if fetch:
            with urlopen(feature_url(name), timeout=30) as response:
                raw = response.read()
        else:
            raw = (directory / f"{name}.tf").read_bytes()
        if S.sha(raw) != expected:
            raise ValueError(f"{name}: pinned feature hash mismatch")
        values = parse_node_feature(raw)
        features[name] = values
        inputs.append({"feature": name, "url": feature_url(name),
                       "sha256": expected, "bytes": len(raw), "word_nodes": len(values)})
    return features, inputs


def inspect_locators(api, issues: dict, features: dict) -> list[dict]:
    words = set(api.F.otype.s("word"))
    if any(set(values) != words for values in features.values()):
        raise ValueError("feature word-node coverage differs from pinned graph")
    rows = []
    for row in A.issue_rows(issues):
        node = row["annotation_tf_node"]
        section = api.T.sectionFromNode(node)
        if api.F.otype.v(node) != "word" or not section:
            raise ValueError("historical locator does not land on a current word")
        reference = f"{S.BOOKS[section[0]]}.{section[1]}.{section[2]}"
        if reference != row["reference_label"]:
            raise ValueError("historical locator current section differs")
        signs = "".join(api.F.sign.v(slot) for slot in api.L.d(node, otype="sign"))
        utf8 = features["g_cons_utf8"][node]
        result = {
            "issue_id": row["issue_id"], "reference_label": reference,
            "annotation_version": row["annotation_data_version"],
            "current_word_node": node,
            "sign_text_sha256": S.sha(signs.encode()),
            "utf8_feature_sha256": S.sha(utf8.encode()),
            "surface_consonants_equal": S.consonants(signs) == S.consonants(utf8),
            "g_cons_equals_g_cons_raw": features["g_cons"][node] == features["g_cons_raw"][node],
        }
        if row["issue_id"] in {"3", "16"}:
            result["target_excerpt"] = {"signs_without_trailing_space": signs.rstrip(" "),
                                        **{f: values[node] for f, values in features.items()}}
        rows.append(result)
    return rows


def build(sp_directory: Path, issues_path: Path, feature_directory: Path | None, fetch: bool) -> dict:
    _, sp_inputs = S.load_sp(sp_directory)
    issues = A.pinned_json(issues_path, A.ISSUES_SHA)
    features, feature_inputs = load_features(feature_directory, fetch)
    from tf.fabric import Fabric
    api = Fabric(locations=str(sp_directory), silent="deep").load("book chapter verse sign", silent="deep")
    rows = inspect_locators(api, issues, features)
    return {
        "schema_version": "1.0.0", "checked_date": "2026-10-10",
        "scope": "Current feature-layer diagnostic at29 upstream annotation node numbers, with two bounded Exodus19:24 token excerpts; not a historical node remapping or manuscript collation",
        "source": {"commit": S.COMMIT, "version": S.VERSION,
                   "issues_sha256": A.ISSUES_SHA, "sp_inputs": sp_inputs,
                   "feature_inputs": feature_inputs,
                   "rights": "Højgaard, Naaijer and Schorch (2023), CC BY-NC4.0. Full source files remain external; only metadata and two bounded local token excerpts exported. No relicensing or manuscript-image rights implied."},
        "mapping": "Historical node numbers are inspected as current diagnostic locators only after current word type and declared section agree. This does not verify their historical token identity. Surface comparison uses the existing Hebrew-consonant normalization, not unnormalized byte equality; original hashes retain trailing spaces and presentation forms.",
        "summary": {"annotation_locators": len(rows),
                    "utf8_surface_matches": sum(r["surface_consonants_equal"] for r in rows),
                    "transliterated_features_identical": sum(r["g_cons_equals_g_cons_raw"] for r in rows)},
        "rows": rows,
        "policy": {"historical_token_identity_verified": False,
                   "historical_feature_changes_reconstructed": False,
                   "surface_agreement_certifies_diplomatic_text": False,
                   "lexical_labels_are_manuscript_letters": False,
                   "all_harmonization_layers_resolved": False,
                   "canonical_change_applied": False,
                   "generated_images_used": False,
                   "full_source_corpus_vendored": False},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sp_tf_directory", type=Path)
    parser.add_argument("issues_json", type=Path)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--feature-directory", type=Path)
    choice.add_argument("--fetch-pinned-features", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    result = build(args.sp_tf_directory, args.issues_json, args.feature_directory, args.fetch_pinned_features)
    if args.verify_only:
        if json.loads(OUT.read_text()) != result:
            raise SystemExit("Saved feature-layer diagnostic differs from reproduction")
        print("Verified current layer diagnostic from pinned sign graph and four word features")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
