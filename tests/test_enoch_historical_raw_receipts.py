"""Recovered original outputs are history, not fresh/full-chapter certification."""
import copy
import json
import unittest
from tools.enoch import historical_evidence as h,bounded_application as t

class HistoricalRawReceiptsTest(unittest.TestCase):
    def test_exact_original_output8_unit_bindings_do_not_approve_other_units(self):
        from tools.enoch import bounded_application as current_transaction
        if (current_transaction.APPLICATIONS/'enoch_full_repair_batch11_20261022/application.json').is_file():
            # Exact original assertions remain below and run at pinned49ed;
            # separate batch11 assertions validate actual current replacements.
            from tools.enoch.replay_29_97_pre_successor import replay
            result = replay('historical-raw')
            self.assertEqual((result['tests_run'], result['skipped'], result['expected_failures']), (1, 0, 0))
            self.assertFalse(result['current_corpus_validated'])
            return
        index=t.ROOT/'sources/enoch/coverage/historical-input-bindings-20261022.json'
        accepted=h.load_current(index)
        self.assertEqual(set(accepted),{(13,v) for v in range(4,11)}|{(14,24)})
        self.assertTrue(all(not v['fresh_review'] and not v['full_chapter_count_certified_by_import'] for v in accepted.values()))
        self.assertEqual(len(h.load_current()),29) # Existing frozen import unchanged.
        self.assertEqual(len(h.load_all_current()),37)
        self.assertEqual(h.load_count_inventories(index),{})
        d=json.loads(index.read_text());self.assertFalse(d['canonical_changed'])
        for p in d['packages']:
            for u in p['units']:
                self.assertEqual(h.verdict(json.loads((t.ROOT/u['review']).read_text()),u['reference']),'accept')

    def test_exact_flat_serializer_does_not_infer_missing_fields_or_new_variants(self):
        row={'reference':'1 Enoch 13:4','source_text':'test-only','source_pages':[70], 'translation':{'text':'Test only.'}}
        result=h.reviewed_input_core(row,'flat-source-text-v1')
        self.assertEqual(result['source_text'],'test-only');self.assertIsNone(result['additional_translation_input'])
        for update in ({'source':{'text':'conflicting fixture'}},{'additional_translation_input':['unreviewed']},{'source_pages':[]}):
            with self.assertRaisesRegex(ValueError,'serializer differs'):h.reviewed_input_core(dict(row,**update),'flat-source-text-v1')
        with self.assertRaisesRegex(ValueError,'serializer differs'):h.reviewed_input_core(row,'guess-the-schema')

if __name__=='__main__':unittest.main()
