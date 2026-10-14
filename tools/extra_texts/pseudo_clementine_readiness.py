"""Audit current evidence for all four works without changing acceptance or publication."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from tools.extra_texts import pseudo_clementine_acceptance as acceptance
from tools.extra_texts import pseudo_clementine_pages as pages
from tools.extra_texts import pseudo_clementine_run as runner
from tools.extra_texts import pseudo_clementine_translation as translation
from tools.extra_texts.pseudo_clementine_selected import load_page, load_selected


def page_inventory() -> dict:
    verified, unverified = [], []
    for page in range(45, 242):
        try:
            _, proof = load_page(page)
            verified.append({"pdf_page": page, "printed_page": proof["printed_page"],
                             "evidence": proof["checked_path"]})
        except FileNotFoundError:
            unverified.append({"pdf_page": page, "status": "accepted_evidence_missing"})
        except (ValueError, KeyError) as exc:
            unverified.append({"pdf_page": page, "status": "evidence_requires_attention", "reason": str(exc)})
    return {"required_pages": 197, "verified_count": len(verified),
            "verified": verified, "unverified": unverified,
            "complete": not unverified}


def work_status(work: str) -> dict:
    result = {"work": work, "title": translation.source.WORKS[work][2],
              "live_publication": "not_verified", "accepted_references": [],
              "ready_for_complete_export": False}
    try:
        source = load_selected(work)
        result["source"] = {"status": "complete_checked_source",
                            "references": [row["reference"] for row in source["passages"]]}
    except (FileNotFoundError, ValueError, KeyError) as exc:
        result["source"] = {"status": "not_complete_or_not_verified", "reason": str(exc)}
        return result
    directory = translation.source.SOURCE_ROOT / work
    try:
        if work == "pseudo_clementine_peter_to_james":
            workflow = directory / "translation_workflow"
            draft = json.loads((workflow / "lagarde-v3.draft.record.json").read_text())
            review = json.loads((workflow / "lagarde-v3.review.record.json").read_text())
            request = json.loads((workflow / "lagarde-v3.review.request.json").read_text())
            response = json.loads((workflow / "lagarde-v3.review.response.json").read_text())
            translation.prepare(work, draft["references"], pages.REVIEWER, draft, source_variant="lagarde1865")
            actual = translation.validate_response(request, response)
            if actual["output_hash"] != review["output_hash"] or not runner.accepted(draft, review):
                raise ValueError("Peter review is not accepted current-source evidence")
            result["accepted_references"] = draft["references"]
        else:
            complete_path = directory / "translation_workflow/accepted-complete.selections.json"
            partial_path = directory / "translation_workflow/accepted-partial.selections.json"
            if not partial_path.exists():
                partial_path = directory / "translation_workflow/lagarde-batch-v1/accepted-sections-partial.selections.json"
            selections_path = complete_path if complete_path.exists() else partial_path
            if selections_path.exists():
                selections = json.loads(selections_path.read_text())
                checked = acceptance.collect(work, selections, complete=selections_path == complete_path)
                result["accepted_references"] = [row["reference"] for row in checked["passages"]]
            else:
                result["acceptance_note"] = "No consolidated selection has passed the acceptance collector"
        result["missing_review_references"] = [ref for ref in result["source"]["references"] if ref not in result["accepted_references"]]
        result["ready_for_complete_export"] = not result["missing_review_references"]
    except (FileNotFoundError, ValueError, KeyError) as exc:
        result["acceptance_error"] = str(exc)
    return result


def audit() -> dict:
    works = [work_status(work) for work in translation.source.WORKS]
    return {"audited_at": datetime.now(timezone.utc).isoformat(),
            "scope": "All four Pseudo-Clementine works; no canon change",
            "source_pages": page_inventory(), "works": works,
            "all_work_reviews_complete": all(work["ready_for_complete_export"] for work in works),
            "publication_verified": False,
            "publication_note": "This local evidence audit does not check a live deployment and cannot establish public availability."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"verified_source_pages": result["source_pages"]["verified_count"],
                      "required_source_pages": 197,
                      "works": [{"work": w["work"], "accepted_sections": len(w["accepted_references"]),
                                 "complete_export_ready": w["ready_for_complete_export"],
                                 "error": w.get("acceptance_error")} for w in result["works"]],
                      "publication_verified": False},ensure_ascii=False,indent=2))
