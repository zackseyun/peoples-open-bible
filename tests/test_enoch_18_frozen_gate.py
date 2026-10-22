"""Narrow replay cannot run arbitrary tests or waive original coverage."""
import json
import unittest
from unittest.mock import patch
from tools.enoch import replay_18_pre_complete_gate as gate


class Frozen18ScopeTest(unittest.TestCase):
    def test_unregistered_case_fails_before_running_any_historical_test(self):
        with self.assertRaisesRegex(ValueError, 'registered case'):
            gate.replay('any-other-test')

    def test_descriptor_cannot_reduce_or_replace_three_original_cases(self):
        for change in ('drop_case', 'replace_method', 'replace_hash', 'replace_successor'):
            data = json.loads(gate.DESCRIPTOR.read_text())
            if change == 'drop_case':
                data['cases'].pop('export18')
            elif change == 'replace_method':
                data['cases']['individual18']['method'] = 'some_other_test'
            elif change == 'replace_hash':
                data['cases']['individual18']['test_sha256'] = '0'*64
            else:
                data['successor'] = 'not-a-reviewed-successor'
            with self.subTest(change=change), patch.object(gate.Path, 'read_text', return_value=json.dumps(data)):
                with self.assertRaisesRegex(ValueError, 'scope differs|original source/test differs'):
                    gate.replay('individual18')


if __name__ == '__main__':
    unittest.main()
