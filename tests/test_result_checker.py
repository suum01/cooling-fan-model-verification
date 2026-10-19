"""Protect the verification tool from false passes on bad output."""
import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('checker',Path(__file__).resolve().parents[1]/'scripts/python/check_results.py')
checker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class ResultCheckerTests(unittest.TestCase):
    def setUp(self):
        self.expected=[{'time':'0','fan_cmd':'0','fault_flag':'0'},
                       {'time':'0.01','fan_cmd':'1','fault_flag':'0'}]

    def test_correct_output(self):
        self.assertEqual(checker.compare(self.expected,self.expected),'')

    def test_missing_samples_fail(self):
        self.assertTrue(checker.compare(self.expected,self.expected[:1]))

    def test_duplicate_timestamp_fails(self):
        bad=[dict(r) for r in self.expected]
        bad[1]['time']='0'
        self.assertTrue(checker.compare(self.expected,bad))

    def test_wrong_boolean_fails(self):
        bad=[dict(r) for r in self.expected]
        bad[1]['fan_cmd']='0'
        self.assertTrue(checker.compare(self.expected,bad))

    def test_invalid_values_fail(self):
        for value in ('nan','inf','0.5','garbage'):
            with self.subTest(value=value):
                bad=[dict(r) for r in self.expected]
                bad[1]['fan_cmd']=value
                self.assertTrue(checker.compare(self.expected,bad))


if __name__=='__main__':
    unittest.main()
