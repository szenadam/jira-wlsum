import unittest

from jira_worklog_sum import convert_to_seconds
from jira_worklog_sum import check_arguments

class TestConvertToSeconds(unittest.TestCase):
    def test_minutes(self):
        self.assertEqual(convert_to_seconds('35m'), 2100)
    def test_zero_minutes(self):
        self.assertEqual(convert_to_seconds('0m'), 0)
    def test_hours(self):
        self.assertEqual(convert_to_seconds('1h'), 3600)
    def test_zero_hour(self):
        self.assertEqual(convert_to_seconds('0h'), 0)
    def test_days(self):
        self.assertEqual(convert_to_seconds('1d'), 86400)
    def test_zero_days(self):
        self.assertEqual(convert_to_seconds('0d'), 0)
    def test_weeks(self):
        self.assertEqual(convert_to_seconds('1w'), 604800)
    def test_zero_weeks(self):
        self.assertEqual(convert_to_seconds('0w'), 0)

class TestCheckArguments(unittest.TestCase):
    def test_zero_arguments(self):
        with self.assertRaises(SystemExit) as cm:
            check_arguments()
        self.assertEqual(cm.exception.code, 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)