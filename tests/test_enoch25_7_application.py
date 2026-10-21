"""Keep the original two-check gate frozen; verify current successors separately."""
import unittest
from tools.enoch import legacy_individual_evidence as legacy
from tools.enoch.current_evidence import verify_current
from tools.enoch.replay_legacy25_7 import replay

class Enoch257Application(unittest.TestCase):
    def test_original_two_checks_replay_unchanged_at_their_applied_checkpoint(self):
        result=replay()
        self.assertEqual(result['tests_run'],2)
        self.assertTrue(result['passed'])
        self.assertFalse(result['current_corpus_validated'])
        self.assertFalse(result['application_approved'])

    def test_current_exact_unit_or_explicitly_reviewed_metadata_successor(self):
        result=verify_current(legacy.transaction.APPLICATIONS/legacy.NAME)
        self.assertEqual(result['references'],['1 Enoch 25:7'])
        self.assertTrue(result['current_targets_or_reviewed_successors_verified'])
        self.assertFalse(result['chapter_publication_approval'])
        self.assertFalse(result['graphic_publication_approved'])

if __name__=='__main__':unittest.main()
