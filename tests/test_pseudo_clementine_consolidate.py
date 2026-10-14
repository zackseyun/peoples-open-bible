import unittest

from tools.extra_texts import pseudo_clementine_translation as tr
from tools.extra_texts.pseudo_clementine_consolidate import choose_selections


def candidate(stamp, text="English.", verdict="accept", blocked=False, refs=("1.1",)):
    return {
        "draft_path": f"draft-{stamp}.json", "review_path": f"review-{stamp}.json",
        "draft": {"output": {"passages": [{"reference": ref, "text": text,
            "source_issues": [{"blocks_publication": True}] if blocked else []} for ref in refs]}},
        "review": {"recorded_at": stamp, "output": {"passages": [{"reference": ref,
            "verdict": verdict, "checks": {k: verdict == "accept" for k in tr.CHECKS},
            "findings": []} for ref in refs]}},
    }


class ConsolidationTests(unittest.TestCase):
    def test_missing_and_blocked_sections_are_not_invented(self):
        chosen = choose_selections([candidate("1"), candidate("2", refs=("1.2",), blocked=True)], ["1.1", "1.2", "1.3"])
        self.assertEqual([r for s in chosen for r in s["references"]], ["1.1"])

    def test_later_adverse_verdict_cannot_be_cherry_picked_away(self):
        self.assertEqual(choose_selections([candidate("1"), candidate("2", verdict="revise")], ["1.1"]), [])
        chosen = choose_selections([candidate("1"), candidate("2", verdict="revise"), candidate("3", text="Corrected.")], ["1.1"])
        self.assertEqual(chosen[0]["review"], "review-3.json")

    def test_source_order_and_shared_bundles_are_preserved(self):
        chosen = choose_selections([candidate("2", refs=("1.1", "1.2")), candidate("1", refs=("1.3",))], ["1.1", "1.2", "1.3"])
        self.assertEqual(chosen[0]["references"], ["1.1", "1.2"])
        self.assertEqual(chosen[1]["references"], ["1.3"])


if __name__ == "__main__":
    unittest.main()
