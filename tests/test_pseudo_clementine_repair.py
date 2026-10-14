import json
from pathlib import Path
import tempfile
import unittest

from tools.extra_texts.pseudo_clementine_repair import filtered_references


class RepairGuardsTests(unittest.TestCase):
    def test_actual_provider_filter_excludes_exact_requested_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'v0.draft.response.json').write_text(json.dumps({'choices':[{'finish_reason':'content_filter'}]}))
            (root/'v0.draft.request.json').write_text(json.dumps({'references':['6.1','6.2']}))
            self.assertEqual(filtered_references(root),{'6.1','6.2'})
            (root/'v1.draft.response.json').write_text(json.dumps({'choices':[{'finish_reason':'length'}]}))
            self.assertEqual(filtered_references(root),{'6.1','6.2'})

    def test_filter_without_reference_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'v0.review.response.json').write_text(json.dumps({'choices':[{'finish_reason':'content_filter'}]}))
            (root/'v0.review.request.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'reference-bound request'):
                filtered_references(root)


if __name__ == '__main__':
    unittest.main()
