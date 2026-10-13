import json
from pathlib import Path
import unittest

from tools.textual_restoration.index_published_parallels import index_document


def fixture(primary=None, parallel=None):
    primary = primary or '<span class="word" data-word-id="10">primary-only</span>'
    parallel = parallel or ('<a href="/transcriptions/Hab/2026-10-06/index.html#v1">(Hab 1,1)</a>'
                            '<span class="word" data-word-id="200" data-parallel-id="10">parallel-only</span>')
    return ('<html><body id="transcription_id_4"><time datetime="2026-10-06"></time>'
            '<main><table class="chapter-column" data-name="1"><tbody>'
            '<tr class="line-verse" id="c1-i10" data-name="1"><td class="line-text">'
            + primary + '</td></tr><tr class="parallel-line"><td><ul>'
            '<li data-manuscript-id="1136">' + parallel + '</li></ul></td></tr>'
            '</tbody></table></main></body></html>').encode()


class PublishedParallelIndexTests(unittest.TestCase):
    def test_primary_and_parallel_ids_remain_separate_without_text_export(self):
        data = index_document(fixture())
        row = data["rows"][0]
        self.assertEqual(row["primary_word_ids"], ["10"])
        self.assertEqual(row["parallel_groups"][0]["primary_word_ids"], ["10"])
        self.assertNotIn("primary-only", json.dumps(data))
        self.assertNotIn("parallel-only", json.dumps(data))
        self.assertFalse(data["policy"]["quotations_adjudicated"])
        self.assertFalse(data["policy"]["preservation_assessed"])

    def test_alternative_ids_are_not_extra_primary_words(self):
        primary = ('<span class="word" data-word-id="10">main</span>'
                   '<span class="alternative-reading level-1">'
                   '<span class="word" data-word-id="10">alternate</span>'
                   '<span class="alternative-reading level-2">'
                   '<span class="word" data-word-id="10">nested</span></span></span>')
        row = index_document(fixture(primary=primary))["rows"][0]
        self.assertEqual(row["primary_word_ids"], ["10"])
        self.assertEqual(row["alternative_word_ids"], ["10"])

    def test_navigation_does_not_create_primary_rows(self):
        raw = fixture().replace(b'<main>', b'<ol><li><a href="#c1-i10">1</a></li></ol><main>')
        self.assertEqual(len(index_document(raw)["rows"]), 1)

    def test_split_reference_groups_keep_their_own_linked_word_ids(self):
        primary = '<span class="word" data-word-id="10">a</span><span class="word" data-word-id="11">b</span>'
        parallel = ('<span class="word" data-word-id="0">…</span>'
                    '<a href="/transcriptions/Hab/2026-10-06/index.html#v1">(Hab 1,1)</a>'
                    '<span class="word" data-parallel-id="10">x</span>'
                    '<a href="/transcriptions/Hab/2026-10-06/index.html#v2">(Hab 1,2)</a>'
                    '<span class="word" data-parallel-id="11">y</span>')
        groups = index_document(fixture(primary, parallel))["rows"][0]["parallel_groups"]
        self.assertEqual([g["primary_word_ids"] for g in groups], [["10"], ["11"]])

    def test_foreign_primary_word_join_fails(self):
        with self.assertRaisesRegex(ValueError, "outside current"):
            index_document(fixture().replace(b'data-parallel-id="10"', b'data-parallel-id="99"'))

    def test_separate_dom_and_stable_word_ids_resolve_to_stable_ids(self):
        primary = ('<span id="395445" class="word" data-word-id="394780">x</span>'
                   '<span id="395446" class="word" data-word-id="394781">y</span>')
        parallel = ('<a href="/transcriptions/Ez/2026-05-21/index.html#v26">(Ez 36,26)</a>'
                    '<span class="word" data-parallel-id="395445">parallel</span>'
                    '<span class="word" data-parallel-id="395446">parallel</span>')
        row = index_document(fixture(primary, parallel))["rows"][0]
        self.assertEqual(row["primary_word_ids"], ["394780", "394781"])
        self.assertEqual(row["parallel_groups"][0]["primary_word_ids"],
                         ["394780", "394781"])

    def test_document_can_use_stable_id_despite_separate_dom_id(self):
        primary = '<span id="100" class="word" data-word-id="10">x</span>'
        row = index_document(fixture(primary=primary))["rows"][0]
        self.assertEqual(row["parallel_groups"][0]["primary_word_ids"], ["10"])

    def test_ambiguous_namespace_fails_instead_of_choosing_a_word(self):
        primary = ('<span id="11" class="word" data-word-id="10">x</span>'
                   '<span id="10" class="word" data-word-id="11">y</span>')
        with self.assertRaisesRegex(ValueError, "ambiguous parallel join"):
            index_document(fixture(primary=primary))

    def test_mixed_namespace_links_fail_instead_of_per_word_fallback(self):
        primary = ('<span id="100" class="word" data-word-id="10">x</span>'
                   '<span id="101" class="word" data-word-id="11">y</span>')
        parallel = ('<a href="/transcriptions/Ez/2026-05-21/index.html#v26">(Ez 36,26)</a>'
                    '<span class="word" data-parallel-id="100">parallel</span>'
                    '<span class="word" data-parallel-id="11">parallel</span>')
        with self.assertRaisesRegex(ValueError, "mixed join namespaces"):
            index_document(fixture(primary, parallel))

    def test_duplicate_dom_join_id_fails_even_with_distinct_stable_ids(self):
        primary = ('<span id="100" class="word" data-word-id="10">x</span>'
                   '<span id="100" class="word" data-word-id="11">y</span>')
        with self.assertRaisesRegex(ValueError, "duplicate primary DOM"):
            index_document(fixture(primary=primary))

    def test_foreign_dom_word_join_fails(self):
        primary = '<span id="100" class="word" data-word-id="10">x</span>'
        parallel = ('<a href="/transcriptions/Ez/2026-05-21/index.html#v26">(Ez 36,26)</a>'
                    '<span class="word" data-parallel-id="101">parallel</span>')
        with self.assertRaisesRegex(ValueError, "outside current"):
            index_document(fixture(primary, parallel))

    def test_duplicate_primary_id_fails(self):
        with self.assertRaisesRegex(ValueError, "duplicate primary word"):
            index_document(fixture(primary='<span class="word" data-word-id="10">a</span>' * 2))

    def test_real_word_before_parallel_reference_fails(self):
        with self.assertRaisesRegex(ValueError, "before reference"):
            index_document(fixture(parallel='<span class="word" data-word-id="200">x</span>'))

    def test_observed_span_and_final_table_repairs_are_disclosed(self):
        raw = fixture().replace(b'<li data-manuscript-id="1136">',
                                b'<li data-manuscript-id="1136"><span class="line-text">')
        raw = raw.replace(b'</table></main>', b'</table></table></main>')
        self.assertEqual(index_document(raw)["html_repairs"],
                         {"implicit_span_closures": 1, "extra_final_table_end": 1})

    def test_truncated_or_structurally_invalid_html_fails(self):
        invalid = [fixture()[:-7],
                   fixture().replace(b'</td></tr>', b'</tr>'),
                   fixture().replace(b'</table></main>', b'</table></table><span>x</span></main>'),
                   fixture().replace(b'</table></main>', b'</table></table>text</main>'),
                   fixture().replace(b'<time datetime="2026-10-06">', b'<time>'),
                   fixture().replace(b'/transcriptions/Hab/', b'https://other.example/transcriptions/Hab/'),
                   fixture().replace(b'</tbody>', b'<tr class="parallel-line"></tr></tbody>')]
        for raw in invalid:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    index_document(raw)

    def test_saved_manual_map_is_not_an_automatic_quotation_claim(self):
        path = Path(__file__).resolve().parents[1] / "sources/textual_restoration/comparisons/habakkuk_pesher_quotation_map.2026-10-12.v1.json"
        data = json.loads(path.read_text())
        self.assertEqual(data["source"]["primary_rows"], 206)
        self.assertEqual(len(data["quotation_segments"]), 46)
        self.assertEqual(len({p for s in data["quotation_segments"] for p in s["passages"]}), 37)
        self.assertFalse(data["policy"]["full_preservation_implied"])
        self.assertFalse(data["policy"]["source_priority_adjudicated"])
        self.assertFalse(data["policy"]["canonical_changes"])
        self.assertTrue(any(s["start"][2] == "9096" for s in data["quotation_segments"]))
        self.assertTrue(any(s["start"][2] == "9402" for s in data["quotation_segments"]))
        self.assertEqual(data["known_link_role_exception"]["primary_word_ids"], ["10039", "10040"])


if __name__ == "__main__":
    unittest.main()
